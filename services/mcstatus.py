# Wraps calls to api.mcstatus.io.

import asyncio
import base64
import io
from dataclasses import dataclass
from typing import Optional

import requests

API_BASE = "https://api.mcstatus.io/v2/status/java"


@dataclass
class ServerStatus:
    online: Optional[bool]
    motd: Optional[str]
    players_online: Optional[int]
    players_max: Optional[int]
    icon_bytes: Optional[io.BytesIO]
    is_aternos: bool


def _fetch_sync(host: str) -> ServerStatus:
    response = requests.get(f"{API_BASE}/{host}", timeout=10)
    response.raise_for_status()
    data = response.json()

    online = data.get("online")
    motd = data.get("motd", {}).get("clean")
    players_online = data.get("players", {}).get("online")
    players_max = data.get("players", {}).get("max")

    icon_bytes = None
    icon_b64 = data.get("icon")
    if icon_b64:
        if "," in icon_b64:
            icon_b64 = icon_b64.split(",")[1]
        icon_bytes = io.BytesIO(base64.b64decode(icon_b64))

    return ServerStatus(
        online=online,
        motd=motd,
        players_online=players_online,
        players_max=players_max,
        icon_bytes=icon_bytes,
        is_aternos="aternos.me" in host,
    )


async def fetch_server_status(host: str) -> ServerStatus:
    """runs the blocking `requests` call in a thread"""
    return await asyncio.to_thread(_fetch_sync, host)