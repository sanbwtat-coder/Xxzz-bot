import os, json, time, re
import telebot, requests

TOKEN = "__BOT_TOKEN__"
OWNER_ID = int("__OWNER_ID__")
BOT_USERNAME = "__BOT_USERNAME__"
DEV_USERNAME = "__DEV_USERNAME__"
BOT_ID = "__BOT_ID__"
MAKER_DATA_FILE = "__MAKER_DATA_FILE__"
OWNER_FORCE_CHANNEL = "__OWNER_FORCE_CHANNEL__"
SOURCE_NAME = "__SOURCE_NAME__"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
DATA_FILE = f"bot_data_{BOT_ID}.json"
DEFAULT = {"users": {}, "groups": {}, "locks": {}, "messages": {}, "points": {}}

def load_json(path, default):
    if not os.path.exists(path):
        save_json(path, default.copy())
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except: return default.copy()

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

data = load_json(DATA_FILE, DEFAULT)

def maker_data(): return load_json(MAKER_DATA_FILE, {"bots": {}})
def bot_info(): return maker_data().get("bots", {}).get(BOT_ID, {"plan": "free", "force_channel": OWNER_FORCE_CHANNEL})
def force_channel():
    info = bot_info()
    return (info.get("force_channel") if info.get("plan") == "paid" else OWNER_FORCE_CHANNEL) or OWNER_FORCE_CHANNEL
def is_paid(): return bot_info().get("plan") == "paid"
def sid(x): return str(x)

def raw_send(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup: payload["reply_markup"] = reply_markup
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload, timeout=15)

def blue(text, callback_data=None, url=None):
    b = {"text": text, "style": "primary"}
    if callback_data: b["callback_data"] = callback_data
    if url: b["url"] = url
    return b

def red(text, callback_data=None, url=None):
    b = {"text": text, "style": "danger"}
    if callback_data: b["callback_data"] = callback_data
    if url: b["url"] = url
    return b

