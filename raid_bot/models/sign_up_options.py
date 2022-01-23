from enum import Enum


class SignUpOptions(str, Enum):
    UNAVAILABLE = "unavailable"
    TENTATIVE = "tentative"
    TANK = "tank"
    DD = "dd"
    HEAL = "heal"
