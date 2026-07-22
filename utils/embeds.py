# Builds the discord.Embed objects used across cogs, so the one-shot /getserverinfo command and the background watcher loop stay visually identical.

import datetime
from typing import Optional

import discord

from config import COLOR_SERVER, COLOR_ERROR
from services.mcstatus import ServerStatus


def build_server_embed(host: str, status: ServerStatus) -> tuple[discord.Embed, Optional[discord.File]]:
    if status.edition == "bedrock":
        title="🟩 Minecraft Bedrock Server"
    elif status.edition == "java":
        title="🟦 Minecraft Java Server"
    else:
        title="Not a server?"
    
    embed = discord.Embed(
        color=COLOR_SERVER,
        title=title,
        description=(
            f"Server Online?: {status.online}\n"
            f"MOTD: {status.motd}\n"
            f"Host: {host}\n"
            f"Players Online: {status.players_online}/{status.players_max}"
        ),
        timestamp=datetime.datetime.now(),
    )
    embed.set_footer(text="Provided by Beacon")

    icon_file = None
    if status.icon_bytes:
        # Fresh copy of the buffer each time this is called, since BytesIO
        # objects are single-use once passed to discord.File.
        status.icon_bytes.seek(0)
        icon_file = discord.File(fp=status.icon_bytes, filename="icon.png")
        embed.set_thumbnail(url="attachment://icon.png")

    return embed, icon_file


def build_aternos_notice() -> str:
    return (
        "**Important for Aternos servers**\n"
        "Due to the nature of how Aternos processes server data, some information reported by the bot may be incorrect, "
        "for example, showing the server as being online even if it isn't.\n"
        "For more information, see section 11 of https://mcstatus.io/about."
    )


def build_error_embed(message: str) -> discord.Embed:
    return discord.Embed(
        color=COLOR_ERROR,
        title="Something went wrong",
        description=message,
    )
