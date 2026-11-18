import os
import logging
from telethon import TelegramClient, events, Button
from database import load_channels, add_channel, remove_channel

logger = logging.getLogger(__name__)

CONTROL_BOT_TOKEN = os.getenv('CONTROL_BOT_TOKEN')
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
ADMIN_ID = int(os.getenv('ADMIN_ID'))

control_bot = TelegramClient('control_bot_session', API_ID, API_HASH)

def is_admin(user_id):
    return user_id == ADMIN_ID

async def show_main_menu(event):
    channels = load_channels()
    buttons = [
        [Button.inline("➕ إضافة قناة للمراقبة", data="add_ch")],
        [Button.inline(f"📋 القنوات المراقبة ({len(channels)})", data="list_ch")],
    ]
    text = "🤖 **لوحة تحكم بوت الصيد**\n\nاختر الإجراء المطلوب:"
    
    if isinstance(event, events.CallbackQuery.Event):
        await event.edit(text, buttons=buttons)
    else:
        await event.respond(text, buttons=buttons)

@control_bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    if not is_admin(event.sender_id):
        return await event.respond("⚠️ عذراً، هذا البوت مخصص للمالك فقط.")
    await show_main_menu(event)

@control_bot.on(events.CallbackQuery)
async def callback_handler(event):
    if not is_admin(event.sender_id):
        return await event.answer("⚠️ غير مصرح لك.", alert=True)

    data = event.data.decode('utf-8')

    if data == "add_ch":
        await event.edit("📝 أرسل الآن **معرف القناة (Username)** أو **رابطها**:", buttons=[[Button.inline("🔙 رجوع", data="back")]])
    
    elif data == "list_ch":
        channels = load_channels()
        if not channels:
            return await event.edit("📭 لا توجد قنوات مراقبة حالياً.", buttons=[[Button.inline("🔙 رجوع", data="back")]])
        
        buttons = []
        for ch in channels:
            buttons.append([Button.inline(f"❌ حذف {ch}", data=f"del_{ch}")])
        buttons.append([Button.inline("🔙 رجوع", data="back")])
        await event.edit("📋 **القنوات المراقبة:**\nاضغط على القناة لحذفها:", buttons=buttons)

    elif data == "back":
        await show_main_menu(event)

    elif data.startswith("del_"):
        ch = data.replace("del_", "")
        if remove_channel(ch):
            await event.answer(f"✅ تم حذف {ch}", alert=True)
            event.data = b"list_ch"
            await callback_handler(event)
        else:
            await event.answer("❌ لم يتم العثور على القناة.", alert=True)

@control_bot.on(events.NewMessage(func=lambda e: e.is_private and not e.text.startswith('/')))
async def add_channel_handler(event):
    if not is_admin(event.sender_id):
        return
    
    channel_input = event.text.strip()
    if add_channel(channel_input):
        await event.respond(f"✅ تم إضافة `{channel_input}` بنجاح!\nالبوت بدأ يراقبها الآن فوراً بدون إعادة تشغيل.", buttons=[[Button.inline("🔙 القائمة الرئيسية", data="back")]])
    else:
        await event.respond("⚠️ هذه القناة مضافة بالفعل.", buttons=[[Button.inline("🔙 القائمة الرئيسية", data="back")]])

async def start_control_bot():
    await control_bot.start(bot_token=CONTROL_BOT_TOKEN)
    logger.info("✅ Control Bot started.")
    await control_bot.run_until_disconnected()