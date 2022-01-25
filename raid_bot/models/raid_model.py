from dataclasses import dataclass
from typing import List, Union


@dataclass
class Raid:
    """Class for keeping track of a raid."""

    raid_id: int
    channel_id: int
    guild_id: int
    author_id: int
    name: str
    mode: str
    description: Union[str, None]
    timestamp: int
    setup: Union[str, None]

    def __init__(self, raid: List):
        self.raid_id = raid[0]
        self.channel_id = raid[1]
        self.guild_id = raid[2]
        self.author_id = raid[3]
        self.name = raid[4]
        self.mode = raid[5]
        self.description = raid[6]
        self.timestamp = raid[7]
        self.setup = raid[8]
