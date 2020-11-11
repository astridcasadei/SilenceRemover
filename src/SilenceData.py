# This Python file uses the following encoding: utf-8

MS_TO_SEC = 0.001


class SilenceData:
    identifier = 0

    # Silence start time [float, s]
    start_time = 0

    # Silence stop time [float, s]
    stop_time = 0

    # Silence start offset [int, ms]
    start_offset = 0

    # Silence stop offset [int, ms]
    stop_offset = 0

    # Start offset changeable [bool]
    start_offset_changeable = True

    # Stop offset changeable [bool]
    stop_offset_changeable = True

    def __init__(self, iden, start_time, stop_time, start_offset, stop_offset,
                 start_offset_changeable, stop_offset_changeable):
        self.identifier = iden
        self.start_time = start_time
        self.stop_time = stop_time
        self.start_offset = start_offset
        self.stop_offset = stop_offset
        self.start_offset_changeable = start_offset_changeable
        self.stop_offset_changeable = stop_offset_changeable

    def duration(self):
        return self.stop_time - self.start_time

    def start_cut(self):
        return min(self.start_time + self.start_offset * MS_TO_SEC, self.stop_time)

    def stop_cut(self):
        return max(self.stop_time - self.stop_offset * MS_TO_SEC, self.start_time)
