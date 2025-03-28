import enum


class EventType(enum.Enum):
    HANDOVER = 1
    ATTACH = 2
    DETACH = 3
    INITIATE_REREGISTRATION = 4
    SUCCESSFUL_REREGISTRATION = 5
    UNSUCCESSFUL_REREGISTRATION = 6

class Event:
    def __init__(self, type: EventType):
        self.type = type

class HandoverEvent(Event):
    def __init__(self, source, target, ue):
        super().__init__(EventType.HANDOVER)
        self.source = source
        self.target = target
        self.ue = ue

class AttachEvent(Event):
    def __init__(self, gnb, ue):
        super().__init__(EventType.ATTACH)
        self.gnb = gnb
        self.ue = ue

class DetachEvent(Event):
    def __init__(self, gnb, ue):
        super().__init__(EventType.DETACH)
        self.gnb = gnb
        self.ue = ue

class InitiateReregistrationEvent(Event):
    def __init__(self, ue, gnb):
        super().__init__(EventType.INITIATE_REREGISTRATION)
        self.ue = ue
        self.gnb = gnb

class SuccessfulReregistrationEvent(Event):
    def __init__(self, ue, gnb):
        super().__init__(EventType.SUCCESSFUL_REREGISTRATION)
        self.gnb = gnb
        self.ue = ue

class UnsuccessfulReregistrationEvent(Event):
    def __init__(self, ue, gnb):
        super().__init__(EventType.UNSUCCESSFUL_REREGISTRATION)
        self.gnb = gnb
        self.ue = ue

class EventLog:
    def __init__(self, time, event):
        self.time = time
        self.event = event
        