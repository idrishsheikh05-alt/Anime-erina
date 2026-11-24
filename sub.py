import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from Nova import DEVS
from Nova.db import SudoDB, Settings, Users

async def is_admin(user_id: int):
    if user_id in DEVS:
        return True
    sudo_user = await SudoDB.find_one({"user_id": user_id})
    return bool(sudo_user)

async def broadcast_notification(client: Client, text: str):
    async for user in Users.find({}):
        user_id = user.get("user_id")
        if not user_id:
            continue
        try:
            await client.send_message(user_id, text)
            await asyncio.sleep(0.05)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await client.send_message(user_id, text)
        except Exception:
            pass

@Client.on_message(filters.command("start_sub"))
async def start_sub_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return

    await Settings.update_one(
        {"_id": "submission_status"}, 
        {"$set": {"is_open": True}}, 
        upsert=True
    )
    
    await message.reply_text(
        "✅ sᴜʙᴍɪssɪᴏɴs ᴏᴘᴇɴᴇᴅ\n\n"
        "✨ ᴛʜᴇ sᴜʙᴍɪssɪᴏɴs ᴀʀᴇ ɴᴏᴡ ᴏᴘᴇɴ. ɴᴏᴛɪғʏɪɴɢ ᴀʟʟ ᴜsᴇʀs ɪɴ ʙᴀᴄᴋɢʀᴏᴜɴᴅ..."
    )

    notify_text = (
        "🔔 ᴀᴜᴄᴛɪᴏɴ ᴜᴘᴅᴀᴛᴇ\n\n"
        "✨ sᴜʙᴍɪssɪᴏɴs ᴀʀᴇ ɴᴏᴡ ᴏᴘᴇɴ!\n"
        "ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴀᴅᴅ ʏᴏᴜʀ ᴘᴏᴋᴇᴍᴏɴs ғᴏʀ ᴛʜᴇ ᴜᴘᴄᴏᴍɪɴɢ ᴀᴜᴄᴛɪᴏɴ ᴜsɪɴɢ ᴛʜᴇ /add ᴄᴏᴍᴍᴀɴᴅ."
    )
    asyncio.create_task(broadcast_notification(client, notify_text))


@Client.on_message(filters.command("end_sub"))
async def end_sub_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return

    await Settings.update_one(
        {"_id": "submission_status"}, 
        {"$set": {"is_open": False}}, 
        upsert=True
    )
    
    await message.reply_text(
        "🚫 sᴜʙᴍɪssɪᴏɴs ᴄʟᴏsᴇᴅ\n\n"
        "⚠️ sᴜʙᴍɪssɪᴏɴs ʜᴀᴠᴇ ʙᴇᴇɴ ᴄʟᴏsᴇᴅ. ɴᴏᴛɪғʏɪɴɢ ᴀʟʟ ᴜsᴇʀs ɪɴ ʙᴀᴄᴋɢʀᴏᴜɴᴅ..."
    )

    notify_text = (
        "🔔 ᴀᴜᴄᴛɪᴏɴ ᴜᴘᴅᴀᴛᴇ\n\n"
        "⚠️ sᴜʙᴍɪssɪᴏɴs ᴀʀᴇ ɴᴏᴡ ᴄʟᴏsᴇᴅ!\n"
        "ʏᴏᴜ ᴄᴀɴ ɴᴏ ʟᴏɴɢᴇʀ ᴀᴅᴅ ɴᴇᴡ ɪᴛᴇᴍs. sᴛᴀʏ ᴛᴜɴᴇᴅ ғᴏʀ ᴛʜᴇ ᴀᴜᴄᴛɪᴏɴ ᴛᴏ ʙᴇɢɪɴ."
    )
    asyncio.create_task(broadcast_notification(client, notify_text))
