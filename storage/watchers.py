# CRUD helpers for the `watchers` table (auto-updating server-info embeds).

# I used ai to help for this because I don't know the sqlite module, someone who does please refactor

from typing import Optional
from storage.db import get_connection


def add_watcher(
    message_id: int,
    channel_id: int,
    guild_id: int,
    host: str,
    interval_mins: int,
    ping_role_id: Optional[int] = None,
    last_status: Optional[str] = None,
    title: Optional[str] = None,
) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO watchers (message_id, channel_id, guild_id, host, interval_mins, last_updated, ping_role_id, last_status, title)
        VALUES (?, ?, ?, ?, ?, NULL, ?, ?, ?)
        """,
        (message_id, channel_id, guild_id, host, interval_mins, ping_role_id, last_status, title),
    )
    conn.commit()


def remove_watcher(message_id: int) -> bool:
    conn = get_connection()
    cur = conn.execute("DELETE FROM watchers WHERE message_id = ?", (message_id,))
    conn.commit()
    return cur.rowcount > 0


def get_watcher(message_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM watchers WHERE message_id = ?", (message_id,)).fetchone()
    return dict(row) if row else None


def get_all_watchers() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM watchers").fetchall()
    return [dict(r) for r in rows]


def update_last_updated(message_id: int, timestamp_iso: str) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE watchers SET last_updated = ? WHERE message_id = ?",
        (timestamp_iso, message_id),
    )
    conn.commit()


def update_status_ping(message_id: int, status: str, ping_message_id: Optional[int]) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE watchers SET last_status = ?, last_ping_message_id = ? WHERE message_id = ?",
        (status, ping_message_id, message_id),
    )
    conn.commit()