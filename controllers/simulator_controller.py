from PyQt5.QtCore import QTimer
from utils.xml_parser import *
from utils.coordinates import *
from models.gnb_loader import *
from models.trajectory import *
from models.event import *

class SimulatorController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_simulation)
        
    def start(self):
        self.model.running = True

    def set_virtual_time(self, virtual_time):
        self.model.sim_time = virtual_time
        self.model.update()
        self.update_view()

        # self.timer.start(1000 // self.model.speed) #QObject::startTimer: Timers can only be used with threads started with QThread
    
    def set_speed(self, value):
        self.model.speed = value

    def load_gnbs(self, lat_range= (33.64, 33.65), lon_range=(-117.86, -117.83)):
        # gnbs = load_gnbs_from_csv(file_path, lat_range, lon_range)
        gnbs = generate_random_gnbs(30, lat_range, lon_range)

        for gnb in gnbs:
            self.model.add_gnb(gnb)
            self.view.place_gnb(gnb.gn_id, gnb.lat, gnb.lon)

        self.model.update_gnb_tree()

    def load_ues(self):
        file_path = r"C:\Users\mahdi\Sumo\test\em_out.xaml"
        # file_path = r"C:\Users\mahdi\Sumo\2025-03-30-15-23-49\em.out.xml"
        trajectory_dict = parse_emission_file(file_path)
        for ue_id, trajectory in trajectory_dict.items():
            # print(f"Sending trajectory for UE {ue_id}")
            time_stamps = trajectory['time']
            latlon = [xy_to_latlon(x, y, 33.6332, -117.8527) for x, y in zip(trajectory['x'], trajectory['y'])]
            latitudes, longitudes = zip(*latlon)  # This unpacks the tuples into separate lists            # for t, x, y in zip(trajectory['time'], trajectory['x'], trajectory['y']):
            trajectory = Trajectory(time_stamps, latitudes, longitudes)
            ue = self.model.add_ue(ue_id, trajectory)   
            self.view.add_ue(ue)


    def stop(self):
        self.model.running = False
        self.timer.stop()

    def run_simulation(self):
        if self.model.running:
            self.model.update()
            self.update_view()
            
            # Print UE stats at time 60
            if self.model.sim_time == 10:
                print(f"--- UE Stats at time {self.model.sim_time} ---")
                total_handovers = 0
                total_success = 0
                total_initiated = 0
                epoch_times = []
                ue_count = len(self.model.ues)

                for ue in self.model.ues:
                    stats = calculate_ue_stats(ue)
                    print(stats)

                    total_handovers += stats["num_handovers"]
                    total_success += stats["successful_reregistrations"]
                    total_initiated += stats["initiated_reregistrations"]
                    if stats["mean_epoch_time"] is not None:
                        epoch_times.append(stats["mean_epoch_time"])

                mean_handovers = total_handovers / ue_count if ue_count else 0
                mean_success = total_success / ue_count if ue_count else 0
                mean_initiated = total_initiated / ue_count if ue_count else 0
                overall_mean_epoch = sum(epoch_times) / len(epoch_times) if epoch_times else None

                print("\n--- Mean Statistics Across All UEs ---")
                print(f"Mean Handovers: {mean_handovers:.2f}")
                print(f"Mean Successful Reregistrations: {mean_success:.2f}")
                print(f"Mean Initiated Reregistrations: {mean_initiated:.2f}")
                print(f"Mean Epoch Time: {str(overall_mean_epoch) if overall_mean_epoch else 'N/A'}")
            


    
    def set_speed(self, value):
        self.model.speed = value
        self.timer.setInterval(1000 // value)


    def update_view(self):
        current_time = self.model.sim_time

        for ue in self.model.ues:
            lat, lon = ue.get_location(current_time)
            self.view.move_ue(ue.ue_id, lat, lon)
            nearest_gnb = ue.connected_gnb

            line_color = "green"
            if ue.event_logs:
                last_event_log = ue.event_logs[-1]
                if last_event_log.time == current_time:
                    self.view.show_ue_event_log(ue.ue_id, last_event_log)
                    if last_event_log.event.type == EventType.SUCCESSFUL_REREGISTRATION:
                        line_color = "blue"
                    elif last_event_log.event.type == EventType.UNSUCCESSFUL_REREGISTRATION:
                        line_color = "red"
                        

            self.view.draw_line(
                a_lat=lat,
                a_lon=lon,
                b_lat=nearest_gnb.lat,
                b_lon=nearest_gnb.lon,
                ue_id=ue.ue_id,
                color=line_color
            )






from datetime import timedelta

def calculate_ue_stats(ue):
    logs = sorted(ue.event_logs, key=lambda e: e.time)
    
    epoch_times = []
    last_success_time = None
    attach_time = None

    num_handovers = 0
    num_success_rereg = 0
    num_initiated_rereg = 0

    for log in logs:
        event_type = log.event.type

        if event_type == EventType.ATTACH:
            attach_time = log.time

        elif event_type == EventType.SUCCESSFUL_REREGISTRATION:
            num_success_rereg += 1
            if last_success_time is not None:
                epoch_times.append((log.time - last_success_time))
            elif attach_time is not None:
                epoch_times.append((log.time - attach_time))
            last_success_time = log.time

        elif event_type == EventType.INITIATE_REREGISTRATION:
            num_initiated_rereg += 1

        elif event_type == EventType.HANDOVER:
            num_handovers += 1

    mean_epoch_time = sum(epoch_times) / len(epoch_times) if epoch_times else None

    return {
        "ue_id": ue.ue_id,
        "mean_epoch_time": mean_epoch_time,
        "num_handovers": num_handovers,
        "successful_reregistrations": num_success_rereg,
        "initiated_reregistrations": num_initiated_rereg
    }

        