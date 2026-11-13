"""
ANIME ARENA — single-file starter
Python 3.11+
Run locally: python bot.py
Render: deploy as a Background Worker and set TELEGRAM_BOT_TOKEN.
"""

import asyncio
import json
import logging
import os
import random
import time
from pathlib import Path

import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from dotenv import load_dotenv

load_dotenv()

# ----------------------------- CONFIG ---------------------------------

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
DB_PATH = os.getenv("DATABASE_PATH", "anime_arena.db")
QUIZ_SECONDS = int(os.getenv("QUIZ_SECONDS", "20"))
XP_PER_CORRECT = 50

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("anime-arena")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing. Add it to your environment.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ----------------------------- QUESTION BANK --------------------------

QUESTIONS = [
    {
        "category": "Anime Knowledge",
        "difficulty": "Easy",
        "question": "Which village is Naruto from?",
        "options": ["Hidden Leaf", "Hidden Sand", "Hidden Mist", "Hidden Cloud"],
        "answer": 0,
        "anime": "Naruto",
    },
    {
        "category": "Anime Knowledge",
        "difficulty": "Easy",
        "question": "What is the name of Luffy's crew?",
        "options": ["Red Hair Pirates", "Straw Hat Pirates", "Blackbeard Pirates", "Heart Pirates"],
        "answer": 1,
        "anime": "One Piece",
    },
    {
        "category": "Anime Knowledge",
        "difficulty": "Medium",
        "question": "What is the name of the notebook in Death Note?",
        "options": ["Soul Book", "Death Note", "Shinigami File", "Black Ledger"],
        "answer": 1,
        "anime": "Death Note",
    },
    {
        "category": "Anime Knowledge",
        "difficulty": "Medium",
        "question": "Which organisation does Tanjiro join?",
        "options": ["Hunter Association", "Survey Corps", "Demon Slayer Corps", "Soul Society"],
        "answer": 2,
        "anime": "Demon Slayer",
    },
    {
        "category": "Anime Knowledge",
        "difficulty": "Hard",
        "question": "What is the name of the island where the Straw Hats reunite after the timeskip?",
        "options": ["Dressrosa", "Sabaody Archipelago", "Punk Hazard", "Fish-Man Island"],
        "answer": 1,
        "anime": "One Piece",
    },
]

# Active quiz timers are runtime tasks. User profiles and scores are stored in SQLite.
quiz_tasks: dict[int, asyncio.Task] = {}
quiz_locks: dict[int, asyncio.Lock] = {}

# ----------------------------- DATABASE --------------------------------

async def db() -> aiosqlite.Connection:
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA foreign_keys=ON")
    return conn

