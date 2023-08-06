# -*- coding: utf-8 -*-

from datetime import datetime


class Timetracker(object):
    STARTED = 0x00
    STOPPED = 0x01

    def __init__(self):
        self._state = Timetracker.STOPPED
        self._starttime = None
        self._endtime = None

    def start_timetracking(self):
        self._state = Timetracker.STARTED
        self._starttime = datetime.now()

    def stop_timetracking(self):
        self._state = Timetracker.STOPPED
        self._endtime = datetime.now()

    def get_starttime(self):
        return self._starttime or datetime(1970, 1, 1, 0, 0)

    def get_endtime(self):
        return self._endtime or datetime(1970, 1, 1, 0, 0)

    def get_duration(self):
        if self._starttime is not None and self._endtime is not None:
            td = self._endtime - self._starttime
            return Timetracker.get_total_seconds(td)
        return 0

    @staticmethod
    def get_total_seconds(timedelta):
        return (timedelta.microseconds + (timedelta.seconds + timedelta.days * 24 * 3600) * 1e6) / 1e6
