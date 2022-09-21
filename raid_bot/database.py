import json
import logging
import sqlite3
from sqlite3 import Connection
from typing import Union

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CONN: Connection | None = None


# region db-creation
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
            "event_id integer, "
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
            "setup_id integer not null,"
            "guild_id integer not null, "
            "channel_id integer not null,"
            "name text not null, "
            "primary key (guild_id, name)"
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
            "timezone text,"
            "guild_events integer, "
            "primary key (guild_id)"
            ");"
        ),
        "timezone": "create table if not exists Timezone ("
                    "user_id integer primary key, "
                    "timezone text"
                    ");",
        "polls": (
            "create table if not exists Polls ("
            "poll_id integer not null,"
            "channel_id integer not null, "
            "guild_id integer not null, "
            "author_id integer not null, "
            "question text,"
            "number_of_options text,"
            "multiple_selection int,"
            "primary key (poll_id)"
            ");"
        ),
        "poll_options": (
            "create table if not exists PollOptions ("
            "poll_id integer not null,"
            "option_id integer not null, "
            "option text,"
            "primary key (poll_id, option_id)"
            ");"
        ),
        "poll_votes": (
            "create table if not exists votes ("
            "poll_id integer not null,"
            "option_id text not null, "
            "user_id integer not null, "
            "primary key (poll_id, user_id)"
            ");"
        ),
    }
    return sql_dict[table_name]


# endregion

# region raid-statements
def insert_raid(
        conn: Connection,
        raid_id: int,
        channel_id: int,
        guild_id: int,
        author_id: int,
        event_id: int | None,
        name: str,
        mode: str,
        description: str,
        timestamp: int,
        setup: int,
):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO raids VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                raid_id,
                channel_id,
                guild_id,
                author_id,
                event_id,
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




# endregion

# region assignment-statements
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
            "SELECT * FROM assignment WHERE player_id = (?) AND raid_id = (?) AND role = (?)",
            (player_id, raid_id, role),
        )

        result = cursor.fetchone()
        if result:
            cursor.execute(
                "DELETE FROM assignment WHERE player_id = (?) AND raid_id = (?) AND role = (?)",
                (player_id, raid_id, role),
            )
        else:
            cursor.execute(
                "INSERT OR REPLACE INTO assignment VALUES (?, ?, ?, ?)",
                (raid_id, player_id, role, timestamp),
            )
        return True
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


# endregion assignment-statements

# region setup-statements
def select_one_setup(conn: Connection, setup_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM setup WHERE setup_id = (?)", [setup_id])
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)


def select_one_setup_by_name(conn: Connection, name: str, guild_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM setup WHERE name = (?) AND guild_id = (?)", [name, guild_id]
        )
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)


def get_all_setup_ids(conn: Connection):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT setup_id FROM setup")
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)


def delete_setup(conn: Connection, setup_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM setup WHERE setup_id = ?", [setup_id])
    except sqlite3.Error as e:
        logger.exception(e)


def select_all_setup_names_for_guild(conn: Connection, guild_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM setup WHERE guild_id = ?", [guild_id])
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)


def insert_or_replace_setup(
        conn: Connection, setup_id: int, guild_id: int, channel_id: int, name: str
):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO setup VALUES (?, ?, ?, ?)",
            (setup_id, guild_id, channel_id, name),
        )
    except sqlite3.Error as e:
        logger.exception(e)


# endregion

# region setup-player-statements
def delete_setupplayers(conn: Connection, setup_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM setupplayers WHERE setup_id = ?", [setup_id])
    except sqlite3.Error as e:
        logger.exception(e)


def insert_or_replace_setupplayer(
        conn: Connection, player_id: int, setup_id: int, role: str
):
    try:

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM SetupPlayers WHERE player_id = (?) AND setup_id = (?) AND role = (?)",
            (player_id, setup_id, role),
        )

        result = cursor.fetchone()
        if result:
            cursor.execute(
                "DELETE FROM SetupPlayers WHERE player_id = (?) AND setup_id = (?) AND role = (?)",
                (player_id, setup_id, role),
            )
        else:
            cursor.execute(
                "INSERT OR REPLACE INTO SetupPlayers VALUES (?, ?, ?)",
                (player_id, setup_id, role),
            )

        return True
    except sqlite3.Error as e:
        logger.exception(e)


def select_all_players_for_setup(conn: Connection, setup_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SetupPlayers where setup_id = ?; ", [setup_id])
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)


# endregion

# region settings-calendar-statements

def select_calendar(conn: Connection, guild_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT calendar FROM settings WHERE guild_id = ? ", [guild_id])
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)

def select_guild_events_bool(conn: Connection, guild_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT guild_events FROM settings WHERE guild_id = ? ", [guild_id])
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)


def insert_or_update_calendars(conn: Connection, guild_id: int, ids: str, guild_events: bool):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO settings(guild_id, calendar, guild_events) VALUES (?, ?, ?) ON CONFLICT (guild_id) DO UPDATE SET calendar = "
            "EXCLUDED.calendar, guild_events = EXCLUDED.guild_events ",
            (guild_id, ids, guild_events),
        )
        return True
    except sqlite3.Error as e:
        logger.exception(e)

