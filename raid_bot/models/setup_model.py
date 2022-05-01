from dataclasses import dataclass
from typing import List


@dataclass
class Setup:
    setup_id: int
    guild_id: int
    channel_id: int
    name: str

    def __init__(self, setup: List):
        self.setup_id = setup[0]
        self.guild_id = setup[1]
        self.channel_id = setup[2]
        self.name = setup[3]
