from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserIsBlocked, PeerIdInvalid

from Nova import DEVS
from Nova.db import SudoDB, Banned

async def is_admin(user_id: int):
    if user_id in DEVS:
        return True
    sudo_user = await SudoDB.find_one({"user_id": user_id})
    return bool(sudo_user)

async def add_ban(user_id: int):
    await Banned.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def rm_ban(user_id: int):
    await Banned.delete_one({"user_id": user_id})

async def get_banned_users():
    return [doc["user_id"] async for doc in Banned.find({})]


@Client.on_message(filters.command("nban"))
async def ban_user_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return

    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("⚠️ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ\n\n💬 ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇɪʀ ɪᴅ.")

    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            mention = message.reply_to_message.from_user.mention
        else:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            mention = user.mention
    except ValueError:
        return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ɪᴅ\n\n🔢 ᴜsᴇʀ ɪᴅ ᴍᴜsᴛ ʙᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.")
    except Exception:
        return await message.reply_text("🔍 ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")

    if await is_admin(user_id):
        return await message.reply_text("⚠️ ᴀᴄᴛɪᴏɴ ᴅᴇɴɪᴇᴅ\n\n🚫 ʏᴏᴜ ᴄᴀɴɴᴏᴛ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ ᴏʀ ᴏᴡɴᴇʀ.")

    # Check if user is already banned
    is_already_banned = await Banned.find_one({"user_id": user_id})
    if is_already_banned:
        return await message.reply_text(f"⚠️ **ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ**\n\n{mention} ɪs ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴛʜᴇ ʙᴏᴛ.")

    await add_ban(user_id)

    dm_status = "ᴅᴇʟɪᴠᴇʀᴇᴅ ✅"
    try:
        await client.send_message(
            user_id,
            "🚫 ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ\n\nʏᴏᴜ ᴀʀᴇ ɴᴏ ʟᴏɴɢᴇʀ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴜsᴇ ᴘᴏᴋᴇɴᴏᴠᴀ ᴀᴜᴄᴛɪᴏɴ ʙᴏᴛ. ɪғ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜɪs ɪs ᴀ ᴍɪsᴛᴀᴋᴇ, ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ᴏᴡɴᴇʀs."
        )
    except (UserIsBlocked, PeerIdInvalid, Exception):
        dm_status = "ғᴀɪʟᴇᴅ ❌ (ʙᴏᴛ ʙʟᴏᴄᴋᴇᴅ)"

    await message.reply_text(
        f"🚫 ᴜsᴇʀ ʙᴀɴɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ\n\n"
        f"👤 ᴜsᴇʀ: {mention}\n"
        f"🆔 ɪᴅ: `{user_id}`\n"
        f"📩 ᴅᴍ sᴛᴀᴛᴜs: {dm_status}"
    )


@Client.on_message(filters.command("nunban"))
async def unban_user_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return

    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("⚠️ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ\n\n💬 ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇɪʀ ɪᴅ.")

    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            mention = message.reply_to_message.from_user.mention
        else:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            mention = user.mention
    except ValueError:
        return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ɪᴅ\n\n🔢 ᴜsᴇʀ ɪᴅ ᴍᴜsᴛ ʙᴇ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.")
    except Exception:
        return await message.reply_text("🔍 ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")

    # Check if user is actually banned before trying to unban
    is_banned = await Banned.find_one({"user_id": user_id})
    if not is_banned:
        return await message.reply_text(f"⚠️ **ɴᴏᴛ ʙᴀɴɴᴇᴅ**\n\n{mention} ɪs ɴᴏᴛ ɪɴ ᴛʜᴇ ʙᴀɴ ʟɪsᴛ.")

    await rm_ban(user_id)

    dm_status = "ᴅᴇʟɪᴠᴇʀᴇᴅ ✅"
    try:
        await client.send_message(
            user_id,
            "✨ ɢᴏᴏᴅ ɴᴇᴡs!\n\nʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴘᴏᴋᴇɴᴏᴠᴀ ᴀᴜᴄᴛɪᴏɴs. ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴘᴀʀᴛɪᴄɪᴘᴀᴛᴇ ᴀɢᴀɪɴ."
        )
    except Exception:
        dm_status = "ғᴀɪʟᴇᴅ ❌"

    await message.reply_text(
        f"✅ ᴜsᴇʀ ᴜɴʙᴀɴɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ\n\n"
        f"👤 ᴜsᴇʀ: {mention}\n"
        f"🆔 ɪᴅ: `{user_id}`\n"
        f"📩 ᴅᴍ sᴛᴀᴛᴜs: {dm_status}"
    )


@Client.on_message(filters.command("banlist"))
async def ban_list_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return

    msg = await message.reply_text("🔄 ғᴇᴛᴄʜɪɴɢ ʙᴀɴ ʟɪsᴛ...")

    banned_users = await get_banned_users()

    if not banned_users:
        return await msg.edit_text("ℹ️ ɴᴏ ʙᴀɴɴᴇᴅ ᴜsᴇʀs ғᴏᴜɴᴅ.")

    text = "⚡ ᴘᴏᴋᴇɴᴏᴠᴀ ʙᴀɴ ʟɪsᴛ ⚡\n\n"
    for user_id in banned_users:
        try:
            user = await client.get_users(user_id)
            text += f"🚫 {user.mention} ⦗`{user_id}`⦘\n"
        except Exception:
            text += f"👻 ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ ⦗`{user_id}`⦘\n"

    await msg.edit_text(text)
