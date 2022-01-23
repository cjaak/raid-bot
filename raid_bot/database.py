import json
import logging
import sqlite3
from sqlite3 import Connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CONN: Connection


def create_connection(db_file):
    """create a database connection to a SQLite database"""
    try:
        conn: Connection = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        logger.exception(e)
        return None
    return conn


def create_table(conn, table_name):
    """create a database table"""
    query = get_table_creation_query(table_name)
    try:
        c = conn.cursor()
        c.execute(query)
        return True
    except sqlite3.Error as e:
        logger.exception(e)


def get_table_creation_query(table):
    sql_dict = {
        "raid": (
            "create table if not exists Raids ("
            "raid_id integer primary key, "
            "channel_id integer not null, "
            "guild_id integer not null, "
            "author_id integer not null, "
            "name text not null, mode text, "
            "description text null,"
            "time integer not null);"
        ),
        "assign": (
            "create table if not exists Assignment ("
            "raid_id integer not null, "
            "player_id integer not null, "
            "role text, "
            "timestamp integer, "
            "primary key (raid_id, player_id), "
            "foreign key (raid_id) references Raids(raid_id)"
            "foreign key (player_id) references Players(player_id)"
            ");"
        ),
    }
    return sql_dict[table]


def insert_raid(
    conn, raid_id, channel_id, guild_id, author_id, name, mode, description, timestamp
):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO raids VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                raid_id,
                channel_id,
                guild_id,
                author_id,
                name,
                mode,
                description,
                timestamp,
            ),
        )
    except sqlite3.Error as e:
        logger.exception(e)


def select_one_raid(conn, raid_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raids WHERE raid_id = (?)", [raid_id])
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)


def select_all_raids_by_guild_id(conn, guild_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raids WHERE guild_id = ?", guild_id)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)


def update_raid(conn, raid_id, column, value):
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE raids SET {column} = ? WHERE raid_id = {raid_id}", value
        )
    except sqlite3.Error as e:
        logger.exception(e)


def insert_or_update_assignment(conn, player_id, raid_id, role, timestamp):
    try:
        cursor = conn.cursor()
        # cursor.execute(
        #     f"UPDATE assignment SET timestamp = {timestamp}, SET role = (?) WHERE raid_id = {raid_id} AND player_id = {player_id}",
        #     role,
        # )
        # if cursor.rowcount == 0:
        cursor.execute(
            # NOTE: workaround until I figure out how to do this properly
            "INSERT OR REPLACE INTO assignment VALUES (?, ?, ?, ?)",
            (raid_id, player_id, role, timestamp),
        )
        return True
    except sqlite3.Error as e:
        logger.exception(e)


def select_all_assignments_by_raid_id(conn, raid_id):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM assignment WHERE raid_id = ? ORDER BY timestamp", [raid_id]
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)


def select_assignments_by_role_for_raid(conn, raid_id, role):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM assignment WHERE raid_id = ? AND WHERE role = ? ORDER BY timestamp",
            (raid_id, role),
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)
