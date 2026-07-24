# Owns the single SQLite connection and table creation.
# Other storage modules import `get_connection()` from here instead of
# opening their own connections, so there's one source of truth for the schema.

# I used ai for this because I don't know the sqlite module, someone who does PLEASE review this

import sqlite3
import threading
from config import DB_PATH

_local = threading.local()


def get_connection() -> sqlite3.Connection:
    """
    Returns a connection scoped to the current thread.
    discord.py commands normally run on the same event-loop thread, but we
    use a thread-local anyway so this is safe if anything ever calls into
    storage from a worker thread (e.g. via asyncio.to_thread).
    """
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect(DB_PATH)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA foreign_keys = ON")
    return _local.conn


def init_db() -> None:
    """Creates tables if they don't already exist. Call once on bot startup."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS hosts (
            guild_id   INTEGER NOT NULL,
            shorthand  TEXT NOT NULL,
            host       TEXT NOT NULL,
            added_by   INTEGER NOT NULL,
            PRIMARY KEY (guild_id, shorthand)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS watchers (
            message_id          INTEGER PRIMARY KEY,
            channel_id          INTEGER NOT NULL,
            guild_id            INTEGER NOT NULL,
            host                TEXT NOT NULL,
            interval_mins       INTEGER NOT NULL,
            last_updated        TEXT,
            ping_role_id        INTEGER,
            last_status         TEXT,
            last_ping_message_id INTEGER,
            title               TEXT
        )
        """
    )
    conn.commit()
    _migrate_watchers_columns(conn)


def _migrate_watchers_columns(conn) -> None:
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(watchers)")}
    required = {
        "ping_role_id": "INTEGER",
        "last_status": "TEXT",
        "last_ping_message_id": "INTEGER",
        "title": "TEXT",
    }
    for column, col_type in required.items():
        if column not in existing:
            conn.execute(f"ALTER TABLE watchers ADD COLUMN {column} {col_type}")
    conn.commit()