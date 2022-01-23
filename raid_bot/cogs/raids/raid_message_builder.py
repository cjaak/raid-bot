from sqlite3 import Connection
from typing import Dict, List

import discord
import logging
from raid_bot.database import select_one_raid, select_all_assignments_by_raid_id
from raid_bot.models.assignment_model import Assignment

from raid_bot.models.raid_model import Raid
from raid_bot.models.sign_up_options import SignUpOptions

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
    sign_ups = build_player_sign_ups(conn, raid_id)
    for role in sign_ups:
        current = len(sign_ups[role])
        # TODO: specify roster in database for limits
        # limit = raid.roster[role]
        field_string = f"{role} {current}/X"
        embed.add_field(
            name=field_string,
            value="\n".join(sign_ups[role]) if len(sign_ups[role]) > 0 else "\u200B",
        )

    return embed


def build_player_sign_ups(conn, raid_id):
    sign_ups = _build_empty_sign_up_dict()
    list_of_assignments: List[Assignment] = [
        Assignment(list_item)
        for list_item in select_all_assignments_by_raid_id(conn, raid_id)
    ]
    logger.info(list_of_assignments)
    for index, assignment in enumerate(list_of_assignments):
        sign_ups[assignment.role].append(f"`{index+1}` <@{assignment.player_id}>")
    logger.info(sign_ups)
    return sign_ups


def _build_empty_sign_up_dict() -> Dict:
    sign_ups: Dict[str, List[str]] = {}
    for role in SignUpOptions:
        sign_ups[role] = []
    return sign_ups
