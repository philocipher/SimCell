from .ue import UE
from datetime import timedelta
from scipy.spatial import KDTree
from .gnb import gNB
from utils.supi_generator import generate_random_supi
from .event import *

class Model:
    def __init__(self):
        self.ues = []
        self.gnb = {}
        self.speed = 1
        self.sim_time = timedelta(seconds=0)  # Virtual time
        self.running = False

    def add_ue(self, ue_id, trajectory):
        ue = UE(ue_id, generate_random_supi(), 1024, 1024, trajectory)
        self.ues.append(ue)
        return ue
    
    def add_gnb(self, gnb):
        self.gnb[gnb.gn_id] = gnb

    def update_gnb_tree(self):
        gnb_values = list(self.gnb.values())
        self.gnb_positions = [(gnb.lat, gnb.lon) for gnb in gnb_values]
        self.gnb_ids = [gnb.gn_id for gnb in gnb_values]
        self.gnb_tree = KDTree(self.gnb_positions)

    def get_closest_gnb(self, lat, lon):
        dist, idx = self.gnb_tree.query([lat, lon])
        return self.gnb[self.gnb_ids[idx]]
    
    def update(self):
        # Advance virtual time
        self.sim_time += 1 * self.speed

        for ue in self.ues:
            if ue.trajectory.time_stamps[0] <= self.sim_time <= ue.trajectory.time_stamps[-1]:
                lat, lon = ue.get_location(self.sim_time)
                nearest_gnb = self.get_closest_gnb(lat, lon)

                if nearest_gnb != ue.connected_gnb:
                    if ue.connected_gnb is not None:
                        handover = HandoverEvent(ue.connected_gnb, nearest_gnb, ue)
                        log = EventLog(self.sim_time, handover)
                        ue.event_logs.append(log)

                        ue.connected_gnb.remove_ue(ue)
                        ue.connected_gnb = nearest_gnb
                        nearest_gnb.add_ue(ue)

                        self.initiate_reregistrasion(ue)
                    else:
                        ue.connected_gnb = nearest_gnb
                        nearest_gnb.add_ue(ue)


    def initiate_reregistrasion(self, ue):
        event = InitiateReregistrationEvent(ue, ue.connected_gnb)
        even_log = EventLog(self.sim_time, event)
        ue.event_logs.append(even_log)
        
        similar_ues = self.find_similar_ues(ue)
        if len(similar_ues)<2:
            event = UnsuccessfulReregistrationEvent(ue, ue.connected_gnb)
            even_log = EventLog(self.sim_time, event)
            ue.event_logs.append(even_log)
            return
        else:
            #TODO: Filter the top 4
            for similar_ue in similar_ues.values():
                event = SuccessfulReregistrationEvent(similar_ue, similar_ue.connected_gnb)
                even_log = EventLog(self.sim_time, event)
                similar_ue.event_logs.append(even_log)
            return
        
    def find_similar_ues(self, ue):
        return ue.connected_gnb.connected_ues





