from pyrogram import Client, filters
from pyrogram.types import Message
from Nova import DEVS
from Nova.db import SudoDB

async def add_sudo(user_id: int):
    await SudoDB.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def rm_sudo(user_id: int):
    await SudoDB.delete_one({"user_id": user_id})

async def get_sudoers():
    return [doc["user_id"] async for doc in SudoDB.find({})]

@Client.on_message(filters.command("addsudo") & filters.user(DEVS))
async def add_sudo_cmd(client: Client, message: Message):
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
        return await message.reply_text("🔍 ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ\n\nᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴇ ᴜsᴇʀ ʜᴀs sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.")

    if user_id in DEVS:
        return await message.reply_text("👑 ᴀʟʀᴇᴀᴅʏ ᴏᴡɴᴇʀ\n\nᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ɪɴ ᴛʜᴇ ᴅᴇᴠs ʟɪsᴛ.")

    # Check if already Sudo
    is_sudo = await SudoDB.find_one({"user_id": user_id})
    if is_sudo:
        return await message.reply_text(f"⚠️ **ᴀʟʀᴇᴀᴅʏ sᴜᴅᴏ**\n\n{mention} ɪs ᴀʟʀᴇᴀᴅʏ ᴀ sᴜᴅᴏ ᴜsᴇʀ.")

    await add_sudo(user_id)
    await message.reply_text(
        f"✨ sᴜᴅᴏ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ\n\n"
        f"👤 ᴜsᴇʀ: {mention}\n"
        f"🆔 ɪᴅ: `{user_id}`\n"
        f"🛡️ ᴘʀᴏᴠɪᴅᴇᴅ ᴀᴄᴄᴇss: ғᴜʟʟ ᴀᴜᴄᴛɪᴏɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ"
    )

@Client.on_message(filters.command("rmsudo") & filters.user(DEVS))
async def rm_sudo_cmd(client: Client, message: Message):
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
        return await message.reply_text("🔍 ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ\n\nᴜɴᴀʙʟᴇ ᴛᴏ ғᴇᴛᴄʜ ᴜsᴇʀ ᴅᴇᴛᴀɪʟs.")

    if user_id in DEVS:
        return await message.reply_text("⚠️ ᴀᴄᴛɪᴏɴ ᴅᴇɴɪᴇᴅ\n\nᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴀɴ ᴏᴡɴᴇʀ ғʀᴏᴍ ᴛʜᴇ sᴜᴅᴏ ʟɪsᴛ.")

    # Check if actually Sudo before trying to remove
    is_sudo = await SudoDB.find_one({"user_id": user_id})
    if not is_sudo:
        return await message.reply_text(f"⚠️ **ɴᴏᴛ sᴜᴅᴏ**\n\n{mention} ɪs ɴᴏᴛ ɪɴ ᴛʜᴇ sᴜᴅᴏ ʟɪsᴛ.")

    await rm_sudo(user_id)
    await message.reply_text(
        f"🗑️ sᴜᴅᴏ ʀᴇᴍᴏᴠᴇᴅ\n\n"
        f"👤 ᴜsᴇʀ: {mention}\n"
        f"🆔 ɪᴅ: `{user_id}`\n"
        f"🚫 ᴀᴄᴄᴇss: ʀᴇᴠᴏᴋᴇᴅ"
    )

@Client.on_message(filters.command("sudolist") & filters.user(DEVS))
async def sudo_list_cmd(client: Client, message: Message):
    msg = await message.reply_text("🔄 ғᴇᴛᴄʜɪɴɢ sᴜᴅᴏ ᴜsᴇʀs...")

    sudoers = await get_sudoers()

    if not sudoers:
        return await msg.edit_text("ℹ️ ɴᴏ sᴜᴅᴏ ᴜsᴇʀs ғᴏᴜɴᴅ\n\nᴛʜᴇʀᴇ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ɴᴏ ᴜsᴇʀs ɪɴ ᴛʜᴇ sᴜᴅᴏ ʟɪsᴛ.")

    text = "⚡ ᴘᴏᴋᴇɴᴏᴠᴀ sᴜᴅᴏ ʟɪsᴛ ⚡\n\n"
    for user_id in sudoers:
        try:
            user = await client.get_users(user_id)
            text += f"⚜️ {user.mention} ⦗`{user_id}`⦘\n"
        except Exception:
            text += f"👻 ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ ⦗`{user_id}`⦘\n"

    await msg.edit_text(text)
