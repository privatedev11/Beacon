# Lets users save shorthand names for server addresses, scoped per-guild.
# Also exposes host_autocomplete(), shared by this cog's own commands and
# by cogs/server.py's `host` parameter.

import discord
from discord import app_commands
from discord.ext import commands

import storage.hosts as hosts_storage


async def host_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """
    Suggests saved shorthands as the user types.
    Shared across cogs, imported directly
    """
    if interaction.guild_id is None:
        return []
    saved = hosts_storage.list_hosts(interaction.guild_id)
    matches = [
        (shorthand, host) for shorthand, host in saved
        if current.lower() in shorthand.lower()
    ]
    return [
        app_commands.Choice(name=f"{shorthand} -> {host}", value=shorthand)
        for shorthand, host in matches[:25]  # Discord caps autocomplete results at 25
    ]


class Hosts(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="addhost", description="Save a shorthand for a Minecraft server address.")
    @app_commands.describe(shorthand="Name to refer to this server by", host="The server address")
    async def addhost(self, interaction: discord.Interaction, shorthand: str, host: str):
        if interaction.guild_id is None:
            await interaction.response.send_message("This command only works in a server.", ephemeral=True)
            return

        hosts_storage.add_host(interaction.guild_id, shorthand, host, interaction.user.id)
        await interaction.response.send_message(
            f"Saved **{shorthand}** -> `{host}`. You can now use `{shorthand}` anywhere a host is expected.",
            ephemeral=True,
        )

    @app_commands.command(name="removehost", description="Remove a saved server shorthand.")
    @app_commands.describe(shorthand="The shorthand to remove")
    @app_commands.autocomplete(shorthand=host_autocomplete)
    async def removehost(self, interaction: discord.Interaction, shorthand: str):
        if interaction.guild_id is None:
            await interaction.response.send_message("This command only works in a server.", ephemeral=True)
            return

        removed = hosts_storage.remove_host(interaction.guild_id, shorthand)
        if removed:
            await interaction.response.send_message(f"Removed shorthand **{shorthand}**.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No shorthand named **{shorthand}** was found.", ephemeral=True)

    @app_commands.command(name="listhosts", description="List all saved server shorthands for this server.")
    async def listhosts(self, interaction: discord.Interaction):
        if interaction.guild_id is None:
            await interaction.response.send_message("This command only works in a server.", ephemeral=True)
            return

        saved = hosts_storage.list_hosts(interaction.guild_id)
        if not saved:
            await interaction.response.send_message("No shorthands saved yet. Use `/addhost` to create one.", ephemeral=True)
            return

        lines = [f"**{shorthand}** -> `{host}`" for shorthand, host in saved]
        embed = discord.Embed(title="Saved Server Shorthands", description="\n".join(lines))
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Hosts(bot))