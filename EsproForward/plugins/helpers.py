# Github.com/devgaganin

import asyncio, subprocess, re, os, time
from datetime import datetime as dt
import math
import cv2
import logging

from pyrogram import Client
from pyrogram.errors import FloodWait, InviteHashInvalid, InviteHashExpired, UserAlreadyParticipant

from telethon import TelegramClient
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

# ----------------- Logging Setup -----------------
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("telethon").setLevel(logging.WARNING)

# ----------------- Video & File Utilities -----------------
def video_metadata(file):
    """Gets width, height, and duration of a video file."""
    vcap = cv2.VideoCapture(file)
    width = round(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = round(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = vcap.get(cv2.CAP_PROP_FPS)
    frame_count = vcap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = round(frame_count / fps) if fps > 0 else 0
    return {'width': width, 'height': height, 'duration': duration}

def TimeFormatter(milliseconds) -> str:
    """Converts a time duration in milliseconds to a human-readable string."""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        (f"{str(days)}d, " if days else "")
        + (f"{str(hours)}h, " if hours else "")
        + (f"{str(minutes)}m, " if minutes else "")
        + (f"{str(seconds)}s, " if seconds else "")
        + (f"{str(milliseconds)}ms, " if milliseconds else "")
    )
    return tmp[:-2]

def humanbytes(size):
    """Converts a size in bytes to a human-readable format."""
    size = int(size)
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return f"{str(round(size, 2))} {Dic_powerN[n]}B"

def hhmmss(seconds):
    """Converts seconds into HH:MM:SS format."""
    return time.strftime('%H:%M:%S', time.gmtime(seconds))

async def screenshot(video, duration, sender):
    """Captures a screenshot from the midpoint of a video using ffmpeg."""
    if os.path.exists(f'{sender}.jpg'):
        return f'{sender}.jpg'
    time_stamp = hhmmss(int(duration) / 2)
    out = dt.now().isoformat("_", "seconds") + ".jpg"
    cmd = ["ffmpeg", "-ss", f"{time_stamp}", "-i", f"{video}", "-frames:v", "1", f"{out}", "-y"]
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await process.communicate()
    return out if os.path.isfile(out) else None

def get_link(string):
    """Finds a URL in a given string using regex."""
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    try:
        return url[0][0] if url else False
    except IndexError:
        return False

# ----------------- Telegram API Interactions -----------------
async def join_chat(client, invite_link):
    """Joins a chat using Pyrogram and handles common errors."""
    try:
        chat = await client.join_chat(invite_link)
        chat_type = "Group" if chat.type.name == "SUPERGROUP" else "Channel"
        return f"✅ Joined {chat_type}: {chat.title}"
    except UserAlreadyParticipant:
        return f"ℹ️ Already joined: {invite_link}"
    except (InviteHashInvalid, InviteHashExpired):
        return f"❌ Invalid or expired link: {invite_link}"
    except FloodWait as e:
        return f"⚠️ Too many requests! Wait {e.value} seconds."
    except Exception as e:
        return f"❌ Error joining {invite_link}: {e}"

async def force_sub(telethon_client, channel, user_id):
    """Checks if a user is a member of a specified channel using Telethon."""
    try:
        await telethon_client(GetParticipantRequest(channel=channel, participant=int(user_id)))
        return True, None
    except UserNotParticipantError:
        return False, f"To use this bot, you must join @{channel}."
    except Exception:
        return False, "ERROR: Could not check force subscribe. Check channel ID or add the bot."

# ----------------- MAIN EXECUTION -----------------
async def main():
    """Main function to run the user-bot and demonstrate utility functions."""
    # Get credentials from user
    api_id = int(input("Enter your API ID: "))
    api_hash = input("Enter your API HASH: ")
    phone_number = input("Enter your phone number with country code (+91...): ")

    # Initialize both Pyrogram and Telethon clients for full functionality
    pyrogram_client = Client("user_session", api_id=api_id, api_hash=api_hash, phone_number=phone_number)
    telethon_client = TelegramClient("user_session", api_id=api_id, api_hash=api_hash)

    async with pyrogram_client:
        me = await pyrogram_client.get_me()
        print(f"\n🔹 Logged in as {me.first_name} (@{me.username})\n")

        # Auto-join predefined channels
        print("👉 Auto joining required channels/groups...")
        for link in ["EsproSupport", "EsproUpdate"]:
            result = await join_chat(pyrogram_client, link)
            print(result)

        # Connect Telethon client to perform the force-sub check
        await telethon_client.connect()
        try:
            is_sub, reason = await force_sub(telethon_client, "TelethonTestChannel", me.id)
            if not is_sub:
                print(f"Force sub check failed: {reason}")
            else:
                print("Force sub check passed.")
        except Exception as e:
            print(f"An error occurred during force_sub check: {e}")
        finally:
            # Ensure the Telethon client is disconnected
            await telethon_client.disconnect()

        # Additional functionality can be added here, like message handlers
        # that use functions like `video_metadata` and `screenshot`.

if __name__ == "__main__":
    asyncio.run(main())

