# /issue collects a title + description via a modal, then lets the user pick
# GitHub or Linear as the destination. All actual API calls live in services/.

import discord
from discord import app_commands, ui
from discord.ext import commands

import services.github as github_service
import services.linear as linear_service
from utils.embeds import build_error_embed


class IssueModal(ui.Modal, title="Report an Issue"):
    issue_title = ui.TextInput(label="Title", placeholder="Short summary of the problem", max_length=100)
    issue_description = ui.TextInput(
        label="Description",
        style=discord.TextStyle.paragraph,
        placeholder="What happened? Steps to reproduce, if any.",
        max_length=1000,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        view = DestinationView(title=str(self.issue_title), description=str(self.issue_description))
        await interaction.response.send_message(
            "Where should this issue be filed?", view=view, ephemeral=True
        )


class DestinationView(ui.View):
    def __init__(self, title: str, description: str):
        super().__init__(timeout=120)
        self.title_text = title
        self.description_text = description

    @ui.button(label="GitHub", style=discord.ButtonStyle.primary)
    async def github_button(self, interaction: discord.Interaction, button: ui.Button):
        await self._submit(interaction, github_service)

    @ui.button(label="Linear", style=discord.ButtonStyle.secondary)
    async def linear_button(self, interaction: discord.Interaction, button: ui.Button):
        await self._submit(interaction, linear_service)

    async def _submit(self, interaction: discord.Interaction, service):
        await interaction.response.defer(ephemeral=True)

        success, result = await service.create_issue(self.title_text, self.description_text)

        if success:
            await interaction.followup.send(f"Issue created: {result}", ephemeral=True)
        else:
            await interaction.followup.send(embed=build_error_embed(result), ephemeral=True)

        self.stop()


class Issues(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="issue", description="Report an issue to the developers!")
    async def issue(self, interaction: discord.Interaction):
        await interaction.response.send_modal(IssueModal())


async def setup(bot: commands.Bot):
    await bot.add_cog(Issues(bot))