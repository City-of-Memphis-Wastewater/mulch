#src.mulch.flags_log_status.py
from enum import Enum, auto

class FlagsLockStatus(Enum):
    MISSING = auto()
    MATCHES = auto()
    DIFFERS = auto()
    EXISTS_NO_LOCK = auto()