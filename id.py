from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

@Client.on_message(filters.command("id"))
async def id_cmd(client: Client, message: Message):
    text = "🪪 ɪᴅ ɪɴғᴏʀᴍᴀᴛɪᴏɴ\n\n"
    
    # 1. Chat / Group ID check
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        text += f"🏢 ɢʀᴏᴜᴘ ɪᴅ : `{message.chat.id}`\n"
    else:
        text += f"💬 ᴄʜᴀᴛ ɪᴅ : `{message.chat.id}`\n"
        
    # 2. Sender (Your) ID
    text += f"👤 ʏᴏᴜʀ ɪᴅ : `{message.from_user.id}`\n"
    
    # 3. Replied User ID (Agar kisi ko reply kiya hai)
    if message.reply_to_message and message.reply_to_message.from_user:
        text += f"🎯 ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ : `{message.reply_to_message.from_user.id}`\n"
        
    await message.reply_text(text)
