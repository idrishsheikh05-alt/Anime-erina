import os

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "BOT_TOKEN")
MONGO_URL = os.getenv(
    "MONGO_URL",
    "YOUR_MONGO_URL"
)