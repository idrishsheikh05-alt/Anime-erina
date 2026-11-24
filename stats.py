import time
from pyrogram import Client, filters
from pyrogram.types import Message

from Nova import DEVS
from Nova.db import Users, Groups, Poke, Banned, Approved

def make_bq(text):
    return "\n".join([f"> {line}" for line in str(text).split("\n")])

# ----------------- /botstats (DEVS ONLY) ----------------- #
@Client.on_message(filters.command(["botstats", "astats"]))
async def botstats_cmd(client: Client, message: Message):
    if message.from_user.id not in DEVS:
        return

    msg = await message.reply_text("🔄 **ғᴇᴛᴄʜɪɴɢ ʙᴏᴛ sᴛᴀᴛs...**")

    # DB Counts
    total_users = await Users.count_documents({})
    total_groups = await Groups.count_documents({})
    banned_users = await Banned.count_documents({})
    appr_users = await Approved.count_documents({})

    total_items = await Poke.count_documents({})
    active_items = await Poke.count_documents({"status": "active"})
    sold_items = await Poke.count_documents({"status": "sold"})
    unsold_items = await Poke.count_documents({"status": "unsold"})
    pending_items = await Poke.count_documents({"status": "pending"})

    # Premium UI Formatting
    network_stats = (
        f"◈ ᴛᴏᴛᴀʟ ᴜsᴇʀs : {total_users}\n"
        f"◈ ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs : {total_groups}\n"
        f"◈ ᴀᴘᴘʀᴏᴠᴇᴅ : {appr_users}\n"
        f"◈ ʙᴀɴɴᴇᴅ : {banned_users}"
    )

    auction_stats = (
        f"⟡ ᴛᴏᴛᴀʟ ɪᴛᴇᴍs : {total_items}\n"
        f"⟡ ᴀᴄᴛɪᴠᴇ : {active_items}\n"
        f"⟡ ᴘᴇɴᴅɪɴɢ : {pending_items}\n"
        f"⟡ sᴏʟᴅ : {sold_items}\n"
        f"⟡ ᴜɴsᴏʟᴅ : {unsold_items}"
    )

    text = (
        "✦ **ᴘᴏᴋᴇɴᴏᴠᴀ sᴛᴀᴛɪsᴛɪᴄs** ✦\n\n"
        "**[ ɴᴇᴛᴡᴏʀᴋ sᴛᴀᴛs ]**\n"
        f"{make_bq(network_stats)}\n\n"
        "**[ ᴀᴜᴄᴛɪᴏɴ ᴅᴀᴛᴀ ]**\n"
        f"{make_bq(auction_stats)}"
    )

    await msg.edit_text(text)


# ----------------- /ping (EVERYONE) ----------------- #
@Client.on_message(filters.command("ping"))
async def ping_cmd(client: Client, message: Message):
    start_time = time.time()
    msg = await message.reply_text("🏓 **ᴘɪɴɢɪɴɢ...**")
    end_time = time.time()

    ms = round((end_time - start_time) * 1000)

    text = (
        "✦ **ᴘᴏɴɢ !** ✦\n\n"
        f"{make_bq(f'⚡ ʟᴀᴛᴇɴᴄʏ : {ms} ᴍs')}"
    )

    await msg.edit_text(text)
