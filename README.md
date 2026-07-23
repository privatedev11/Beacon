# Beacon

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/privatedev11/Beacon)
![GitHub last commit](https://img.shields.io/github/last-commit/privatedev11/Beacon)
![GitHub License](https://img.shields.io/github/license/privatedev11/Beacon)
![GitHub Repo stars](https://img.shields.io/github/stars/privatedev11/Beacon)

A small Discord bot to display Minecraft server information

# Running
You will need to create a `.env` file with the `DISCORD_TOKEN` variable equal to your Discord bot token, obtained from the Discord Developer Portal, and the `DEV_GUILD` variable set to the guild ID of the server you want to use the bot in. This means that when commands are added or updated, they are instantly updated in that server specifically.

You will need to install the following pip packages:
- discord
- python-dotenv
- requests
- urllib3
- pillow

Make sure to invite the bot to your server and it should then work!

You can view the full documentation for either running on Docker or manually setting it up on the [documentation page.](https://docs.beacondev.org/en/latest/gettingstarted/)