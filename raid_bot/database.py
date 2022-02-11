import json
import logging
import sqlite3
from sqlite3 import Connection
from typing import Union

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CONN: Connection


def create_connection(db_file):
    """create a database connection to a SQLite database.

    Args:
        db_file: database file

    Returns:
        connection to database
    """
    try:
        conn: Connection = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        logger.exception(e)
        return None
    return conn


def create_table(conn: Connection, table_name: str):
    """create a database table"""
    query = get_table_creation_query(table_name)
    try:
        c = conn.cursor()
        c.execute(query)
        return True
    except sqlite3.Error as e:
        logger.exception(e)


def get_table_creation_query(table_name: str):
    sql_dict = {
        "raid": (
            "create table if not exists Raids ("
            "raid_id integer primary key, "
            "channel_id integer not null, "
            "guild_id integer not null, "
            "author_id integer not null, "
            "name text not null, "
            "mode text, "
            "description text null,"
            "time integer not null,"
            "setup text,"
            "foreign key (setup) references Setup(setup_id)"
            ");"
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
        "setup": (
            "create table if not exists Setup ("
            "setup_id text not null,"
            "guild_id integer not null, "
            "name text not null, "
            "primary key (setup_id)"
            ");"
        ),
        "setup_players": (
            "create table if not exists SetupPlayers ("
            "player_id integer not null,"
            "setup_id integer not null,"
            "role text not null,"
            "primary key (player_id, setup_id)"
            "foreign key (setup_id) references Setup(setup_id)"
            ");"
        ),
        "settings": (
            "create table if not exists Settings ("
            "guild_id integer not null,"
            "calendar text,"
            "primary key (guild_id)"
            ");"
        ),
    }
    return sql_dict[table_name]


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
    setup: str,
):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO raids VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                raid_id,
                channel_id,
                guild_id,
                author_id,
                name,
                mode,
                description,
                timestamp,
                setup,
            ),
        )
    except sqlite3.Error as e:
        logger.exception(e)


def select_one_raid(conn: Connection, raid_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raids WHERE raid_id = (?)", [raid_id])
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)


def get_all_raid_ids(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT raid_id FROM raids")
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)


def get_all_raids(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raids")
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)


def select_all_raids_by_guild_id(conn: Connection, guild_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raids WHERE guild_id = ?", [guild_id])
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)


def update_raid(conn: Connection, raid_id: int, column: str, value: Union[str, int]):
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE raids SET {column} = ? WHERE raid_id = {raid_id}", [value]
        )
    except sqlite3.Error as e:
        logger.exception(e)


def delete_raid(conn: Connection, raid_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM raids WHERE raid_id = ?", [raid_id])
    except sqlite3.Error as e:
        logger.exception(e)


def delete_assignment(conn: Connection, raid_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assignment WHERE raid_id = ?", [raid_id])
    except sqlite3.Error as e:
        logger.exception(e)


def insert_or_update_assignment(
    conn: Connection, player_id: int, raid_id: int, role: str, timestamp: int
):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO assignment VALUES (?, ?, ?, ?)",
            (raid_id, player_id, role, timestamp),
        )
        return True
    except sqlite3.Error as e:
        logger.exception(e)


def insert_or_replace_setup(conn: Connection, guild_id: int, name: str):
    setup_id: str = str(guild_id) + name
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO setup VALUES (?, ?, ?)", (setup_id, guild_id, name)
        )
    except sqlite3.Error as e:
        logger.exception(e)


def select_all_players_for_setup(conn: Connection, setup_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM setupplayers where setup_id = ?; ", [setup_id])
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)


def select_all_assignments_by_raid_id(conn: Connection, raid_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM assignment WHERE raid_id = ? ORDER BY timestamp", [raid_id]
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)


def select_assignments_by_role_for_raid(conn: Connection, raid_id: int, role: str):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM assignment WHERE raid_id = ? AND WHERE role = ? ORDER BY timestamp",
            (raid_id, role),
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)

def select_calendar(conn: Connection, guild_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT calendar FROM settings WHERE guild_id = ? ",
            [guild_id]
        )
        return cursor.fetchone()
    except sqlite3.Error as e:
        logger.exception(e)


def insert_or_replace_calendar(conn: Connection, guild_id: int, ids: str):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO settings VALUES (?, ?)",
            (guild_id, ids),
        )
        return True
    except sqlite3.Error as e:
        logger.exception(e)
