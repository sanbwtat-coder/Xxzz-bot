import os, json, time, random, string, threading, subprocess, requests
import telebot
from config import MAKER_TOKEN, OWNER_ID, OWNER_FORCE_CHANNEL, DEV_USERNAME, SOURCE_NAME, PRICES_TEXT

bot = telebot.TeleBot(MAKER_TOKEN, parse_mode="HTML")
DATA_FILE = "maker_data.json"
BOTS_DIR = "made_bots"
os.makedirs(BOTS_DIR, exist_ok=True)
running_processes = {}
waiting = {}
DEFAULT_DATA = {"users": {}, "bots": {}, "codes": {}, "blocked": [], "stats": {"groups": 0}}
PLANS = {"1m": {"name":"شهر واحد","days":30}, "2m":{"name":"شهرين","days":60}, "3m":{"name":"3 أشهر","days":90}, "6m":{"name":"6 أشهر","days":180}, "1y":{"name":"سنة كاملة","days":365}}

def load_data():
    if not os.path.exists(DATA_FILE): save_data(DEFAULT_DATA.copy())
    try:
        with open(DATA_FILE,"r",encoding="utf-8") as f: d=json.load(f)
    except: d=DEFAULT_DATA.copy()
    for k,v in DEFAULT_DATA.items(): d.setdefault(k,v)
    return d

def save_data(d):
    with open(DATA_FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)

data=load_data()
def sid(x): return str(x)

def raw_send(chat_id,text,reply_markup=None):
    payload={"chat_id":chat_id,"text":text,"parse_mode":"HTML"}
    if reply_markup: payload["reply_markup"]=reply_markup
    requests.post(f"https://api.telegram.org/bot{MAKER_TOKEN}/sendMessage",json=payload,timeout=15)

def blue(text,callback_data=None,url=None):
    b={"text":text,"style":"primary"}
    if callback_data: b["callback_data"]=callback_data
    if url: b["url"]=url
    return b

def red(text,callback_data=None,url=None):
    b={"text":text,"style":"danger"}
    if callback_data: b["callback_data"]=callback_data
    if url: b["url"]=url
    return b

def main_keyboard():
    return {"inline_keyboard":[
        [blue("صنع بوت حماية","make_protection")],
        [blue("بوتاتي","my_bots"),blue("تفعيل اشتراك","activate_code")],
        [blue("اسعار الاشتراكات","prices"),blue("الدعم",url=f"https://t.me/{DEV_USERNAME}")],
        [blue("قناة الصانع",url="https://t.me/"+OWNER_FORCE_CHANNEL.replace("@",""))],
        [red(SOURCE_NAME,url=f"https://t.me/{DEV_USERNAME}")]
    ]}

def owner_keyboard():
    return {"inline_keyboard":[
        [blue("انشاء كود شهر","gen_1m"),blue("انشاء كود شهرين","gen_2m")],
        [blue("انشاء كود 3 اشهر","gen_3m"),blue("انشاء كود 6 اشهر","gen_6m")],
        [blue("انشاء كود سنة","gen_1y")],
        [blue("الاحصائيات","owner_stats"),blue("البوتات","owner_bots")],
        [blue("المستخدمين","owner_users")],
        [red(SOURCE_NAME,url=f"https://t.me/{DEV_USERNAME}")]
    ]}

def bot_panel_keyboard(bot_id):
    info=data["bots"].get(bot_id,{})
    return {"inline_keyboard":[
        [blue("حالة البوت: "+("مدفوع" if info.get("plan")=="paid" else "مجاني"),"noop")],
        [blue("تشغيل البوت",f"run_{bot_id}"),blue("ايقاف البوت",f"stop_{bot_id}")],
        [blue("تغيير الاشتراك الاجباري",f"set_force_{bot_id}")],
        [blue("تفعيل اشتراك","activate_code"),blue("اسعار الاشتراكات","prices")],
        [red(SOURCE_NAME,url=f"https://t.me/{DEV_USERNAME}")]
    ]}

def register_user(message):
    uid=sid(message.from_user.id)
    if uid not in data["users"]:
        data["users"][uid]={"name":message.from_user.first_name or "","username":message.from_user.username or "","joined":int(time.time())}
        save_data(data)

def make_code(plan_key):
    code="FADI-"+plan_key.upper()+"-"+"".join(random.choices(string.ascii_uppercase+string.digits,k=6))
    data["codes"][code]={"plan_key":plan_key,"days":PLANS[plan_key]["days"],"used":False,"created_at":int(time.time())}
    save_data(data); return code

def get_bot_username(token):
    try:
        r=requests.get(f"https://api.telegram.org/bot{token}/getMe",timeout=15).json()
        if r.get("ok"): return r["result"]["username"], r["result"].get("first_name","Protection Bot")
    except: pass
    return None,None

