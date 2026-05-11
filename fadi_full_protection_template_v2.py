# protection_template.py
# SOURCE FADI - Protection + Music Bot Template
# ارفع هذا الملف بدل protection_template.py القديم داخل مشروع الصانع

import os, re, json, time, random, threading, requests
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
    "users": {}, "groups": {}, "messages": {}, "points": {}, "money": {}, "bank_accounts": {},
    "robbers": {}, "cooldowns": {}, "locks": {}, "lock_actions": {}, "ranks": {}, "warns": {},
    "muted": {}, "restricted": {}, "banned": {}, "kicked": {}, "blocked_words": {}, "replies": {},
    "tags": {}, "titles": {}, "marriages": {}, "waiting": {}, "waiting_games": {}, "fast_games": {},
    "id_template": {}, "links": {}, "media_messages": {},
    "settings": {"id": True, "id_photo": True, "welcome": False}
}

LOCK_TYPES = {
    "التاك":"tag","القنوات":"channels","الصور":"photo","الروابط":"links","الرابط":"links",
    "الفشار":"bad_words","التكرار":"spam","الفيديو":"video","الدخول":"join","الاضافه":"add",
    "الإضافه":"add","الاغاني":"audio","الأغاني":"audio","الصوت":"voice","الملفات":"document",
    "التفليش":"flood","الدردشه":"chat","الدردشة":"chat","الجهات":"contact","السيلفي":"video_note",
    "التثبيت":"pin","الشارحه":"long","الشارحة":"long","الكلايش":"long","البوتات":"bots",
    "التوجيه":"forward","التعديل":"edit","المعرفات":"username","المعرف":"username","الكيبورد":"keyboard",
    "الفارسيه":"persian","الفارسية":"persian","الانكليزيه":"english","الانكليزي":"english",
    "الانجليزي":"english","الملصقات":"sticker","الاشعارات":"service","الإشعارات":"service",
    "الماركداون":"markdown","المتحركه":"animation","المتحركة":"animation"
}
RANK_LEVEL = {"عضو":0,"مميز":1,"ادمن":2,"مشرف":2,"مدير":3,"منشئ":4,"منشئ اساسي":5,"منشئ أساسي":5,"مالك":6}
RANK_NAMES = ["مميز","ادمن","مشرف","مدير","منشئ","منشئ اساسي","منشئ أساسي","مالك"]
BAD_WORDS = ["كس","زب","عير","قحبة","كواد","خرا","نياكة"]
EN_RE = re.compile(r"[A-Za-z]")
PERSIAN_RE = re.compile(r"[پچژگ]")
URL_RE = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/)", re.I)

MOVIES = [
    ("Interstellar","خيال علمي / دراما","2014","رحلة عبر الفضاء بحثًا عن كوكب صالح للبشرية."),
    ("The Dark Knight","أكشن / جريمة","2008","باتمان يواجه الجوكر في صراع فوضوي داخل غوثام."),
    ("Joker","دراما / نفسي","2019","تحول رجل مهمش إلى شخصية الجوكر الشهيرة."),
    ("Inception","خيال علمي / إثارة","2010","سرقة الأفكار داخل الأحلام بطبقات معقدة."),
    ("Parasite","دراما / إثارة","2019","عائلتان من طبقتين مختلفتين تتقاطع حياتهما بشكل خطير.")
]
QURAN = [
    ("سورة الفاتحة","عبد الباسط عبد الصمد","https://server7.mp3quran.net/basit/001.mp3"),
    ("سورة الإخلاص","عبد الباسط عبد الصمد","https://server7.mp3quran.net/basit/112.mp3"),
    ("سورة الفلق","عبد الباسط عبد الصمد","https://server7.mp3quran.net/basit/113.mp3"),
    ("سورة الناس","عبد الباسط عبد الصمد","https://server7.mp3quran.net/basit/114.mp3")
]
CHANTS = [("ترتيلة بيزنطية","ضع رابط MP3 هنا"),("ترتيلة أرثوذكسية عربية","ضع رابط MP3 هنا"),("Catholic Chant","ضع رابط MP3 هنا")]
PUZZLES = [("شنو عاصمة أستراليا؟",["سيدني","ملبورن","كانبرا"],"كانبرا"),("شي كلما أخذت منه كبر؟",["الحفرة","الماء","البيت"],"الحفرة"),("شي يمشي بلا رجلين؟",["النهر","الكتاب","القلم"],"النهر"),("ما هو الشيء الذي يسمع بلا أذن ويتكلم بلا لسان؟",["الهاتف","الصدى","الراديو"],"الصدى")]
ARABIC_Q = [("جمع كلمة كتاب؟",["كتب","كتابات","كاتب"],"كتب"),("ضد كلمة طويل؟",["قصير","كبير","قديم"],"قصير"),("معنى الغيث؟",["المطر","الشمس","الريح"],"المطر")]
FLAGS = [("🇮🇶 شنو اسم هذا العلم؟",["العراق","مصر","سوريا"],"العراق"),("🇬🇷 شنو اسم هذا العلم؟",["اليونان","إيطاليا","فرنسا"],"اليونان"),("🇹🇷 شنو اسم هذا العلم؟",["تركيا","تونس","المغرب"],"تركيا")]
CARS = [("🚗 شنو اسم السيارة؟",["تويوتا","BMW","KIA"],"تويوتا"),("🚙 شنو اسم السيارة؟",["مرسيدس","نيسان","هوندا"],"مرسيدس")]
FAMOUS = [("👤 منو هذا المشهور؟",["ميسي","رونالدو","نيمار"],"ميسي"),("👤 منو هذا المشهور؟",["فيروز","ام كلثوم","وردة"],"فيروز")]
KT = ["شنو أكثر شي تحبه؟","شنو حلمك؟","منو أقرب شخص الك؟","شنو أكثر شي يضوجك؟"]
WOULD = ["لو خيروك تعيش غني وحيد لو فقير ويا أصحاب؟","لو خيروك ترجع للماضي لو تشوف المستقبل؟"]
FAST_WORDS = ["تفاحة","سيارة","عراق","قلم","ماء","كتاب","ذهب"]

def load_json(path, default):
    if not os.path.exists(path): save_json(path, default.copy())
    try:
        with open(path,"r",encoding="utf-8") as f: d=json.load(f)
    except Exception: d=default.copy()
    for k,v in default.items(): d.setdefault(k,v)
    return d

def save_json(path, d):
    with open(path,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)

