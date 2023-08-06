__author__ = 'jos'

from pybm.util import enum

Status = enum(OK="ok", WARNING="warning", ERROR="error", UNKNOWN="unknown", BUILDING="building", DISABLED='disabled')

class Job():
    def __init__(self, name, status, percentage, queue_position=None):
        self.name = name
        self.status = status
        self.percentage = percentage
        self.queue_position = queue_position