def create_bot_file(bot_id):
    info=data["bots"][bot_id]
    template=open("protection_template.py",encoding="utf-8").read()
    code=(template.replace("__BOT_TOKEN__",info["token"]).replace("__OWNER_ID__",str(info["owner_id"]))
          .replace("__OWNER_FORCE_CHANNEL__",OWNER_FORCE_CHANNEL).replace("__DEV_USERNAME__",DEV_USERNAME)
          .replace("__BOT_USERNAME__",info["username"]).replace("__BOT_ID__",bot_id)
          .replace("__MAKER_DATA_FILE__",DATA_FILE).replace("__SOURCE_NAME__",SOURCE_NAME))
    path=os.path.join(BOTS_DIR,f"{bot_id}.py")
    open(path,"w",encoding="utf-8").write(code)
    return path

def run_created_bot(bot_id):
    if bot_id in running_processes and running_processes[bot_id].poll() is None: return True
    path=create_bot_file(bot_id)
    running_processes[bot_id]=subprocess.Popen(["python",path])
    return True

def stop_created_bot(bot_id):
    p=running_processes.get(bot_id)
    if p and p.poll() is None:
        try: p.terminate()
        except: pass
    running_processes.pop(bot_id,None)

def check_expired_loop():
    while True:
        now=int(time.time()); changed=False
        for bot_id,info in list(data["bots"].items()):
            if info.get("plan")=="paid" and info.get("expires_at") and now>info["expires_at"]:
                info["plan"]="free"; info["expires_at"]=None; info["force_channel"]=OWNER_FORCE_CHANNEL; changed=True
        if changed: save_data(data)
        time.sleep(3600)

@bot.message_handler(commands=["start"])
def start(message):
    register_user(message)
    if message.from_user.id==OWNER_ID:
        txt=("✦ لوحة المطور ✦\n\n"+f"• عدد المستخدمين : {len(data['users'])}\n"+f"• عدد البوتات المصنوعة : {len(data['bots'])}\n"+f"• البوتات المدفوعة : {sum(1 for b in data['bots'].values() if b.get('plan')=='paid')}\n"+f"• البوتات المجانية : {sum(1 for b in data['bots'].values() if b.get('plan')=='free')}\n")
        raw_send(message.chat.id,txt,owner_keyboard())
    else:
        raw_send(message.chat.id,"• هلا بك في صانع بوتات فادي\n\n• اصنع بوت حماية مجاني أو فعّل اشتراك مدفوع.",main_keyboard())

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    try: bot.answer_callback_query(call.id)
    except: pass
    uid=call.from_user.id; d=call.data
    if d=="noop": return
    if d=="prices": return raw_send(call.message.chat.id,PRICES_TEXT,main_keyboard())
    if d=="make_protection": waiting[uid]={"step":"bot_token"}; return raw_send(call.message.chat.id,"ارسل توكن بوت الحماية الجديد:")
    if d=="activate_code": waiting[uid]={"step":"activate_code"}; return raw_send(call.message.chat.id,"ارسل كود التفعيل:")
    if d=="my_bots":
        arr=[(bid,b) for bid,b in data["bots"].items() if b["owner_id"]==uid]
        if not arr: return raw_send(call.message.chat.id,"ما عندك بوتات بعد.",main_keyboard())
        for bid,info in arr:
            exp="لا يوجد" if not info.get("expires_at") else time.strftime("%Y-%m-%d",time.localtime(info["expires_at"]))
            txt=f"• اسم البوت: {info.get('name')}\n• يوزر البوت: @{info.get('username')}\n• حالة البوت: {'مدفوع' if info.get('plan')=='paid' else 'مجاني'}\n• الاشتراك الإجباري: {info.get('force_channel')}\n• ينتهي: {exp}"
            raw_send(call.message.chat.id,txt,bot_panel_keyboard(bid))
        return
    if d.startswith("gen_") and uid==OWNER_ID:
        plan=d.replace("gen_",""); code=make_code(plan)
        return raw_send(call.message.chat.id,f"تم إنشاء كود {PLANS[plan]['name']}:\n\n<code>{code}</code>\n\nارسله للمستخدم.")
    if d=="owner_stats" and uid==OWNER_ID:
        txt=f"✦ الاحصائيات ✦\n\n• عدد المستخدمين : {len(data['users'])}\n• عدد الكروبات : {data.get('stats',{}).get('groups',0)}\n• عدد البوتات المصنوعة : {len(data['bots'])}\n• البوتات المدفوعة : {sum(1 for b in data['bots'].values() if b.get('plan')=='paid')}\n• البوتات المجانية : {sum(1 for b in data['bots'].values() if b.get('plan')=='free')}"
        return raw_send(call.message.chat.id,txt,owner_keyboard())
    if d=="owner_bots" and uid==OWNER_ID:
        txt="• البوتات المصنوعة:\n\n" if data["bots"] else "ماكو بوتات."
        for bid,info in list(data["bots"].items())[:30]: txt+=f"- @{info.get('username')} | {info.get('plan')} | owner: {info.get('owner_id')}\n"
        return raw_send(call.message.chat.id,txt)
    if d=="owner_users" and uid==OWNER_ID:
        txt="• المستخدمين:\n\n"
        for u,info in list(data["users"].items())[:40]: txt+=f"- {info.get('name')} | @{info.get('username') or 'ماكو'} | {u}\n"
        return raw_send(call.message.chat.id,txt)
    if d.startswith("run_"):
        bot_id=d.replace("run_",""); info=data["bots"].get(bot_id)
        if not info or (uid!=info["owner_id"] and uid!=OWNER_ID): return
        run_created_bot(bot_id); return raw_send(call.message.chat.id,"تم تشغيل البوت.")
    if d.startswith("stop_"):
        bot_id=d.replace("stop_",""); info=data["bots"].get(bot_id)
        if not info or (uid!=info["owner_id"] and uid!=OWNER_ID): return
        stop_created_bot(bot_id); return raw_send(call.message.chat.id,"تم ايقاف البوت.")
    if d.startswith("set_force_"):
        bot_id=d.replace("set_force_",""); info=data["bots"].get(bot_id)
        if not info or info["owner_id"]!=uid: return
        if info.get("plan")!="paid": return raw_send(call.message.chat.id,"هذه الميزة للمدفوع فقط. المجاني اشتراكه إجباري بقناة الصانع.")
        waiting[uid]={"step":"set_force","bot_id":bot_id}; return raw_send(call.message.chat.id,"ارسل معرف قناتك مثل:\n@channel")

