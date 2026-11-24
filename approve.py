from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserIsBlocked, PeerIdInvalid

from Nova import DEVS
from Nova.db import SudoDB, Approved

async def is_admin(user_id: int):
    if user_id in DEVS:
        return True
    sudo_user = await SudoDB.find_one({"user_id": user_id})
    return bool(sudo_user)

async def add_approval(user_id: int):
    await Approved.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def rm_approval(user_id: int):
    await Approved.delete_one({"user_id": user_id})


@Client.on_message(filters.command("verify"))
async def approve_cmd(client: Client, message: Message):
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

    # Check if user is already verified
    is_already_verified = await Approved.find_one({"user_id": user_id})
    if is_already_verified:
        return await message.reply_text(f"⚠️ **ᴀʟʀᴇᴀᴅʏ ᴠᴇʀɪғɪᴇᴅ**\n\n{mention} ɪs ᴀʟʀᴇᴀᴅʏ ᴠᴇʀɪғɪᴇᴅ ᴀɴᴅ ᴄᴀɴ ᴀᴅᴅ ɪᴛᴇᴍs.")

    await add_approval(user_id)

    dm_status = "ᴅᴇʟɪᴠᴇʀᴇᴅ ✅"
    try:
        await client.send_message(
            user_id,
            "🎉 ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs!\n\nʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴀᴘᴘʀᴏᴠᴇᴅ ʙʏ ᴀᴅᴍɪɴs. ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴀᴅᴅ ɪᴛᴇᴍs ᴛᴏ ᴘᴏᴋᴇɴᴏᴠᴀ ᴀᴜᴄᴛɪᴏɴs."
        )
    except (UserIsBlocked, PeerIdInvalid, Exception):
        dm_status = "ғᴀɪʟᴇᴅ ❌ (ʙᴏᴛ ʙʟᴏᴄᴋᴇᴅ)"

    await message.reply_text(
        f"✅ ᴜsᴇʀ ᴀᴘᴘʀᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ\n\n"
        f"👤 ᴜsᴇʀ: {mention}\n"
        f"🆔 ɪᴅ: `{user_id}`\n"
        f"📩 ᴅᴍ sᴛᴀᴛᴜs: {dm_status}"
    )


@Client.on_message(filters.command("unverify"))
async def unapprove_cmd(client: Client, message: Message):
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

    # Check if user is actually verified before revoking
    is_verified = await Approved.find_one({"user_id": user_id})
    if not is_verified:
        return await message.reply_text(f"⚠️ **ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ**\n\n{mention} ɪs ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ ʏᴇᴛ, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜɴᴠᴇʀɪғʏ ᴛʜᴇᴍ.")

    await rm_approval(user_id)

    dm_status = "ᴅᴇʟɪᴠᴇʀᴇᴅ ✅"
    try:
        await client.send_message(
            user_id,
            "⚠️ ᴀᴘᴘʀᴏᴠᴀʟ ʀᴇᴠᴏᴋᴇᴅ\n\nʏᴏᴜʀ ᴀᴘᴘʀᴏᴠᴀʟ ᴛᴏ ᴀᴅᴅ ɪᴛᴇᴍs ɪɴ ᴘᴏᴋᴇɴᴏᴠᴀ ᴀᴜᴄᴛɪᴏɴs ʜᴀs ʙᴇᴇɴ ʀᴇᴠᴏᴋᴇᴅ ʙʏ ᴀᴅᴍɪɴs."
        )
    except Exception:
        dm_status = "ғᴀɪʟᴇᴅ ❌"

    await message.reply_text(
        f"🚫 ᴀᴘᴘʀᴏᴠᴀʟ ʀᴇᴠᴏᴋᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ\n\n"
        f"👤 ᴜsᴇʀ: {mention}\n"
        f"🆔 ɪᴅ: `{user_id}`\n"
        f"📩 ᴅᴍ sᴛᴀᴛᴜs: {dm_status}"
    )
