class UE:
    def __init__(self, ue_id, trajectory = None):
        self.ue_id = ue_id
        self.trajectory = trajectory
        # self.latitude = latitude
        # self.longitude = longitude

    def move(self, lat, lon):
        self.latitude = lat
        self.longitude = lon

    def get_location(self, time_input):
        return self.trajectory.get_location(time_input)