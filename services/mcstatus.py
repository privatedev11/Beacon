# Wraps calls to Minecraft servers using the mcstatus package.

import base64
import io
import time
from dataclasses import dataclass
from typing import Optional

from mcstatus import JavaServer
from mcstatus.bedrock import BedrockServer
import re

MINECRAFT_FORMATTING = re.compile(r"§[0-9a-fk-or]", re.IGNORECASE)
ICON_CACHE_TTL = 60 * 60 * 24  # 24 hours

# host -> (expires_at, icon_bytes)
_icon_cache: dict[str, tuple[float, bytes]] = {}


def _clean_motd(motd) -> Optional[str]:
    if motd is None:
        return None

    # mcstatus may return a Description object
    if hasattr(motd, "to_plain"):
        motd = motd.to_plain()

    elif not isinstance(motd, str):
        motd = str(motd)

    return MINECRAFT_FORMATTING.sub("", motd)

@dataclass
class ServerStatus:
    online: bool
    is_server: bool
    edition: Optional[str]
    motd: Optional[str]
    players_online: Optional[int]
    players_max: Optional[int]
    icon_bytes: Optional[io.BytesIO]
    is_aternos: bool


def _get_cached_icon(host: str) -> Optional[io.BytesIO]:
    cached = _icon_cache.get(host)
    if cached is None:
        return None

    expires_at, icon = cached

    if expires_at <= time.time():
        del _icon_cache[host]
        return None

    return io.BytesIO(icon)


def _cache_icon(host: str, icon: bytes) -> io.BytesIO:
    _icon_cache[host] = (time.time() + ICON_CACHE_TTL, icon)
    return io.BytesIO(icon)


async def fetch_server_status(host: str) -> ServerStatus:
    is_aternos = "aternos.me" in host

    # try Java edition
    try:
        server = await JavaServer.async_lookup(host)
        status = await server.async_status()

        icon_bytes = _get_cached_icon(host)

        if icon_bytes is None and status.icon:
            icon = base64.b64decode(
                status.icon.removeprefix("data:image/png;base64,")
            )
            icon_bytes = _cache_icon(host, icon)

        return ServerStatus(
            online=True,
            is_server=True,
            edition="java",
            motd=_clean_motd(status.description),
            players_online=status.players.online,
            players_max=status.players.max,
            icon_bytes=icon_bytes,
            is_aternos=is_aternos
        )

    except Exception:
        pass

    try:
        server = BedrockServer (host, port)
        status = await server. async_status ()
            
        return ServerStatus(
            online=True,
            is_server=True,
            edition="bedrock",
            motd=_clean_motd (status. motd),
            players_online=status.players_online,
            players_max=status.players_max,
            icon_bytes=None, # Bedrock does not provide server icons here
            is_aternos=is_aternos,
        except Exception:
            pass
            
            # Not a Minecraft server / unreachable
        return ServerStatus(
            online=False,
            is_server=False,
            edition=None,
            motd=None,
            players_online=None,
            players_max=None,
            icon_bytes=None,
            is_aternos=is_aternos,
                    
