import re
import math
import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from Nova.db import Poke

AUCTION_CHANNEL_ID = -1004230427074
ITEMS_PER_PAGE = 10

SAVAGE_MSG = "⚠️ ᴀʙᴇ ɴᴀʟʟᴇ, ᴀᴘɴᴀ ᴄᴏᴍᴍᴀɴᴅ ᴜsᴇ ᴋᴀʀ! ᴅᴜsʀᴏ ᴋᴇ ʙᴜᴛᴛᴏɴs ᴘᴇ ᴜɴɢʟɪ ᴍᴀᴛ ᴋᴀʀ! 😂"

CAT_MAP = {
    "nonleg": "NON - LEGENDARY",
    "leg": "LEGENDARY",
    "shiny": "SHINY",
    "tms": "TMS",
    "tutor": "TUTOR"
}

CAT_DISPLAY = {
    "nonleg": "0ʟ (ɴᴏɴ - ʟᴇɢᴇɴᴅᴀʀʏ)",
    "leg": "6ʟ (ʟᴇɢᴇɴᴅᴀʀʏ)",
    "shiny": "sʜɪɴʏ",
    "tms": "ᴛᴍs",
    "tutor": "ᴛᴜᴛᴏʀs"
}

async def get_category_menu_buttons(user_id: int):
    # Fetch live counts for all categories
    nonleg_c = await Poke.count_documents({"category": "NON - LEGENDARY", "status": "active"})
    leg_c = await Poke.count_documents({"category": "LEGENDARY", "status": "active"})
    shiny_c = await Poke.count_documents({"category": "SHINY", "status": "active"})
    tms_c = await Poke.count_documents({"category": "TMS", "status": "active"})
    tutor_c = await Poke.count_documents({"category": "TUTOR", "status": "active"})

    # Helper function: Count 0 hai to normal name, warna name ke aage (count)
    def fmt_btn(name, count):
        return f"{name} ({count})" if count > 0 else name

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(fmt_btn("0ʟ", nonleg_c), callback_data=f"itcat_{user_id}_nonleg_0"),
            InlineKeyboardButton(fmt_btn("6ʟ", leg_c), callback_data=f"itcat_{user_id}_leg_0")
        ],
        [
            InlineKeyboardButton(fmt_btn("sʜɪɴʏ", shiny_c), callback_data=f"itcat_{user_id}_shiny_0"),
            InlineKeyboardButton(fmt_btn("ᴛᴍs", tms_c), callback_data=f"itcat_{user_id}_tms_0")
        ],
        [
            InlineKeyboardButton(fmt_btn("ᴛᴜᴛᴏʀs", tutor_c), callback_data=f"itcat_{user_id}_tutor_0")
        ],
        [
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data=f"itcat_{user_id}_close")
        ]
    ])

async def get_category_items(user_id: int, cat_key: str, page: int):
    category = CAT_MAP.get(cat_key)
    if not category:
        return "❌ <b>ɪɴᴠᴀʟɪᴅ ᴄᴀᴛᴇɢᴏʀʏ.</b>", None

    total_items = await Poke.count_documents({"category": category, "status": "active"})
    cat_title = CAT_DISPLAY.get(cat_key, category)

    if total_items == 0:
        text = f"📋 <b>ᴀᴄᴛɪᴠᴇ ɪᴛᴇᴍs : {cat_title}</b>\n\nℹ️ ɴᴏ ᴀᴄᴛɪᴠᴇ ɪᴛᴇᴍs ғᴏᴜɴᴅ ɪɴ ᴛʜɪs ᴄᴀᴛᴇɢᴏʀʏ."
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data=f"itcat_{user_id}_back")],
            [InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data=f"itcat_{user_id}_close")]
        ])
        return text, btn

    total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
    if page >= total_pages:
        page = total_pages - 1
    if page < 0:
        page = 0

    cursor = Poke.find({"category": category, "status": "active"}).skip(page * ITEMS_PER_PAGE).limit(ITEMS_PER_PAGE)
    items = await cursor.to_list(length=ITEMS_PER_PAGE)

    gc_id_str = str(AUCTION_CHANNEL_ID).replace("-100", "")
    text = f"📋 <b>ᴀᴄᴛɪᴠᴇ ɪᴛᴇᴍs : {cat_title}</b>\n\n"

    start_idx = page * ITEMS_PER_PAGE + 1
    for idx, item in enumerate(items, start=start_idx):
        name = html.escape(str(item.get("name", "Unknown Item")).strip())
        info = str(item.get("info", ""))
        msg_id = item.get("bid_msg_id")

        if cat_key in ["nonleg", "leg", "shiny"]:
            nature_text = ""
            if "Nature:" in info:
                match = re.search(r"Nature:\s*([a-zA-Z]+)", info)
                if match:
                    clean_nature = html.escape(match.group(1).strip())
                    nature_text = f" <b>[{clean_nature}]</b>"
            display_title = f"{name}{nature_text}"
        elif cat_key == "tms":
            display_title = f"<b>[TMS]</b> {name}"
        elif cat_key == "tutor":
            display_title = f"<b>[TUTORS]</b> {name}"
        else:
            display_title = name

        link = f"https://t.me/c/{gc_id_str}/{msg_id}" if msg_id else ""
        if link:
            text += f"<code>{idx}.</code> <a href='{link}'>{display_title}</a>\n"
        else:
            text += f"<code>{idx}.</code> {display_title}\n"

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Pʀᴇ", callback_data=f"itcat_{user_id}_{cat_key}_{page-1}"))
    else:
        nav_row.append(InlineKeyboardButton("❌", callback_data=f"noop_{user_id}"))

    nav_row.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data=f"noop_{user_id}"))

    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Nᴇxᴛ ➡️", callback_data=f"itcat_{user_id}_{cat_key}_{page+1}"))
    else:
        nav_row.append(InlineKeyboardButton("❌", callback_data=f"noop_{user_id}"))

    keyboard = [
        nav_row,
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data=f"itcat_{user_id}_back")],
        [InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data=f"itcat_{user_id}_close")]
    ]

    return text, InlineKeyboardMarkup(keyboard)

