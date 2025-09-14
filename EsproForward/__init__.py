# Join me at Telegram @EsproUpdate

import os
import logging
import asyncio
from decouple import config
from pyrogram import Client
from pyrogram.errors import FloodWait, UserAlreadyParticipant

# ───────────────────────────
# Logging setup
# ───────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ───────────────────────────
# Environment variables
# ───────────────────────────
API_ID = config("API_ID", cast=int)
API_HASH = config("API_HASH")
BOT_TOKEN = config("BOT_TOKEN", default=None)
SESSION = config("SESSION")  # Must exist
AUTH = config("AUTH", default="")
SUDO_USERS = {int(x) for x in AUTH.split()} if AUTH else set()

# Groups / Channels to auto join
AUTO_JOIN = ["@EsproSupport", "@EsproUpdate"]

# ───────────────────────────
# Helper: Auto-join groups/channels
# ───────────────────────────
async def auto_join_chats(client, chats):
    for target in chats:
        try:
            await client.join_chat(target)
            logging.info(f"✅ Joined {target}")
        except UserAlreadyParticipant:
            logging.info(f"ℹ Already a member of {target}")
        except FloodWait as e:
            logging.warning(f"⏱ Flood wait {e.x} seconds for {target}")
            await asyncio.sleep(e.x)
        except Exception as e:
            logging.warning(f"⚠️ Could not join {target}: {e}")

# ───────────────────────────
# Start userbot
# ───────────────────────────
async def start_userbot():
    if not SESSION:
        logging.error("❌ SESSION missing! Add SESSION string to .env")
        return None

    try:
        userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
        await userbot.start()
        logging.info("✅ Userbot started with session string")
        # Auto join groups
        await auto_join_chats(userbot, AUTO_JOIN)
        return userbot
    except Exception as e:
        logging.error(f"❌ Userbot failed to start: {e}")
        return None

# ───────────────────────────
# Start bot
# ───────────────────────────
async def start_bot():
    if not BOT_TOKEN:
        logging.warning("⚠️ BOT_TOKEN not found, skipping bot start")
        return None
    try:
        bot = Client("EsproBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
        await bot.start()
        logging.info("✅ Bot started successfully")
        return bot
    except Exception as e:
        logging.error(f"❌ Bot failed to start: {e}")
        return None

# ───────────────────────────
# Main async runner
# ───────────────────────────
async def main():
    userbot_task = asyncio.create_task(start_userbot())
    bot_task = asyncio.create_task(start_bot())

    # Wait for both to start
    userbot_client, bot_client = await asyncio.gather(userbot_task, bot_task)

    if userbot_client or bot_client:
        logging.info("🚀 Both bot and userbot are running...")
        # Keep script running
        while True:
            await asyncio.sleep(60)
    else:
        logging.error("❌ Neither bot nor userbot could start. Exiting.")

# ───────────────────────────
# Run
# ───────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
