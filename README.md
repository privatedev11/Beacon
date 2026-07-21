# Beacon
A small Discord bot to display Minecraft server information

# Running
You will need to create a `.env` file with the `DISCORD_TOKEN` variable equal to your Discord bot token, obtained from the Discord Developer Portal, and the `DEV_GUILD` variable set to the guild ID of the server you want to use the bot in. This means that when commands are added or updated, they are instantly updated in that server specifically.

You will need to install the following pip packages:
- discord
- python-dotenv
- requests
- urllib3