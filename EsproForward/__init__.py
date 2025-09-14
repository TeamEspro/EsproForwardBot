# Join me at telegram @EsproUpdate

from pyrogram import Client
from decouple import config
import logging, sys, os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ───────────────────────────
# Variables from .env
# ───────────────────────────
API_ID = config("API_ID", cast=int)
API_HASH = config("API_HASH")
BOT_TOKEN = config("BOT_TOKEN", default=None)
SESSION = config("SESSION", default=None)   # Userbot Session String
AUTH = config("AUTH", default="")           # Sudo User IDs (space separated)
ENV_PATH = ".env"                            # .env file path

SUDO_USERS = {int(x) for x in AUTH.split()} if AUTH else set()

# Groups / Channels to auto join
AUTO_JOIN = ["@EsproSupport", "@EsproUpdate"]

# ───────────────────────────
# Function to save SESSION to .env
# ───────────────────────────
def save_session_to_env(session_str):
    print("\n⚡ Saving session string to .env file...")
    if not os.path.exists(ENV_PATH):
        print("❌ .env file not found!")
        return
    with open(ENV_PATH, "r") as f:
        lines = f.readlines()
    with open(ENV_PATH, "w") as f:
        updated = False
        for line in lines:
            if line.startswith("SESSION="):
                f.write(f"SESSION={session_str}\n")
                updated = True
            else:
                f.write(line)
        if not updated:
            f.write(f"SESSION={session_str}\n")
    print("✅ SESSION string saved to .env!")

# ───────────────────────────
# Userbot
# ───────────────────────────
if not SESSION:
    print("📱 No session string found in .env")
    print("➡ Logging in with phone number (enter OTP when asked)...")
    try:
        userbot = Client("myacc", api_id=API_ID, api_hash=API_HASH)
        with userbot:
            print("✅ Userbot login successful!")
            session_str = userbot.export_session_string()
            print("\n⚡ SESSION string generated:")
            print(session_str)
            save_session_to_env(session_str)
        sys.exit("🔄 Restart the script after .env is updated with SESSION")
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
# Auto join groups/channels
# ───────────────────────────
for target in AUTO_JOIN:
    try:
        userbot.join_chat(target)
        logging.info(f"✅ Joined {target} successfully")
    except Exception as e:
        logging.warning(f"⚠️ Failed to join {target}: {e}")

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