def start_keyboard():
    return {"inline_keyboard": [
        [blue("اضفني +", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [blue("المطور", url=f"https://t.me/{DEV_USERNAME}"), blue("الأوامر", callback_data="commands")],
        [blue("حالة البوت: " + ("مدفوع" if is_paid() else "مجاني"), callback_data="status")],
        [red(SOURCE_NAME, url=f"https://t.me/{DEV_USERNAME}")]
    ]}

def commands_keyboard():
    return {"inline_keyboard": [
        [blue("• 1 •", "cmd_1"), blue("• 2 •", "cmd_2")],
        [blue("• 3 •", "cmd_3"), blue("• 4 •", "cmd_4")],
        [blue("• 5 •", "cmd_5"), blue("• 6 •", "cmd_6")],
        [red(SOURCE_NAME, url=f"https://t.me/{DEV_USERNAME}")]
    ]}

COMMANDS = {
"cmd_1": """- اوامر القفل والفتح

- قفل/فتح الروابط
- قفل/فتح الصور
- قفل/فتح الملصقات
- قفل/فتح المتحركات
- قفل/فتح الفيديو
- قفل/فتح التوجيه
- قفل/فتح الملفات
- قفل/فتح الصوت
- قفل/فتح التاك
- قفل/فتح القنوات
- قفل/فتح البوتات
- قفل/فتح الكلايش""",
"cmd_2": """- اوامر مشرفين المجموعة

- القوائم
- الميديا
- نزلني
- انذار
- تثبيت
- الاعدادات
- صلاحياتي
- تاك للكل
- ضع رابط
- ضع وصف
- ضع صوره
- ضع اسم
- ضع ترحيب
- منع / الغاء منع""",
"cmd_3": """- اوامر المسح

- مسح بالرد
- مسح + العدد
- مسح الردود
- مسح الميديا
- مسح الادمنيه
- مسح المميزين
- مسح المكتومين
- مسح المحظورين""",
"cmd_4": """- اوامر الرفع والحظر

- طرد
- كتم / الغاء كتم
- حظر / الغاء حظر
- تقييد / الغاء تقييد
- رفع / تنزيل مميز
- رفع / تنزيل ادمن
- رفع / تنزيل مشرف
- تنزيل الكل""",
"cmd_5": """- اوامر الترفيه

- زوجني
- ز
- زوجتي
- زوجي
- نسبه الحب
- نسبه الجمال
- ثنائي اليوم
- غنيلي
- شعر
- فلم
- مسلسل""",
"cmd_6": """- الالعاب

- لغز
- XO
- سيارات
- اعلام
- عربي
- المشاهير
- كت
- حجرة
- الاسرع
- لو خيروك
- نقاطي
- بيع نقاطي"""
}

def register(message):
    if not message.from_user: return
    uid = sid(message.from_user.id)
    data["users"].setdefault(uid, {"name": message.from_user.first_name or "", "username": message.from_user.username or ""})
    if message.chat.type in ["group", "supergroup"]:
        gid = sid(message.chat.id)
        data["groups"].setdefault(gid, {"title": message.chat.title or ""})
        data["messages"].setdefault(gid, {})
        data["messages"][gid][uid] = data["messages"][gid].get(uid, 0) + 1
    save_json(DATA_FILE, data)

def is_subscribed(user_id):
    ch = force_channel()
    try:
        m = bot.get_chat_member(ch, user_id)
        return m.status in ["member", "administrator", "creator"]
    except: return True

def check_sub(message):
    if message.from_user and not is_subscribed(message.from_user.id):
        ch = force_channel()
        raw_send(message.chat.id, "⚠️ لازم تشترك بالقناة أولاً", {"inline_keyboard": [[blue("اشترك بالقناة", url="https://t.me/" + ch.replace("@", ""))]]})
        return False
    return True

def is_admin(message):
    if message.from_user.id == OWNER_ID: return True
    try:
        m = bot.get_chat_member(message.chat.id, message.from_user.id)
        return m.status in ["administrator", "creator"]
    except: return False

@bot.message_handler(content_types=["new_chat_members", "left_chat_member"])
def delete_join_leave(message):
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass

@bot.message_handler(commands=["start"])
def start(message):
    register(message)
    if not check_sub(message): return
    txt = f"• هلا بك في بوت حماية فادي\n\n• اضفني للكروب وارفعني مشرف\n\n• حالة البوت: {'مدفوع' if is_paid() else 'مجاني'}\n• الاشتراك الإجباري: {force_channel()}"
    raw_send(message.chat.id, txt, start_keyboard())

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    try: bot.answer_callback_query(call.id)
    except: pass
    if call.data == "commands": return raw_send(call.message.chat.id, "- اختر قسم الاوامر", commands_keyboard())
    if call.data in COMMANDS: return raw_send(call.message.chat.id, COMMANDS[call.data], commands_keyboard())
    if call.data == "status": return raw_send(call.message.chat.id, f"• حالة البوت: {'مدفوع' if is_paid() else 'مجاني'}\n• الاشتراك الإجباري: {force_channel()}")

@bot.message_handler(content_types=["text", "photo", "video", "sticker", "animation", "document", "voice", "audio"])
def handler(message):
    register(message)
    if message.chat.type != "private" and not check_sub(message): return
    text = message.text or message.caption or ""
    if text in ["الاوامر", "الأوامر", "اوامر"]: return raw_send(message.chat.id, "- اختر قسم الاوامر", commands_keyboard())
    if text == "سورس": return raw_send(message.chat.id, SOURCE_NAME, {"inline_keyboard": [[red(SOURCE_NAME, url=f"https://t.me/{DEV_USERNAME}")]]})
    if text == "المطور": return bot.reply_to(message, f"https://t.me/{DEV_USERNAME}")
    if text.startswith("قفل ") or text.startswith("فتح "):
        if not is_admin(message): return
        name = text.split(maxsplit=1)[1].strip(); gid = sid(message.chat.id)
        data["locks"].setdefault(gid, {})[name] = text.startswith("قفل ")
        save_json(DATA_FILE, data)
        return bot.reply_to(message, "تم " + ("قفل " if text.startswith("قفل ") else "فتح ") + name)
    if message.chat.type in ["group", "supergroup"] and message.from_user and not is_admin(message):
        gid = sid(message.chat.id); locks = data["locks"].get(gid, {})
        content_map = {"الصور":"photo", "الملصقات":"sticker", "المتحركات":"animation", "الفيديو":"video", "الملفات":"document", "الصوت":"voice", "الاغاني":"audio"}
        for lname, ctype in content_map.items():
            if locks.get(lname) and message.content_type == ctype:
                try: bot.delete_message(message.chat.id, message.message_id)
                except: pass
                return
        if locks.get("الروابط") and re.search(r"(https?://|t\.me/|www\.)", text):
            try: bot.delete_message(message.chat.id, message.message_id)
            except: pass
            return
    if text == "ا":
        uid, gid = sid(message.from_user.id), sid(message.chat.id)
        msgs = data["messages"].get(gid, {}).get(uid, 0)
        return bot.reply_to(message, f"- الاسم: {message.from_user.first_name}\n- الايدي: <code>{message.from_user.id}</code>\n- الرسائل: {msgs}")

print("Created protection bot running...")
bot.infinity_polling(skip_pending=True)
