# protection_template.py
import os
import json
import time
import re
import random
import requests
import threading
import telebot
import yt_dlp

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
DOWNLOADS = f"downloads_{BOT_ID}"
os.makedirs(DOWNLOADS, exist_ok=True)

DEFAULT = {
    "users": {}, "groups": {}, "locks": {}, "lock_actions": {}, "ranks": {},
    "messages": {}, "points": {}, "bank": {}, "muted": {}, "banned": {},
    "restricted": {}, "warns": {}, "blocked_words": {}, "waiting": {},
    "waiting_games": {}, "custom_replies": {}, "custom_commands": {}, "links": {},
    "welcome": {}, "id_template": {},
    "settings": {"id": True, "id_photo": True, "welcome": False}
}

LOCK_TYPES = {
    "التاك": "tag", "القنوات": "channels", "الصور": "photo", "الروابط": "links",
    "الفشار": "bad_words", "التكرار": "spam", "الفيديو": "video", "الدخول": "join",
    "الاضافه": "add", "الاغاني": "audio", "الصوت": "voice", "الملفات": "document",
    "التفليش": "flood", "الدردشه": "chat", "الجهات": "contact", "السيلفي": "video_note",
    "التثبيت": "pin", "الشارحه": "long", "الكلايش": "long", "البوتات": "bots",
    "التوجيه": "forward", "التعديل": "edit", "المعرفات": "username", "الكيبورد": "keyboard",
    "الفارسيه": "persian", "الفارسية": "persian", "الانكليزيه": "english",
    "الانكليزي": "english", "الانجليزي": "english", "الملصقات": "sticker",
    "الاشعارات": "service", "الماركداون": "markdown", "المتحركه": "animation", "المتحركة": "animation"
}

BAD_WORDS = ["كس", "زب", "عير", "قحبة", "كواد", "خرا", "نياكة"]
EN_RE = re.compile(r"[A-Za-z]")
PERSIAN_RE = re.compile(r"[پچژگ]")
URL_RE = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/)", re.I)
RANKS = {"عضو": 0, "مميز": 1, "ادمن": 2, "مشرف": 2, "مدير": 3, "منشئ": 4, "مالك": 5}
RANK_NAMES = ["مميز", "ادمن", "مشرف", "مدير", "منشئ", "مالك"]


def load_json(path, default):
    if not os.path.exists(path):
        save_json(path, default.copy())
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        d = default.copy()
    for k, v in default.items():
        d.setdefault(k, v)
    return d


def save_json(path, d):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


data = load_json(DATA_FILE, DEFAULT)


def maker_data():
    return load_json(MAKER_DATA_FILE, {"bots": {}})


def bot_info():
    m = maker_data()
    return m.get("bots", {}).get(BOT_ID, {"plan": "free", "force_channel": OWNER_FORCE_CHANNEL})


def is_paid():
    return bot_info().get("plan") == "paid"


def force_channel():
    info = bot_info()
    if info.get("plan") == "paid":
        return info.get("force_channel") or OWNER_FORCE_CHANNEL
    return OWNER_FORCE_CHANNEL


def sid(x):
    return str(x)


def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)[:80]


def blue(text, callback_data=None, url=None):
    b = {"text": text, "style": "primary"}
    if callback_data:
        b["callback_data"] = callback_data
    if url:
        b["url"] = url
    return b


def red(text, callback_data=None, url=None):
    b = {"text": text, "style": "danger"}
    if callback_data:
        b["callback_data"] = callback_data
    if url:
        b["url"] = url
    return b


def raw_send(chat_id, text, reply_markup=None, reply_to=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload, timeout=15)
    except Exception:
        pass


