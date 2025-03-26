class Trajectory:
    def __init__(self, time_stamps, latitudes, longitudes):
        if not (len(time_stamps) == len(latitudes) == len(longitudes)):
            raise ValueError("All input lists must be of the same length")
        self.time_stamps = time_stamps
        self.latitudes = latitudes
        self.longitudes = longitudes

    def get_location(self, time_input):
        if time_input <= self.time_stamps[0]:
            return self.latitudes[0], self.longitudes[0]
        if time_input >= self.time_stamps[-1]:
            return self.latitudes[-1], self.longitudes[-1]

        # Linear interpolation between the closest timestamps
        for i in range(1, len(self.time_stamps)):
            t0 = self.time_stamps[i - 1]
            t1 = self.time_stamps[i]
            if t0 <= time_input <= t1:
                ratio = (time_input - t0) / (t1 - t0)
                lat = self.latitudes[i - 1] + ratio * (self.latitudes[i] - self.latitudes[i - 1])
                lon = self.longitudes[i - 1] + ratio * (self.longitudes[i] - self.longitudes[i - 1])
                return lat, lon

        raise ValueError("Time input is outside the trajectory range")
