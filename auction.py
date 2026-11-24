import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from Nova import DEVS
from Nova.db import Poke, SudoDB, Settings

AUCTION_CHANNEL_ID = -1004230427074
ADMIN_GC_ID = -1004299578852 

async def is_admin(user_id: int):
    if user_id in DEVS:
        return True
    sudo_user = await SudoDB.find_one({"user_id": user_id})
    return bool(sudo_user)

@Client.on_message(filters.command("start_auc") & filters.group)
async def start_auction_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return

    # Enable bidding globally
    await Settings.update_one({"_id": "bidding_status"}, {"$set": {"is_open": True}}, upsert=True)

    await message.reply_text("✅ **ᴀᴜᴄᴛɪᴏɴ ᴏғғɪᴄɪᴀʟʟʏ sᴛᴀʀᴛᴇᴅ!** ᴜsᴇʀs ᴄᴀɴ ɴᴏᴡ ᴘʟᴀᴄᴇ ʙɪᴅs ᴏɴ ᴀʟʟ ᴀᴄᴛɪᴠᴇ ɪᴛᴇᴍs.")
    try:
        await client.send_message(AUCTION_CHANNEL_ID, "🟢 **ᴀᴜᴄᴛɪᴏɴ ɪs ɴᴏᴡ ʟɪᴠᴇ!**\n\nʙɪᴅᴅɪɴɢ ɪs ᴏᴘᴇɴ ғᴏʀ ᴀʟʟ ᴀᴘᴘʀᴏᴠᴇᴅ ɪᴛᴇᴍs.")
    except: pass

