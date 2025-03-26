from .ue import UE
from datetime import timedelta
from scipy.spatial import KDTree
from .gnb import gNB

class Model:
    def __init__(self):
        self.ues = []
        self.gnb = {}
        self.speed = 1
        self.sim_time = timedelta(seconds=0)  # Virtual time

    def add_ue(self, ue_id, trajectory):
        ue = UE(ue_id, trajectory)
        self.ues.append(ue)
    
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
        self.sim_time += timedelta(seconds=1 * self.speed)




        