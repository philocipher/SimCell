class UE:
    def __init__(self, ue_id, supi, ambr_downlink, ambr_uplink, trajectory = None):
        self.ue_id = ue_id
        self.supi = supi # IMSI number of the UE. IMSI = [MCC|MNC|MSISDN] (In total 15 digits)
        self.ambr_downlink = ambr_downlink #  Aggregate Maximum Bit Rate. Mbps
        self.ambr_uplink = ambr_uplink


        self.trajectory = trajectory
        self.connected_gnb = None      # Tracks the current gNB
        self.current_location = None   # Tuple of (lat, lon)
        self.event_logs = [] 

    def move(self, lat, lon):
        self.current_location = (lat, lon)

    def get_location(self, time_input):
        return self.trajectory.get_location(time_input)