data = load_json(DATA_FILE, DEFAULT)
def sid(x): return str(x)
def maker_data(): return load_json(MAKER_DATA_FILE, {"bots": {}})
def bot_info(): return maker_data().get("bots",{}).get(BOT_ID, {"plan":"free","force_channel":OWNER_FORCE_CHANNEL,"owner_id":OWNER_ID})
def is_paid(): return bot_info().get("plan") == "paid"
def force_channel():
    info=bot_info()
    return (info.get("force_channel") or OWNER_FORCE_CHANNEL) if info.get("plan")=="paid" else OWNER_FORCE_CHANNEL
def owner_id(): return int(bot_info().get("owner_id") or OWNER_ID)
def blue(text, callback_data=None, url=None):
    b={"text":text,"style":"primary"}
    if callback_data: b["callback_data"]=callback_data
    if url: b["url"]=url
    return b
def red(text, callback_data=None, url=None):
    b={"text":text,"style":"danger"}
    if callback_data: b["callback_data"]=callback_data
    if url: b["url"]=url
    return b

def raw_send(chat_id, text, reply_markup=None, reply_to=None):
    payload={"chat_id":chat_id,"text":text,"parse_mode":"HTML"}
    if reply_markup: payload["reply_markup"]=reply_markup
    if reply_to: payload["reply_to_message_id"]=reply_to
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json=payload,timeout=15)
    except Exception: pass

def raw_edit(chat_id, message_id, text, reply_markup=None):
    payload={"chat_id":chat_id,"message_id":message_id,"text":text,"parse_mode":"HTML"}
    if reply_markup: payload["reply_markup"]=reply_markup
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/editMessageText",json=payload,timeout=15)
    except Exception: pass

def delete_after(chat_id, message_id, seconds=2):
    def run():
        time.sleep(seconds)
        try: bot.delete_message(chat_id,message_id)
        except Exception: pass
    threading.Thread(target=run,daemon=True).start()

def clean_filename(name): return re.sub(r'[\\/*?:"<>|]',"",name)[:90]
def source_markup_raw():
    return str({"inline_keyboard":[[{"text":SOURCE_NAME,"url":f"https://t.me/{DEV_USERNAME}","style":"danger"}]]}).replace("'",'"')