@Client.on_message(filters.command("end_auc") & filters.group)
async def end_auction_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return

    # 1. Sabse pehle globally bidding OFF kardo taaki aur koi bid na kar paye
    await Settings.update_one({"_id": "bidding_status"}, {"$set": {"is_open": False}}, upsert=True)

    # 2. Database se saare 'active' items uthao
    active_items = await Poke.find({"status": "active"}).to_list(length=None)

    if not active_items:
        return await message.reply_text("🛑 **ʙɪᴅᴅɪɴɢ ᴄʟᴏsᴇᴅ, ʙᴜᴛ ɴᴏ ᴀᴄᴛɪᴠᴇ ɪᴛᴇᴍs ғᴏᴜɴᴅ ᴛᴏ ᴇɴᴅ.**")

    msg = await message.reply_text(f"🛑 **ᴇɴᴅɪɴɢ ᴀᴜᴄᴛɪᴏɴs ғᴏʀ {len(active_items)} ɪᴛᴇᴍs... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.**")

    sold_count = 0
    unsold_count = 0

    # 3. Har ek item ko check aur process karo
    for item in active_items:
        actual_item_id = item["item_id"]
        highest_bidder = item.get("highest_bidder")
        current_bid = item.get("current_bid")

        if highest_bidder:
            status = "sold"
            winner_mention = item.get("highest_bidder_mention")
            sold_count += 1

            # Update Channel Bid Message (Remove buttons, show winner)
            final_channel_text = (
                f"🎉 **ᴀᴜᴄᴛɪᴏɴ ᴇɴᴅᴇᴅ - sᴏʟᴅ!** 🎉\n\n"
                f"➤ ɪᴛᴇᴍ : **{item['name']}** (`{actual_item_id}`)\n"
                f"➤ ᴡɪɴɴᴇʀ : **{winner_mention}**\n"
                f"➤ ғɪɴᴀʟ ᴘʀɪᴄᴇ : **{current_bid:,} ɴᴏᴠᴀʀᴜᴘᴇᴇ**"
            )
            try: await client.edit_message_text(chat_id=AUCTION_CHANNEL_ID, message_id=item["bid_msg_id"], text=final_channel_text, reply_markup=None)
            except: pass

            # DMs to Buyer & Seller
            try: await client.send_message(highest_bidder, f"🎊 **ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs!**\n\nʏᴏᴜ ᴡᴏɴ ᴛʜᴇ ᴀᴜᴄᴛɪᴏɴ ғᴏʀ **{item['name']}** ᴀᴛ **{current_bid:,} ɴᴏᴠᴀʀᴜᴘᴇᴇ**!\n👤 sᴇʟʟᴇʀ: {item['seller_mention']}\n\nᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ sᴇʟʟᴇʀ ᴛᴏ ᴄᴏᴍᴘʟᴇᴛᴇ ᴛʜᴇ ᴛʀᴀᴅᴇ.")
            except: pass
            try: await client.send_message(item["seller_id"], f"🎉 **ɢᴏᴏᴅ ɴᴇᴡs!**\n\nʏᴏᴜʀ ɪᴛᴇᴍ **{item['name']}** ᴡᴀs **sᴏʟᴅ** ᴛᴏ {winner_mention} ғᴏʀ **{current_bid:,} ɴᴏᴠᴀʀᴜᴘᴇᴇ**!\n\nᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ʙᴜʏᴇʀ ᴛᴏ ᴄᴏᴍᴘʟᴇᴛᴇ ᴛʜᴇ ᴛʀᴀᴅᴇ.")
            except: pass

            # Log into Admin GC
            try:
                log_text = (
                    f"🛑 **ᴀᴜᴄᴛɪᴏɴ ᴇɴᴅᴇᴅ (sᴏʟᴅ)**\n\n"
                    f"➤ ɪᴛᴇᴍ : `{actual_item_id}` ({item['name']})\n"
                    f"➤ sᴇʟʟᴇʀ : {item['seller_mention']} (`{item['seller_id']}`)\n"
                    f"➤ ᴡɪɴɴᴇʀ : {winner_mention} (`{highest_bidder}`)\n"
                    f"➤ ғɪɴᴀʟ ᴘʀɪᴄᴇ : **{current_bid:,} ɴᴏᴠᴀʀᴜᴘᴇᴇ**"
                )
                await client.send_message(ADMIN_GC_ID, log_text)
            except: pass

        else:
            status = "unsold"
            unsold_count += 1

            # Update Channel Message
            final_channel_text = f"😔 **ᴀᴜᴄᴛɪᴏɴ ᴇɴᴅᴇᴅ - ᴜɴsᴏʟᴅ** 😔\n\n➤ ɪᴛᴇᴍ : **{item['name']}** (`{actual_item_id}`)\n➤ ɴᴏ ʙɪᴅs ᴡᴇʀᴇ ᴘʟᴀᴄᴇᴅ."
            try: await client.edit_message_text(chat_id=AUCTION_CHANNEL_ID, message_id=item["bid_msg_id"], text=final_channel_text, reply_markup=None)
            except: pass

            # DM Seller
            try: await client.send_message(item["seller_id"], f"⚠️ **ᴀᴜᴄᴛɪᴏɴ ᴜᴘᴅᴀᴛᴇ**\n\nᴜɴғᴏʀᴛᴜɴᴀᴛᴇʟʏ, ʏᴏᴜʀ ɪᴛᴇᴍ **{item['name']}** ʀᴇᴄᴇɪᴠᴇᴅ ɴᴏ ʙɪᴅs ᴀɴᴅ ᴡᴀs ᴍᴀʀᴋᴇᴅ ᴀs **ᴜɴsᴏʟᴅ**.")
            except: pass

            # Log into Admin GC
            try:
                log_text = (
                    f"🛑 **ᴀᴜᴄᴛɪᴏɴ ᴇɴᴅᴇᴅ (ᴜɴsᴏʟᴅ)**\n\n"
                    f"➤ ɪᴛᴇᴍ : `{actual_item_id}` ({item['name']})\n"
                    f"➤ sᴇʟʟᴇʀ : {item['seller_mention']} (`{item['seller_id']}`)\n"
                    f"➤ sᴛᴀᴛᴜs : ɴᴏ ʙɪᴅs ʀᴇᴄᴇɪᴠᴇᴅ"
                )
                await client.send_message(ADMIN_GC_ID, log_text)
            except: pass

        # Final DB Update For Current Item
        await Poke.update_one({"item_id": actual_item_id}, {"$set": {"status": status}})
        
        # Telegram API Flood se bachne ke liye chota delay
        await asyncio.sleep(0.5)

    # 4. Final Confirmation
    await msg.edit_text(f"✅ **ᴀᴜᴄᴛɪᴏɴ sᴇssɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇʟʏ ᴇɴᴅᴇᴅ!**\n\n🛍 **sᴏʟᴅ ɪᴛᴇᴍs:** {sold_count}\n😔 **ᴜɴsᴏʟᴅ ɪᴛᴇᴍs:** {unsold_count}")
    
    try:
        await client.send_message(AUCTION_CHANNEL_ID, "🛑 **ᴀᴜᴄᴛɪᴏɴ ɪs ɴᴏᴡ ᴄʟᴏsᴇᴅ!**\n\nᴀʟʟ ᴀᴄᴛɪᴠᴇ ʙɪᴅs ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇsᴏʟᴠᴇᴅ. ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ᴘᴀʀᴛɪᴄɪᴘᴀᴛɪɴɢ.")
    except: pass
