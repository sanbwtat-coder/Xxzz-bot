import os, json, time, re, random, requests, yt_dlp
import telebot

TOKEN = "__BOT_TOKEN__"
OWNER_ID = int("__OWNER_ID__")
BOT_USERNAME = "__BOT_USERNAME__"
DEV_USERNAME = "__DEV_USERNAME__"
BOT_ID = "__BOT_ID__"
MAKER_DATA_FILE = "__MAKER_DATA_FILE__"
OWNER_FORCE_CHANNEL = "__OWNER_FORCE_CHANNEL__"
SOURCE_NAME = "__SOURCE_NAME__"

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
DATA_FILE = f'bot_data_{BOT_ID}.json'
DOWNLOADS = f'downloads_{BOT_ID}'
os.makedirs(DOWNLOADS, exist_ok=True)

DEFAULT = {'users': {}, 'groups': {}, 'locks': {}, 'ranks': {}, 'messages': {}, 'points': {}, 'bank': {}, 'waiting_games': {}, 'settings': {'id': True, 'id_photo': True}}
RANKS = {'عضو':0,'مميز':1,'ادمن':2,'مشرف':2,'مدير':3,'منشئ':4,'مالك':5}

def load_json(path, default):
    if not os.path.exists(path): save_json(path, default.copy())
    try:
        with open(path,'r',encoding='utf-8') as f: d=json.load(f)
    except: d=default.copy()
    for k,v in default.items(): d.setdefault(k,v)
    return d

def save_json(path,d):
    with open(path,'w',encoding='utf-8') as f: json.dump(d,f,ensure_ascii=False,indent=2)

data=load_json(DATA_FILE, DEFAULT)

def sid(x): return str(x)
def clean_filename(name): return re.sub(r'[\\/*?:"<>|]', '', name)[:80]
def maker_data(): return load_json(MAKER_DATA_FILE, {'bots': {}})
def bot_info(): return maker_data().get('bots',{}).get(BOT_ID, {'plan':'free','force_channel':OWNER_FORCE_CHANNEL})
def is_paid(): return bot_info().get('plan')=='paid'
def force_channel():
    info=bot_info()
    if info.get('plan')=='paid': return info.get('force_channel') or OWNER_FORCE_CHANNEL
    return OWNER_FORCE_CHANNEL

def button(text, cb=None, url=None, style='primary'):
    b={'text':text,'style':style}
    if cb: b['callback_data']=cb
    if url: b['url']=url
    return b

def raw(chat_id,text,kb=None,reply_to=None):
    p={'chat_id':chat_id,'text':text,'parse_mode':'HTML'}
    if kb: p['reply_markup']=kb
    if reply_to: p['reply_to_message_id']=reply_to
    try: requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage',json=p,timeout=15)
    except: pass

def start_kb():
    return {'inline_keyboard':[[button('اضفني +',url=f'https://t.me/{BOT_USERNAME}?startgroup=true')],[button('المطور',url=f'https://t.me/{DEV_USERNAME}'),button('الأوامر','commands')],[button('حالة البوت: '+('مدفوع' if is_paid() else 'مجاني'),'status')],[button(SOURCE_NAME,url=f'https://t.me/{DEV_USERNAME}',style='danger')]]}

def commands_kb():
    return {'inline_keyboard':[[button('• 1 •','cmd_1'),button('• 2 •','cmd_2')],[button('• 3 •','cmd_3'),button('• 4 •','cmd_4')],[button('• 5 •','cmd_5'),button('• 6 •','cmd_6')],[button(SOURCE_NAME,url=f'https://t.me/{DEV_USERNAME}',style='danger')]]}

COMMANDS={
'cmd_1':'''• اوامر القفل والفتح

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
- المتحركه''',
'cmd_2':'''- اوامر مشرفين المجموعة

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
- منع / الغاء منع''',
'cmd_3':'''- اوامر مسح المشرفين

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
- مسح + العدد''',
'cmd_4':'''- اوامر الرفع والحظر

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
- رفع / تنزيل مشرف''',
'cmd_5':'''- اوامر ترفيه الاعضاء

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
- مسلسل''',
'cmd_6':'''- الالعاب

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
- بيع نقاطي'''
}

