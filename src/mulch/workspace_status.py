from enum import Enum, auto

class WorkspaceStatus(Enum):
    MISSING = auto()
    MATCHES = auto()
    DIFFERS = auto()
    EXISTS_NO_LOCK = auto()
