from enum import Enum


class TaskStatus(Enum):
    SCANNING = 0
    SCANNED = 1
    FINISHED = 2
    FAILURE = 3
    SCAN_FAILED = 4