async def init_db():
    Path(DB_PATH).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    async with await db() as conn:
        await conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT NOT NULL,
            xp INTEGER NOT NULL DEFAULT 0,
            coins INTEGER NOT NULL DEFAULT 0,
            quiz_correct INTEGER NOT NULL DEFAULT 0,
            quiz_played INTEGER NOT NULL DEFAULT 0,
            created_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS quiz_matches (
            chat_id INTEGER PRIMARY KEY,
            host_id INTEGER NOT NULL,
            question_index INTEGER NOT NULL DEFAULT 0,
            question_json TEXT NOT NULL,
            started_at INTEGER NOT NULL,
            ends_at INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        );

        CREATE TABLE IF NOT EXISTS quiz_answers (
            chat_id INTEGER NOT NULL,
            question_index INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            answer_index INTEGER NOT NULL,
            correct INTEGER NOT NULL,
            PRIMARY KEY(chat_id, question_index, user_id)
        );
        """)
        # An interrupted in-memory timer cannot safely resume after a restart.
        # Mark old active quizzes as interrupted instead of leaving dead lobbies.
        await conn.execute(
            "UPDATE quiz_matches SET status='interrupted' WHERE status='active'"
        )
        await conn.commit()

async def ensure_user(user_id: int, username: str | None, first_name: str):
    async with await db() as conn:
        await conn.execute("""
            INSERT INTO users(user_id, username, first_name, created_at)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name
        """, (user_id, username, first_name, int(time.time())))
        await conn.commit()

async def add_xp(user_id: int, amount: int, correct: bool = False):
    async with await db() as conn:
        await conn.execute("""
            UPDATE users
            SET xp=xp+?, coins=coins+?, quiz_correct=quiz_correct+?,
                quiz_played=quiz_played+1
            WHERE user_id=?
        """, (amount, max(1, amount // 10) if correct else 0, 1 if correct else 0, user_id))
        await conn.commit()

async def get_user(user_id: int):
    async with await db() as conn:
        cur = await conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return await cur.fetchone()

# ----------------------------- UI HELPERS ------------------------------

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🧠 Anime Quiz", callback_data="menu:quiz"),
            InlineKeyboardButton(text="🕵️ Imposter", callback_data="menu:imposter"),
        ],
        [
            InlineKeyboardButton(text="🌙 Anime Mafia", callback_data="menu:mafia"),
            InlineKeyboardButton(text="👤 Profile", callback_data="menu:profile"),
        ],
        [InlineKeyboardButton(text="🏆 Leaderboard", callback_data="menu:top")],
    ])

def quiz_keyboard(chat_id: int, question_index: int, options: list[str]):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{'🅰️' if i == 0 else '🅱️' if i == 1 else '🅲' if i == 2 else '🅳'} {option}",
            callback_data=f"qa:{chat_id}:{question_index}:{i}"
        )]
        for i, option in enumerate(options)
    ])

def level_for_xp(xp: int) -> int:
    return (xp // 500) + 1

def title_for_level(level: int) -> str:
    if level <= 5:
        return "Beginner"
    if level <= 10:
        return "Otaku"
    if level <= 20:
        return "Anime Fan"
    if level <= 30:
        return "Anime Expert"
    if level <= 50:
        return "Elite"
    if level <= 75:
        return "Champion"
    if level <= 100:
        return "Legend"
    return "Arena God"

# ----------------------------- BASIC COMMANDS --------------------------

@dp.message(CommandStart())
async def start_cmd(message: Message):
    user = message.from_user
    await ensure_user(user.id, user.username, user.first_name)
    await message.answer(
        "⚔️ <b>ANIME ARENA</b>\n"
        "<i>Quiz • Deception • Competition</i>\n\n"
        "Welcome to the arena. Choose a game or open your profile.",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "<b>ANIME ARENA — COMMANDS</b>\n\n"
        "/start — Open main menu\n"
        "/profile — View your profile\n"
        "/top — Global XP leaderboard\n"
        "/quiz — Start a group quiz (send in a group)\n"
        "/quizstop — Stop your active group quiz\n\n"
        "Imposter and Mafia engines are the next development stages.",
        parse_mode="HTML",
    )

@dp.message(Command("profile"))
async def profile_cmd(message: Message):
    u = message.from_user
    await ensure_user(u.id, u.username, u.first_name)
    row = await get_user(u.id)
    level = level_for_xp(row["xp"])
    progress = row["xp"] % 500
    await message.answer(
        f"👤 <b>{u.first_name}</b>\n"
        f"🏅 {title_for_level(level)} · Level {level}\n"
        f"✨ XP: <b>{row['xp']}</b> ({progress}/500 to next level)\n"
        f"🪙 Coins: <b>{row['coins']}</b>\n"
        f"🧠 Quiz correct: {row['quiz_correct']}\n"
        f"🎮 Quiz answered: {row['quiz_played']}",
        parse_mode="HTML",
    )

@dp.message(Command("top"))
async def top_cmd(message: Message):
    async with await db() as conn:
        cur = await conn.execute(
            "SELECT first_name, xp FROM users ORDER BY xp DESC LIMIT 10"
        )
        rows = await cur.fetchall()
    if not rows:
        await message.answer("No arena players yet. Be the first to play!")
        return
    lines = ["🏆 <b>ANIME ARENA — GLOBAL TOP 10</b>", ""]
    for i, row in enumerate(rows, 1):
        lines.append(f"{i}. {row['first_name']} — <b>{row['xp']} XP</b>")
    await message.answer("\n".join(lines), parse_mode="HTML")

# ----------------------------- QUIZ ENGINE -----------------------------

async def send_quiz_question(chat_id: int, question_index: int):
    q = QUESTIONS[question_index]
    ends_at = int(time.time()) + QUIZ_SECONDS
    async with await db() as conn:
        await conn.execute("""
            UPDATE quiz_matches
            SET question_index=?, question_json=?, ends_at=?, status='active'
            WHERE chat_id=?
        """, (question_index, json.dumps(q), ends_at, chat_id))
        await conn.commit()

    text = (
        f"🧠 <b>ANIME ARENA — QUIZ</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"Question <b>{question_index + 1}/{len(QUESTIONS)}</b>\n"
        f"🎯 {q['category']} · {q['difficulty']}\n\n"
        f"<b>{q['question']}</b>\n\n"
        f"⏳ Time: {QUIZ_SECONDS} seconds\n"
        f"<i>Tap an answer below. Each player gets one attempt.</i>"
    )
    sent = await bot.send_message(
        chat_id, text,
        reply_markup=quiz_keyboard(chat_id, question_index, q["options"]),
        parse_mode="HTML",
    )
    task = asyncio.create_task(question_timeout(chat_id, question_index, sent.message_id))
    old = quiz_tasks.get(chat_id)
    if old and old is not asyncio.current_task() and not old.done():
        old.cancel()
    quiz_tasks[chat_id] = task

async def question_timeout(chat_id: int, question_index: int, message_id: int):
    try:
        await asyncio.sleep(QUIZ_SECONDS)
        async with await db() as conn:
            cur = await conn.execute(
                "SELECT question_json, status, question_index FROM quiz_matches WHERE chat_id=?",
                (chat_id,),
            )
            match = await cur.fetchone()
            if not match or match["status"] != "active" or match["question_index"] != question_index:
                return
            q = json.loads(match["question_json"])
            cur = await conn.execute("""
                SELECT COUNT(*) AS total, SUM(correct) AS correct
                FROM quiz_answers WHERE chat_id=? AND question_index=?
            """, (chat_id, question_index))
            stats = await cur.fetchone()
            await conn.commit()

        try:
            await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        except Exception:
            pass

        await bot.send_message(
            chat_id,
            f"⏰ <b>Time's up!</b>\n"
            f"✅ Correct answer: <b>{q['options'][q['answer']]}</b>\n"
            f"📊 Answers submitted: {stats['total'] or 0} · Correct: {stats['correct'] or 0}",
            parse_mode="HTML",
        )
        next_index = question_index + 1
        if next_index < len(QUESTIONS):
            await asyncio.sleep(2)
            await send_quiz_question(chat_id, next_index)
        else:
            await finish_quiz(chat_id)
    except asyncio.CancelledError:
        return
    except Exception:
        log.exception("Quiz timer failed for chat %s", chat_id)

async def finish_quiz(chat_id: int):
    async with await db() as conn:
        cur = await conn.execute("""
            SELECT u.first_name, SUM(a.correct) AS correct_count, u.user_id
            FROM quiz_answers a
            JOIN users u ON u.user_id=a.user_id
            WHERE a.chat_id=?
            GROUP BY u.user_id
            ORDER BY correct_count DESC, u.first_name ASC
            LIMIT 10
        """, (chat_id,))
        rows = await cur.fetchall()
        await conn.execute(
            "UPDATE quiz_matches SET status='finished' WHERE chat_id=?", (chat_id,)
        )
        await conn.commit()

    lines = ["🏆 <b>QUIZ RESULTS</b>", "━━━━━━━━━━━━━━"]
    if rows:
        for i, row in enumerate(rows, 1):
            lines.append(f"{i}. {row['first_name']} — <b>{row['correct_count']}</b> correct")
    else:
        lines.append("Nobody answered this match.")
    lines.append("\nUse /quiz to play again.")
    await bot.send_message(chat_id, "\n".join(lines), parse_mode="HTML")

@dp.message(Command("quiz"))
async def quiz_cmd(message: Message):
    if message.chat.type == "private":
        await message.answer("Start a quiz from a Telegram group so everyone can play together.")
        return
    async with await db() as conn:
        cur = await conn.execute(
            "SELECT status FROM quiz_matches WHERE chat_id=?", (message.chat.id,)
        )
        existing = await cur.fetchone()
        if existing and existing["status"] == "active":
            await message.reply("A quiz is already running in this group.")
            return
        await conn.execute("DELETE FROM quiz_answers WHERE chat_id=?", (message.chat.id,))
        await conn.execute("""
            INSERT INTO quiz_matches(chat_id, host_id, question_index, question_json, started_at, ends_at, status)
            VALUES(?, ?, -1, '{}', ?, ?, 'active')
            ON CONFLICT(chat_id) DO UPDATE SET
                host_id=excluded.host_id, question_index=-1, question_json='{}',
                started_at=excluded.started_at, ends_at=excluded.ends_at, status='active'
        """, (message.chat.id, message.from_user.id, int(time.time()), int(time.time())))
        await conn.commit()
    await message.answer(
        "🎮 <b>ANIME QUIZ STARTING</b>\n"
        "Five questions. One answer per player per question.\n"
        "Get ready!",
        parse_mode="HTML",
    )
    await asyncio.sleep(2)
    await send_quiz_question(message.chat.id, 0)

@dp.message(Command("quizstop"))
async def quizstop_cmd(message: Message):
    async with await db() as conn:
        cur = await conn.execute(
            "SELECT host_id, status FROM quiz_matches WHERE chat_id=?", (message.chat.id,)
        )
        row = await cur.fetchone()
        if not row or row["status"] != "active":
            await message.reply("There is no active quiz.")
            return
        if row["host_id"] != message.from_user.id:
            member = await bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ("administrator", "creator"):
                await message.reply("Only the quiz host or a group admin can stop this quiz.")
                return
        await conn.execute(
            "UPDATE quiz_matches SET status='stopped' WHERE chat_id=?", (message.chat.id,)
        )
        await conn.commit()
    task = quiz_tasks.get(message.chat.id)
    if task and not task.done():
        task.cancel()
    await message.answer("🛑 Quiz stopped.")

@dp.callback_query(F.data.startswith("qa:"))
async def quiz_answer_callback(callback: CallbackQuery):
    try:
        _, chat_id_s, q_index_s, answer_s = callback.data.split(":")
        chat_id, q_index, answer_index = int(chat_id_s), int(q_index_s), int(answer_s)
    except (ValueError, AttributeError):
        await callback.answer("Invalid answer button.", show_alert=True)
        return

    if not callback.message or callback.message.chat.id != chat_id:
        await callback.answer("This quiz button is no longer valid.", show_alert=True)
        return

    user = callback.from_user
    await ensure_user(user.id, user.username, user.first_name)

    async with await db() as conn:
        cur = await conn.execute(
            "SELECT question_index, question_json, status FROM quiz_matches WHERE chat_id=?",
            (chat_id,),
        )
        match = await cur.fetchone()
        if not match or match["status"] != "active" or match["question_index"] != q_index:
            await callback.answer("This question has ended.", show_alert=True)
            return
        q = json.loads(match["question_json"])
        if answer_index < 0 or answer_index >= len(q["options"]):
            await callback.answer("Invalid option.", show_alert=True)
            return
        cur = await conn.execute("""
            SELECT 1 FROM quiz_answers
            WHERE chat_id=? AND question_index=? AND user_id=?
        """, (chat_id, q_index, user.id))
        if await cur.fetchone():
            await callback.answer("You've already answered this question.")
            return
        correct = int(answer_index == q["answer"])
        await conn.execute("""
            INSERT INTO quiz_answers(chat_id, question_index, user_id, answer_index, correct)
            VALUES(?, ?, ?, ?, ?)
        """, (chat_id, q_index, user.id, answer_index, correct))
        await conn.execute(
            "UPDATE users SET quiz_played=quiz_played+1 WHERE user_id=?", (user.id,)
        )
        if correct:
            await conn.execute(
                "UPDATE users SET xp=xp+?, coins=coins+5, quiz_correct=quiz_correct+1 WHERE user_id=?",
                (XP_PER_CORRECT, user.id),
            )
        await conn.commit()

    await callback.answer("Correct! +50 XP" if correct else "Not quite — try the next one!")
    if correct:
        try:
            await callback.message.reply(f"⚡ {user.first_name} got it right! +{XP_PER_CORRECT} XP")
        except Exception:
            pass

# ----------------------------- MENU CALLBACKS --------------------------

@dp.callback_query(F.data.startswith("menu:"))
async def menu_callback(callback: CallbackQuery):
    section = callback.data.split(":", 1)[1]
    if section == "profile":
        await ensure_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
        row = await get_user(callback.from_user.id)
        level = level_for_xp(row["xp"])
        await callback.message.answer(
            f"👤 <b>{row['first_name']}</b>\n"
            f"🏅 {title_for_level(level)} · Level {level}\n"
            f"✨ XP: <b>{row['xp']}</b>\n🪙 Coins: <b>{row['coins']}</b>",
            parse_mode="HTML",
        )
    elif section == "top":
        await top_cmd(callback.message)
    elif section == "quiz":
        await callback.answer("Use /quiz in a group to start a match.", show_alert=True)
        return
    elif section == "imposter":
        await callback.answer("Guess the Imposter will be added in a later development stage.", show_alert=True)
        return
    elif section == "mafia":
        await callback.answer("Anime Mafia will be added in a later development stage.", show_alert=True)
        return
    await callback.answer()

# ----------------------------- STARTUP ----------------------------------

async def main():
    await init_db()
    log.info("ANIME ARENA is starting...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("ANIME ARENA stopped.")
