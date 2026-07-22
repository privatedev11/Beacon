# Beacon - a small Discord bot to display Minecraft server information.
# Copyright (C) 2026 PrivateMe
# This program is licenced under the GNU General Public Licence v3. If you did
# not receive a copy of this licence with the program, please visit
# https://www.gnu.org/licenses/

import discord
from discord.ext import commands
from discord import app_commands

from config import DISCORD_TOKEN, GUILD_ID
from storage.db import init_db

EXTENSIONS = [
    "cogs.about",
    "cogs.server",
    "cogs.hosts",
    "cogs.issues",
]


class Client(commands.Bot):
    async def setup_hook(self):
        init_db()
        for extension in EXTENSIONS:
            print(f"loading extension {extension}")
            await self.load_extension(extension)
            print(f"loaded extension {extension}")

        print(self.tree.get_commands())
        print(self.tree.get_commands(guild=discord.Object(id=GUILD_ID)))

        guild = discord.Object(id=GUILD_ID)
        synced = await self.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands to guild {GUILD_ID}")

    async def on_ready(self):
        print(f"Logged on as {self.user}")

    async def on_message(self, message):
        if message.author == self.user:
            return


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)


@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f"ERROR: {error}")

    error_msg = (
        "Something went wrong running that command. "
        "If it involved a server address (e.g. via a free host like Aternos), that may be why. "
        "Otherwise, please open an issue: https://github.com/privatedev11/Beacon/issues"
    )

    try:
        if interaction.response.is_done():
            await interaction.followup.send(error_msg, ephemeral=True)
        else:
            await interaction.response.send_message(error_msg, ephemeral=True)
    except Exception as e:
        print(f"Failed to send error response to user: {e}")


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
