from dataclasses import dataclass
from typing import List, Union

from raid_bot.models.sign_up_options import SignUpOptions


@dataclass
class Assignment:
    """Class for keeping track of an assignment for a raid."""

    raid_id: int
    player_id: int
    role: SignUpOptions
    timestamp: int

    def __init__(self, raid: List):
        self.raid_id = raid[0]
        self.player_id = raid[1]
        self.role = raid[2]
        self.timestamp = raid[3]