def raw_edit(chat_id, message_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText", json=payload, timeout=15)
    except Exception:
        pass


def delete_after(chat_id, message_id, seconds=2):
    def run():
        time.sleep(seconds)
        try:
            bot.delete_message(chat_id, message_id)
        except Exception:
            pass
    threading.Thread(target=run, daemon=True).start()


def start_kb():
    return {"inline_keyboard": [
        [blue("اضفني +", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [blue("المطور", url=f"https://t.me/{DEV_USERNAME}"), blue("الأوامر", "commands")],
        [blue("حالة البوت: " + ("مدفوع" if is_paid() else "مجاني"), "status")],
        [red(SOURCE_NAME, url=f"https://t.me/{DEV_USERNAME}")]
    ]}


def commands_kb():
    return {"inline_keyboard": [
        [blue("• 1 •", "cmd_1"), blue("• 2 •", "cmd_2")],
        [blue("• 3 •", "cmd_3"), blue("• 4 •", "cmd_4")],
        [blue("• 5 •", "cmd_5"), blue("• 6 •", "cmd_6")],
        [red(SOURCE_NAME, url=f"https://t.me/{DEV_USERNAME}")]
    ]}


def back_kb():
    return {"inline_keyboard": [[blue("رجوع", "commands")], [red(SOURCE_NAME, url=f"https://t.me/{DEV_USERNAME}")]]}


COMMANDS = {
"cmd_1": """• اوامر القفل والفتح

• بالكتم • بالطرد • بالتقييد

- التاك
- القنوات
- الصور
- الروابط
- الفشار
- التكرار
- الفيديو
- الدخول
- الاضافه
- الاغاني
- الصوت
- الملفات
- التفليش
- الدردشه
- الجهات
- السيلفي
- التثبيت
- الشارحه
- الكلايش
- البوتات
- التوجيه
- التعديل
- المعرفات
- الكيبورد
- الفارسيه
- الانكليزيه
- الملصقات
- الاشعارات
- الماركداون
- المتحركه""",
"cmd_2": """- اوامر مشرفين المجموعة

- القوائم
- الميديا
- نزلني
- انذار
- تثبيت
- الاعدادات
- التفعيلات
- صلاحياتي
- تصفير الترند
- ضبط الحمايه
- اضف رد
- اضف امر
- تاك للكل
- ضع رابط
- ضع تحذير
- ضع وصف
- ضع صوره
- ضع اسم
- ضع ترحيب
- منع / الغاء منع
- تعيين الايدي
- تغيير الايدي""",
"cmd_3": """- اوامر مسح المشرفين

- مسح رد
- مسح تاك
- مسح امر
- مسح بالرد
- مسح الرابط
- مسح رد عام
- مسح الصوره
- مسح الايدي
- مسح المدراء
- مسح التحذير
- مسح الترحيب
- مسح المنشئين
- مسح المالكين
- مسح الادمنيه
- مسح المميزين
- المقيدين
- المكتومين
- قائمه المنع
- المطرودين
- المحظورين
- مسح + العدد""",
"cmd_4": """- اوامر الرفع والحظر

- طرد
- تحكم
- تنزيل الكل
- رفع القيود
- كشف القيود
- كتم / الغاء كتم
- حظر / الغاء حظر
- تقييد / الغاء تقييد
- رفع / تنزيل منشئ
- رفع / تنزيل مدير
- رفع / تنزيل ادمن
- رفع / تنزيل مميز
- رفع / تنزيل مشرف""",
"cmd_5": """- اوامر ترفيه الاعضاء

- نداء
- جمالي
- زوجني
- ز
- زوجتي
- زوجي
- ثنائي اليوم
- نسبه الحب
- نسبه الكره
- نسبه الرجوله
- نسبه الانوثه
- نسبه الجمال
- غنيلي
- صوره
- اغنيه
- متحركه
- ميمز
- ريمكس
- شعر
- قصيده
- فلم
- مسلسل""",
"cmd_6": """- الالعاب

- لغز
- XO
- سيارات
- اعلام
- مشاهير
- عربي
- كت
- حجرة
- الاسرع
- لو خيروك
- نقاطي
- بيع نقاطي"""
}


def register(message):
    if not message.from_user:
        return
    uid = sid(message.from_user.id)
    data["users"].setdefault(uid, {"name": message.from_user.first_name or "", "username": message.from_user.username or ""})
    if message.chat.type in ["group", "supergroup"]:
        gid = sid(message.chat.id)
        data["groups"].setdefault(gid, {"title": message.chat.title or ""})
        data["messages"].setdefault(gid, {})
        data["messages"][gid][uid] = data["messages"][gid].get(uid, 0) + 1
    save_json(DATA_FILE, data)


def get_rank(chat_id, user_id):
    if user_id == OWNER_ID:
        return "مالك"
    return data["ranks"].get(sid(chat_id), {}).get(sid(user_id), "عضو")


def rank_level(chat_id, user_id):
    return RANKS.get(get_rank(chat_id, user_id), 0)


def is_admin_msg(message):
    if message.from_user.id == OWNER_ID:
        return True
    try:
        m = bot.get_chat_member(message.chat.id, message.from_user.id)
        if m.status in ["administrator", "creator"]:
            return True
    except Exception:
        pass
    return rank_level(message.chat.id, message.from_user.id) >= 1


def target_user(message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    return None


def is_subscribed(user_id):
    ch = force_channel()
    if not ch:
        return True
    try:
        m = bot.get_chat_member(ch, user_id)
        return m.status in ["member", "administrator", "creator"]
    except Exception:
        return True


def check_sub(message):
    if message.from_user and not is_subscribed(message.from_user.id):
        ch = force_channel()
        raw_send(message.chat.id, "⚠️ لازم تشترك بالقناة أولاً", {"inline_keyboard": [[blue("اشترك بالقناة", url="https://t.me/" + ch.replace("@", ""))]]}, message.message_id)
        return False
    return True


def punish(message, lock_key):
    gid = sid(message.chat.id)
    action = data["lock_actions"].get(gid, {}).get(lock_key, "delete")
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass
    if action == "mute":
        try:
            bot.restrict_chat_member(message.chat.id, message.from_user.id, can_send_messages=False)
            data["muted"].setdefault(gid, [])
            if sid(message.from_user.id) not in data["muted"][gid]:
                data["muted"][gid].append(sid(message.from_user.id))
            save_json(DATA_FILE, data)
        except Exception:
            pass
    elif action == "kick":
        try:
            bot.ban_chat_member(message.chat.id, message.from_user.id)
            bot.unban_chat_member(message.chat.id, message.from_user.id)
        except Exception:
            pass
    elif action == "restrict":
        try:
            bot.restrict_chat_member(message.chat.id, message.from_user.id, can_send_messages=False, until_date=int(time.time()) + 3600)
            data["restricted"].setdefault(gid, [])
            if sid(message.from_user.id) not in data["restricted"][gid]:
                data["restricted"][gid].append(sid(message.from_user.id))
            save_json(DATA_FILE, data)
        except Exception:
            pass


def is_lock_enabled(chat_id, key):
    return data["locks"].get(sid(chat_id), {}).get(key, False)


def detect_violation(message, text):
    if message.chat.type not in ["group", "supergroup"] or not message.from_user:
        return None
    if rank_level(message.chat.id, message.from_user.id) >= 1 or is_admin_msg(message):
        return None
    if is_lock_enabled(message.chat.id, "chat"):
        return "chat"
    media_map = {"photo": "photo", "video": "video", "sticker": "sticker", "animation": "animation", "document": "document", "voice": "voice", "audio": "audio", "contact": "contact", "video_note": "video_note"}
    if message.content_type in media_map and is_lock_enabled(message.chat.id, media_map[message.content_type]):
        return media_map[message.content_type]
    if is_lock_enabled(message.chat.id, "links") and URL_RE.search(text): return "links"
    if is_lock_enabled(message.chat.id, "channels") and ("t.me/" in text or "@" in text): return "channels"
    if is_lock_enabled(message.chat.id, "tag") and "@" in text: return "tag"
    if is_lock_enabled(message.chat.id, "username") and "@" in text: return "username"
    if is_lock_enabled(message.chat.id, "english") and EN_RE.search(text): return "english"
    if is_lock_enabled(message.chat.id, "persian") and PERSIAN_RE.search(text): return "persian"
    if is_lock_enabled(message.chat.id, "bad_words") and any(w in text.lower() for w in BAD_WORDS): return "bad_words"
    if is_lock_enabled(message.chat.id, "long") and len(text) > 350: return "long"
    if is_lock_enabled(message.chat.id, "markdown") and any(x in text for x in ["[", "](", "`", "*", "__"]): return "markdown"
    if is_lock_enabled(message.chat.id, "forward") and getattr(message, "forward_date", None): return "forward"
    return None


@bot.message_handler(content_types=["new_chat_members", "left_chat_member"])
def delete_join_leave(message):
    try: bot.delete_message(message.chat.id, message.message_id)
    except Exception: pass
    if message.content_type == "new_chat_members":
        try:
            for u in message.new_chat_members:
                if u.is_bot and is_lock_enabled(message.chat.id, "bots"):
                    bot.ban_chat_member(message.chat.id, u.id); bot.unban_chat_member(message.chat.id, u.id)
        except Exception: pass


@bot.message_handler(commands=["start"])
def start(message):
    register(message)
    if not check_sub(message): return
    txt = "• هلا بك في بوت حماية فادي\n\n• اضفني للكروب وارفعني مشرف\n\n" + f"• حالة البوت: {'مدفوع' if is_paid() else 'مجاني'}\n• الاشتراك الإجباري: {force_channel()}"
    raw_send(message.chat.id, txt, start_kb())


@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    try: bot.answer_callback_query(call.id)
    except Exception: pass
    if call.data == "commands":
        return raw_edit(call.message.chat.id, call.message.message_id, "- اختر قسم الاوامر", commands_kb())
    if call.data in COMMANDS:
        return raw_edit(call.message.chat.id, call.message.message_id, COMMANDS[call.data], back_kb())
    if call.data == "status":
        return raw_send(call.message.chat.id, f"• حالة البوت: {'مدفوع' if is_paid() else 'مجاني'}\n• الاشتراك الإجباري: {force_channel()}")
    if call.data.startswith("quiz_"):
        parts = call.data.split("_", 2)
        if len(parts) < 3: return
        game_id, answer = parts[1], parts[2]
        game = data.get("waiting_games", {}).get(game_id)
        if not game:
            wrong = bot.send_message(call.message.chat.id, "انتهت اللعبة"); delete_after(call.message.chat.id, wrong.message_id, 2); return
        if answer == game["answer"]:
            uid = sid(call.from_user.id)
            data["points"][uid] = data["points"].get(uid, 0) + 1
            data["waiting_games"].pop(game_id, None)
            save_json(DATA_FILE, data)
            bot.send_message(call.message.chat.id, f"✅ إجابة صحيحة\nربحت نقطة\nنقاطك: {data['points'][uid]}")
            return
        wrong = bot.send_message(call.message.chat.id, "❌ إجابة خاطئة"); delete_after(call.message.chat.id, wrong.message_id, 2); return


def add_quiz(chat_id, question, choices, answer):
    game_id = str(int(time.time())) + str(random.randint(100, 999))
    data["waiting_games"][game_id] = {"answer": answer}
    save_json(DATA_FILE, data)
    kb = {"inline_keyboard": []}
    for c in choices[:3]: kb["inline_keyboard"].append([blue(c, f"quiz_{game_id}_{c}")])
    raw_send(chat_id, question, kb)

PUZZLES = [("شنو عاصمة أستراليا؟", ["سيدني", "ملبورن", "كانبرا"], "كانبرا"), ("شي كلما أخذت منه كبر؟", ["الحفرة", "الماء", "البيت"], "الحفرة"), ("شي يمشي بلا رجلين؟", ["النهر", "الكتاب", "القلم"], "النهر")]
ARABIC_Q = [("جمع كلمة كتاب؟", ["كتب", "كتابات", "كاتب"], "كتب"), ("ضد كلمة طويل؟", ["قصير", "كبير", "قديم"], "قصير")]
FLAGS = [("🇮🇶 شنو اسم هذا العلم؟", ["العراق", "مصر", "سوريا"], "العراق"), ("🇬🇷 شنو اسم هذا العلم؟", ["اليونان", "إيطاليا", "فرنسا"], "اليونان")]
CARS = [("🚗 شنو اسم السيارة؟", ["تويوتا", "BMW", "KIA"], "تويوتا"), ("🚙 شنو اسم السيارة؟", ["مرسيدس", "نيسان", "هوندا"], "مرسيدس")]
FAMOUS = [("👤 منو هذا المشهور؟", ["ميسي", "رونالدو", "نيمار"], "ميسي"), ("👤 منو هذا المشهور؟", ["فيروز", "ام كلثوم", "وردة"], "فيروز")]
KT = ["شنو أكثر شي تحبه؟", "شنو حلمك؟", "منو أقرب شخص الك؟", "شنو أكثر شي يضوجك؟"]
WOULD = ["لو خيروك تعيش غني وحيد لو فقير ويا أصحاب؟", "لو خيروك ترجع للماضي لو تشوف المستقبل؟"]
FAST_WORDS = ["تفاحة", "سيارة", "عراق", "قلم", "ماء", "كتاب", "ذهب"]


def source_markup_raw():
    return str({"inline_keyboard": [[{"text": SOURCE_NAME, "url": f"https://t.me/{DEV_USERNAME}", "style": "danger"}]]}).replace("'", '"')


def download_audio(query):
    base_opts = {"format": "bestaudio[filesize<45M]/bestaudio/best", "outtmpl": f"{DOWNLOADS}/%(title)s.%(ext)s", "cookiefile": "cookies.txt", "noplaylist": True, "quiet": True, "no_warnings": True, "socket_timeout": 20, "retries": 4, "fragment_retries": 4, "concurrent_fragment_downloads": 5}
    sources = [(f"ytsearch10:{query}", ["android"]), (f"ytsearch10:{query}", ["ios"]), (f"ytsearch10:{query}", ["web"]), (f"scsearch5:{query}", None)]
    last_error = None
    for search, client in sources:
        try:
            opts = base_opts.copy()
            if client: opts["extractor_args"] = {"youtube": {"player_client": client}}
            else: opts.pop("cookiefile", None)
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(search, download=True)
                if info and "entries" in info:
                    for item in info["entries"]:
                        if item: info = item; break
                if not info: continue
                title = clean_filename(info.get("title", "song")); file_path = ydl.prepare_filename(info); return file_path, title
        except Exception as e:
            last_error = e
            continue
    raise Exception(last_error)


def send_audio_with_source(chat_id, file_path, title, reply_to_message_id):
    with open(file_path, "rb") as audio:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendAudio", data={"chat_id": chat_id, "title": title, "performer": "Song fadi", "caption": f"🎧 {title}", "reply_to_message_id": reply_to_message_id, "reply_markup": source_markup_raw()}, files={"audio": audio}, timeout=120)


def show_id(message):
    if not data["settings"].get("id", True): return
    uid, gid = sid(message.from_user.id), sid(message.chat.id)
    msgs = data["messages"].get(gid, {}).get(uid, 0); pts = data["points"].get(uid, 0); rank = get_rank(message.chat.id, message.from_user.id)
    template = data["id_template"].get(gid) or "- الاسم: {name}\n- الايدي: {id}\n- الرتبة: {rank}\n- الرسائل: {messages}\n- النقاط: {points}"
    txt = template.format(name=message.from_user.first_name, id=message.from_user.id, rank=rank, messages=msgs, points=pts)
    return bot.reply_to(message, txt)


def list_top(message):
    gid = sid(message.chat.id); items = sorted(data["messages"].get(gid, {}).items(), key=lambda x: x[1], reverse=True)[:10]
    if not items: return bot.reply_to(message, "ماكو تفاعل بعد")
    out = "- ترند المجموعة\n\n"
    for i, (uid, count) in enumerate(items, 1):
        name = data["users"].get(uid, {}).get("name", uid); out += f"{i}- {name} ↢ {count} رسالة\n"
    return bot.reply_to(message, out)


@bot.message_handler(content_types=["text", "photo", "video", "sticker", "animation", "document", "voice", "audio", "contact", "video_note"])
def handler(message):
    register(message)
    if message.chat.type != "private" and not check_sub(message): return
    text = message.text or message.caption or ""
    violation = detect_violation(message, text)
    if violation: punish(message, violation); return
    if text in ["الاوامر", "الأوامر", "اوامر"]: return raw_send(message.chat.id, "- اختر قسم الاوامر", commands_kb())
    if text == "سورس": return raw_send(message.chat.id, SOURCE_NAME, {"inline_keyboard": [[red(SOURCE_NAME, url=f"https://t.me/{DEV_USERNAME}")]]})
    if text == "المطور": return bot.reply_to(message, f"https://t.me/{DEV_USERNAME}")
    if text.startswith("يوت ") or text.startswith("تشغيل "):
        query = text.replace("يوت ", "", 1).replace("تشغيل ", "", 1).strip()
        if not query: return bot.reply_to(message, "اكتب اسم الاغنية")
        wait = bot.reply_to(message, "🔎 جاري البحث...")
        try:
            file_path, title = download_audio(query)
            try: bot.delete_message(message.chat.id, wait.message_id)
            except Exception: pass
            send_audio_with_source(message.chat.id, file_path, title, message.message_id)
            try: os.remove(file_path)
            except Exception: pass
        except Exception as e: bot.reply_to(message, f"❌ صار خطأ:\n{e}")
        return
    if text.startswith("قفل ") or text.startswith("فتح "):
        if not is_admin_msg(message): return
        action = "قفل" if text.startswith("قفل ") else "فتح"; rest = text.replace(action + " ", "", 1).strip(); lock_action = "delete"
        for phrase, val in [("بالكتم", "mute"), ("بالطرد", "kick"), ("بالتقييد", "restrict")]:
            if phrase in rest: lock_action = val; rest = rest.replace(phrase, "").strip()
        key = LOCK_TYPES.get(rest)
        if not key: return bot.reply_to(message, "هذا القفل غير موجود")
        gid = sid(message.chat.id); data["locks"].setdefault(gid, {}); data["lock_actions"].setdefault(gid, {}); data["locks"][gid][key] = action == "قفل"; data["lock_actions"][gid][key] = lock_action; save_json(DATA_FILE, data)
        return bot.reply_to(message, "تم " + ("قفل " if action == "قفل" else "فتح ") + rest)
    if text == "نزلني":
        gid, uid = sid(message.chat.id), sid(message.from_user.id)
        if gid in data["ranks"] and uid in data["ranks"][gid]: data["ranks"][gid].pop(uid, None); save_json(DATA_FILE, data)
        return bot.reply_to(message, "تم تنزيلك من جميع الرتب")
    if text.startswith("رفع ") or text.startswith("تنزيل "):
        if not is_admin_msg(message): return
        u = target_user(message)
        if not u: return bot.reply_to(message, "رد على الشخص")
        act, rank = text.split(maxsplit=1); rank = rank.strip()
        if rank not in RANK_NAMES: return
        gid = sid(message.chat.id); data["ranks"].setdefault(gid, {})
        if act == "رفع": data["ranks"][gid][sid(u.id)] = rank; save_json(DATA_FILE, data); return bot.reply_to(message, f"تم رفعه {rank}")
        data["ranks"][gid].pop(sid(u.id), None); save_json(DATA_FILE, data); return bot.reply_to(message, "تم تنزيله")
    if text == "انذار":
        if not is_admin_msg(message): return
        u = target_user(message)
        if not u: return bot.reply_to(message, "رد على الشخص")
        gid, uid = sid(message.chat.id), sid(u.id); data["warns"].setdefault(gid, {}); data["warns"][gid][uid] = data["warns"][gid].get(uid, 0) + 1; save_json(DATA_FILE, data); return bot.reply_to(message, f"تم انذاره\nعدد انذاراته: {data['warns'][gid][uid]}")
    if text == "صلاحياتي":
        try:
            m = bot.get_chat_member(message.chat.id, message.from_user.id); attrs = [("حذف الرسائل", "can_delete_messages"), ("حظر المستخدمين", "can_restrict_members"), ("تقييد المستخدمين", "can_restrict_members"), ("تثبيت الرسائل", "can_pin_messages"), ("دعوة المستخدمين", "can_invite_users"), ("تغيير معلومات المجموعة", "can_change_info"), ("إضافة مشرفين", "can_promote_members"), ("إدارة المكالمات", "can_manage_video_chats")]
            perms = [f"- {name}: {'✓' if getattr(m, attr, False) else '✗'}" for name, attr in attrs]
            gid, uid = sid(message.chat.id), sid(message.from_user.id); txt = "• صلاحياتك:\n\n" + f"- الرتبة: {get_rank(message.chat.id, message.from_user.id)}\n" + "\n".join(perms) + f"\n\n- الرسائل: {data['messages'].get(gid, {}).get(uid, 0)}\n- النقاط: {data['points'].get(uid, 0)}\n- الانذارات: {data['warns'].get(gid, {}).get(uid, 0)}"
            return bot.reply_to(message, txt)
        except Exception: return bot.reply_to(message, "ما اكدر اجيب صلاحياتك")
    if text == "ترند": return list_top(message)
    if text == "تصفير الترند":
        if not is_admin_msg(message): return
        data["messages"][sid(message.chat.id)] = {}; save_json(DATA_FILE, data); return bot.reply_to(message, "تم تصفير الترند")
    if text in ["تعيين الايدي", "تغيير الايدي"]:
        if not is_admin_msg(message): return
        data["waiting"][sid(message.from_user.id)] = {"step": "set_id_template", "chat": sid(message.chat.id)}; save_json(DATA_FILE, data); return bot.reply_to(message, "ارسل كليشة الايدي الجديدة\n\nالمتغيرات:\n{name}\n{id}\n{rank}\n{messages}\n{points}")
    if sid(message.from_user.id) in data["waiting"]:
        w = data["waiting"].get(sid(message.from_user.id))
        if w.get("step") == "set_id_template": data["id_template"][w["chat"]] = text; data["waiting"].pop(sid(message.from_user.id), None); save_json(DATA_FILE, data); return bot.reply_to(message, "تم تعيين كليشة الايدي")
    if text == "ا": return show_id(message)
    if text == "قائمه المنع":
        arr = data["blocked_words"].get(sid(message.chat.id), []); return bot.reply_to(message, "\n".join(arr) if arr else "ماكو كلمات ممنوعة")
    if text.startswith("منع "):
        if not is_admin_msg(message): return
        word = text.replace("منع ", "", 1).strip(); data["blocked_words"].setdefault(sid(message.chat.id), [])
        if word not in data["blocked_words"][sid(message.chat.id)]: data["blocked_words"][sid(message.chat.id)].append(word)
        save_json(DATA_FILE, data); return bot.reply_to(message, "تم منع الكلمة")
    if text.startswith("الغاء منع "):
        if not is_admin_msg(message): return
        word = text.replace("الغاء منع ", "", 1).strip()
        try: data["blocked_words"][sid(message.chat.id)].remove(word)
        except Exception: pass
        save_json(DATA_FILE, data); return bot.reply_to(message, "تم الغاء المنع")
    for word in data["blocked_words"].get(sid(message.chat.id), []):
        if word and word in text and not is_admin_msg(message):
            try: bot.delete_message(message.chat.id, message.message_id)
            except Exception: pass
            return
    if text == "المكتومين":
        arr = data["muted"].get(sid(message.chat.id), []); return bot.reply_to(message, "\n".join(arr) if arr else "ماكو مكتومين")
    if text == "المقيدين":
        arr = data["restricted"].get(sid(message.chat.id), []); return bot.reply_to(message, "\n".join(arr) if arr else "ماكو مقيدين")
    if text == "المحظورين":
        arr = data["banned"].get(sid(message.chat.id), []); return bot.reply_to(message, "\n".join(arr) if arr else "ماكو محظورين")
    if text in ["مسح بالرد", "مسح"] and message.reply_to_message:
        if not is_admin_msg(message): return
        try: bot.delete_message(message.chat.id, message.reply_to_message.message_id); bot.delete_message(message.chat.id, message.message_id)
        except Exception: pass
        return
    if text.startswith("مسح ") and re.search(r"\d+", text):
        if not is_admin_msg(message): return
        count = min(int(re.findall(r"\d+", text)[0]), 100)
        for i in range(count + 1):
            try: bot.delete_message(message.chat.id, message.message_id - i)
            except Exception: pass
        return
    if text == "لغز": q = random.choice(PUZZLES); return add_quiz(message.chat.id, "لغز:\n" + q[0], q[1], q[2])
    if text == "عربي": q = random.choice(ARABIC_Q); return add_quiz(message.chat.id, "عربي:\n" + q[0], q[1], q[2])
    if text == "اعلام": q = random.choice(FLAGS); return add_quiz(message.chat.id, q[0], q[1], q[2])
    if text == "سيارات": q = random.choice(CARS); return add_quiz(message.chat.id, q[0], q[1], q[2])
    if text in ["مشاهير", "المشاهير"]: q = random.choice(FAMOUS); return add_quiz(message.chat.id, q[0], q[1], q[2])
    if text in ["كت", "كت تويت"]: return bot.reply_to(message, random.choice(KT))
    if text == "لو خيروك": return bot.reply_to(message, random.choice(WOULD))
    if text == "الاسرع":
        word = random.choice(FAST_WORDS); data["waiting_games"][sid(message.chat.id)] = {"fast": word}; save_json(DATA_FILE, data); return bot.reply_to(message, f"⚡ لعبة الاسرع\n\nاكتب:\n{word}")
    if sid(message.chat.id) in data["waiting_games"] and data["waiting_games"][sid(message.chat.id)].get("fast") == text:
        uid = sid(message.from_user.id); data["points"][uid] = data["points"].get(uid, 0) + 1; data["waiting_games"].pop(sid(message.chat.id), None); save_json(DATA_FILE, data); return bot.reply_to(message, f"✅ فزت بلعبة الاسرع\nنقاطك: {data['points'][uid]}")
    if text == "نقاطي": return bot.reply_to(message, f"نقاطك: {data['points'].get(sid(message.from_user.id), 0)}")
    if text.startswith("بيع نقاطي"):
        uid, gid = sid(message.from_user.id), sid(message.chat.id); pts = data["points"].get(uid, 0); nums = re.findall(r"\d+", text); amount = int(nums[0]) if nums else pts
        if amount <= 0 or pts < amount: return bot.reply_to(message, "نقاطك ما تكفي")
        data["points"][uid] -= amount; data["messages"].setdefault(gid, {}); data["messages"][gid][uid] = data["messages"][gid].get(uid, 0) + amount * 5; save_json(DATA_FILE, data); return bot.reply_to(message, f"تم بيع {amount} نقطة\nتمت إضافة {amount * 5} رسالة")

print("Created protection bot running...")
bot.infinity_polling(skip_pending=True)