def register(m):
    if m.from_user:
        uid=sid(m.from_user.id); data['users'].setdefault(uid, {'name':m.from_user.first_name or '', 'username':m.from_user.username or ''})
        if m.chat.type in ['group','supergroup']:
            gid=sid(m.chat.id); data['groups'].setdefault(gid, {'title':m.chat.title or ''}); data['messages'].setdefault(gid,{})
            data['messages'][gid][uid]=data['messages'][gid].get(uid,0)+1
        save_json(DATA_FILE,data)

def get_rank(chat_id,user_id):
    if user_id==OWNER_ID: return 'مالك'
    return data['ranks'].get(sid(chat_id),{}).get(sid(user_id),'عضو')
def rank_level(chat_id,user_id): return RANKS.get(get_rank(chat_id,user_id),0)
def is_admin(m):
    if m.from_user.id==OWNER_ID: return True
    try:
        cm=bot.get_chat_member(m.chat.id,m.from_user.id)
        if cm.status in ['administrator','creator']: return True
    except: pass
    return rank_level(m.chat.id,m.from_user.id)>=1

def is_subscribed(user_id):
    ch=force_channel()
    if not ch: return True
    try:
        m=bot.get_chat_member(ch,user_id); return m.status in ['member','administrator','creator']
    except: return True

def check_sub(m):
    if m.from_user and not is_subscribed(m.from_user.id):
        ch=force_channel(); raw(m.chat.id,'⚠️ لازم تشترك بالقناة أولاً',{'inline_keyboard':[[button('اشترك بالقناة',url='https://t.me/'+ch.replace('@',''))]]},m.message_id); return False
    return True

@bot.message_handler(content_types=['new_chat_members','left_chat_member'])
def delete_join_leave(m):
    try: bot.delete_message(m.chat.id,m.message_id)
    except: pass

