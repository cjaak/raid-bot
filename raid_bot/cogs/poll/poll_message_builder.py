from sqlite3 import Connection
from typing import Dict, List, Tuple

import datetime
import discord
import logging
from raid_bot.database import (
    select_one_raid,
    select_all_assignments_by_raid_id,
    select_one_poll,
    select_options_for_poll,
    count_votes,
    count_votes_for_option,
)
from raid_bot.models.assignment_model import Assignment
from raid_bot.models.poll_emoji import POLL_EMOJI, OpinionOptions, OPINION_EMOJI
from raid_bot.models.poll_model import Poll
from raid_bot.models.poll_option_model import PollOption

from raid_bot.models.raid_model import Raid
from raid_bot.models.sign_up_options import SignUpOptions, EMOJI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def build_poll_message(conn: Connection, poll_id: int):
    poll: Poll = Poll(select_one_poll(conn, poll_id))

    votes = count_votes(conn, poll_id)
    embed = discord.Embed(title=poll.question, description=f"VOTES: {votes}")

    list_of_options: List[PollOption] = [
        PollOption(list_item) for list_item in select_options_for_poll(conn, poll_id)
    ]

    for option in list_of_options:
        name_field = f"{POLL_EMOJI[option.option_id]}: {option.option}"
        embed.add_field(name=name_field, value="\u200B", inline=False)

    return embed


def build_poll_result_message(conn: Connection, poll_id: int):
    poll: Poll = Poll(select_one_poll(conn, poll_id))
    votes = count_votes(conn, poll_id)
    embed = discord.Embed(
        title=f"RESULT: {poll.question}", description=f"{votes} people voted"
    )

    list_of_options: List[PollOption] = [
        PollOption(list_item) for list_item in select_options_for_poll(conn, poll_id)
    ]

    for option in list_of_options:
        result = count_votes_for_option(conn, option.option_id, poll.poll_id)
        percentage = get_percentage(result, votes)
        value = f"{result} votes ({percentage})"
        name_field = f"{POLL_EMOJI[option.option_id]}: {option.option}"
        embed.add_field(name=name_field, value=value, inline=False)

    return embed


def get_percentage(part, whole):
    percentage = 100 * float(part) / float(whole)
    return str(round(percentage, 2)) + "%"


def build_opinion_message(conn: Connection, poll_id: int):
    poll: Poll = Poll(select_one_poll(conn, poll_id))
    votes = count_votes(conn, poll_id)
    embed = discord.Embed(title=poll.question, description=f"VOTES: {votes}")
    opinion_yes = count_votes_for_option(conn, OpinionOptions.YES, poll.poll_id)
    opinion_no = count_votes_for_option(conn, OpinionOptions.NO, poll.poll_id)
    opinion = opinion_yes - opinion_no
    opinion = opinion if opinion <= 0 else f"+{opinion}"
    perc_yes = "0.0%"
    perc_no = "0.0%"
    if votes > 0:
        perc_yes = get_percentage(opinion_yes, votes)
        perc_no = get_percentage(opinion_no, votes)

    embed.add_field(
        name=f"Opinion: {opinion}",
        value=f"{OPINION_EMOJI[OpinionOptions.YES]}\t {perc_yes} \n \n {OPINION_EMOJI[OpinionOptions.NO]}\t {perc_no}",
    )

    return embed
