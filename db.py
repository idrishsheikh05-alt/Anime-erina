import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

# Yeh parameter strict X509 checking ko bypass kar dega
client = AsyncIOMotorClient(
    MONGO_URL, 
    tls=True, 
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True
)
db = client["NovaAuctionBot"]

# Collections
Users = db["USERS"]
Groups = db["GROUPS"]
Banned = db["BANNED"]
Poke = db["POKEMON"]
SudoDB = db["SUDODB"]
Settings = db["SETTINGS"]
Approved = db["APPROVED"]