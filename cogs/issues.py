# /issue collects a title + description via a modal, pushes it to GitHub. All actual API calls live in services/.

import discord
from discord import app_commands, ui
from discord.ext import commands

import services.github as github_service
from utils.embeds import build_error_embed


class Issues(commands.Cog):
        def __init__(self, bot: commands.Bot):
            self.bot = bot

        @app_commands.command(name="issue", description="Report an issue to the developers!")
        @app_commands.checks.cooldown(2, 1800.0, key=lambda i: i.user.id)
        async def issue(self, interaction: discord.Interaction):
            await interaction.response.send_modal(IssueModal())

        # Error handler to catch the cooldown and notify the user
        @issue.error
        async def issue_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
            if isinstance(error, app_commands.CommandOnCooldown):
                    # Convert remaining seconds to minutes for a cleaner message
                    minutes_left = round(error.retry_after / 60)
                    await interaction.response.send_message(
                    f"You are opening issues too fast! Please try again in about {minutes_left} minutes. \nNeed to open more issues? Open one directly on the [GitHub](https://github.com/privatedev11/Beacon).",
                    ephemeral=True
                    )
            else:
                    # Fallback for other potential errors
                    await interaction.response.send_message(
                            "An unexpected error occurred.",
                            ephemeral=True
                    )

async def setup(bot: commands.Bot):
        await bot.add_cog(Issues(bot))

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
        success, result = await github_service.create_issue(
            self.issue_title.value,
            self.issue_description.value,
        )

        if success:
            await interaction.response.send_message(
                f"Issue created successfully!\n{result}",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"Failed to create issue:\n{result}",
                ephemeral=True,
            )


