# CRUD helpers for the `hosts` table (per-guild shorthand -> address mapping).

# I used ai for this because I don't know the sqlite module, someone who does please refactor

from typing import Optional
from storage.db import get_connection


def add_host(guild_id: int, shorthand: str, host: str, added_by: int) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO hosts (guild_id, shorthand, host, added_by)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(guild_id, shorthand) DO UPDATE SET
            host = excluded.host,
            added_by = excluded.added_by
        """,
        (guild_id, shorthand.lower(), host, added_by),
    )
    conn.commit()


def remove_host(guild_id: int, shorthand: str) -> bool:
    """Returns True if a row was actually deleted."""
    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM hosts WHERE guild_id = ? AND shorthand = ?",
        (guild_id, shorthand.lower()),
    )
    conn.commit()
    return cur.rowcount > 0


def get_host(guild_id: int, shorthand: str) -> Optional[str]:
    conn = get_connection()
    row = conn.execute(
        "SELECT host FROM hosts WHERE guild_id = ? AND shorthand = ?",
        (guild_id, shorthand.lower()),
    ).fetchone()
    return row["host"] if row else None


def list_hosts(guild_id: int) -> list[tuple[str, str]]:
    """Returns a list of (shorthand, host) tuples for the guild."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT shorthand, host FROM hosts WHERE guild_id = ? ORDER BY shorthand",
        (guild_id,),
    ).fetchall()
    return [(r["shorthand"], r["host"]) for r in rows]


def resolve_host(guild_id: int, input_str: str) -> str:
    """
    Resolves user input to an actual server address:
    checks saved shorthands first, falls back to treating input as a literal host.
    """
    saved = get_host(guild_id, input_str)
    return saved if saved else input_str