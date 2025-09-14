# Join me at telegram @EsproUpdate

from pyrogram import Client
from decouple import config
import logging, sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ───────────────────────────
# Variables
# ───────────────────────────
API_ID = config("API_ID", cast=int)
API_HASH = config("API_HASH")
BOT_TOKEN = config("BOT_TOKEN", default=None)
SESSION = config("SESSION", default=None)   # Userbot Session String
AUTH = config("AUTH", default="")           # Sudo User IDs (space separated)

SUDO_USERS = {int(x) for x in AUTH.split()} if AUTH else set()

# ───────────────────────────
# Userbot
# ───────────────────────────
if not SESSION:
    print("📱 No session string found in .env")
    print("➡ Logging in with phone number (enter OTP when asked)...")
    try:
        # Pyrogram v2 userbot login
        userbot = Client("myacc", api_id=API_ID, api_hash=API_HASH)
        with userbot:
            print("✅ Userbot login successful!")
            session_str = userbot.export_session_string()
            print("\n⚡ Copy this SESSION string to your .env file:\n")
            print(f"SESSION={session_str}\n")
        sys.exit("🔄 Restart script after adding SESSION string to .env")
    except Exception as e:
        logging.error(f"❌ Failed to login userbot: {e}")
        sys.exit(1)
else:
    try:
        userbot = Client("myacc", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
        userbot.start()
        logging.info("✅ Userbot started with session string")
    except Exception as e:
        logging.error(f"❌ Userbot session error: {e}")
        sys.exit(1)

# ───────────────────────────
# Bot Client
# ───────────────────────────
if BOT_TOKEN:
    try:
        bot = Client("EsproBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)
        bot.start()
        logging.info("✅ Bot started successfully")
    except Exception as e:
        logging.error(f"❌ Bot start error: {e}")
        sys.exit(1)
else:
    logging.warning("⚠️ BOT_TOKEN not found, bot client skipped")

# ───────────────────────────
# Script Ready
# ───────────────────────────
print("🚀 Both bot and userbot are running...")
