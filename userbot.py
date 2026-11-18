import os
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from database import load_channels

logger = logging.getLogger(__name__)

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
STRING_SESSION = os.getenv('STRING_SESSION')

KEYWORDS = ['Claim', 'Now', 'CLAIM', 'NOW']
BUTTON_TEXTS = ['Claim', 'Now', 'CLAIM', 'NOW']

clicked_messages = set()

user_client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

def clean_channel_id(channel_str):
    ch = str(channel_str).replace('@', '').strip()
    if "t.me/" in ch:
        ch = ch.split("t.me/")[-1].replace("/", "")
    return ch

@user_client.on(events.NewMessage())
async def global_monitor_handler(event):
    if not event.is_channel:
        return

    monitored_channels = load_channels()
    if not monitored_channels:
        return

    current_chat_id = str(event.chat_id)
    current_chat_username = event.chat.username if hasattr(event.chat, 'username') else None
    
    is_target_channel = False
    for ch in monitored_channels:
        if (current_chat_id == str(ch)) or (current_chat_username and current_chat_username.lower() == clean_channel_id(ch).lower()):
            is_target_channel = True
            break

    if not is_target_channel:
        return

    message = event.message
    message_id = message.id
    chat_id = event.chat_id

    if (chat_id, message_id) in clicked_messages:
        return

    text = message.text or ""
    has_keyword = any(keyword.lower() in text.lower() for keyword in KEYWORDS)
    has_buttons = False
    target_button = None

    if message.reply_markup and hasattr(message.reply_markup, 'rows'):
        for row in message.reply_markup.rows:
            for button in row.buttons:
                if hasattr(button, 'text') and any(b_text.lower() in button.text.lower() for b_text in BUTTON_TEXTS):
                    has_buttons = True
                    target_button = button
                    break
            if has_buttons: break

    if has_keyword or has_buttons:
        logger.info(f"🎯 Target in {current_chat_username or current_chat_id}")
        if target_button:
            try:
                await user_client(GetBotCallbackAnswerRequest(
                    peer=chat_id, msg_id=message_id, data=target_button.data
                ))
                logger.info(f"✅ Clicked '{target_button.text}'")
                clicked_messages.add((chat_id, message_id))
                if len(clicked_messages) > 1000: clicked_messages.clear()
                await asyncio.sleep(1)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"❌ Error: {e}")

async def start_userbot():
    await user_client.start()
    logger.info("✅ Userbot started.")
    await user_client.run_until_disconnected()