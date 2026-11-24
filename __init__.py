# __init__.py

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
import logging

# 🔥 Logging Setup
logging.basicConfig(
    format="[PoKe-Realm-Bot] %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs.txt"),
        logging.StreamHandler()
    ],
    level=logging.INFO
)

# 🔥 Plugin directory (change here only)
command_directory = "Nova/Command"

# 🔥 Main Bot Client
bot = Client(
    "NovaAuction-Bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root=command_directory)
)

DEVS=[8758766563, 7753964339]
ADMINS=[8758766563]