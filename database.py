import json
import os

DB_FILE = 'channels.json'

def load_channels():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return []

def save_channels(channels):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(channels, f, ensure_ascii=False, indent=4)

def add_channel(channel_id):
    channels = load_channels()
    # تنظيف الإدخال من الروابط والرموز
    ch = str(channel_id).replace('@', '').strip()
    if "t.me/" in ch:
        ch = ch.split("t.me/")[-1].replace("/", "")
    
    if ch not in channels:
        channels.append(ch)
        save_channels(channels)
        return True
    return False

def remove_channel(channel_id):
    channels = load_channels()
    ch = str(channel_id).replace('@', '').strip()
    if ch in channels:
        channels.remove(ch)
        save_channels(channels)
        return True
    return False