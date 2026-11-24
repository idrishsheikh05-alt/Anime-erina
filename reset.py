from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from Nova import DEVS
from Nova.db import Users, Groups, Banned, Poke, SudoDB, Approved, Settings

@Client.on_message(filters.command(["resetdb", "reset"]) & filters.user(DEVS))
async def reset_db_cmd(client: Client, message: Message):
    text = (
        "⚠️ **ᴅᴀᴛᴀʙᴀsᴇ ʀᴇsᴇᴛ ᴡᴀʀɴɪɴɢ** ⚠️\n\n"
        "ʏᴏᴜ ᴀʀᴇ ᴀʙᴏᴜᴛ ᴛᴏ ᴇʀᴀsᴇ ᴛʜᴇ **ᴇɴᴛɪʀᴇ ᴅᴀᴛᴀʙᴀsᴇ**. ᴛʜɪs ᴀᴄᴛɪᴏɴ ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ:\n\n"
        "➤ ᴀʟʟ ᴀᴜᴄᴛɪᴏɴ ɪᴛᴇᴍs\n"
        "➤ ᴀʟʟ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜsᴇʀs & sᴜᴅᴏᴇʀs\n"
        "➤ ᴀʟʟ ʙᴀɴɴᴇᴅ ᴜsᴇʀ ʀᴇᴄᴏʀᴅs\n"
        "➤ ᴀʟʟ ᴜsᴇʀ & ɢʀᴏᴜᴘ ᴅᴀᴛᴀ\n"
        "➤ ᴀᴜᴄᴛɪᴏɴ sᴇᴛᴛɪɴɢs & ɪᴛᴇᴍ ᴄᴏᴜɴᴛᴇʀs\n\n"
        "🚨 **ᴛʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ.** ᴀʀᴇ ʏᴏᴜ ᴀʙsᴏʟᴜᴛᴇʟʏ sᴜʀᴇ?"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ᴄᴏɴғɪʀᴍ ʀᴇsᴇᴛ", callback_data="confirm_reset")],
        [InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="cancel_reset")]
    ])
    
    await message.reply_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^cancel_reset$") & filters.user(DEVS))
async def cancel_reset_cb(client: Client, cb: CallbackQuery):
    await cb.message.edit_text("❌ **ᴅᴀᴛᴀʙᴀsᴇ ʀᴇsᴇᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ.**\n\nʏᴏᴜʀ ᴅᴀᴛᴀ ɪs sᴀғᴇ.")


@Client.on_callback_query(filters.regex("^confirm_reset$") & filters.user(DEVS))
async def confirm_reset_cb(client: Client, cb: CallbackQuery):
    await cb.message.edit_text("🔄 **ᴇʀᴀsɪɴɢ ᴅᴀᴛᴀʙᴀsᴇ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.**")
    
    try:
        # Har ek collection ko clear kar rahe hain
        await Users.delete_many({})
        await Groups.delete_many({})
        await Banned.delete_many({})
        await Poke.delete_many({})
        await SudoDB.delete_many({})
        await Approved.delete_many({})
        await Settings.delete_many({})
        
        success_text = (
            "✅ **ᴅᴀᴛᴀʙᴀsᴇ ʀᴇsᴇᴛ sᴜᴄᴄᴇssғᴜʟ** ✅\n\n"
            "ᴀʟʟ ᴄᴏʟʟᴇᴄᴛɪᴏɴs ʜᴀᴠᴇ ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ. ᴛʜᴇ ʙᴏᴛ ɪs ɴᴏᴡ ᴄᴏᴍᴘʟᴇᴛᴇʟʏ ғʀᴇsʜ ᴀɴᴅ ʀᴇᴀᴅʏ ᴛᴏ sᴛᴀʀᴛ ᴏᴠᴇʀ."
        )
        await cb.message.edit_text(success_text)
        
    except Exception as e:
        await cb.message.edit_text(f"❌ **ᴇʀʀᴏʀ ᴅᴜʀɪɴɢ ʀᴇsᴇᴛ:**\n`{e}`")
