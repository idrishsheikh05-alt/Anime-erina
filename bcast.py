import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from Nova import DEVS
from Nova.db import SudoDB, Users, Groups

async def is_admin(user_id: int):
    if user_id in DEVS:
        return True
    sudo_user = await SudoDB.find_one({"user_id": user_id})
    return bool(sudo_user)

# ----------------- /bcast (BROADCAST) ----------------- #
@Client.on_message(filters.command(["bcast", "broadcast"]))
async def bcast_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return
        
    if not message.reply_to_message:
        return await message.reply_text("⚠️ **ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ.**")
        
    msg = await message.reply_text("🔄 **sᴛᴀʀᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.**")
    
    users = await Users.find({}).to_list(length=None)
    groups = await Groups.find({}).to_list(length=None)
    
    usr_sent = 0
    usr_failed = 0
    grp_sent = 0
    grp_failed = 0
    
    # Broadcast to Users
    for user in users:
        try:
            # .copy() se buttons, media aur forwards sab retain hote hain
            await message.reply_to_message.copy(user["user_id"])
            usr_sent += 1
            await asyncio.sleep(0.1) # Flood limit se bachne ke liye thoda wait
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(user["user_id"])
            usr_sent += 1
        except Exception:
            usr_failed += 1
            
    # Broadcast to Groups
    for group in groups:
        try:
            await message.reply_to_message.copy(group["chat_id"])
            grp_sent += 1
            await asyncio.sleep(0.1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(group["chat_id"])
            grp_sent += 1
        except Exception:
            grp_failed += 1
            
    text = (
        "✅ **ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!**\n\n"
        "👤 **ᴜsᴇʀs ʀᴇsᴜʟᴛ:**\n"
        f"➤ sᴇɴᴛ : {usr_sent}\n"
        f"➤ ғᴀɪʟᴇᴅ : {usr_failed}\n\n"
        "👥 **ɢʀᴏᴜᴘs ʀᴇsᴜʟᴛ:**\n"
        f"➤ sᴇɴᴛ : {grp_sent}\n"
        f"➤ ғᴀɪʟᴇᴅ : {grp_failed}"
    )
    await msg.edit_text(text)


# ----------------- /msg (PERSONAL MESSAGE) ----------------- #
@Client.on_message(filters.command("msg"))
async def send_msg_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return
        
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ **ᴜsᴀɢᴇ:**\n"
            "➤ `/msg <ᴜsᴇʀ_ɪᴅ> <ᴍᴇssᴀɢᴇ>`\n"
            "➤ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ `/msg <ᴜsᴇʀ_ɪᴅ>`"
        )
        
    target_id = message.command[1]
    
    # Check ID valid hai ya nahi
    try:
        target_id = int(target_id)
    except ValueError:
        return await message.reply_text("❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ. ɪᴛ ᴍᴜsᴛ ʙᴇ ᴀ ɴᴜᴍʙᴇʀ.**")
        
    try:
        if message.reply_to_message:
            # Agar kisi media/button message pe reply karke id di
            await message.reply_to_message.copy(target_id)
        else:
            # Agar direct `/msg ID hello bhai` likha
            if len(message.command) < 3:
                return await message.reply_text("⚠️ **ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴇɴᴅ.**")
            text_to_send = message.text.split(None, 2)[2]
            await client.send_message(target_id, f"🔔 **ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴀᴅᴍɪɴs:**\n\n{text_to_send}")
            
        await message.reply_text(f"✅ **ᴍᴇssᴀɢᴇ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴛᴏ `{target_id}`.**")
        
    except Exception as e:
        await message.reply_text(f"❌ **ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇ.**\nᴛʜᴇ ᴜsᴇʀ ᴍɪɢʜᴛ ʜᴀᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n`{e}`")