def insert_or_update_calendar_id(conn: Connection, guild_id: int, ids: str):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO settings(guild_id, calendar) VALUES (?, ?) ON CONFLICT (guild_id) DO UPDATE SET calendar = "
            "EXCLUDED.calendar",
            (guild_id, ids))
        return True
    except sqlite3.Error as e:
        logger.exception(e)


# endregion

# region settings-timezone-statements

def insert_or_update_server_timezone(conn: Connection, guild_id: int, timezone: str):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO settings(guild_id, timezone) VALUES (?, ?) ON CONFLICT (guild_id) DO UPDATE SET calendar = "
            "EXCLUDED.timezone",
            (timezone, guild_id),
        )
        return True
    except sqlite3.Error as e:
        logger.exception(e)


def select_server_timezone(conn: Connection, guild_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT timezone FROM settings WHERE guild_id = (?)", [guild_id])
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)


# endregion

# region personal-timezone-statements

def insert_or_replace_personal_timezone(conn: Connection, guild_id, timezone):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO timezone VALUES (?, ?)", (guild_id, timezone)
        )
        return True
    except sqlite3.Error as e:
        logger.exception(e)
def select_personal_timezone(conn: Connection, user_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT timezone FROM timezone WHERE user_id = (?)", [user_id])
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)


# endregion

# region poll-statements
def insert_or_replace_poll(
        conn: Connection,
        poll_id: int,
        channel_id: int,
        guild_id: int,
        author_id: int,
        number_of_options: int,
        multiple_selection: bool,
):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO polls(poll_id, channel_id, guild_id, author_id, number_of_options, "
            "multiple_selection) VALUES (?, ?, ?, ?, ?, ?)",
            (
                poll_id,
                channel_id,
                guild_id,
                author_id,
                number_of_options,
                multiple_selection,
            ),
        )
        return True
    except sqlite3.Error as e:
        logger.exception(e)


def set_question_for_poll(conn: Connection, poll_id: int, question: str):
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE polls SET question = ? WHERE poll_id = {poll_id}", [question]
        )
    except sqlite3.Error as e:
        logger.exception(e)


def select_one_poll(conn: Connection, poll_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM polls WHERE poll_id = (?)", [poll_id])
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)


def select_options_for_poll(conn: Connection, poll_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM PollOptions WHERE poll_id = ?", [poll_id])
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.exception(e)


def insert_or_replace_poll_option(conn: Connection, poll_id, option_id, option):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO PollOptions VALUES (?, ?, ?)",
            (poll_id, option_id, option),
        )
        return True
    except sqlite3.Error as e:
        logger.exception(e)


def insert_or_replace_vote(
        conn: Connection, user_id: int, poll_id: int, option_id: int
):
    try:

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM votes WHERE user_id = (?) AND poll_id = (?) AND option_id = (?)",
            (user_id, poll_id, str(option_id)),
        )

        result = cursor.fetchone()
        if result:
            cursor.execute(
                "DELETE FROM votes WHERE user_id = (?) AND poll_id = (?) AND option_id = (?)",
                (user_id, poll_id, str(option_id)),
            )
            return []
        else:
            cursor.execute(
                "INSERT OR REPLACE INTO votes VALUES (?, ?, ?)",
                (poll_id, str(option_id), user_id),
            )
        return [option_id]
    except sqlite3.Error as e:
        logger.exception(e)


def count_votes(conn: Connection, poll_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM votes WHERE poll_id = ?", [poll_id])
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)


def delete_poll_votes_options(conn: Connection, poll_id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM votes WHERE poll_id = ?", [poll_id])
        cursor.execute("DELETE FROM pollOptions WHERE poll_id = ?", [poll_id])
        cursor.execute("DELETE FROM polls WHERE poll_id = ?", [poll_id])
        return True
    except sqlite3.Error as e:
        logger.exception(e)


def count_votes_for_option(conn: Connection, option_id, poll_id):
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT COUNT(*) FROM votes WHERE poll_id = {poll_id} AND option_id LIKE ?",
            [f"%{option_id}%"],
        )
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)


def set_or_add_vote(conn: Connection, user_id, poll_id, option_id):
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT COUNT(*) FROM votes WHERE poll_id = {poll_id} AND user_id = {user_id}"
        )
        result = cursor.fetchone()
        if result[0] == 0:
            cursor.execute(
                "INSERT INTO votes VALUES (?, ?, ?)",
                (poll_id, f"{option_id};", user_id),
            )
            return [f"{option_id}"]
        cursor.execute(
            f"SELECT option_id FROM votes WHERE poll_id = {poll_id} AND user_id = {user_id}"
        )
        ids = cursor.fetchone()[0]
        if str(option_id) in ids:
            ids = ids.replace(f"{option_id};", "")
        else:
            ids = f"{ids}{option_id};"

        cursor.execute(
            f"UPDATE votes SET option_id = (?) WHERE poll_id = {poll_id} AND user_id = {user_id}",
            [str(ids)],
        )
        return ids.split(";")
    except sqlite3.Error as e:
        logger.exception(e)

# endregion
