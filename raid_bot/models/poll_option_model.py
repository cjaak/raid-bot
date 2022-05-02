from dataclasses import dataclass
from typing import List, Union


@dataclass
class PollOption:
    """Class for keeping track of a poll"""

    poll_id: int
    option_id: int
    option: str

    def __init__(self, poll_option: List):
        self.poll_id = poll_option[0]
        self.option_id = poll_option[1]
        self.option = poll_option[2]
