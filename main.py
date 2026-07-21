# Beacon - a small Discord bot to display Minecraft server information.
# Copyright (C) 2026 PrivateMe
# This program is licenced under the GNU General Pu+blic Licence v3. If you did not recieve a copy of this licence with the program, please visit https://www.gnu.org/licenses/
version = "26.07.1"
import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import requests
import urllib
import base64
from PIL import Image
import io
import datetime

load_dotenv()

class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}")

        try:
            guild = discord.Object(id=1528725991273398342)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to dev guild of ID {guild.id}")

        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_message(self, message):
        if message.author == self.user:
            return
        
intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=1528725991273398342)

@client.tree.command(name="about", description="Shows info about the bot.", guild=GUILD_ID)
async def aboutCmd(interaction: discord.Interaction):
    aboutEmbed = discord.Embed(
    color=5868799,
    title="Beacon",
    description=f"A small Discord bot to display Minecraft server information.\nVersion {version}\nFor more information, check out the [Github repository](https://github.com/privatedev11/Beacon).",
)
    aboutEmbed.set_thumbnail(url="https://i.postimg.cc/Pq4ckf86/Beacon-Logo.png")
    aboutEmbed.set_footer(
        text="Copyright (C) 2026 PrivateMe.",
        icon_url="https://i.postimg.cc/QNbkYjb4/New-PFP.jpg",
    )
    await interaction.response.send_message(embed=aboutEmbed, ephemeral=True)

@client.tree.command(name="getserverinfo", description="Gets info about a Minecraft server.", guild=GUILD_ID)
async def serverInfoCmd(interaction: discord.Interaction, host: str):
    await interaction.response.defer()
    aternosText = None
    if "aternos.me" in host:
        aternosText = (
            "**Important for Aternos servers**\n"
            "Due to the nature of how Aternos processes server data, some information reported by the bot may be incorrect, for example, showing the server as being online even if it isn't.\n"
            "For more information, see section 11 of https://mcstatus.io/about."
        )
    mcServerSearch = requests.get(f"https://api.mcstatus.io/v2/status/java/{host}")
    mcServerSearchJson = mcServerSearch.json()
    
    onlineStatus = mcServerSearchJson.get("online")
    motd = mcServerSearchJson.get("motd", {}).get("clean")
    playersOnline = mcServerSearchJson.get("players", {}).get("online")
    maxPlayers = mcServerSearchJson.get("players", {}).get("max")
    
    # The API returns images as Base64, which means I have to do this fuckery for it to display.
    iconBase64 = mcServerSearchJson.get("icon")
    
    iconFile = None

    if iconBase64:
        if "," in iconBase64:
            iconBase64 = iconBase64.split(",")[1]
        
        imageBytes = base64.b64decode(iconBase64)
        imageBuffer = io.BytesIO(imageBytes)
        iconFile = discord.File(fp=imageBuffer, filename="icon.png")

    serverInfoCmdEmbed = discord.Embed(
    color=3447003,
    title="Server Information",
    description=f"Server Online?: {onlineStatus}\nMOTD: {motd}\nHost: {host}\nPlayers Online: {playersOnline}/{maxPlayers}",
    timestamp=datetime.datetime.now(),
)
    serverInfoCmdEmbed.set_thumbnail(url="attachment://icon.png")
    serverInfoCmdEmbed.set_footer(
        text="Provided by Beacon and mcstatus.io",
    )

    if iconFile:
        await interaction.followup.send(content=aternosText, embed=serverInfoCmdEmbed, file=iconFile)
    # This is required as otherwise servers with no image return an error.
    else:
       await interaction.followup.send(content=aternosText, embed=serverInfoCmdEmbed)
# This might work? AI helped with this part unfortunately
@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f"ERROR: {error}")

    serverInfoCmdErrorMsg = (
        "Error returned when checking server data. "
        "If your server link was by a free hosting provider such as Aternos, this could be why. "
        "If not, make an issue on the GitHub: https://github.com/privatedev11/Beacon/issues"
    )

    try:
        # Check if response was already deferred or sent
        if interaction.response.is_done():
            await interaction.followup.send(serverInfoCmdErrorMsg, ephemeral=True)
        else:
            await interaction.response.send_message(serverInfoCmdErrorMsg, ephemeral=True)
    except Exception as e:
        # Catch any send failures so the error handler itself never crashes
        print(f"Failed to send error response to user: {e}")



token = os.getenv("DISCORD_TOKEN")
client.run(token)