def start_kb():
    return {"inline_keyboard":[[blue("اضفني +",url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],[blue("المطور",url=f"https://t.me/{DEV_USERNAME}"), blue("الأوامر","commands")],[blue("حالة البوت: " + ("مدفوع" if is_paid() else "مجاني"),"status")],[red(SOURCE_NAME,url=f"https://t.me/{DEV_USERNAME}")]]}

def commands_text():
    return """الاوامر

- اليك اوامر البوت

- [ 1م ] اوامر الحمايه
- [ 2م ] اوامر المشرفين
- [ 3م ] اوامر المسح
- [ 4م ] اوامر الرفع والحظر
- [ 5م ] اوامر الترفيه
- [ 6م ] اوامر الالعاب"""

def commands_kb():
    return {"inline_keyboard":[[blue("• 1 •","cmd_1"),blue("• 2 •","cmd_2")],[blue("• 3 •","cmd_3"),blue("• 4 •","cmd_4")],[blue("• 5 •","cmd_5"),blue("• 6 •","cmd_6")],[red(SOURCE_NAME,url=f"https://t.me/{DEV_USERNAME}")]]}

def back_kb(): return {"inline_keyboard":[[blue("رجوع","commands")],[red(SOURCE_NAME,url=f"https://t.me/{DEV_USERNAME}")]]}

COMMANDS = {
"cmd_1": "• اوامر القفل والفتح\n\n• بالكتم • بالطرد • بالتقييد\n\n- التاك\n- القنوات\n- الصور\n- الروابط\n- الفشار\n- التكرار\n- الفيديو\n- الدخول\n- الاضافه\n- الاغاني\n- الصوت\n- الملفات\n- التفليش\n- الدردشه\n- الجهات\n- السيلفي\n- التثبيت\n- الشارحه\n- الكلايش\n- البوتات\n- التوجيه\n- التعديل\n- المعرفات\n- الكيبورد\n- الفارسيه\n- الانكليزيه\n- الملصقات\n- الاشعارات\n- الماركداون\n- المتحركه",
"cmd_2": "- اوامر مشرفين المجموعة\n\n- القوائم\n- الميديا\n- نزلني\n- انذار\n- تثبيت\n- ت\n- الاعدادات\n- التفعيلات\n- صلاحياتي\n- تصفير الترند\n- ضبط الحمايه\n- اضف رد\n- حذف رد\n- الردود\n- اضف امر\n- تاك للكل\n- تاك للمشرفين\n- ضع رابط\n- ضع تحذير\n- ضع وصف\n- ضع صوره\n- ضع اسم\n- ضع ترحيب\n- منع / الغاء منع\n- تعيين الايدي\n- تغيير الايدي\n- اضف لقب\n- اضف نقاط\n- اضف تاك",
"cmd_3": "- اوامر مسح المشرفين\n\n- مسح رد\n- مسح تاك\n- مسح امر\n- مسح بالرد\n- مسح الرابط\n- مسح الصوره\n- مسح الايدي\n- مسح الترحيب\n- مسح المدراء\n- مسح المنشئين\n- مسح المالكين\n- مسح الادمنيه\n- مسح المميزين\n- المقيدين\n- المكتومين\n- قائمه المنع\n- المطرودين\n- المحظورين\n- تنظيف روابط\n- تنظيف ميديا\n- تنظيف الصور\n- تنظيف الملصقات\n- تنظيف الفيديوهات\n- تنظيف المتحركات\n- مسح + العدد",
"cmd_4": "- اوامر الرفع والحظر\n\n- طرد\n- تحكم\n- تنزيل الكل\n- رفع القيود\n- كشف القيود\n- كتم / الغاء كتم\n- حظر / الغاء حظر\n- تقييد / الغاء تقييد\n- رفع / تنزيل منشئ\n- رفع / تنزيل مدير\n- رفع / تنزيل ادمن\n- رفع / تنزيل مميز\n- رفع / تنزيل مشرف\n- م\n- اد\n- كشف",
"cmd_5": "- اوامر ترفيه الاعضاء\n\n- نداء\n- جمالي\n- زوجني\n- ز\n- ط\n- زوجتي\n- زوجي\n- زواج\n- ثنائي اليوم\n- نسبة الحب\n- نسبة الكره\n- نسبة الرجوله\n- نسبة الانوثه\n- نسبة الجمال\n- غنيلي\n- صوره\n- اغنيه\n- متحركه\n- ميمز\n- ريمكس\n- شعر\n- قصيده\n- فلم\n- مسلسل\n- افلام\n- طقس\n- قران\n- تراتيل\n- بوسه\n- بوسها\n- همسه",
"cmd_6": "- الالعاب\n\n- لغز\n- XO\n- سيارات\n- اعلام\n- مشاهير\n- عربي\n- كت\n- حجرة\n- الاسرع\n- لو خيروك\n- نقاطي\n- بيع نقاطي"
}
BOT_COMMANDS = {"ا","ايدي","الاوامر","الأوامر","اوامر","سورس","المطور","نقاطي","لغز","عربي","اعلام","سيارات","مشاهير","المشاهير","كت","كت تويت","لو خيروك","الاسرع","غنيلي","قران","تراتيل","افلام","ترند","ر","فلوسي","حسابي","راتب","بخشيش"}
def needs_sub(text): return text in BOT_COMMANDS or text.startswith("يوت ") or text.startswith("تشغيل ") or text.startswith("طقس") or text.startswith("بيع نقاطي")

def register(message):
    if not message.from_user: return
    uid=sid(message.from_user.id)
    data["users"].setdefault(uid,{"name":message.from_user.first_name or "","username":message.from_user.username or ""})
    if message.chat.type in ["group","supergroup"]:
        gid=sid(message.chat.id); data["groups"].setdefault(gid,{"title":message.chat.title or ""}); data["messages"].setdefault(gid,{})
        data["messages"][gid][uid]=data["messages"][gid].get(uid,0)+1
    save_json(DATA_FILE,data)

def get_rank(chat_id,user_id):
    if user_id == OWNER_ID or user_id == owner_id(): return "مالك"
    return data["ranks"].get(sid(chat_id),{}).get(sid(user_id),"عضو")
def rank_level(chat_id,user_id): return RANK_LEVEL.get(get_rank(chat_id,user_id),0)
def is_group_admin(chat_id,user_id):
    if user_id in [OWNER_ID, owner_id()]: return True
    try:
        m=bot.get_chat_member(chat_id,user_id); return m.status in ["administrator","creator"]
    except Exception: return False
def is_admin_msg(message): return bool(message.from_user and (is_group_admin(message.chat.id,message.from_user.id) or rank_level(message.chat.id,message.from_user.id)>=1))
def is_creator_basic(message): return bool(message.from_user and (is_group_admin(message.chat.id,message.from_user.id) or rank_level(message.chat.id,message.from_user.id)>=5))
def target_user(message): return message.reply_to_message.from_user if message.reply_to_message and message.reply_to_message.from_user else None
def display_user(uid):
    info=data["users"].get(sid(uid),{})
    return "@"+info["username"] if info.get("username") else (info.get("name") or str(uid))

def bank(uid):
    uid=sid(uid); data["money"].setdefault(uid,1000); data["bank_accounts"].setdefault(uid,random.randint(100000,999999)); return data["money"][uid]
def save_bank(uid, amount): data["money"][sid(uid)]=amount; save_json(DATA_FILE,data)
def cooldown(uid,key,seconds):
    uid=sid(uid); now=int(time.time()); data["cooldowns"].setdefault(uid,{})
    last=data["cooldowns"][uid].get(key,0)
    if now-last<seconds: return False, seconds-(now-last)
    data["cooldowns"][uid][key]=now; save_json(DATA_FILE,data); return True,0

def is_subscribed(user_id):
    ch=force_channel()
    if not ch: return True
    try:
        m=bot.get_chat_member(ch,user_id); return m.status in ["member","administrator","creator"]
    except Exception: return True

def check_sub(message):
    if message.from_user and not is_subscribed(message.from_user.id):
        ch=force_channel()
        raw_send(message.chat.id,"⚠️ لازم تشترك بالقناة أولاً",{"inline_keyboard":[[blue("اشترك بالقناة",url="https://t.me/"+ch.replace("@",""))]]},message.message_id)
        return False
    return True

def save_media(message):
    if message.chat.type not in ["group","supergroup"] or message.content_type not in ["photo","video","sticker","animation"]: return
    gid=sid(message.chat.id); data["media_messages"].setdefault(gid,[])
    data["media_messages"][gid].append({"id":message.message_id,"type":message.content_type}); data["media_messages"][gid]=data["media_messages"][gid][-1000:]; save_json(DATA_FILE,data)

def notify_added(message):
    try:
        link="لا يوجد"
        try: link=bot.export_chat_invite_link(message.chat.id)
        except Exception: pass
        count="غير معروف"
        try: count=bot.get_chat_member_count(message.chat.id)
        except Exception: pass
        by=f"@{message.from_user.username}" if message.from_user and message.from_user.username else (message.from_user.first_name if message.from_user else "غير معروف")
        txt=f"🔔 تم إضافة البوت إلى كروب\n\n• اسم الكروب: {message.chat.title}\n• ايدي الكروب: <code>{message.chat.id}</code>\n• رابط الكروب: {link}\n• عدد الأعضاء: {count}\n• بواسطة: {by}"
        raw_send(owner_id(),txt)
        if OWNER_ID != owner_id(): raw_send(OWNER_ID,txt)
    except Exception: pass

def punish(message, lock_key):
    gid=sid(message.chat.id); action=data["lock_actions"].get(gid,{}).get(lock_key,"delete")
    try: bot.delete_message(message.chat.id,message.message_id)
    except Exception: pass
    if action=="mute":
        try:
            bot.restrict_chat_member(message.chat.id,message.from_user.id,can_send_messages=False); data["muted"].setdefault(gid,[])
            if sid(message.from_user.id) not in data["muted"][gid]: data["muted"][gid].append(sid(message.from_user.id))
            save_json(DATA_FILE,data)
        except Exception: pass
    elif action=="kick":
        try:
            bot.ban_chat_member(message.chat.id,message.from_user.id); bot.unban_chat_member(message.chat.id,message.from_user.id)
            data["kicked"].setdefault(gid,[]); data["kicked"][gid].append(sid(message.from_user.id)); save_json(DATA_FILE,data)
        except Exception: pass
    elif action=="restrict":
        try:
            bot.restrict_chat_member(message.chat.id,message.from_user.id,can_send_messages=False,until_date=int(time.time())+3600); data["restricted"].setdefault(gid,[])
            if sid(message.from_user.id) not in data["restricted"][gid]: data["restricted"][gid].append(sid(message.from_user.id))
            save_json(DATA_FILE,data)
        except Exception: pass

def is_lock(chat_id,key): return data["locks"].get(sid(chat_id),{}).get(key,False)
def detect_violation(message,text):
    if message.chat.type not in ["group","supergroup"] or not message.from_user or is_admin_msg(message): return None
    if is_lock(message.chat.id,"chat"): return "chat"
    cmap={"photo":"photo","video":"video","sticker":"sticker","animation":"animation","document":"document","voice":"voice","audio":"audio","contact":"contact","video_note":"video_note"}
    key=cmap.get(message.content_type)
    if key and is_lock(message.chat.id,key): return key
    if is_lock(message.chat.id,"links") and URL_RE.search(text): return "links"
    if is_lock(message.chat.id,"channels") and ("t.me/" in text or "@" in text): return "channels"
    if is_lock(message.chat.id,"tag") and "@" in text: return "tag"
    if is_lock(message.chat.id,"username") and "@" in text: return "username"
    if is_lock(message.chat.id,"english") and EN_RE.search(text): return "english"
    if is_lock(message.chat.id,"persian") and PERSIAN_RE.search(text): return "persian"
    if is_lock(message.chat.id,"bad_words") and any(w in text.lower() for w in BAD_WORDS): return "bad_words"
    if is_lock(message.chat.id,"long") and len(text)>350: return "long"
    if is_lock(message.chat.id,"markdown") and any(x in text for x in ["[","](","`","*","__"]): return "markdown"
    if is_lock(message.chat.id,"forward") and getattr(message,"forward_date",None): return "forward"
    return None

def download_audio(query):
    base_opts={"format":"bestaudio[filesize<45M]/bestaudio/best","outtmpl":f"{DOWNLOADS}/%(title)s.%(ext)s","cookiefile":"cookies.txt","noplaylist":True,"quiet":True,"no_warnings":True,"socket_timeout":20,"retries":4,"fragment_retries":4,"concurrent_fragment_downloads":5}
    sources=[(f"ytsearch10:{query}",["android"]),(f"ytsearch10:{query}",["ios"]),(f"ytsearch10:{query}",["web"]),(f"scsearch5:{query}",None)]
    last_error=None
    for search,client in sources:
        try:
            opts=base_opts.copy()
            if client: opts["extractor_args"]={"youtube":{"player_client":client}}
            else: opts.pop("cookiefile",None)
            with yt_dlp.YoutubeDL(opts) as ydl:
                info=ydl.extract_info(search,download=True)
                if info and "entries" in info:
                    for item in info["entries"]:
                        if item: info=item; break
                if not info: continue
                title=clean_filename(info.get("title","song")); file_path=ydl.prepare_filename(info); return file_path,title
        except Exception as e: last_error=e
    raise Exception(last_error)

def send_audio_with_source(chat_id,file_path,title,reply_to_message_id):
    with open(file_path,"rb") as audio:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendAudio",data={"chat_id":chat_id,"title":title,"performer":"Song fadi","caption":f"🎧 {title}","reply_to_message_id":reply_to_message_id,"reply_markup":source_markup_raw()},files={"audio":audio},timeout=120)

def add_quiz(chat_id,question,choices,answer):
    game_id=str(int(time.time()))+str(random.randint(100,999)); data["waiting_games"][game_id]={"answer":answer}; save_json(DATA_FILE,data)
    kb={"inline_keyboard":[]}
    for c in choices[:3]: kb["inline_keyboard"].append([blue(c,f"quiz_{game_id}_{c}")])
    raw_send(chat_id,question,kb)

def show_id(message):
    if not data["settings"].get("id",True): return
    uid,gid=sid(message.from_user.id),sid(message.chat.id); msgs=data["messages"].get(gid,{}).get(uid,0); pts=data["points"].get(uid,0); rank=get_rank(message.chat.id,message.from_user.id); title=data["titles"].get(gid,{}).get(uid,"لا يوجد")
    template=data["id_template"].get(gid) or "- الاسم: {name}\n- الايدي: {id}\n- الرتبة: {rank}\n- اللقب: {title}\n- الرسائل: {messages}\n- النقاط: {points}"
    txt=template.format(name=message.from_user.first_name,id=message.from_user.id,rank=rank,title=title,messages=msgs,points=pts)
    if data["settings"].get("id_photo",True):
        try:
            photos=bot.get_user_profile_photos(message.from_user.id,limit=1)
            if photos.total_count>0: return bot.send_photo(message.chat.id,photos.photos[0][-1].file_id,caption=txt,reply_to_message_id=message.message_id)
        except Exception: pass
    return bot.reply_to(message,txt)

def list_top(message):
    gid=sid(message.chat.id); items=sorted(data["messages"].get(gid,{}).items(),key=lambda x:x[1],reverse=True)[:10]
    if not items: return bot.reply_to(message,"ماكو تفاعل بعد")
    out="- ترند المجموعة\n\n"
    for i,(uid,count) in enumerate(items,1): out+=f"{i}- {display_user(uid)} ↢ {count} رسالة\n"
    return bot.reply_to(message,out)

def tag_users(message,only_admins=False):
    gid=sid(message.chat.id); ids=list(data["messages"].get(gid,{}).keys())
    if only_admins: ids=[uid for uid in ids if rank_level(message.chat.id,int(uid))>=1 or is_group_admin(message.chat.id,int(uid))]
    if not ids: return bot.reply_to(message,"ماكو أعضاء مخزنين")
    chunk=""
    for uid in ids[:80]:
        chunk += f"<a href='tg://user?id={uid}'>.</a> "
        if len(chunk)>3500: bot.send_message(message.chat.id,chunk); chunk=""
    if chunk: bot.send_message(message.chat.id,chunk)

def clean_media(message,types):
    if not is_creator_basic(message): return
    gid=sid(message.chat.id); saved=data["media_messages"].get(gid,[]); deleted=0; keep=[]
    for item in saved:
        if item["type"] in types:
            try: bot.delete_message(message.chat.id,item["id"]); deleted+=1
            except Exception: pass
        else: keep.append(item)
    data["media_messages"][gid]=keep; save_json(DATA_FILE,data); bot.reply_to(message,f"تم تنظيف {deleted} رسالة")

def handle_waiting(message,text):
    uid=sid(message.from_user.id); w=data["waiting"].get(uid)
    if not w: return False
    step=w.get("step"); gid=w.get("chat",sid(message.chat.id))
    if step=="set_id_template": data["id_template"][gid]=text; data["waiting"].pop(uid,None); save_json(DATA_FILE,data); bot.reply_to(message,"تم تعيين كليشة الايدي"); return True
    if step=="add_reply_word": data["waiting"][uid]={"step":"add_reply_answer","chat":gid,"word":text}; save_json(DATA_FILE,data); bot.reply_to(message,"ارسل الرد"); return True
    if step=="add_reply_answer": data["replies"].setdefault(gid,{}); data["replies"][gid][w["word"]]=text; data["waiting"].pop(uid,None); save_json(DATA_FILE,data); bot.reply_to(message,"تم إضافة الرد"); return True
    if step=="del_reply": data["replies"].setdefault(gid,{}); data["replies"][gid].pop(text,None); data["waiting"].pop(uid,None); save_json(DATA_FILE,data); bot.reply_to(message,"تم حذف الرد"); return True
    if step=="add_tag_name": data["waiting"][uid]={"step":"add_tag_user","chat":gid,"name":text}; save_json(DATA_FILE,data); bot.reply_to(message,"ارسل اليوزر"); return True
    if step=="add_tag_user": data["tags"].setdefault(gid,{}); data["tags"][gid][w["name"]]=text; data["waiting"].pop(uid,None); save_json(DATA_FILE,data); bot.reply_to(message,"تم إضافة التاك"); return True
    if step=="whisper_text":
        whisper_id=str(int(time.time()))+str(random.randint(100,999)); data["waiting_games"][whisper_id]={"type":"whisper","from":message.from_user.id,"to":w["to"],"text":text}
        data["waiting"].pop(uid,None); save_json(DATA_FILE,data); kb={"inline_keyboard":[[blue("رؤية الهمسة",f"whisper_{whisper_id}")]]}
        raw_send(w["chat"], f"• الهمسه لـ {display_user(w['to'])}\n• من ← {message.from_user.first_name}", kb); bot.reply_to(message,"تم إرسال الهمسة بالكروب"); return True
    return False

@bot.message_handler(content_types=["new_chat_members","left_chat_member"])
def delete_join_leave(message):
    try: bot.delete_message(message.chat.id,message.message_id)
    except Exception: pass
    if message.content_type=="new_chat_members":
        for u in message.new_chat_members:
            try:
                if u.id == bot.get_me().id: notify_added(message)
                if u.is_bot and is_lock(message.chat.id,"bots"):
                    bot.ban_chat_member(message.chat.id,u.id); bot.unban_chat_member(message.chat.id,u.id)
            except Exception: pass

@bot.message_handler(commands=["start"])
def start(message):
    register(message); uid=sid(message.from_user.id)
    if uid in data["waiting"] and data["waiting"][uid].get("step")=="whisper_text":
        return bot.send_message(message.chat.id,"اكتب الهمسة هنا بالخاص، وسيتم إرسالها بالكروب.")
    if not check_sub(message): return
    raw_send(message.chat.id,"• هلا بك في بوت حماية فادي\n\n• اضفني للكروب وارفعني مشرف\n\n• اكتب:\nالاوامر\nيوت اسم الاغنية",start_kb())

@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    try: bot.answer_callback_query(call.id)
    except Exception: pass
    if call.data=="noop": return
    if call.data=="commands": return raw_edit(call.message.chat.id,call.message.message_id,commands_text(),commands_kb())
    if call.data in COMMANDS: return raw_edit(call.message.chat.id,call.message.message_id,COMMANDS[call.data],back_kb())
    if call.data=="status": return raw_send(call.message.chat.id,f"• حالة البوت: {'مدفوع' if is_paid() else 'مجاني'}\n• الاشتراك الإجباري: {force_channel()}")
    if call.data.startswith("quiz_"):
        parts=call.data.split("_",2)
        if len(parts)<3: return
        game_id,answer=parts[1],parts[2]; game=data.get("waiting_games",{}).get(game_id)
        if not game:
            msg=bot.send_message(call.message.chat.id,"انتهت اللعبة"); delete_after(call.message.chat.id,msg.message_id,2); return
        if answer==game["answer"]:
            uid=sid(call.from_user.id); data["points"][uid]=data["points"].get(uid,0)+1; data["waiting_games"].pop(game_id,None); save_json(DATA_FILE,data)
            return bot.send_message(call.message.chat.id,f"✅ إجابة صحيحة\nربحت نقطة\nنقاطك: {data['points'][uid]}")
        msg=bot.send_message(call.message.chat.id,"❌ إجابة خاطئة"); delete_after(call.message.chat.id,msg.message_id,2); return
    if call.data.startswith("whisper_"):
        wid=call.data.replace("whisper_",""); w=data.get("waiting_games",{}).get(wid)
        if not w or w.get("type")!="whisper": return bot.answer_callback_query(call.id,"• الهمسة غير موجودة",show_alert=True)
        if call.from_user.id != w["to"]: return bot.answer_callback_query(call.id,"• الهمسة لا تخصك",show_alert=True)
        return bot.answer_callback_query(call.id,w["text"],show_alert=True)

@bot.message_handler(content_types=["text","photo","video","sticker","animation","document","voice","audio","contact","video_note"])
def handler(message):
    register(message); save_media(message); text=message.text or message.caption or ""
    if message.chat.type=="private" and handle_waiting(message,text): return
    if message.chat.type!="private" and needs_sub(text) and not check_sub(message): return
    if message.chat.type!="private" and handle_waiting(message,text): return
    violation=detect_violation(message,text)
    if violation: punish(message,violation); return
    gid=sid(message.chat.id)

    if text in data["replies"].get(gid,{}): return bot.reply_to(message,data["replies"][gid][text])
    if text in data["tags"].get(gid,{}): return bot.reply_to(message,data["tags"][gid][text])

    if text in ["الاوامر","الأوامر","اوامر"]: return raw_send(message.chat.id,commands_text(),commands_kb())
    if text=="سورس": return raw_send(message.chat.id,"• سورس فادي",{"inline_keyboard":[[red(SOURCE_NAME,url=f"https://t.me/{DEV_USERNAME}")]]})
    if text=="المطور": return raw_send(message.chat.id,"• حساب المطور",{"inline_keyboard":[[blue("المطور",url=f"https://t.me/{DEV_USERNAME}")]]})

    if text.startswith("يوت ") or text.startswith("تشغيل "):
        query=text.replace("يوت ","",1).replace("تشغيل ","",1).strip()
        if not query: return bot.reply_to(message,"اكتب اسم الاغنية")
        wait=bot.reply_to(message,"🔎 جاري البحث...")
        try:
            file_path,title=download_audio(query)
            try: bot.delete_message(message.chat.id,wait.message_id)
            except Exception: pass
            send_audio_with_source(message.chat.id,file_path,title,message.message_id)
            try: os.remove(file_path)
            except Exception: pass
        except Exception as e: bot.reply_to(message,f"❌ صار خطأ:\n{e}")
        return

    if text.startswith("قفل ") or text.startswith("فتح "):
        if not is_admin_msg(message): return
        action="قفل" if text.startswith("قفل ") else "فتح"; rest=text.replace(action+" ","",1).strip(); lock_action="delete"
        if "بالكتم" in rest: lock_action="mute"; rest=rest.replace("بالكتم","").strip()
        elif "بالطرد" in rest: lock_action="kick"; rest=rest.replace("بالطرد","").strip()
        elif "بالتقييد" in rest: lock_action="restrict"; rest=rest.replace("بالتقييد","").strip()
        key=LOCK_TYPES.get(rest)
        if not key: return bot.reply_to(message,"هذا القفل غير موجود")
        data["locks"].setdefault(gid,{}); data["lock_actions"].setdefault(gid,{})
        data["locks"][gid][key]=action=="قفل"; data["lock_actions"][gid][key]=lock_action; save_json(DATA_FILE,data)
        return bot.reply_to(message,"تم "+("قفل " if action=="قفل" else "فتح ")+rest)

    if text in ["تثبيت","ت"]:
        if not is_admin_msg(message) or not message.reply_to_message: return
        try: bot.pin_chat_message(message.chat.id,message.reply_to_message.message_id); return bot.reply_to(message,"تم تثبيت الرسالة")
        except Exception: return bot.reply_to(message,"ما اكدر اثبت")
    if text=="الغاء تثبيت":
        if not is_admin_msg(message): return
        try: bot.unpin_chat_message(message.chat.id); return bot.reply_to(message,"تم الغاء التثبيت")
        except Exception: return

    if text=="م" and message.reply_to_message: text="رفع مميز"
    if text=="اد" and message.reply_to_message: text="رفع ادمن"
    if text.startswith("رفع ") or text.startswith("تنزيل "):
        if not is_admin_msg(message): return
        u=target_user(message)
        if not u: return bot.reply_to(message,"رد على الشخص")
        act,rank=text.split(maxsplit=1); rank=rank.strip()
        if rank not in RANK_NAMES: return
        data["ranks"].setdefault(gid,{})
        if act=="رفع": data["ranks"][gid][sid(u.id)]=rank; save_json(DATA_FILE,data); return bot.reply_to(message,f"تم رفعه {rank}")
        data["ranks"][gid].pop(sid(u.id),None); save_json(DATA_FILE,data); return bot.reply_to(message,"تم تنزيله")

    if text=="نزلني": data["ranks"].setdefault(gid,{}); data["ranks"][gid].pop(sid(message.from_user.id),None); save_json(DATA_FILE,data); return bot.reply_to(message,"تم تنزيلك من جميع الرتب")
    if text=="كشف" and message.reply_to_message:
        u=message.reply_to_message.from_user; uid=sid(u.id)
        return bot.reply_to(message,f"- الاسم: {u.first_name}\n- الايدي: <code>{u.id}</code>\n- اليوزر: @{u.username or 'ماكو'}\n- رتبة البوت: {get_rank(message.chat.id,u.id)}\n- الرسائل: {data['messages'].get(gid,{}).get(uid,0)}\n- النقاط: {data['points'].get(uid,0)}")
    if text=="صلاحياتي":
        try:
            m=bot.get_chat_member(message.chat.id,message.from_user.id); attrs=[("حذف الرسائل","can_delete_messages"),("حظر المستخدمين","can_restrict_members"),("تقييد المستخدمين","can_restrict_members"),("تثبيت الرسائل","can_pin_messages"),("دعوة المستخدمين","can_invite_users"),("تغيير معلومات المجموعة","can_change_info"),("إضافة مشرفين","can_promote_members")]
            lines=[f"- {n}: {'✓' if getattr(m,a,False) else '✗'}" for n,a in attrs]; uid=sid(message.from_user.id)
            return bot.reply_to(message,"• صلاحياتك:\n\n"+f"- الرتبة: {get_rank(message.chat.id,message.from_user.id)}\n"+"\n".join(lines)+f"\n\n- الرسائل: {data['messages'].get(gid,{}).get(uid,0)}\n- النقاط: {data['points'].get(uid,0)}\n- الانذارات: {data['warns'].get(gid,{}).get(uid,0)}")
        except Exception: return bot.reply_to(message,"ما اكدر اجيب صلاحياتك")

    if text=="اضف رد":
        if not is_admin_msg(message): return
        data["waiting"][sid(message.from_user.id)]={"step":"add_reply_word","chat":gid}; save_json(DATA_FILE,data); return bot.reply_to(message,"ارسل الكلمة")
    if text in ["حذف رد","مسح رد"]:
        if not is_admin_msg(message): return
        data["waiting"][sid(message.from_user.id)]={"step":"del_reply","chat":gid}; save_json(DATA_FILE,data); return bot.reply_to(message,"ارسل الكلمة")
    if text=="الردود":
        arr=list(data["replies"].get(gid,{}).keys()); return bot.reply_to(message,"• الردود المضافة:\n\n"+("\n".join("- "+x for x in arr) if arr else "ماكو ردود"))

    if text=="اضف تاك":
        if not is_admin_msg(message): return
        data["waiting"][sid(message.from_user.id)]={"step":"add_tag_name","chat":gid}; save_json(DATA_FILE,data); return bot.reply_to(message,"ارسل الاسم")
    if text.startswith("مسح تاك "):
        if not is_admin_msg(message): return
        name=text.replace("مسح تاك ","",1).strip(); data["tags"].setdefault(gid,{}); data["tags"][gid].pop(name,None); save_json(DATA_FILE,data); return bot.reply_to(message,"تم حذف التاك")

    if text.startswith("اضف نقاط ") and message.reply_to_message:
        if not is_admin_msg(message): return
        nums=re.findall(r"\d+",text); amount=int(nums[0]) if nums else 0; uid=sid(message.reply_to_message.from_user.id); data["points"][uid]=data["points"].get(uid,0)+amount; save_json(DATA_FILE,data); return bot.reply_to(message,f"تم إضافة {amount} نقطة")
    if text=="نقاطي": return bot.reply_to(message,f"نقاطك: {data['points'].get(sid(message.from_user.id),0)}")
    if text.startswith("بيع نقاطي"):
        uid=sid(message.from_user.id); pts=data["points"].get(uid,0); nums=re.findall(r"\d+",text); amount=int(nums[0]) if nums else pts
        if amount<=0 or pts<amount: return bot.reply_to(message,"نقاطك ما تكفي")
        data["points"][uid]-=amount; data["messages"].setdefault(gid,{}); data["messages"][gid][uid]=data["messages"][gid].get(uid,0)+amount*3; save_json(DATA_FILE,data); return bot.reply_to(message,f"تم بيع {amount} نقطة\nتمت إضافة {amount*3} رسالة")

    if text in ["تعيين الايدي","تغيير الايدي"]:
        if not is_admin_msg(message): return
        data["waiting"][sid(message.from_user.id)]={"step":"set_id_template","chat":gid}; save_json(DATA_FILE,data); return bot.reply_to(message,"ارسل كليشة الايدي\nالمتغيرات:\n{name}\n{id}\n{rank}\n{title}\n{messages}\n{points}")
    if text in ["ا","ايدي"]: return show_id(message)
    if text=="تفع": data["settings"]["id_photo"]=True; save_json(DATA_FILE,data); return bot.reply_to(message,"تم تفعيل ايدي بالصورة")
    if text=="تعط": data["settings"]["id_photo"]=False; save_json(DATA_FILE,data); return bot.reply_to(message,"تم تعطيل ايدي بالصورة")

    if text=="ر":
        link=data["links"].get(gid)
        if not link:
            try: link=bot.export_chat_invite_link(message.chat.id); data["links"][gid]=link; save_json(DATA_FILE,data)
            except Exception: link="ماكو رابط"
        return bot.reply_to(message,link)
    if text=="ضع رابط":
        if not is_admin_msg(message): return
        try: link=bot.export_chat_invite_link(message.chat.id); data["links"][gid]=link; save_json(DATA_FILE,data); return bot.reply_to(message,"تم وضع الرابط")
        except Exception: return bot.reply_to(message,"ما اكدر اسوي رابط")
    if text=="ترند": return list_top(message)
    if text=="تصفير الترند":
        if not is_creator_basic(message): return
        data["messages"][gid]={}; save_json(DATA_FILE,data); return bot.reply_to(message,"تم تصفير الترند")
    if text=="تاك للكل":
        if not is_admin_msg(message): return
        return tag_users(message,False)
    if text=="تاك للمشرفين":
        if not is_admin_msg(message): return
        return tag_users(message,True)

    if text=="تنظيف ميديا": return clean_media(message,["photo","video","sticker","animation"])
    if text=="تنظيف الصور": return clean_media(message,["photo"])
    if text=="تنظيف الفيديوهات": return clean_media(message,["video"])
    if text=="تنظيف الملصقات": return clean_media(message,["sticker"])
    if text=="تنظيف المتحركات": return clean_media(message,["animation"])
    if text in ["مسح بالرد","مسح"] and message.reply_to_message:
        if not is_admin_msg(message): return
        try: bot.delete_message(message.chat.id,message.reply_to_message.message_id); bot.delete_message(message.chat.id,message.message_id)
        except Exception: pass
        return
    if text.startswith("مسح ") and re.search(r"\d+",text):
        if not is_creator_basic(message): return
        count=min(int(re.findall(r"\d+",text)[0]),100)
        for i in range(count+1):
            try: bot.delete_message(message.chat.id,message.message_id-i)
            except Exception: pass
        return

    if text=="قائمه المنع":
        arr=data["blocked_words"].get(gid,[]); return bot.reply_to(message,"\n".join(arr) if arr else "ماكو كلمات ممنوعة")
    if text.startswith("منع "):
        if not is_admin_msg(message): return
        word=text.replace("منع ","",1).strip(); data["blocked_words"].setdefault(gid,[])
        if word not in data["blocked_words"][gid]: data["blocked_words"][gid].append(word)
        save_json(DATA_FILE,data); return bot.reply_to(message,"تم منع الكلمة")
    if text.startswith("الغاء منع "):
        if not is_admin_msg(message): return
        word=text.replace("الغاء منع ","",1).strip()
        try: data["blocked_words"][gid].remove(word)
        except Exception: pass
        save_json(DATA_FILE,data); return bot.reply_to(message,"تم الغاء المنع")
    for word in data["blocked_words"].get(gid,[]):
        if word and word in text and not is_admin_msg(message):
            try: bot.delete_message(message.chat.id,message.message_id)
            except Exception: pass
            return
    if text=="المكتومين": return bot.reply_to(message,"\n".join(data["muted"].get(gid,[])) or "ماكو مكتومين")
    if text=="المقيدين": return bot.reply_to(message,"\n".join(data["restricted"].get(gid,[])) or "ماكو مقيدين")
    if text=="المحظورين": return bot.reply_to(message,"\n".join(data["banned"].get(gid,[])) or "ماكو محظورين")

    if text in ["انشاء حساب بنكي","انشاء"]: bank(message.from_user.id); save_json(DATA_FILE,data); return bot.reply_to(message,"تم إنشاء حسابك البنكي")
    if text=="مسح حساب بنكي": data["money"].pop(sid(message.from_user.id),None); data["bank_accounts"].pop(sid(message.from_user.id),None); save_json(DATA_FILE,data); return bot.reply_to(message,"تم مسح حسابك البنكي")
    if text=="حسابي": bank(message.from_user.id); return bot.reply_to(message,f"رقم حسابك: <code>{data['bank_accounts'][sid(message.from_user.id)]}</code>")
    if text=="فلوسي": return bot.reply_to(message,f"فلوسك: {bank(message.from_user.id)}$")
    if text=="راتب":
        ok,left=cooldown(message.from_user.id,"salary",1200)
        if not ok: return bot.reply_to(message,f"انتظر {left} ثانية")
        money=bank(message.from_user.id)+random.randint(500,1500); save_bank(message.from_user.id,money); return bot.reply_to(message,f"تم استلام راتبك\nفلوسك: {money}$")
    if text=="بخشيش":
        ok,left=cooldown(message.from_user.id,"tip",600)
        if not ok: return bot.reply_to(message,f"انتظر {left} ثانية")
        money=bank(message.from_user.id)+random.randint(100,500); save_bank(message.from_user.id,money); return bot.reply_to(message,f"بخشيش وصل\nفلوسك: {money}$")
    if text in ["زرف","سرقه","سرقة"] and message.reply_to_message:
        ok,left=cooldown(message.from_user.id,"rob",600)
        if not ok: return bot.reply_to(message,f"انتظر {left} ثانية")
        victim=message.reply_to_message.from_user; amount=min(bank(victim.id),random.randint(50,500)); save_bank(victim.id,bank(victim.id)-amount); save_bank(message.from_user.id,bank(message.from_user.id)+amount); data["robbers"][sid(message.from_user.id)]=data["robbers"].get(sid(message.from_user.id),0)+1; save_json(DATA_FILE,data); return bot.reply_to(message,f"زرفته {amount}$")
    if text.startswith("استثمار ") or text.startswith("حظ ") or text.startswith("مضاربه "):
        nums=re.findall(r"\d+",text)
        if not nums: return
        amount=int(nums[0]); bal=bank(message.from_user.id)
        if bal<amount: return bot.reply_to(message,"فلوسك ما تكفي")
        if text.startswith("استثمار "):
            profit=int(amount*random.randint(1,15)/100); save_bank(message.from_user.id,bal+profit); return bot.reply_to(message,f"ربحت {profit}$")
        if text.startswith("حظ "):
            if random.choice([True,False]): save_bank(message.from_user.id,bal+amount); return bot.reply_to(message,f"فزت {amount}$")
            save_bank(message.from_user.id,bal-amount); return bot.reply_to(message,f"خسرت {amount}$")
        percent=random.randint(-90,90); change=int(amount*percent/100); save_bank(message.from_user.id,bal+change); return bot.reply_to(message,f"النسبة: {percent}%\nالنتيجة: {change}$")
    if text=="توب الفلوس":
        items=sorted(data["money"].items(),key=lambda x:x[1],reverse=True)[:10]; return bot.reply_to(message,"\n".join([f"{i+1}- {display_user(uid)}: {m}$" for i,(uid,m) in enumerate(items)]) or "ماكو")
    if text=="توب الحراميه":
        items=sorted(data["robbers"].items(),key=lambda x:x[1],reverse=True)[:10]; return bot.reply_to(message,"\n".join([f"{i+1}- {display_user(uid)}: {c}" for i,(uid,c) in enumerate(items)]) or "ماكو")

    if text=="المالك":
        try:
            admins=bot.get_chat_administrators(message.chat.id); owner=next((a.user for a in admins if a.status=="creator"),None)
            if owner: return bot.reply_to(message,f"• مالك المجموعة:\n- الاسم: {owner.first_name}\n- اليوزر: @{owner.username or 'ماكو'}\n- الايدي: <code>{owner.id}</code>")
        except Exception: pass
        return bot.reply_to(message,"ما قدرت اجيب المالك")
    if text=="لقبي": return bot.reply_to(message,f"• لقبك: {data['titles'].get(gid,{}).get(sid(message.from_user.id),'لا يوجد')}")
    if text.startswith("اضف لقب ") and message.reply_to_message:
        if not is_admin_msg(message): return
        title=text.replace("اضف لقب ","",1).strip(); data["titles"].setdefault(gid,{}); data["titles"][gid][sid(message.reply_to_message.from_user.id)]=title; save_json(DATA_FILE,data); return bot.reply_to(message,"تم إضافة اللقب")
    if text in ["نسبة الحب","نسبة الكره","نسبة الرجوله","نسبة الانوثه","نسبة الجمال"]: return bot.reply_to(message,f"{text}: {random.randint(0,100)}%")
    if text in ["بوسه","بوسها"] and message.reply_to_message: return bot.reply_to(message,f"💋 {message.from_user.first_name} باس {message.reply_to_message.from_user.first_name}")
    if text=="ز":
        ids=[x for x in list(data["messages"].get(gid,{}).keys()) if x != sid(message.from_user.id)]
        if not ids: return bot.reply_to(message,"ماكو أعضاء")
        partner=random.choice(ids); data["marriages"][sid(message.from_user.id)]=partner; save_json(DATA_FILE,data); return bot.reply_to(message,f"مبروك زوجتك {display_user(partner)}")
    if text in ["زوجتي","زوجي"]:
        p=data["marriages"].get(sid(message.from_user.id)); return bot.reply_to(message,f"زوجتك/زوجك: {display_user(p)}" if p else "انت أعزب")
    if text=="ط": data["marriages"].pop(sid(message.from_user.id),None); save_json(DATA_FILE,data); return bot.reply_to(message,"تم الطلاق")
    if text=="زواج" and message.reply_to_message:
        price=min(bank(message.from_user.id),500); data["marriages"][sid(message.from_user.id)]=sid(message.reply_to_message.from_user.id); save_bank(message.from_user.id,bank(message.from_user.id)-price); return bot.reply_to(message,f"تم الزواج\nالمهر: {price}$")

    if text=="همسه" and message.reply_to_message:
        if message.chat.type == "private": return
        data["waiting"][sid(message.from_user.id)]={"step":"whisper_text","chat":message.chat.id,"to":message.reply_to_message.from_user.id}; save_json(DATA_FILE,data)
        kb={"inline_keyboard":[[blue("كتابة الهمسة",url=f"https://t.me/{BOT_USERNAME}?start=whisper")]]}
        return bot.reply_to(message,f"• تم تحديد الهمسة لـ {message.reply_to_message.from_user.first_name}\n• اضغط الزر لكتابة الهمسة بالخاص",reply_markup=kb)

    if text=="افلام" or text.startswith("فلم"):
        m=random.choice(MOVIES); return bot.reply_to(message,f"🎬 اسم الفيلم: {m[0]}\n🎭 النوع: {m[1]}\n📅 السنة: {m[2]}\n📝 الوصف: {m[3]}")
    if text.startswith("طقس"):
        city=text.replace("طقس","",1).strip() or "بغداد"; return bot.reply_to(message,f"🌤 حالة الطقس في {city}\n🌡 الحرارة: 32°\n🥶 البرودة: 29°\n💨 الرياح: 12 كم\n☁️ الحالة: غائم جزئياً")
    if text=="قران":
        s,rec,url=random.choice(QURAN); return bot.send_audio(message.chat.id,url,title=s,performer=rec,caption=f"📖 {s}\nالقارئ: {rec}")
    if text=="تراتيل":
        name,url=random.choice(CHANTS); return bot.reply_to(message,f"🎼 {name}\nارفع روابط التراتيل الصحيحة داخل القائمة حتى يرسلها صوت.")
    if text=="غنيلي": return bot.reply_to(message,random.choice(["🎵 يا ليل يا عين","🎶 غنيتلك من گلبي","🎧 اكتب: يوت اسم الأغنية"]))

    if text=="لغز": q=random.choice(PUZZLES); return add_quiz(message.chat.id,"لغز:\n"+q[0],q[1],q[2])
    if text=="عربي": q=random.choice(ARABIC_Q); return add_quiz(message.chat.id,"عربي:\n"+q[0],q[1],q[2])
    if text=="اعلام": q=random.choice(FLAGS); return add_quiz(message.chat.id,q[0],q[1],q[2])
    if text=="سيارات": q=random.choice(CARS); return add_quiz(message.chat.id,q[0],q[1],q[2])
    if text in ["مشاهير","المشاهير"]: q=random.choice(FAMOUS); return add_quiz(message.chat.id,q[0],q[1],q[2])
    if text in ["كت","كت تويت"]: return bot.reply_to(message,random.choice(KT))
    if text=="لو خيروك": return bot.reply_to(message,random.choice(WOULD))
    if text=="الاسرع":
        word=random.choice(FAST_WORDS); data["fast_games"][gid]=word; save_json(DATA_FILE,data); return bot.reply_to(message,f"⚡ لعبة الاسرع\n\nاكتب:\n{word}")
    if data["fast_games"].get(gid)==text:
        uid=sid(message.from_user.id); data["points"][uid]=data["points"].get(uid,0)+1; data["fast_games"].pop(gid,None); save_json(DATA_FILE,data); return bot.reply_to(message,f"✅ فزت بلعبة الاسرع\nنقاطك: {data['points'][uid]}")

print("SOURCE FADI PROTECTION BOT RUNNING")
bot.infinity_polling(skip_pending=True)
