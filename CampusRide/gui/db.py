import mysql.connector
import configparser
import os

config = configparser.ConfigParser()

config_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "config.ini"
)

loaded = config.read(config_path)

if not loaded:
    raise FileNotFoundError("config.ini was not found!")

if "mysql" not in config:
    raise ValueError("Missing [mysql] section in config.ini")


def connect():
    """Connect to the MySQL database."""

    return mysql.connector.connect(
        host=config["mysql"]["host"],
        user=config["mysql"]["user"],
        password=config["mysql"]["password"],
        database=config["mysql"]["database"],
        port=int(config["mysql"]["port"])
    )


def fetch_all(sql, params=None):
    """Execute a SELECT query and return all rows."""

    conn = connect()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(sql, params or ())
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def call_proc(name, args):
    """Call a stored procedure."""

    conn = connect()
    cursor = conn.cursor()

    try:
        result = cursor.callproc(name, args)

        # Collect any result sets produced by the procedure
        results = []

        for item in cursor.stored_results():
            results.append(item.fetchall())

        conn.commit()

        return result, results

    except mysql.connector.Error:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()