@bot.message_handler(func=lambda m: True)
def text_handler(message):
    register_user(message); uid=message.from_user.id; txt=(message.text or "").strip()
    if uid not in waiting:
        if txt.startswith("تفعيل "): waiting[uid]={"step":"activate_code"}; txt=txt.replace("تفعيل ","",1).strip()
        else: return
    st=waiting.get(uid,{}); step=st.get("step")
    if step=="bot_token":
        username,name=get_bot_username(txt)
        if not username: return raw_send(message.chat.id,"التوكن غلط أو البوت غير صالح. ارسل توكن صحيح.")
        bot_id=str(int(time.time()))+str(random.randint(100,999))
        data["bots"][bot_id]={"owner_id":uid,"owner_name":message.from_user.first_name or "","owner_username":message.from_user.username or "","token":txt,"username":username,"name":name,"type":"protection","plan":"free","force_channel":OWNER_FORCE_CHANNEL,"expires_at":None,"created_at":int(time.time()),"active":True}
        save_data(data); create_bot_file(bot_id); run_created_bot(bot_id); waiting.pop(uid,None)
        owner_link=f"https://t.me/{message.from_user.username}" if message.from_user.username else f"tg://user?id={uid}"
        raw_send(OWNER_ID,f"🔔 تم صنع بوت جديد\n\n• الاسم: {message.from_user.first_name}\n• اليوزر: @{message.from_user.username or 'ماكو'}\n• الايدي: <code>{uid}</code>\n\n• نوع البوت: حماية\n• اسم البوت: {name}\n• يوزر البوت: @{username}\n• الخطة: مجانية\n• حسابه: {owner_link}")
        return raw_send(message.chat.id,f"تم صنع بوت الحماية بنجاح.\n\n• يوزر البوت: @{username}\n• الحالة: مجاني\n• الاشتراك الإجباري: {OWNER_FORCE_CHANNEL}",bot_panel_keyboard(bot_id))
    if step=="activate_code":
        code=txt.replace("تفعيل ","",1).strip(); c=data["codes"].get(code)
        if not c: return raw_send(message.chat.id,"الكود غير صحيح.")
        if c.get("used"): return raw_send(message.chat.id,"الكود مستخدم سابقًا.")
        user_bots=[(bid,b) for bid,b in data["bots"].items() if b["owner_id"]==uid]
        if not user_bots: return raw_send(message.chat.id,"ما عندك بوت. اصنع بوت أولاً.")
        bot_id,info=user_bots[-1]; now=int(time.time()); start=max(now,info.get("expires_at") or now)
        info["plan"]="paid"; info["expires_at"]=start+c["days"]*86400; c["used"]=True; c["used_by"]=uid; c["used_at"]=now
        save_data(data); waiting.pop(uid,None)
        return raw_send(message.chat.id,f"تم تفعيل الاشتراك.\n\n• البوت: @{info['username']}\n• المدة: {c['days']} يوم\n• الحالة: مدفوع\n\nتقدر الآن تضيف قناتك للاشتراك الإجباري.",bot_panel_keyboard(bot_id))
    if step=="set_force":
        bot_id=st["bot_id"]; ch=txt.strip()
        if not ch.startswith("@"): return raw_send(message.chat.id,"ارسل معرف القناة مع @")
        data["bots"][bot_id]["force_channel"]=ch; save_data(data); waiting.pop(uid,None)
        return raw_send(message.chat.id,f"تم تغيير الاشتراك الإجباري إلى:\n{ch}",bot_panel_keyboard(bot_id))

threading.Thread(target=check_expired_loop,daemon=True).start()
print("Maker bot running...")
bot.infinity_polling(skip_pending=True)