@Client.on_message(filters.command(["items"], prefixes=["/", "."]))
async def items_cmd_user(client: Client, message: Message):
    user_id = message.from_user.id
    text = (
        "📦 <b>ʙʀᴏᴡsᴇ ᴀᴜᴄᴛɪᴏɴ ɪᴛᴇᴍs ʙʏ ᴄᴀᴛᴇɢᴏʀʏ</b>\n\n"
        "sᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ғʀᴏᴍ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ᴀᴄᴛɪᴠᴇ ʟɪsᴛɪɴɢs:"
    )
    
    # Await required because get_category_menu_buttons is now async
    reply_markup = await get_category_menu_buttons(user_id)
    
    await message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^itcat_(\d+)_([a-zA-Z]+)_(\d+)$"))
async def category_page_cb(client: Client, cb: CallbackQuery):
    owner_id = int(cb.matches[0].group(1))
    if cb.from_user.id != owner_id:
        return await cb.answer(SAVAGE_MSG, show_alert=True)

    cat_key = cb.matches[0].group(2)
    page = int(cb.matches[0].group(3))

    text, reply_markup = await get_category_items(owner_id, cat_key, page)
    try:
        await cb.message.edit_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await cb.answer()

@Client.on_callback_query(filters.regex(r"^itcat_(\d+)_back$"))
async def category_back_cb(client: Client, cb: CallbackQuery):
    owner_id = int(cb.matches[0].group(1))
    if cb.from_user.id != owner_id:
        return await cb.answer(SAVAGE_MSG, show_alert=True)

    text = (
        "📦 <b>ʙʀᴏᴡsᴇ ᴀᴜᴄᴛɪᴏɴ ɪᴛᴇᴍs ʙʏ ᴄᴀᴛᴇɢᴏʀʏ</b>\n\n"
        "sᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ғʀᴏᴍ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ᴀᴄᴛɪᴠᴇ ʟɪsᴛɪɴɢs:"
    )
    
    reply_markup = await get_category_menu_buttons(owner_id)
    
    try:
        await cb.message.edit_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await cb.answer()

@Client.on_callback_query(filters.regex(r"^itcat_(\d+)_close$"))
async def category_close_cb(client: Client, cb: CallbackQuery):
    owner_id = int(cb.matches[0].group(1))
    if cb.from_user.id != owner_id:
        return await cb.answer(SAVAGE_MSG, show_alert=True)
    try:
        await cb.message.delete()
    except Exception:
        pass
    await cb.answer()

@Client.on_callback_query(filters.regex(r"^noop_(\d+)$"))
async def noop_cb(client: Client, cb: CallbackQuery):
    owner_id = int(cb.matches[0].group(1))
    if cb.from_user.id != owner_id:
        return await cb.answer(SAVAGE_MSG, show_alert=True)
    await cb.answer()
