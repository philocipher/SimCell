class gNB:
    def __init__(self, gn_id, latitude, longitude, radio=None, mcc=None, net=None, area=None, unit=None,
                 range=None, samples=None, changeable=None, created=None, updated=None, averageSignal=None):
        self.gn_id = gn_id  # typically cellid
        self.lat = latitude
        self.lon = longitude
        self.radio = radio
        self.mcc = mcc
        self.net = net
        self.area = area
        self.unit = unit
        self.range = range
        self.samples = samples
        self.changeable = changeable
        self.created = created
        self.updated = updated
        self.averageSignal = averageSignal
