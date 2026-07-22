# Just the /about command.

import discord
from discord import app_commands
from discord.ext import commands

from config import VERSION, COLOR_INFO


class About(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="about", description="Shows info about the bot.")
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(
            color=COLOR_INFO,
            title="Beacon",
            description=(
                f"A small Discord bot to display Minecraft server information.\n"
                f"Version {VERSION}\n"
                f"For more information, check out the [Github repository](https://github.com/privatedev11/Beacon)."
            ),
        )
        embed.set_thumbnail(url="https://i.postimg.cc/Pq4ckf86/Beacon-Logo.png")
        embed.set_footer(
            text="Copyright (C) 2026 Beacon.",
            icon_url="https://i.postimg.cc/QNbkYjb4/New-PFP.jpg",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(About(bot))