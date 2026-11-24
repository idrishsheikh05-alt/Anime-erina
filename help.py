from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from Nova import DEVS
from Nova.db import SudoDB

async def is_admin(user_id: int):
    if user_id in DEVS:
        return True
    sudo_user = await SudoDB.find_one({"user_id": user_id})
    return bool(sudo_user)

def make_bq(text):
    return "\n".join([f"> {line}" for line in str(text).split("\n")])

# --- MENUS TEXT ---

MAIN_TEXT = (
    "✨ **ᴘᴏᴋᴇɴᴏᴠᴀ ᴀᴜᴄᴛɪᴏɴs ʜᴇʟᴘ ᴍᴇɴᴜ** ✨\n\n"
    "ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ʜᴇʟᴘ ᴄᴇɴᴛᴇʀ! ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ʟᴇᴀʀɴ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ, "
    "ᴀᴅᴅ ʏᴏᴜʀ ɪᴛᴇᴍs, ᴀɴᴅ ᴘᴀʀᴛɪᴄɪᴘᴀᴛᴇ ɪɴ ᴛʜᴇ ᴀᴜᴄᴛɪᴏɴ.\n\n"
    "👇 **sᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ:**"
)

USERS_TEXT = (
    "👤 **ᴜsᴇʀ ᴄᴏᴍᴍᴀɴᴅs** 👤\n\n"
    "➤ `/start` - ᴛᴏ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ\n"
    "➤ `/help` - ᴛᴏ ᴏᴘᴇɴ ʜᴇʟᴘ ᴍᴇɴᴜ\n"
    "➤ `/add` - ᴛᴏ ᴀᴅᴅ ᴘᴏᴋᴇᴍᴏɴ/ɪᴛᴇᴍs ɪɴ ᴀᴜᴄᴛɪᴏɴ\n"
    "➤ `/profile` - ᴛᴏ sᴇᴇ ʏᴏᴜʀ ᴘʀᴏғɪʟᴇ sᴛᴀᴛs\n"
    "➤ `/myitems` - ᴛᴏ sᴇᴇ ʏᴏᴜʀ sᴏʟᴅ/ʙᴏᴜɢʜᴛ ɪᴛᴇᴍs\n"
    "➤ `/items` - ᴛᴏ sᴇᴇ ᴀᴄᴛɪᴠᴇ ᴀᴜᴄᴛɪᴏɴ ɪᴛᴇᴍs\n"
    "➤ `/topbuyers` - ᴛᴏ sᴇᴇ ᴛᴏᴘ ʙᴜʏᴇʀs ʟɪsᴛ\n"
    "➤ `/topsellers` - ᴛᴏ sᴇᴇ ᴛᴏᴘ sᴇʟʟᴇʀs ʟɪsᴛ\n"
    "➤ `/report` - ᴛᴏ ʀᴇᴘᴏʀᴛ ᴀɴʏ ʙᴜɢ ɪɴ ʙᴏᴛ\n"
)

ADMINS_TEXT = (
    "👑 **ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs [sᴜᴅᴏ]** 👑\n\n"
    "**[ ᴀᴜᴄᴛɪᴏɴ ᴄᴏɴᴛʀᴏʟs ]**\n"
    "➤ `/start_sub` / `/end_sub` - ᴏᴘᴇɴ/ᴄʟᴏsᴇ ᴀᴅᴅɪᴛɪᴏɴs\n"
    "➤ `/start_auc` - ᴏᴘᴇɴ ʙɪᴅᴅɪɴɢ ɢʟᴏʙᴀʟʟʏ ɪɴ ᴄʜᴀɴɴᴇʟ\n"
    "➤ `/end_auc` - ᴇɴᴅ sᴇssɪᴏɴ & ʀᴇsᴏʟᴠᴇ ᴀʟʟ ɪᴛᴇᴍs\n\n"
    "**[ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ]**\n"
    "➤ `/verify` / `/unverify` - ᴀᴘᴘʀᴏᴠᴇ ᴜsᴇʀ ᴛᴏ sᴇʟʟ\n"
    "➤ `/ban` / `/unban` - ʙᴀɴ/ᴜɴʙᴀɴ ᴜsᴇʀs\n"
    "➤ `/addsudo` / `/rmsudo` - ᴀᴅᴅ/ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴs\n"
    "➤ `/bcast` - ʙʀᴏᴀᴅᴄᴀsᴛ ᴀ ᴍᴇssᴀɢᴇ\n"
    "➤ `/msg <ɪᴅ>` - ᴅᴍ ᴀ ᴜsᴇʀ ᴠɪᴀ ʙᴏᴛ"
)

