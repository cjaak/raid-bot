from enum import Enum
from typing import Dict


class SignUpOptions(str, Enum):
    TANK = "Tank"
    DD = "DD"
    HEAL = "Heal"
    TENTATIVE = "Tentative"
    UNAVAILABLE = "Unavailable"


EMOJI: Dict[str, str] = {
    SignUpOptions.TANK: "\U0001F6E1",
    SignUpOptions.DD: "\U0001F4A5",
    SignUpOptions.HEAL: "\U0000267B",
    SignUpOptions.TENTATIVE: "\U00002753",
    SignUpOptions.UNAVAILABLE: "\U0000274C",
}
