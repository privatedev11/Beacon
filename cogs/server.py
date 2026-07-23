# Everything related to looking up a Minecraft server: the one-shot command
# and the auto-updating embed feature. Grouped together since they share the
# same lookup, embed-building, and host-resolution logic.

import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import MIN_WATCH_INTERVAL_MINUTES
from services.registry import registry
from storage.hosts import resolve_host
import storage.watchers as watcher_storage
from utils.embeds import build_server_embed, build_error_embed, build_aternos_notice
from cogs.hosts import host_autocomplete


class Server(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.refresh_watchers.start()

    def cog_unload(self):
        self.refresh_watchers.cancel()

    # ---------- one-shot lookup ----------

    @app_commands.command(name="getserverinfo", description="Gets info about a Minecraft server.")
    @app_commands.describe(host="A server address, or a saved shorthand from /addhost")
    @app_commands.autocomplete(host=host_autocomplete)
    async def getserverinfo(self, interaction: discord.Interaction, host: str):
        await interaction.response.defer()

        resolved_host = resolve_host(interaction.guild_id, host) if interaction.guild_id else host
        status = await registry.get_status(resolved_host)
        embed, icon_file = build_server_embed(resolved_host, status)

        content = build_aternos_notice() if status.is_aternos else None

        if icon_file:
            await interaction.followup.send(content=content, embed=embed, file=icon_file)
        else:
            await interaction.followup.send(content=content, embed=embed)

    # ---------- auto-updating embed ----------

    @app_commands.command(name="watchserver", description="Posts a server-info embed that keeps itself updated.")
    @app_commands.describe(
        host="A server address, or a saved shorthand from /addhost",
        interval="How often to refresh, in minutes (minimum 2)",
        ping_role="Role to mention when the server's online/offline status changes",
    )
    @app_commands.autocomplete(host=host_autocomplete)
    async def watchserver(
        self,
        interaction: discord.Interaction,
        host: str,
        interval: int = 5,
        ping_role: Optional[discord.Role] = None,
    ):
        if interval < MIN_WATCH_INTERVAL_MINUTES:
            await interaction.response.send_message(
                f"Interval must be at least {MIN_WATCH_INTERVAL_MINUTES} minutes.", ephemeral=True
            )
            return

        await interaction.response.defer()

        resolved_host = resolve_host(interaction.guild_id, host) if interaction.guild_id else host
        status = await registry.get_status(resolved_host)
        embed, icon_file = build_server_embed(resolved_host, status)
        content = build_aternos_notice() if status.is_aternos else None

        if icon_file:
            message = await interaction.followup.send(content=content, embed=embed, file=icon_file, wait=True)
        else:
            message = await interaction.followup.send(content=content, embed=embed, wait=True)

        watcher_storage.add_watcher(
            message_id=message.id,
            channel_id=message.channel.id,
            guild_id=interaction.guild_id,
            host=resolved_host,
            interval_mins=interval,
            ping_role_id=ping_role.id if ping_role else None,
            last_status="online" if status.online else "offline",
        )
        watcher_storage.update_last_updated(message.id, datetime.datetime.now(datetime.timezone.utc).isoformat())

    @app_commands.command(name="unwatch", description="Stops auto-updating a server-info embed.")
    @app_commands.describe(message_id="The ID of the message to stop updating (right-click -> Copy Message ID)")
    async def unwatch(self, interaction: discord.Interaction, message_id: str):
        try:
            parsed_id = int(message_id)
        except ValueError:
            await interaction.response.send_message("That doesn't look like a valid message ID.", ephemeral=True)
            return

        removed = watcher_storage.remove_watcher(parsed_id)
        if removed:
            await interaction.response.send_message("Stopped updating that embed.", ephemeral=True)
        else:
            await interaction.response.send_message("No watcher found for that message ID.", ephemeral=True)

    # ---------- background refresh ----------

    @tasks.loop(minutes=1)
    async def refresh_watchers(self):
        now = datetime.datetime.now(datetime.timezone.utc)

        due_watchers = []
        for watcher in watcher_storage.get_all_watchers():
            last_updated = watcher["last_updated"]
            due = True
            if last_updated:
                elapsed_mins = (now - datetime.datetime.fromisoformat(last_updated)).total_seconds() / 60
                due = elapsed_mins >= watcher["interval_mins"]

            if due:
                due_watchers.append(watcher)

        watchers_by_host: dict[str, list[dict]] = {}
        for watcher in due_watchers:
            watchers_by_host.setdefault(watcher["host"], []).append(watcher)

        for host, watchers in watchers_by_host.items():
            status = await registry.get_status(host)
            for watcher in watchers:
                await self._refresh_one(watcher, status)

    async def _refresh_one(self, watcher: dict, status):
        try:
            channel = self.bot.get_channel(watcher["channel_id"]) or await self.bot.fetch_channel(watcher["channel_id"])
            message = await channel.fetch_message(watcher["message_id"])
        except discord.NotFound:
            watcher_storage.remove_watcher(watcher["message_id"])
            return
        except discord.HTTPException as e:
            print(f"Failed to fetch watcher target {watcher['message_id']}: {e}")
            return

        try:
            embed, icon_file = build_server_embed(watcher["host"], status)
            # Editing a message can't swap its attachment via `file=`, so if the
            # icon changes shape this won't re-attach it - acceptable tradeoff
            # to avoid deleting/resending the message on every refresh.
            await message.edit(embed=embed)
        except Exception as e:
            print(f"Failed to refresh watcher {watcher['message_id']}: {e}")
            return

        watcher_storage.update_last_updated(
            watcher["message_id"], datetime.datetime.now(datetime.timezone.utc).isoformat()
        )

        new_status = "online" if status.online else "offline"
        if new_status != watcher["last_status"]:
            await self._handle_status_change(watcher, message.channel, new_status)

    async def _handle_status_change(self, watcher: dict, channel, new_status: str):
        if watcher["ping_role_id"]:
            old_ping_id = watcher["last_ping_message_id"]
            if old_ping_id:
                try:
                    old_ping = await channel.fetch_message(old_ping_id)
                    await old_ping.delete()
                except discord.HTTPException:
                    pass

            try:
                ping_message = await channel.send(
                    f"<@&{watcher['ping_role_id']}> **{watcher['host']}** is now **{new_status}**."
                )
                new_ping_id = ping_message.id
            except discord.HTTPException as e:
                print(f"Failed to send status ping for watcher {watcher['message_id']}: {e}")
                new_ping_id = watcher["last_ping_message_id"]
        else:
            new_ping_id = None

        watcher_storage.update_status_ping(watcher["message_id"], new_status, new_ping_id)

    @refresh_watchers.before_loop
    async def before_refresh_watchers(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Server(bot))