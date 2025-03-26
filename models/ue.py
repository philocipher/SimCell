class UE:
    def __init__(self, ue_id, trajectory = None):
        self.ue_id = ue_id
        self.trajectory = trajectory
        self.connected_gnb = None      # Tracks the current gNB
        self.current_location = None   # Tuple of (lat, lon)

    def move(self, lat, lon):
        self.current_location = (lat, lon)

    def get_location(self, time_input):
        return self.trajectory.get_location(time_input)