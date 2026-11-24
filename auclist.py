from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from Nova import DEVS
from Nova.db import SudoDB, Poke

async def is_admin(user_id: int):
    if user_id in DEVS:
        return True
    sudo_user = await SudoDB.find_one({"user_id": user_id})
    return bool(sudo_user)

# ----------------- /auclist (ADMINS ONLY) ----------------- #
@Client.on_message(filters.command(["auclist"], prefixes=["/", "."]))
async def auclist_cmd(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return

    msg = await message.reply_text("🔄 **ғᴇᴛᴄʜɪɴɢ sᴛᴀᴛs...**")

    non_leg_count = await Poke.count_documents({"category": "NON - LEGENDARY", "status": "active"})
    leg_count = await Poke.count_documents({"category": "LEGENDARY", "status": "active"})
    shiny_count = await Poke.count_documents({"category": "SHINY", "status": "active"})
    tms_count = await Poke.count_documents({"category": "TMS", "status": "active"})
    tutor_count = await Poke.count_documents({"category": "TUTOR", "status": "active"})

    total_count = non_leg_count + leg_count + shiny_count + tms_count + tutor_count

    text = (
        "📊 **ᴀᴜᴄᴛɪᴏɴ sᴛᴀᴛs** 📊\n\n"
        f"➤ ɴᴏɴ-ʟᴇɢᴇɴᴅᴀʀʏ : `{non_leg_count}`\n"
        f"➤ ʟᴇɢᴇɴᴅᴀʀʏ : `{leg_count}`\n"
        f"➤ sʜɪɴʏ : `{shiny_count}`\n"
        f"➤ ᴛᴍs : `{tms_count}`\n"
        f"➤ ᴛᴜᴛᴏʀs : `{tutor_count}`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"📈 **ᴛᴏᴛᴀʟ ᴀᴄᴛɪᴠᴇ : `{total_count}`**\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
