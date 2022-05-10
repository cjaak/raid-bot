from enum import Enum
from typing import Dict, List


class OpinionOptions(str, Enum):
    YES = "yes"
    IDC = "idc"
    NO = "no"


OPINION_EMOJI: Dict[str, str] = {
    OpinionOptions.YES: "\U0001F44D",
    OpinionOptions.IDC: "\U0001F937",
    OpinionOptions.NO: "\U0001F44E",
}

POLL_EMOJI: List[str] = ["\U0001F1E6", "\U0001F1E7", "\U0001F1E8", "\U0001F1E9", "\U0001F1EA"]
