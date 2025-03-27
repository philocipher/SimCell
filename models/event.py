import enum


class EventType(enum.Enum):
    HANDOVER = 1
    ATTACH = 2
    DETACH = 3
    SUCCESSFUL_REREGISTRATION = 4
    UNSUCCESSFUL_REREGISTRATION = 5

class Event:
    def __init__(self, type: EventType):
        self.type = type

class HandoverEvent(Event):
    def __init__(self, source, target, ue):
        super().__init__(EventType.HANDOVER)
        self.source = source
        self.target = target
        self.ue = ue


class EventLog:
    def __init__(self, time, event):
        self.time = time
        self.event = event
        