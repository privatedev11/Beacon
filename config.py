# Beacon - config.py
# Loads environment variables once and exposes them as constants.
# Every other module should import from here instead of calling os.getenv directly.

import os
from dotenv import load_dotenv

load_dotenv()

VERSION = "26.07.1"

# --- Discord ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "1528725991273398342"))

# --- Issue tracker integrations ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "privatedev11/Beacon")

# --- Misc ---
DB_PATH = os.getenv("BEACON_DB_PATH", "beacon.db")

# --- Embed colors (for consistency) ---
COLOR_INFO = 5868799
COLOR_SERVER = 3447003
COLOR_ERROR = 15158332

# --- Watcher settings ---
MIN_WATCH_INTERVAL_MINUTES = 2  # floor, to avoid hitting rate limits

# --- Host registry settings ---
HOST_MIN_QUERY_INTERVAL_SECONDS = int(os.getenv("HOST_MIN_QUERY_INTERVAL_SECONDS", "60"))
HOST_BACKOFF_BASE_SECONDS = int(os.getenv("HOST_BACKOFF_BASE_SECONDS", "60"))
HOST_BACKOFF_MAX_SECONDS = int(os.getenv("HOST_BACKOFF_MAX_SECONDS", "1800"))