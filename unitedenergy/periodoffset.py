from enum import Enum

class PeriodOffset(Enum):
    current = 0
    prior = 1
    timebeforelast = 2