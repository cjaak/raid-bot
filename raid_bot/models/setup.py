from dataclasses import dataclass
from typing import List

@dataclass
class Setup:
    guild_id: int
    name: str
    setup_id: str

    def __init__(self, setup: List):
        self.guild_id = setup[0]
        self.name = setup[1]
        self.setup_id = setup[2]