from PyQt5.QtCore import QTimer
from utils.xml_parser import *
from utils.coordinates import *
from models.gnb_loader import *
from models.trajectory import *

class SimulatorController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_simulation)
        
    def start(self):
        self.model.running = True



        # self.timer.start(1000 // self.model.speed) #QObject::startTimer: Timers can only be used with threads started with QThread


    def load_gnbs(self):
        lat_range = (33.64, 33.65)
        lon_range = (-117.86, -117.83)
        # gnbs = load_gnbs_from_csv(file_path, lat_range, lon_range)
        gnbs = generate_random_gnbs(90, lat_range, lon_range)

        for gnb in gnbs:
            self.view.place_gnb(gnb.gn_id, gnb.lat, gnb.lon)

    def load_ues(self):
        file_path = r"C:\Users\mahdi\Sumo\test\em_out.xaml"
        trajectory_dict = parse_emission_file(file_path)
        for ue_id, trajectory in trajectory_dict.items():
            # print(f"Sending trajectory for UE {ue_id}")
            time_stamps = trajectory['time']
            latlon = [xy_to_latlon(x, y, 33.6332, -117.8527) for x, y in zip(trajectory['x'], trajectory['y'])]
            latitudes, longitudes = zip(*latlon)  # This unpacks the tuples into separate lists            # for t, x, y in zip(trajectory['time'], trajectory['x'], trajectory['y']):
            trajectory = Trajectory(time_stamps, latitudes, longitudes)
            self.model.add_ue(ue_id, trajectory)   


    def stop(self):
        self.model.running = False
        self.timer.stop()

    def run_simulation(self):
        if self.model.running:
            self.model.update()
            # self.view.update_map()
            # Get current simulation time
            current_time = self.model.sim_time.total_seconds()
            
            # Update UE positions on the map
            for ue in self.model.ues:
                lat, lon = ue.get_location(current_time)
                self.view.move_ue(ue.ue_id, lat, lon)
    
    def set_speed(self, value):
        self.model.speed = value
        self.timer.setInterval(1000 // value)