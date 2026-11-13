# ANIME ARENA — Starter

This is the first coding milestone for the single-file ANIME ARENA bot.

## Included in this milestone
- Aiogram 3 bot foundation
- SQLite user profiles
- XP, coins, levels and titles
- Global XP leaderboard
- A playable five-question group quiz
- One answer per player per question
- Quiz timers and result summary
- Environment-variable configuration

## Not implemented yet
Guess the Imposter and Anime Mafia are not implemented in this first milestone. They will be added as complete game engines in later updates, not as fake placeholder games. Persistent recovery of active game sessions will also be added with those engines.

## Run locally on Android (Termux) or a computer
1. Install Python 3.11 or newer.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`.
4. Put your NEW Telegram bot token in `.env`.
5. Run:
   `python bot.py`

Never upload `.env` or your real token to GitHub.

## Deploy on Render
Use a **Background Worker**, not a Web Service, because this bot uses Telegram long polling and does not serve HTTP requests.

- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `python bot.py`
- Environment variable: `TELEGRAM_BOT_TOKEN` = your newly rotated BotFather token
- Optional: `QUIZ_SECONDS` = `20`
- Set `DATABASE_PATH` to `/var/data/anime_arena.db` if you attach a persistent disk mounted at `/var/data`.

### SQLite persistence warning
Render's default filesystem is ephemeral. Without a persistent disk, SQLite data can be lost on restarts or redeploys. Render currently documents persistent disks as available on paid services, including background workers. If you need a free deployment, we should switch the database plan before storing real player progress.

## GitHub
Upload `bot.py`, `requirements.txt`, `.env.example`, and `README.md`.
Do not upload `.env`, database files, or bot tokens.
