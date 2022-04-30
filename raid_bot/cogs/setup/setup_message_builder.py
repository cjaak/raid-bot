from sqlite3 import Connection
from typing import Dict, List, Tuple

import datetime
import discord
import logging
from raid_bot.database import (
    select_one_raid,
    select_all_assignments_by_raid_id,
    select_one_setup,
)
from raid_bot.models.assignment_model import Assignment

import logging
from raid_bot.models.sign_up_options import SignUpOptions, EMOJI
from raid_bot.models.setup_model import Setup
from raid_bot.models.setup_player_model import SetupPlayer
from raid_bot.database import (
    insert_or_replace_setup,
    select_all_players_for_setup,
    create_table,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def build_setup_embed(conn: Connection, setup_id: int):
    setup: Setup = Setup(select_one_setup(conn, setup_id))
    sign_ups, total = build_players_for_setup(conn, setup_id)
    embed: discord.Embed = discord.Embed(title=f"Sign up to be part of {setup.name}")
    for role in sign_ups:
        current = len(sign_ups[role])
        field_string = f"{role} ({current})"
        embed.add_field(
            name=field_string,
            value="\n".join(sign_ups[role]) if len(sign_ups[role]) > 0 else "\u200B",
        )
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"total sign ups: {total} ")

    return embed


def build_players_for_setup(conn: Connection, setup_id: int):
    sign_ups = {
        SignUpOptions.TANK: [],
        SignUpOptions.DD: [],
        SignUpOptions.HEAL: [],
    }

    list_of_players: List[SetupPlayer] = [
        SetupPlayer(item) for item in select_all_players_for_setup(conn, setup_id)
    ]

    for index, player in enumerate(list_of_players):
        sign_ups[player.role].append(
            f"`{index + 1}` {EMOJI[player.role]} <@{player.player_id}>"
        )
    total = len(list_of_players)

    return sign_ups, total
