from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import PeerIdInvalid

from Nova import DEVS
from Nova.db import Poke, Approved, Banned, SudoDB

def make_bq(text):
    return "\n".join([f"> {line}" for line in str(text).split("\n")])

@Client.on_message(filters.command(["profile", "me"], prefixes=["/", "."]))
async def profile_cmd(client: Client, message: Message):
    target_user = message.from_user
    if message.reply_to_message and message.reply_to_message.from_user:
        target_user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target_user = await client.get_users(int(message.command[1]))
        except (ValueError, PeerIdInvalid):
            return await message.reply_text("⟡ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ ᴏʀ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")

    user_id = target_user.id
    mention = target_user.mention

    msg = await message.reply_text("🔄 **ғᴇᴛᴄʜɪɴɢ ᴘʀᴏғɪʟᴇ ᴅᴀᴛᴀ...**")

    try:
        # Role check (Cleaned symbols)
        role = "ᴜsᴇʀ"
        is_sudo = await SudoDB.find_one({"user_id": user_id})
        
        if user_id in DEVS:
            role = "ᴏᴡɴᴇʀ"
        elif is_sudo:
            role = "ᴀᴅᴍɪɴ"
        else:
            is_appr = await Approved.find_one({"user_id": user_id})
            if is_appr:
                role = "ᴀᴘᴘʀᴏᴠᴇᴅ"

        # Items count
        bought_count = await Poke.count_documents({"buyer_id": user_id, "status": "sold"})
        sold_count = await Poke.count_documents({"seller_id": user_id, "status": "sold"})

        # Total Spent Calculate (Safe Aggregation)
        spent_cursor = Poke.aggregate([
            {"$match": {"buyer_id": user_id, "status": "sold"}},
            {"$group": {"_id": None, "total": {"$sum": "$current_bid"}}} # Changed to current_bid as per your DB
        ])
        spent_data = await spent_cursor.to_list(length=1)
        total_spent = int(spent_data[0].get("total") or 0) if spent_data else 0

        # Total Earned Calculate (Safe Aggregation)
        earned_cursor = Poke.aggregate([
            {"$match": {"seller_id": user_id, "status": "sold"}},
            {"$group": {"_id": None, "total": {"$sum": "$current_bid"}}}
        ])
        earned_data = await earned_cursor.to_list(length=1)
        total_earned = int(earned_data[0].get("total") or 0) if earned_data else 0

        # Premium UI Format (No Emojis)
        details = (
            f"⟡ ɴᴀᴍᴇ : {mention}\n"
            f"⟡ ɪᴅ : `{user_id}`\n"
            f"⟡ ʀᴏʟᴇ : {role}"
        )

        stats = (
            f"⟡ ɪᴛᴇᴍs ʙᴏᴜɢʜᴛ : {bought_count}\n"
            f"⟡ ᴛᴏᴛᴀʟ sᴘᴇɴᴛ : {total_spent:,} ɴᴏᴠᴀʀᴜᴘᴇᴇ\n\n"
            f"⟡ ɪᴛᴇᴍs sᴏʟᴅ : {sold_count}\n"
            f"⟡ ᴛᴏᴛᴀʟ ᴇᴀʀɴᴇᴅ : {total_earned:,} ɴᴏᴠᴀʀᴜᴘᴇᴇ"
        )

        text = (
            "✦ **ᴜsᴇʀ ᴘʀᴏғɪʟᴇ** ✦\n\n"
            "**[ ᴜsᴇʀ ɪɴғᴏ ]**\n"
            f"{make_bq(details)}\n\n"
            "**[ ᴛʀᴀᴅᴇ sᴛᴀᴛs ]**\n"
            f"{make_bq(stats)}"
        )

        # Close Button
        close_btn = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ ❖", callback_data=f"close_prof_{message.from_user.id}")]])

        # Safe Photo Fetching
        photo_id = None
        try:
            full_user = await client.get_chat(user_id)
            if full_user.photo:
                photo_id = full_user.photo.big_file_id
        except Exception:
            pass

        if photo_id:
            await msg.delete()
            await message.reply_photo(photo=photo_id, caption=text, reply_markup=close_btn)
        else:
            await msg.edit_text(text, reply_markup=close_btn)

    except Exception as e:
        await msg.edit_text(f"⟡ **ᴇʀʀᴏʀ:** ᴄᴏᴜʟᴅ ɴᴏᴛ ғᴇᴛᴄʜ ᴘʀᴏғɪʟᴇ ᴅᴀᴛᴀ.\n`{e}`")


@Client.on_callback_query(filters.regex(r"^close_prof_(\d+)$"))
async def close_profile_cb(client: Client, cb: CallbackQuery):
    owner_id = int(cb.matches[0].group(1))
    
    if cb.from_user.id != owner_id:
        return await cb.answer("⚠️ ᴀʙᴇ ɴᴀʟʟᴇ, ᴀᴘɴᴀ ᴄᴏᴍᴍᴀɴᴅ ᴜsᴇ ᴋᴀʀ! 😂", show_alert=True)
        
    try:
        await cb.message.delete()
    except Exception:
        pass
    await cb.answer()
