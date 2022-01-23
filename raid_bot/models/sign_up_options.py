from enum import Enum


class SignUpOptions(str, Enum):
    TANK = "Tank"
    DD = "DD"
    HEAL = "Heal"
    UNAVAILABLE = "Unavailable"
    TENTATIVE = "Tentative"
