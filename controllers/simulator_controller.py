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
        self.update_view()

        # self.timer.start(1000 // self.model.speed) #QObject::startTimer: Timers can only be used with threads started with QThread


    def load_gnbs(self, lat_range= (33.64, 33.65), lon_range=(-117.86, -117.83)):
        # gnbs = load_gnbs_from_csv(file_path, lat_range, lon_range)
        gnbs = generate_random_gnbs(90, lat_range, lon_range)

        for gnb in gnbs:
            self.model.add_gnb(gnb)
            self.view.place_gnb(gnb.gn_id, gnb.lat, gnb.lon)

        self.model.update_gnb_tree()

    def load_ues(self):
        file_path = r"C:\Users\mahdi\Sumo\test\em_out.xaml"
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
            
            
            


    
    def set_speed(self, value):
        self.model.speed = value
        self.timer.setInterval(1000 // value)


    def update_view(self):
        # Get current simulation time
        current_time = self.model.sim_time

        # Update UE positions on the map
        for ue in self.model.ues:
            lat, lon = ue.get_location(current_time)
            self.view.move_ue(ue.ue_id, lat, lon)
            nearest_gnb = self.model.get_closest_gnb(lat, lon)
            if nearest_gnb != ue.connected_gnb:
                if ue.connected_gnb is not None:
                    handover = HandoverEvent(ue.connected_gnb, nearest_gnb, ue)
                    log = EventLog(current_time, handover)
                    ue.event_logs.append(log)

                    # Send event log to frontend
                    self.view.show_ue_event_log(ue.ue_id, log)

                    ue.connected_gnb.remove_ue(ue)

                    ue.connected_gnb = nearest_gnb
                    nearest_gnb.add_ue(ue)

                    self.model.initiate_reregistrasion(ue)
                
                else:
                    ue.connected_gnb = nearest_gnb
                    nearest_gnb.add_ue(ue)

            
            line_color = "green"
            if ue.event_logs:
                last_event_log = ue.event_logs[-1]
                if last_event_log.time == current_time:
                    if last_event_log.event.type == EventType.SUCCESSFUL_REREGISTRATION:
                        line_color = "blue"
                    elif last_event_log.event.type == EventType.UNSUCCESSFUL_REREGISTRATION:
                        line_color = "red"
                
            # print(f"UE {ue.ue_id} is closest to GNB {nearest_gnb.gn_id}")
            self.view.draw_line(
                a_lat=lat,
                a_lon=lon,
                b_lat=nearest_gnb.lat,
                b_lon=nearest_gnb.lon,
                ue_id=ue.ue_id,
                color=line_color
            )