import json
import logging
import sqlite3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        logger.exception(e)
    return conn


def create_table(conn, table):
    """ create a database table """
    sql = table_sqls(table)
    try:
        c = conn.cursor()
        c.execute(sql)
    except sqlite3.Error as e:
        logger.exception(e)


def table_sqls(table):
    sql_dict = {
            'raid': "create table if not exists Raids ("
                    "raid_id integer primary key, "
                    "channel_id integer not null, "
                    "guild_id integer not null, "
                    "author_id integer not null, "
                    "name text not null, "
                    "mode text, "
                    "time integer not null, "
                    ");",


            'assign': "create table if not exists Assignment ("
                      "raid_id integer not null, "
                      "player_id integer not null, "
                      "role text, "
                      "timestamp integer, "
                      "primary key (raid_id, player_id), "
                      "foreign key (raid_id) references Raids(raid_id)"
                      "foreign kez (player_id) references Players(player_id)"
                      ");",
    }
    return sql_dict[table]


def insert_raid(conn, *args):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO raids VALUES ?", args)
    except sqlite3.Error as e:
        logger.exception(e)


def select_one_raid(conn, raid_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM raids WHERE raid_id = ?", raid_id)
        result = cursor.fetchone()
        if result and len(result) == 1:
            return result[0]
        return result
    except sqlite3.Error as e:
        logger.exception(e)


def update_raid(conn, raid_id, column, value):
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE raids SET {column} = ?", value)
    except sqlite3.Error as e:
        logger.exception(e)


def insert_or_update_assignment(conn, player_id, raid_id, role, timestamp):
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE assignment SET timestamp = {timestamp}, SET role = ? WHERE raid_id = {raid_id} AND player_id = {player_id}", role)
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO assignment VALUES ?", raid_id, player_id, role, timestamp)
        return True
    except sqlite3.Error as e:
        logger.exception(e)
