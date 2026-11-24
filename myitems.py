import math
import html
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from Nova.db import Poke

ITEMS_PER_PAGE = 10
SAVAGE_MSG = "⚠️ ᴀʙᴇ ɴᴀʟʟᴇ, ᴀᴘɴᴀ ᴄᴏᴍᴍᴀɴᴅ ᴜsᴇ ᴋᴀʀ! ᴅᴜsʀᴏ ᴋᴇ ʙᴜᴛᴛᴏɴs ᴘᴇ ᴜɴɢʟɪ ᴍᴀᴛ ᴋᴀʀ! 😂"

CAT_MAP = {
    "nonleg": "NON - LEGENDARY",
    "leg": "LEGENDARY",
    "shiny": "SHINY",
    "tms": "TMS",
    "tutor": "TUTOR"
}

async def get_myitems_ui(user_id: int, tab: str, cat_key: str, page: int):
    # Query Setup
    query = {"status": "sold"}
    
    if tab == "bought":
        query["buyer_id"] = user_id
        title_prefix = "🛒 <b>ʏᴏᴜʀ ʙᴏᴜɢʜᴛ ɪᴛᴇᴍs</b>"
    else:
        query["seller_id"] = user_id
        title_prefix = "💰 <b>ʏᴏᴜʀ sᴏʟᴅ ɪᴛᴇᴍs</b>"

    # Category Filter
    if cat_key != "all" and cat_key in CAT_MAP:
        query["category"] = CAT_MAP[cat_key]
        cat_name = CAT_MAP[cat_key]
    else:
        cat_name = "ALL CATEGORIES"

    total_items = await Poke.count_documents(query)

    if total_items == 0:
        text = f"{title_prefix}\n🗂 <b>Cᴀᴛᴇɢᴏʀʏ:</b> {cat_name}\n\nℹ️ ʏᴏᴜ ʜᴀᴠᴇ ɴᴏ {tab} ɪᴛᴇᴍs ɪɴ ᴛʜɪs ᴄᴀᴛᴇɢᴏʀʏ."
        total_pages = 1
        items = []
    else:
        total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
        if page >= total_pages:
            page = total_pages - 1
        if page < 0:
            page = 0

        cursor = Poke.find(query).skip(page * ITEMS_PER_PAGE).limit(ITEMS_PER_PAGE)
        items = await cursor.to_list(length=ITEMS_PER_PAGE)

        text = f"{title_prefix}\n🗂 <b>Cᴀᴛᴇɢᴏʀʏ:</b> {cat_name}\n\n"
        start_idx = page * ITEMS_PER_PAGE + 1

        for idx, item in enumerate(items, start=start_idx):
            name = str(item.get("name", "Unknown")).strip()
            name = html.escape(name)
            item_id = item.get("item_id", "Unknown")
            price = item.get("sold_price", item.get("base_price", 0))

            if tab == "bought":
                other_person = html.escape(item.get("seller_mention", "Unknown Seller"))
                text += f"<code>{idx}.</code> <b>{name}</b> (<code>{item_id}</code>)\n➤ 💰 <b>{price:,}</b> | 👤 ғʀᴏᴍ: {other_person}\n\n"
            else:
                other_person = html.escape(item.get("buyer_mention", "Unknown Buyer"))
                text += f"<code>{idx}.</code> <b>{name}</b> (<code>{item_id}</code>)\n➤ 💰 <b>{price:,}</b> | 👤 ᴛᴏ: {other_person}\n\n"

    # --- Buttons Setup ---
    buttons = []
    cb_base = f"myi_{user_id}"

    # 1. Main Tabs Row
    btn_bought = "🍁 ʙᴏᴜɢʜᴛ" if tab == "bought" else "ʙᴏᴜɢʜᴛ"
    btn_sold = "🍁 sᴏʟᴅ" if tab == "sold" else "sᴏʟᴅ"
    
    buttons.append([
        InlineKeyboardButton(btn_bought, callback_data=f"{cb_base}_bought_{cat_key}_0"),
        InlineKeyboardButton(btn_sold, callback_data=f"{cb_base}_sold_{cat_key}_0")
    ])

    # 2. Categories Row
    def cat_btn(key, label):
        prefix = "★ " if cat_key == key else ""
        return InlineKeyboardButton(f"{prefix}{label}", callback_data=f"{cb_base}_{tab}_{key}_0")

    buttons.append([
        cat_btn("all", "Aʟʟ"), 
        cat_btn("nonleg", "0ʟ"), 
        cat_btn("leg", "6ʟ")
    ])
    buttons.append([
        cat_btn("shiny", "Sʜɪɴʏ"), 
        cat_btn("tms", "TMs"), 
        cat_btn("tutor", "Tᴜᴛᴏʀs")
    ])

    # 3. Pagination Row
    if total_pages > 1:
        row = []
        if page > 0:
            row.append(InlineKeyboardButton("⬅️ Pʀᴇ", callback_data=f"{cb_base}_{tab}_{cat_key}_{page-1}"))
        else:
            row.append(InlineKeyboardButton("❌", callback_data=f"noop_{user_id}"))

        row.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data=f"noop_{user_id}"))

        if page < total_pages - 1:
            row.append(InlineKeyboardButton("Nᴇxᴛ ➡️", callback_data=f"{cb_base}_{tab}_{cat_key}_{page+1}"))
        else:
            row.append(InlineKeyboardButton("❌", callback_data=f"noop_{user_id}"))

        buttons.append(row)
        
    # 4. Close Button
    buttons.append([InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data=f"close_myitems_{user_id}")])

    return text, InlineKeyboardMarkup(buttons)


@Client.on_message(filters.command(["myitems"], prefixes=["/", "."]))
async def myitems_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    text, reply_markup = await get_myitems_ui(user_id, "bought", "all", 0)
    await message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^myi_(\d+)_(bought|sold)_([a-zA-Z]+)_(\d+)$"))
async def myitems_cb(client: Client, cb: CallbackQuery):
    owner_id = int(cb.matches[0].group(1))
    
    if cb.from_user.id != owner_id:
        return await cb.answer(SAVAGE_MSG, show_alert=True)

    tab = cb.matches[0].group(2)
    cat_key = cb.matches[0].group(3)
    page = int(cb.matches[0].group(4))

    text, reply_markup = await get_myitems_ui(owner_id, tab, cat_key, page)

    try:
        await cb.message.edit_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await cb.answer()


@Client.on_callback_query(filters.regex(r"^close_myitems_(\d+)$"))
async def close_myitems_cb(client: Client, cb: CallbackQuery):
    owner_id = int(cb.matches[0].group(1))
    if cb.from_user.id != owner_id:
        return await cb.answer(SAVAGE_MSG, show_alert=True)
    try:
        await cb.message.delete()
    except Exception:
        pass
    await cb.answer()
