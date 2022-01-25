from raid_bot.models.sign_up_options import SignUpOptions
from dataclasses import dataclass
from typing import List


@dataclass
class SetupPlayer:
    """Class for keeping track of a player in a setup."""

    player_id: int
    setup_id: str
    role: SignUpOptions

    def __init__(self, setup_player: List):
        self.player_id = setup_player[0]
        self.setup_id = setup_player[1]
        self.role = setup_player[2]
