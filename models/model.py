from .ue import UE
from datetime import timedelta

class Model:
    def __init__(self):
        self.ues = []
        self.gnbs = []
        self.speed = 1
        self.sim_time = timedelta(seconds=0)  # Virtual time

    def add_ue(self, ue_id, trajectory):
        ue = UE(ue_id, trajectory)
        self.ues.append(ue)


    def update(self):
        # Advance virtual time
        self.sim_time += timedelta(seconds=1 * self.speed)


        