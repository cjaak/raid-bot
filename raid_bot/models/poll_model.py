from dataclasses import dataclass
from typing import List, Union


@dataclass
class Poll:
    """Class for keeping track of a poll"""

    poll_id: int
    channel_id: int
    guild_id: int
    author_id: int
    question: str
    number_of_options: int
    multiple_selection: bool

    def __init__(self, poll: List):
        self.poll_id = poll[0]
        self.channel_id = poll[1]
        self.guild_id = poll[2]
        self.author_id = poll[3]
        self.question = poll[4]
        self.number_of_options = poll[5]
        self.multiple_selection = bool(poll[6])
