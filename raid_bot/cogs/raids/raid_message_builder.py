from sqlite3 import Connection
from typing import Dict, List, Tuple

import datetime
import discord
import logging

from raid_bot.database import select_all_assignments_by_raid_id, select_one_raid
from raid_bot.models.assignment_model import Assignment

from raid_bot.models.raid_model import Raid
from raid_bot.models.sign_up_options import SignUpOptions, EMOJI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def build_raid_message(conn: Connection, raid_id: int):
    """Build the embed part of a discord message.

    Args:
        conn: connection to the database
        raid_id: The id of the raid to build an embed for

    Returns:
        The embed containing the data of the input
    """

    raid: Raid = Raid(select_one_raid(conn, raid_id))

    embed_title: str = f"{raid.name} {raid.mode}\n<t:{raid.timestamp}:F>"
    embed = discord.Embed(
        title=embed_title, description=raid.description, colour=0x4B34EF
    )
    sign_ups, total = build_player_sign_ups(conn, raid_id)
    for role in sign_ups:
        current = len(sign_ups[role])
        # TODO: specify roster in database for limits
        field_string = f"{role} ({current})"
        embed.add_field(
            name=field_string,
            value="\n".join(sign_ups[role]) if len(sign_ups[role]) > 0 else "\u200B",
        )
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"total sign ups: {total} ")

    return embed


def build_player_sign_ups(
    conn: Connection, raid_id: int
) -> Tuple[Dict[str, List[str]], int]:
    """Build formatted strings out of signed up players for the raid.

    Args:
        conn: connection to the database
        raid_id: The id of the raid to build an embed for

    Returns:
        A dict that contains a list of player strings for each role
    """

    sign_ups = _build_empty_sign_up_dict()
    list_of_assignments: List[Assignment] = [
        Assignment(list_item)
        for list_item in select_all_assignments_by_raid_id(conn, raid_id)
    ]
    logger.info(list_of_assignments)
    number: int = 0
    for index, assignment in enumerate(list_of_assignments):
        if assignment.timestamp > 0:
            number += 1
        sign_ups[assignment.role].append(
            f"`{number}` {EMOJI[assignment.role]} <@{assignment.player_id}>"
        )
    total = len(list_of_assignments)
    return sign_ups, total


def _build_empty_sign_up_dict() -> Dict[str, List]:
    """Build an empty dict with each role option as a key.
    Ex.:
    {
        role1: []
        role2: []
        role3: []
    }

    Args:
        conn: connection to the database
        raid_id: The id of the raid to build an embed for

    Returns:
        the dict containing each role as a key and an empty list as value
    """
    sign_ups: Dict[str, List[str]] = {}
    for role in SignUpOptions:
        sign_ups[role] = []
    return sign_ups
