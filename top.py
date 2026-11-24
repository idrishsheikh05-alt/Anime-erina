from pyrogram import Client, filters
from pyrogram.types import Message

from Nova.db import Poke

def make_bq(text):
    return "\n".join([f"> {line}" for line in str(text).split("\n")])

@Client.on_message(filters.command("topbuyers"))
async def top_buyers_cmd(client: Client, message: Message):
    msg = await message.reply_text("🔄 **ғᴇᴛᴄʜɪɴɢ ᴛᴏᴘ ʙᴜʏᴇʀs...**")

    # Aggregation to group by buyer, sum spent NovaRupee, and sort descending
    pipeline = [
        {"$match": {"status": "sold", "buyer_id": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": "$buyer_id", 
            "total_spent": {"$sum": "$sold_price"}, 
            "mention": {"$first": "$buyer_mention"}
        }},
        {"$sort": {"total_spent": -1}},
        {"$limit": 10}
    ]
    
    cursor = Poke.aggregate(pipeline)
    top_buyers = await cursor.to_list(length=10)

    if not top_buyers:
        return await msg.edit_text("ℹ️ ɴᴏ ʙᴜʏᴇʀs ғᴏᴜɴᴅ ʏᴇᴛ.")

    text = "🏆 **ᴛᴏᴘ 10 ʙᴜʏᴇʀs** 🏆\n\n"
    
    # Compact format
    details_list = []
    for idx, buyer in enumerate(top_buyers, start=1):
        mention = buyer.get("mention", "Unknown Buyer")
        spent = buyer.get("total_spent", 0)
        details_list.append(f"`{idx}.` {mention} ━ 💸 **{spent:,} ɴᴏᴠᴀʀᴜᴘᴇᴇ**")
        
    text += make_bq("\n".join(details_list))

    await msg.edit_text(text)


@Client.on_message(filters.command("topsellers"))
async def top_sellers_cmd(client: Client, message: Message):
    msg = await message.reply_text("🔄 **ғᴇᴛᴄʜɪɴɢ ᴛᴏᴘ sᴇʟʟᴇʀs...**")

    # Aggregation to group by seller, sum earned NovaRupee, and sort descending
    pipeline = [
        {"$match": {"status": "sold", "seller_id": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": "$seller_id", 
            "total_earned": {"$sum": "$sold_price"}, 
            "mention": {"$first": "$seller_mention"}
        }},
        {"$sort": {"total_earned": -1}},
        {"$limit": 10}
    ]
    
    cursor = Poke.aggregate(pipeline)
    top_sellers = await cursor.to_list(length=10)

    if not top_sellers:
        return await msg.edit_text("ℹ️ ɴᴏ sᴇʟʟᴇʀs ғᴏᴜɴᴅ ʏᴇᴛ.")

    text = "🏆 **ᴛᴏᴘ 10 sᴇʟʟᴇʀs** 🏆\n\n"
    
    # Compact format
    details_list = []
    for idx, seller in enumerate(top_sellers, start=1):
        mention = seller.get("mention", "Unknown Seller")
        earned = seller.get("total_earned", 0)
        details_list.append(f"`{idx}.` {mention} ━ 📈 **{earned:,} ɴᴏᴠᴀʀᴜᴘᴇᴇ**")
        
    text += make_bq("\n".join(details_list))

    await msg.edit_text(text)
