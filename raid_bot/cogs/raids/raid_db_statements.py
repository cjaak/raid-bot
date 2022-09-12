import logging
from sqlite3 import Connection
from typing import Union

from raid_bot.database import select_one, select_all_for_guild, update_value, delete_row

TABLE = "raids"
PRIMARY_KEY = "raid_id"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def select_one_raid(conn: Connection, raid_id: int):
    return select_one(conn, TABLE, PRIMARY_KEY, raid_id)


def insert_raid(
    conn: Connection,
    raid_id: int,
    channel_id: int,
    guild_id: int,
    author_id: int,
    name: str,
    mode: str,
    description: str,
    timestamp: int,
    setup: int,
):
    pass


def get_all_raid_ids(conn: Connection):
    pass


def select_all_raids_by_guild_id(conn: Connection, guild_id: int):
    return select_all_for_guild(conn, TABLE, guild_id)


def update_raid(conn: Connection, raid_id: int, column: str, value: Union[str, int]):
    return update_value(conn, TABLE, column, PRIMARY_KEY, raid_id, value)


def delete_raid(conn: Connection, raid_id: int):
    return delete_row(conn, TABLE, PRIMARY_KEY, raid_id)


def delete_assignment(conn: Connection, raid_id: int):
    pass


def insert_or_update_assignment(
    conn: Connection, player_id: int, raid_id: int, role: str, timestamp: int
):
    pass
