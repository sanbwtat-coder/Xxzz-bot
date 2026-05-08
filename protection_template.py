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
    "users": {},
    "groups": {},
    "locks": {},
    "ranks": {},
    "messages": {},
    "points": {},
    "bank": {},
    "muted": {},
    "banned": {},
    "waiting_games": {},
    "settings": {"id": True, "id_photo": True}
}

def load_json(path, default):
    if not os.path.exists(path):
        save_json(path, default.copy())
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
    except:
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
    return m.get("bots", {}).get(BOT_ID, {
        "plan": "free",
        "force_channel": OWNER_FORCE_CHANNEL
    })

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
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if reply_to:
        payload["reply_to_message_id"] = reply_to

    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json=payload,
            timeout=15
        )
    except:
        pass

def delete_after(chat_id, message_id, seconds=2):
    def run():
        time.sleep(seconds)
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass

    threading.Thread(target=run, daemon=True).start()

def start_kb():
    return {
        "inline_keyboard": [
            [blue("اضفني +", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
            [
                blue("المطور", url=f"https://t.me/{DEV_USERNAME}"),
                blue("الأوامر", "commands")
            ],
            [blue("حالة البوت: " + ("مدفوع" if is_paid() else "مجاني"), "status")],
            [red(SOURCE_NAME, url=f"https://t.me/{DEV_USERNAME}")]
        ]
    }

def commands_kb():
    return {
        "inline_keyboard": [
            [blue("• 1 •", "cmd_1"), blue("• 2 •", "cmd_2")],
            [blue("• 3 •", "cmd_3"), blue("• 4 •", "cmd_4")],
            [blue("• 5 •", "cmd_5"), blue("• 6 •", "cmd_6")],
            [red(SOURCE_NAME, url=f"https://t.me/{DEV_USERNAME}")]
        ]
    }

def back_kb():
    return {
        "inline_keyboard": [
            [blue("رجوع", "commands")],
            [red(SOURCE_NAME, url=f"https://t.me/{DEV_USERNAME}")]
        ]
    }

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
- منع / الغاء منع""",

"cmd_3": """- اوامر مسح المشرفين

- رد
- تاك
- امر
- بالرد
- الرابط
- رد عام
- الصوره
- الايدي
- المدراء
- التحذير
- الترحيب
- رد مميز
- المنشئين
- المالكين
- الادمنيه
- المميزين
- المقيدين
- رد متعدد
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

RANKS = {
    "عضو": 0,
    "مميز": 1,
    "ادمن": 2,
    "مشرف": 2,
    "مدير": 3,
    "منشئ": 4,
    "مالك": 5
}

def register(message):
    if message.from_user:
        uid = sid(message.from_user.id)

        data["users"].setdefault(uid, {
            "name": message.from_user.first_name or "",
            "username": message.from_user.username or ""
        })

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
    except:
        pass

    return rank_level(message.chat.id, message.from_user.id) >= 1

def is_subscribed(user_id):
    ch = force_channel()

    if not ch:
        return True

    try:
        m = bot.get_chat_member(ch, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return True

def check_sub(message):
    if message.from_user and not is_subscribed(message.from_user.id):
        ch = force_channel()

        raw_send(
            message.chat.id,
            "⚠️ لازم تشترك بالقناة أولاً",
            {
                "inline_keyboard": [
                    [blue("اشترك بالقناة", url="https://t.me/" + ch.replace("@", ""))]
                ]
            },
            message.message_id
        )

        return False

    return True

@bot.message_handler(content_types=["new_chat_members", "left_chat_member"])
def delete_join_leave(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

@bot.message_handler(commands=["start"])
def start(message):
    register(message)

    if not check_sub(message):
        return

    txt = (
        "• هلا بك في بوت حماية فادي\n\n"
        "• اضفني للكروب وارفعني مشرف\n\n"
        f"• حالة البوت: {'مدفوع' if is_paid() else 'مجاني'}\n"
        f"• الاشتراك الإجباري: {force_channel()}"
    )

    raw_send(message.chat.id, txt, start_kb())

@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    try:
        bot.answer_callback_query(call.id)
    except:
        pass

    if call.data == "commands":
        return raw_send(call.message.chat.id, "- اختر قسم الاوامر", commands_kb())

    if call.data in COMMANDS:
        return raw_send(call.message.chat.id, COMMANDS[call.data], back_kb())

    if call.data == "status":
        return raw_send(
            call.message.chat.id,
            f"• حالة البوت: {'مدفوع' if is_paid() else 'مجاني'}\n"
            f"• الاشتراك الإجباري: {force_channel()}"
        )

    if call.data.startswith("quiz_"):
        parts = call.data.split("_", 2)

        if len(parts) < 3:
            return

        game_id = parts[1]
        answer = parts[2]

        game = data.get("waiting_games", {}).get(game_id)

        if not game:
            wrong = bot.send_message(call.message.chat.id, "انتهت اللعبة")
            delete_after(call.message.chat.id, wrong.message_id, 2)
            return

        if answer == game["answer"]:
            uid = sid(call.from_user.id)
            data["points"][uid] = data["points"].get(uid, 0) + 1
            data["waiting_games"].pop(game_id, None)
            save_json(DATA_FILE, data)

            bot.send_message(
                call.message.chat.id,
                f"✅ إجابة صحيحة\nربحت نقطة\nنقاطك: {data['points'][uid]}"
            )
            return

        wrong = bot.send_message(call.message.chat.id, "❌ إجابة خاطئة")
        delete_after(call.message.chat.id, wrong.message_id, 2)
        return

def add_quiz(chat_id, question, choices, answer):
    game_id = str(int(time.time())) + str(random.randint(100, 999))
    data["waiting_games"][game_id] = {"answer": answer}
    save_json(DATA_FILE, data)

    kb = {"inline_keyboard": []}

    for c in choices[:3]:
        kb["inline_keyboard"].append([blue(c, f"quiz_{game_id}_{c}")])

    raw_send(chat_id, question, kb)

PUZZLES = [
    ("شنو عاصمة أستراليا؟", ["سيدني", "ملبورن", "كانبرا"], "كانبرا"),
    ("شي كلما أخذت منه كبر؟", ["الحفرة", "الماء", "البيت"], "الحفرة"),
    ("شي يمشي بلا رجلين؟", ["النهر", "الكتاب", "القلم"], "النهر"),
    ("ما هو الشيء الذي يسمع بلا أذن ويتكلم بلا لسان؟", ["الهاتف", "الصدى", "الراديو"], "الصدى"),
    ("شي إذا أكلته كله تستفيد وإذا أكلت نصفه تموت؟", ["سمسم", "تمر", "رمان"], "سمسم"),
]

ARABIC_Q = [
    ("جمع كلمة كتاب؟", ["كتب", "كتابات", "كاتب"], "كتب"),
    ("ضد كلمة طويل؟", ["قصير", "كبير", "قديم"], "قصير"),
    ("معنى الغيث؟", ["المطر", "الشمس", "الريح"], "المطر"),
]

FLAGS = [
    ("🇮🇶 شنو اسم هذا العلم؟", ["العراق", "مصر", "سوريا"], "العراق"),
    ("🇬🇷 شنو اسم هذا العلم؟", ["اليونان", "إيطاليا", "فرنسا"], "اليونان"),
    ("🇹🇷 شنو اسم هذا العلم؟", ["تركيا", "تونس", "المغرب"], "تركيا"),
]

CARS = [
    ("🚗 شنو اسم السيارة؟", ["تويوتا", "BMW", "KIA"], "تويوتا"),
    ("🚙 شنو اسم السيارة؟", ["مرسيدس", "نيسان", "هوندا"], "مرسيدس"),
]

FAMOUS = [
    ("👤 منو هذا المشهور؟", ["ميسي", "رونالدو", "نيمار"], "ميسي"),
    ("👤 منو هذا المشهور؟", ["فيروز", "ام كلثوم", "وردة"], "فيروز"),
]

KT = [
    "شنو أكثر شي تحبه؟",
    "شنو حلمك؟",
    "منو أقرب شخص الك؟",
    "شنو أكثر شي يضوجك؟",
    "شنو أكثر موقف محرج صار وياك؟"
]

WOULD = [
    "لو خيروك تعيش غني وحيد لو فقير ويا أصحاب؟",
    "لو خيروك ترجع للماضي لو تشوف المستقبل؟"
]

FAST_WORDS = ["تفاحة", "سيارة", "عراق", "قلم", "ماء", "كتاب", "ذهب"]

def source_markup_raw():
    return str({
        "inline_keyboard": [
            [
                {
                    "text": SOURCE_NAME,
                    "url": f"https://t.me/{DEV_USERNAME}",
                    "style": "danger"
                }
            ]
        ]
    }).replace("'", '"')

def download_audio(query):
    base_opts = {
        "format": "bestaudio[filesize<45M]/bestaudio/best",
        "outtmpl": f"{DOWNLOADS}/%(title)s.%(ext)s",
        "cookiefile": "cookies.txt",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 20,
        "retries": 4,
        "fragment_retries": 4,
        "concurrent_fragment_downloads": 5,
    }

    sources = [
        (f"ytsearch10:{query}", ["android"]),
        (f"ytsearch10:{query}", ["ios"]),
        (f"ytsearch10:{query}", ["web"]),
        (f"scsearch5:{query}", None),
    ]

    last_error = None

    for search, client in sources:
        try:
            opts = base_opts.copy()

            if client:
                opts["extractor_args"] = {
                    "youtube": {
                        "player_client": client
                    }
                }
            else:
                opts.pop("cookiefile", None)

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(search, download=True)

                if info and "entries" in info:
                    for item in info["entries"]:
                        if item:
                            info = item
                            break

                if not info:
                    continue

                title = clean_filename(info.get("title", "song"))
                file_path = ydl.prepare_filename(info)

                return file_path, title

        except Exception as e:
            last_error = e
            continue

    raise Exception(last_error)

def send_audio_with_source(chat_id, file_path, title, reply_to_message_id):
    with open(file_path, "rb") as audio:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendAudio",
            data={
                "chat_id": chat_id,
                "title": title,
                "performer": "Song fadi",
                "caption": f"🎧 {title}",
                "reply_to_message_id": reply_to_message_id,
                "reply_markup": source_markup_raw()
            },
            files={
                "audio": audio
            },
            timeout=120
        )

@bot.message_handler(content_types=["text", "photo", "video", "sticker", "animation", "document", "voice", "audio"])
def handler(message):
    register(message)

    if message.chat.type != "private" and not check_sub(message):
        return

    text = message.text or message.caption or ""

    if text in ["الاوامر", "الأوامر", "اوامر"]:
        return raw_send(message.chat.id, "- اختر قسم الاوامر", commands_kb())

    if text == "سورس":
        return raw_send(
            message.chat.id,
            SOURCE_NAME,
            {
                "inline_keyboard": [
                    [red(SOURCE_NAME, url=f"https://t.me/{DEV_USERNAME}")]
                ]
            }
        )

    if text == "المطور":
        return bot.reply_to(message, f"https://t.me/{DEV_USERNAME}")

    if text.startswith("يوت ") or text.startswith("تشغيل "):
        query = text.replace("يوت ", "", 1).replace("تشغيل ", "", 1).strip()

        if not query:
            return bot.reply_to(message, "اكتب اسم الاغنية")

        wait = bot.reply_to(message, "🔎 جاري البحث...")

        try:
            file_path, title = download_audio(query)

            try:
                bot.delete_message(message.chat.id, wait.message_id)
            except:
                pass

            send_audio_with_source(
                message.chat.id,
                file_path,
                title,
                message.message_id
            )

            try:
                os.remove(file_path)
            except:
                pass

        except Exception as e:
            bot.reply_to(message, f"❌ صار خطأ:\n{e}")

        return

    if text.startswith("قفل ") or text.startswith("فتح "):
        if not is_admin_msg(message):
            return

        name = text.split(maxsplit=1)[1].strip()
        gid = sid(message.chat.id)

        data["locks"].setdefault(gid, {})
        data["locks"][gid][name] = text.startswith("قفل ")

        save_json(DATA_FILE, data)

        return bot.reply_to(
            message,
            "تم " + ("قفل " if text.startswith("قفل ") else "فتح ") + name
        )

    if message.chat.type in ["group", "supergroup"] and not is_admin_msg(message):
        gid = sid(message.chat.id)
        locks = data["locks"].get(gid, {})

        content_map = {
            "الصور": "photo",
            "الملصقات": "sticker",
            "المتحركات": "animation",
            "الفيديو": "video",
            "الملفات": "document",
            "الصوت": "voice",
            "الاغاني": "audio"
        }

        for lname, ctype in content_map.items():
            if locks.get(lname) and message.content_type == ctype:
                try:
                    bot.delete_message(message.chat.id, message.message_id)
                except:
                    pass
                return

        if locks.get("الروابط") and re.search(r"(https?://|t\.me/|www\.)", text):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
            return

    if text == "ا":
        if not data["settings"].get("id", True):
            return

        uid, gid = sid(message.from_user.id), sid(message.chat.id)
        msgs = data["messages"].get(gid, {}).get(uid, 0)
        pts = data["points"].get(uid, 0)

        txt = (
            f"- الاسم: {message.from_user.first_name}\n"
            f"- الايدي: <code>{message.from_user.id}</code>\n"
            f"- الرتبة: {get_rank(message.chat.id, message.from_user.id)}\n"
            f"- الرسائل: {msgs}\n"
            f"- النقاط: {pts}"
        )

        return bot.reply_to(message, txt)

    if text == "لغز":
        q = random.choice(PUZZLES)
        return add_quiz(message.chat.id, "لغز:\n" + q[0], q[1], q[2])

    if text == "عربي":
        q = random.choice(ARABIC_Q)
        return add_quiz(message.chat.id, "عربي:\n" + q[0], q[1], q[2])

    if text == "اعلام":
        q = random.choice(FLAGS)
        return add_quiz(message.chat.id, q[0], q[1], q[2])

    if text == "سيارات":
        q = random.choice(CARS)
        return add_quiz(message.chat.id, q[0], q[1], q[2])

    if text in ["مشاهير", "المشاهير"]:
        q = random.choice(FAMOUS)
        return add_quiz(message.chat.id, q[0], q[1], q[2])

    if text in ["كت", "كت تويت"]:
        return bot.reply_to(message, random.choice(KT))

    if text == "لو خيروك":
        return bot.reply_to(message, random.choice(WOULD))

    if text == "الاسرع":
        word = random.choice(FAST_WORDS)
        data["waiting_games"][sid(message.chat.id)] = {"fast": word}
        save_json(DATA_FILE, data)

        return bot.reply_to(message, f"⚡ لعبة الاسرع\n\nاكتب:\n{word}")

    if sid(message.chat.id) in data["waiting_games"] and data["waiting_games"][sid(message.chat.id)].get("fast") == text:
        uid = sid(message.from_user.id)

        data["points"][uid] = data["points"].get(uid, 0) + 1
        data["waiting_games"].pop(sid(message.chat.id), None)

        save_json(DATA_FILE, data)

        return bot.reply_to(message, f"✅ فزت بلعبة الاسرع\nنقاطك: {data['points'][uid]}")

    if text == "نقاطي":
        return bot.reply_to(message, f"نقاطك: {data['points'].get(sid(message.from_user.id), 0)}")

    if text.startswith("بيع نقاطي"):
        uid, gid = sid(message.from_user.id), sid(message.chat.id)
        pts = data["points"].get(uid, 0)

        nums = re.findall(r"\d+", text)
        amount = int(nums[0]) if nums else pts

        if amount <= 0 or pts < amount:
            return bot.reply_to(message, "نقاطك ما تكفي")

        data["points"][uid] -= amount
        data["messages"].setdefault(gid, {})
        data["messages"][gid][uid] = data["messages"][gid].get(uid, 0) + amount * 5

        save_json(DATA_FILE, data)

        return bot.reply_to(
            message,
            f"تم بيع {amount} نقطة\nتمت إضافة {amount * 5} رسالة"
        )

print("Created protection bot running...")
bot.infinity_polling(skip_pending=True)