AUCTION_TEXT = (
    "🛍 **ʜᴏᴡ ᴛᴏ ᴀᴅᴅ ɪᴛᴇᴍs ɪɴ ᴀᴜᴄᴛɪᴏɴ** 🛍\n\n"
    "> 1. ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴛʀᴀᴅᴇ ɢʀᴏᴜᴘ & ᴀᴜᴄᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ.\n"
    "> 2. ʏᴏᴜ ᴍᴜsᴛ ʙᴇ **ᴠᴇʀɪғɪᴇᴅ** ʙʏ ᴀᴅᴍɪɴs. ɪғ ɴᴏᴛ, ᴛᴀɢ @ExtremeeDev ɪɴ ᴛʜᴇ ᴛʀᴀᴅᴇ ɢʀᴏᴜᴘ.\n"
    "> 3. ɢᴏ ᴛᴏ ʙᴏᴛ ᴅᴍ ᴀɴᴅ ᴛʏᴘᴇ `/add`.\n"
    "> 4. sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴄᴀᴛᴇɢᴏʀʏ (ʟᴇɢᴇɴᴅᴀʀʏ, sʜɪɴʏ, ᴇᴛᴄ).\n"
    "> 5. ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ɪɴғᴏ, ɪᴠs, ᴀɴᴅ ᴍᴏᴠᴇsᴇᴛ ᴘᴀɢᴇs **ᴇxᴀᴄᴛʟʏ** ғʀᴏᴍ @PokeNova_Bot.\n"
    "> 6. ᴇɴᴛᴇʀ ʏᴏᴜʀ ʙᴀsᴇ ᴘʀɪᴄᴇ (ɴᴜᴍʙᴇʀs ᴏɴʟʏ).\n"
    "> 7. ᴡᴀɪᴛ ғᴏʀ ᴀᴅᴍɪɴ ᴀᴘᴘʀᴏᴠᴀʟ!"
)

BIDDING_TEXT = (
    "💰 **ʜᴏᴡ ᴛᴏ ʙɪᴅ ɪɴ ᴀᴜᴄᴛɪᴏɴs** 💰\n\n"
    "> 1. ᴀᴜᴄᴛɪᴏɴs ᴡɪʟʟ ʙᴇ ʜᴏsᴛᴇᴅ ɪɴ ᴛʜᴇ ᴏғғɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟ.\n"
    "> 2. ᴄʟɪᴄᴋ ᴛʜᴇ **'ᴘʟᴀᴄᴇ ʙɪᴅ'** ʙᴜᴛᴛᴏɴ ᴏɴ ᴛʜᴇ ᴀᴜᴄᴛɪᴏɴ ᴘᴏsᴛ.\n"
    "> 3. ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ᴅᴍ ʏᴏᴜ; ᴛʏᴘᴇ ʏᴏᴜʀ ʙɪᴅ ᴀᴍᴏᴜɴᴛ ᴛʜᴇʀᴇ.\n"
    "> 4. ʏᴏᴜ ᴄᴀɴ ᴜsᴇ sʜᴏʀᴛᴄᴜᴛs ʟɪᴋᴇ **15k** (15,000) ᴏʀ **2m** (2,000,000).\n"
    "> 5. ᴛʜᴇ ʜɪɢʜᴇsᴛ ʙɪᴅᴅᴇʀ ᴡɪɴs ᴡʜᴇɴ ᴀᴅᴍɪɴs ᴇɴᴅ ᴛʜᴇ ᴀᴜᴄᴛɪᴏɴ sᴇssɪᴏɴ.\n"
    "> 6. ʏᴏᴜ ᴡɪʟʟ ʀᴇᴄᴇɪᴠᴇ ᴀ ᴅᴍ ᴡɪᴛʜ ᴛʜᴇ sᴇʟʟᴇʀ's ᴅᴇᴛᴀɪʟs ᴛᴏ ᴄᴏᴍᴘʟᴇᴛᴇ ᴛʜᴇ ᴛʀᴀᴅᴇ."
)

# --- KEYBOARDS ---

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 ᴜsᴇʀs", callback_data="help_users"), 
         InlineKeyboardButton("🔵 ᴀᴅᴍɪɴs", callback_data="help_admins")],
        [InlineKeyboardButton("🔵 ᴀᴜᴄᴛɪᴏɴ", callback_data="help_auction"), 
         InlineKeyboardButton("🔴 ʙɪᴅᴅɪɴɢ", callback_data="help_bidding")]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ", callback_data="help_back")]
    ])


# --- HANDLERS ---

@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.reply_text(MAIN_TEXT, reply_markup=get_main_keyboard())


@Client.on_callback_query(filters.regex("^help_"))
async def help_callback(client: Client, cb: CallbackQuery):
    action = cb.data.split("_")[1]

    if action == "back":
        await cb.message.edit_text(MAIN_TEXT, reply_markup=get_main_keyboard())
        
    elif action == "users":
        await cb.message.edit_text(USERS_TEXT, reply_markup=get_back_keyboard())
        
    elif action == "admins":
        if not await is_admin(cb.from_user.id):
            return await cb.answer("⚠️ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴠɪᴇᴡ ᴛʜɪs ᴍᴇɴᴜ!", show_alert=True)
        await cb.message.edit_text(ADMINS_TEXT, reply_markup=get_back_keyboard())
        
    elif action == "auction":
        await cb.message.edit_text(AUCTION_TEXT, reply_markup=get_back_keyboard())
        
    elif action == "bidding":
        await cb.message.edit_text(BIDDING_TEXT, reply_markup=get_back_keyboard())

    await cb.answer()