@bot.message_handler(commands=['start'])
def start(m):
    register(m)
    if not check_sub(m): return
    raw(m.chat.id, f"• هلا بك في بوت حماية فادي\n\n• اضفني للكروب وارفعني مشرف\n\n• حالة البوت: {'مدفوع' if is_paid() else 'مجاني'}\n• الاشتراك الإجباري: {force_channel()}", start_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    try: bot.answer_callback_query(c.id)
    except: pass
    if c.data=='commands': return raw(c.message.chat.id,'- اختر قسم الاوامر',commands_kb())
    if c.data in COMMANDS: return raw(c.message.chat.id,COMMANDS[c.data],commands_kb())
    if c.data=='status': return raw(c.message.chat.id,f"• حالة البوت: {'مدفوع' if is_paid() else 'مجاني'}\n• الاشتراك الإجباري: {force_channel()}")
    if c.data.startswith('quiz_'):
        _,gid,ans=c.data.split('_',2); g=data.get('waiting_games',{}).get(gid)
        if not g: return
        if ans==g['answer']:
            uid=sid(c.from_user.id); data['points'][uid]=data['points'].get(uid,0)+1; save_json(DATA_FILE,data)
            return raw(c.message.chat.id,f"✅ إجابة صحيحة\nربحت نقطة\nنقاطك: {data['points'][uid]}")
        return raw(c.message.chat.id,'❌ إجابة خاطئة')

def add_quiz(chat_id,q,choices,answer):
    gid=str(int(time.time()))+str(random.randint(100,999)); data['waiting_games'][gid]={'answer':answer}; save_json(DATA_FILE,data)
    kb={'inline_keyboard':[[button(c,f'quiz_{gid}_{c}')] for c in choices]}
    raw(chat_id,q,kb)

PUZZLES=[('شنو عاصمة أستراليا؟',['سيدني','ملبورن','كانبرا'],'كانبرا'),('شي كلما أخذت منه كبر؟',['الحفرة','الماء','البيت'],'الحفرة'),('شي يمشي بلا رجلين؟',['النهر','الكتاب','القلم'],'النهر')]
ARABIC_Q=[('جمع كلمة كتاب؟',['كتب','كتابات','كاتب'],'كتب'),('ضد كلمة طويل؟',['قصير','كبير','قديم'],'قصير')]
FLAGS=[('🇮🇶 شنو اسم هذا العلم؟',['العراق','مصر','سوريا'],'العراق'),('🇬🇷 شنو اسم هذا العلم؟',['اليونان','إيطاليا','فرنسا'],'اليونان')]
CARS=[('🚗 شنو اسم السيارة؟',['تويوتا','BMW','KIA'],'تويوتا'),('🚙 شنو اسم السيارة؟',['مرسيدس','نيسان','هوندا'],'مرسيدس')]
FAMOUS=[('👤 منو هذا المشهور؟',['ميسي','رونالدو','نيمار'],'ميسي'),('👤 منو هذا المشهور؟',['فيروز','ام كلثوم','وردة'],'فيروز')]
KT=['شنو أكثر شي تحبه؟','شنو حلمك؟','منو أقرب شخص الك؟','شنو أكثر شي يضوجك؟']
WOULD=['لو خيروك تعيش غني وحيد لو فقير ويا أصحاب؟','لو خيروك ترجع للماضي لو تشوف المستقبل؟']
FAST=['تفاحة','سيارة','عراق','قلم','ماء']

def source_button(chat_id): raw(chat_id,SOURCE_NAME,{'inline_keyboard':[[button(SOURCE_NAME,url=f'https://t.me/{DEV_USERNAME}',style='danger')]]})

def download_audio(query):
    base={'format':'bestaudio[filesize<45M]/bestaudio/best','outtmpl':f'{DOWNLOADS}/%(title)s.%(ext)s','cookiefile':'cookies.txt','noplaylist':True,'quiet':True,'no_warnings':True,'socket_timeout':20,'retries':4,'fragment_retries':4,'concurrent_fragment_downloads':5}
    sources=[(f'ytsearch10:{query}',['android']),(f'ytsearch10:{query}',['ios']),(f'ytsearch10:{query}',['web']),(f'scsearch5:{query}',None)]
    last=None
    for search,client in sources:
        try:
            opts=base.copy()
            if client: opts['extractor_args']={'youtube':{'player_client':client}}
            else: opts.pop('cookiefile',None)
            with yt_dlp.YoutubeDL(opts) as ydl:
                info=ydl.extract_info(search,download=True)
                if info and 'entries' in info:
                    for item in info['entries']:
                        if item: info=item; break
                if not info: continue
                return ydl.prepare_filename(info), clean_filename(info.get('title','song'))
        except Exception as e: last=e
    raise Exception(last)

@bot.message_handler(content_types=['text','photo','video','sticker','animation','document','voice','audio'])
def handler(m):
    register(m)
    if m.chat.type!='private' and not check_sub(m): return
    text=m.text or m.caption or ''
    if text in ['الاوامر','الأوامر','اوامر']: return raw(m.chat.id,'- اختر قسم الاوامر',commands_kb())
    if text=='سورس': return source_button(m.chat.id)
    if text=='المطور': return bot.reply_to(m,f'https://t.me/{DEV_USERNAME}')
    if text.startswith('يوت ') or text.startswith('تشغيل '):
        q=text.replace('يوت ','',1).replace('تشغيل ','',1).strip()
        if not q: return bot.reply_to(m,'اكتب اسم الاغنية')
        wait=bot.reply_to(m,'🔎 جاري البحث...')
        try:
            path,title=download_audio(q)
            try: bot.delete_message(m.chat.id,wait.message_id)
            except: pass
            with open(path,'rb') as audio: bot.send_audio(m.chat.id,audio,title=title,performer='Song fadi',caption=f'🎧 {title}',reply_to_message_id=m.message_id)
            source_button(m.chat.id)
            try: os.remove(path)
            except: pass
        except Exception as e: bot.reply_to(m,f'❌ صار خطأ:\n{e}')
        return
    if text.startswith('قفل ') or text.startswith('فتح '):
        if not is_admin(m): return
        name=text.split(maxsplit=1)[1].strip(); gid=sid(m.chat.id); data['locks'].setdefault(gid,{})
        data['locks'][gid][name]=text.startswith('قفل '); save_json(DATA_FILE,data)
        return bot.reply_to(m,'تم '+('قفل ' if text.startswith('قفل ') else 'فتح ')+name)
    if m.chat.type in ['group','supergroup'] and not is_admin(m):
        locks=data['locks'].get(sid(m.chat.id),{})
        cmap={'الصور':'photo','الملصقات':'sticker','المتحركات':'animation','الفيديو':'video','الملفات':'document','الصوت':'voice','الاغاني':'audio'}
        for lname,ctype in cmap.items():
            if locks.get(lname) and m.content_type==ctype:
                try: bot.delete_message(m.chat.id,m.message_id)
                except: pass
                return
        if locks.get('الروابط') and re.search(r'(https?://|t\.me/|www\.)',text):
            try: bot.delete_message(m.chat.id,m.message_id)
            except: pass
            return
    if text=='ا':
        uid,gid=sid(m.from_user.id),sid(m.chat.id); msgs=data['messages'].get(gid,{}).get(uid,0); pts=data['points'].get(uid,0)
        return bot.reply_to(m,f'- الاسم: {m.from_user.first_name}\n- الايدي: <code>{m.from_user.id}</code>\n- الرتبة: {get_rank(m.chat.id,m.from_user.id)}\n- الرسائل: {msgs}\n- النقاط: {pts}')
    if text=='لغز': q=random.choice(PUZZLES); return add_quiz(m.chat.id,'لغز:\n'+q[0],q[1],q[2])
    if text=='عربي': q=random.choice(ARABIC_Q); return add_quiz(m.chat.id,'عربي:\n'+q[0],q[1],q[2])
    if text=='اعلام': q=random.choice(FLAGS); return add_quiz(m.chat.id,q[0],q[1],q[2])
    if text=='سيارات': q=random.choice(CARS); return add_quiz(m.chat.id,q[0],q[1],q[2])
    if text in ['مشاهير','المشاهير']: q=random.choice(FAMOUS); return add_quiz(m.chat.id,q[0],q[1],q[2])
    if text in ['كت','كت تويت']: return bot.reply_to(m,random.choice(KT))
    if text=='لو خيروك': return bot.reply_to(m,random.choice(WOULD))
    if text=='الاسرع':
        word=random.choice(FAST); data['waiting_games'][sid(m.chat.id)]={'fast':word}; save_json(DATA_FILE,data)
        return bot.reply_to(m,f'⚡ لعبة الاسرع\n\nاكتب:\n{word}')
    if sid(m.chat.id) in data['waiting_games'] and data['waiting_games'][sid(m.chat.id)].get('fast')==text:
        uid=sid(m.from_user.id); data['points'][uid]=data['points'].get(uid,0)+1; data['waiting_games'].pop(sid(m.chat.id),None); save_json(DATA_FILE,data)
        return bot.reply_to(m,f"✅ فزت بلعبة الاسرع\nنقاطك: {data['points'][uid]}")
    if text=='نقاطي': return bot.reply_to(m,f"نقاطك: {data['points'].get(sid(m.from_user.id),0)}")
    if text.startswith('بيع نقاطي'):
        uid,gid=sid(m.from_user.id),sid(m.chat.id); pts=data['points'].get(uid,0); nums=re.findall(r'\d+',text); amount=int(nums[0]) if nums else pts
        if amount<=0 or pts<amount: return bot.reply_to(m,'نقاطك ما تكفي')
        data['points'][uid]-=amount; data['messages'].setdefault(gid,{}); data['messages'][gid][uid]=data['messages'][gid].get(uid,0)+amount*5; save_json(DATA_FILE,data)
        return bot.reply_to(m,f'تم بيع {amount} نقطة\nتمت إضافة {amount*5} رسالة')

print('Created protection bot running...')
bot.infinity_polling(skip_pending=True)
