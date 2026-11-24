from pyrogram import Client, filters
from pyrogram.types import Message

from Nova import DEVS
from Nova.db import SudoDB, Poke

async def is_admin(user_id: int):
    if user_id in DEVS:
        return True
    sudo_user = await SudoDB.find_one({"user_id": user_id})
    return bool(sudo_user)

@Client.on_message(filters.command(["rmitem", "removeitem"]))
async def remove_item_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return
        
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **ᴜsᴀɢᴇ:** `/rmitem <ɪᴛᴇᴍ_ɪᴅ>`\nᴇxᴀᴍᴘʟᴇ: `/rmitem Nova-0001`")
        
    item_id = message.command[1]
    
    # Database se delete karna
    result = await Poke.delete_one({"item_id": item_id})
    
    if result.deleted_count > 0:
        await message.reply_text(f"✅ **ɪᴛᴇᴍ `{item_id}` sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.**")
    else:
        await message.reply_text(f"❌ **ɪᴛᴇᴍ `{item_id}` ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ.**")
