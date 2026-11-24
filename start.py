
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatType
from pyrogram.errors import UserNotParticipant

from Nova.db import Users, Groups, Banned

# ⚠️ Yahan Apne Groups & Channels Ki ID Daal Dena
AUCTION_CHANNEL_ID = -1004230427074
AUCTION_GC_ID = -1004447793839
TRADE_GC_ID = -1003603924513

IMAGE_URL = "https://files.catbox.moe/nzmjn5.jpg" 

async def is_banned(user_id: int):
    user = await Banned.find_one({"user_id": user_id})
    return bool(user)

async def add_user(user_id: int, username: str, name: str):
    await Users.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "username": username, "name": name}},
        upsert=True
    )

async def add_group(chat_id: int, title: str):
    await Groups.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id, "title": title}},
        upsert=True
    )

async def check_forcesub(client: Client, user_id: int):
    """Background check for group/channel membership"""
    try:
        await client.get_chat_member(AUCTION_CHANNEL_ID, user_id)
        await client.get_chat_member(AUCTION_GC_ID, user_id)
        await client.get_chat_member(TRADE_GC_ID, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return False

@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    user_id = message.from_user.id

    if await is_banned(user_id):
        return await message.reply_text("🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ\n\nʏᴏᴜ ᴀʀᴇ ɴᴏ ʟᴏɴɢᴇʀ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.")

    username = message.from_user.username or "None"
    name = message.from_user.first_name or "Unknown"
    await add_user(user_id, username, name)

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await add_group(message.chat.id, message.chat.title)
        bot_info = await client.get_me()
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 sᴛᴀʀᴛ ɪɴ ᴅᴍ", url=f"https://t.me/{bot_info.username}?start=start")]])
        return await message.reply_text("✨ ʜᴇʏ ᴛʜᴇʀᴇ! ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴍᴇ ɪɴ ᴅᴍ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.", reply_markup=btn)

    is_joined = await check_forcesub(client, user_id)

    # Deep Link Handler
    if len(message.command) > 1:
        payload = message.command[1]
        if payload == "add":
            if is_joined:
                return await message.reply_text("🔮 ᴛʏᴘᴇ `/add` ᴛᴏ sᴛᴀʀᴛ sᴜʙᴍɪᴛᴛɪɴɢ ʏᴏᴜʀ ɪᴛᴇᴍs!")
            # Agar joined nahi hai to neechay force sub aayega

    if is_joined:
        # 🟢 VIP WELCOME (ALREADY JOINED) - NO BUTTON
        text = (
            f"✨ ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏ ᴘᴏᴋᴇɴᴏᴠᴀ ᴀᴜᴄᴛɪᴏɴs, {message.from_user.mention}! ✨\n\n"
            "🌟 ɪ ᴀᴍ ᴀ ʜɪɢʜ-sᴘᴇᴇᴅ, ᴀᴅᴠᴀɴᴄᴇᴅ ᴀᴜᴄᴛɪᴏɴ ʙᴏᴛ ᴅᴇsɪɢɴᴇᴅ ғᴏʀ sᴇᴀᴍʟᴇss ʙɪᴅᴅɪɴɢ ᴀɴᴅ ᴛʀᴀᴅɪɴɢ.\n\n"
            "> ✅ ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴠᴇʀɪғɪᴇᴅ ᴀɴᴅ ʀᴇᴀᴅʏ ᴛᴏ ɢᴏ!\n"
            "💬 ᴛʏᴘᴇ `/help` ᴛᴏ sᴇᴇ ᴀʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs."
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 ᴀᴜᴄᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ", url="https://t.me/PokemonNova_Auction")],
            [InlineKeyboardButton("💬 ᴀᴜᴄᴛɪᴏɴ ɢʀᴏᴜᴘ", url="https://t.me/PokeNovaAuction"),
             InlineKeyboardButton("🔄 ᴛʀᴀᴅᴇ ɢʀᴏᴜᴘ", url="https://t.me/+P13LuYK4b6s4NDU1")]
        ])
        await message.reply_photo(photo=IMAGE_URL, caption=text, reply_markup=buttons)

    else:
        # 🔴 FORCE SUB MESSAGE (NOT JOINED)
        text = (
            f"✋ **ʜᴏʟᴅ ᴏɴ, {message.from_user.mention}!**\n\n"
            "⚠️ ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴏғғɪᴄɪᴀʟ ɴᴇᴛᴡᴏʀᴋs ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.\n"
            "> ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ɢʀᴏᴜᴘs ʙᴇʟᴏᴡ, ᴛʜᴇɴ ᴄʟɪᴄᴋ 'ɪ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ' ᴛᴏ ᴠᴇʀɪғʏ."
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 ᴀᴜᴄᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ", url="https://t.me/PokemonNova_Auction")],
            [InlineKeyboardButton("💬 ᴀᴜᴄᴛɪᴏɴ ɢʀᴏᴜᴘ", url="https://t.me/PokeNovaAuction"),
             InlineKeyboardButton("🔄 ᴛʀᴀᴅᴇ ɢʀᴏᴜᴘ", url="https://t.me/+P13LuYK4b6s4NDU1")],
            [InlineKeyboardButton("✅ ɪ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ", callback_data="confirm_joined")]
        ])
        await message.reply_photo(photo=IMAGE_URL, caption=text, reply_markup=buttons)

@Client.on_callback_query(filters.regex("^confirm_joined$"))
async def confirm_joined_cb(client: Client, cb: CallbackQuery):
    user_id = cb.from_user.id
    
    if await check_forcesub(client, user_id):
        text = (
            f"🎉 **ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ sᴜᴄᴄᴇssғᴜʟ!**\n\n"
            f"✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴘᴏᴋᴇɴᴏᴠᴀ ᴀᴜᴄᴛɪᴏɴs, {cb.from_user.mention}! ✨\n\n"
            "🌟 ɪ ᴀᴍ ᴀ ʜɪɢʜ-sᴘᴇᴇᴅ, ᴀᴅᴠᴀɴᴄᴇᴅ ᴀᴜᴄᴛɪᴏɴ ʙᴏᴛ ᴅᴇsɪɢɴᴇᴅ ғᴏʀ sᴇᴀᴍʟᴇss ʙɪᴅᴅɪɴɢ ᴀɴᴅ ᴛʀᴀᴅɪɴɢ.\n\n"
            "> ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ɪs ɴᴏᴡ ᴀᴄᴛɪᴠᴇ. ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴘᴀʀᴛɪᴄɪᴘᴀᴛᴇ ɪɴ ᴀᴜᴄᴛɪᴏɴs ᴀɴᴅ sᴜʙᴍɪᴛ ʏᴏᴜʀ ɪᴛᴇᴍs.\n"
            "💬 ᴛʏᴘᴇ `/help` ᴛᴏ sᴇᴇ ᴀʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs."
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 ᴀᴜᴄᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ", url="https://t.me/PokemonNova_Auction")],
            [InlineKeyboardButton("💬 ᴀᴜᴄᴛɪᴏɴ ɢʀᴏᴜᴘ", url="https://t.me/PokeNovaAuction"),
             InlineKeyboardButton("🔄 ᴛʀᴀᴅᴇ ɢʀᴏᴜᴘ", url="https://t.me/+P13LuYK4b6s4NDU1")]
        ])
        await cb.message.edit_caption(caption=text, reply_markup=buttons)
        await cb.answer("✅ Verification Successful!", show_alert=True)
    else:
        await cb.answer("❌ You haven't joined the Channel & Groups yet!", show_alert=True)
