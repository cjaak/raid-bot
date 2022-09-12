import logging
from sqlite3 import Connection
from typing import Union

from raid_bot.database import select_one, select_all_for_guild, update_value, delete_row

TABLE = "assignments"
PRIMARY_KEY = "raid_id"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def delete_assignment(conn: Connection, raid_id: int):
    return delete_row(conn, TABLE, PRIMARY_KEY, raid_id)


def insert_or_update_assignment(
    conn: Connection, player_id: int, raid_id: int, role: str, timestamp: int
):
    pass
