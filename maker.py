import os, json, time, random, string, subprocess, threading, requests
import telebot
from config import MAKER_TOKEN, OWNER_ID, OWNER_FORCE_CHANNEL, DEV_USERNAME, SOURCE_NAME, PRICES_TEXT

bot = telebot.TeleBot(MAKER_TOKEN, parse_mode='HTML')
DATA_FILE = 'maker_data.json'
BOTS_DIR = 'made_bots'
os.makedirs(BOTS_DIR, exist_ok=True)
running = {}
waiting = {}
DEFAULT = {'users': {}, 'bots': {}, 'codes': {}, 'stats': {'groups': 0}}
PLANS = {'1m':('شهر واحد',30),'2m':('شهرين',60),'3m':('3 أشهر',90),'6m':('6 أشهر',180),'1y':('سنة كاملة',365)}

def load():
    if not os.path.exists(DATA_FILE): save(DEFAULT.copy())
    try:
        with open(DATA_FILE,'r',encoding='utf-8') as f: d=json.load(f)
    except: d=DEFAULT.copy()
    for k,v in DEFAULT.items(): d.setdefault(k,v)
    return d

def save(d):
    with open(DATA_FILE,'w',encoding='utf-8') as f: json.dump(d,f,ensure_ascii=False,indent=2)

data=load()

def sid(x): return str(x)
def button(text, cb=None, url=None, style='primary'):
    b={'text':text,'style':style}
    if cb: b['callback_data']=cb
    if url: b['url']=url
    return b

def raw(chat_id,text,kb=None):
    p={'chat_id':chat_id,'text':text,'parse_mode':'HTML'}
    if kb: p['reply_markup']=kb
    try: requests.post(f'https://api.telegram.org/bot{MAKER_TOKEN}/sendMessage',json=p,timeout=15)
    except: pass

def main_kb():
    return {'inline_keyboard':[[button('صنع بوت حماية','make')],[button('بوتاتي','mine'),button('تفعيل اشتراك','activate')],[button('اسعار الاشتراكات','prices'),button('الدعم',url=f'https://t.me/{DEV_USERNAME}')],[button('قناة الصانع',url='https://t.me/'+OWNER_FORCE_CHANNEL.replace('@',''))],[button(SOURCE_NAME,url=f'https://t.me/{DEV_USERNAME}',style='danger')]]}

def owner_kb():
    return {'inline_keyboard':[[button('كود شهر','gen_1m'),button('كود شهرين','gen_2m')],[button('كود 3 اشهر','gen_3m'),button('كود 6 اشهر','gen_6m')],[button('كود سنة','gen_1y')],[button('الاحصائيات','stats'),button('البوتات','allbots')],[button('المستخدمين','users')],[button(SOURCE_NAME,url=f'https://t.me/{DEV_USERNAME}',style='danger')]]}

def bot_kb(bid):
    info=data['bots'].get(bid,{})
    return {'inline_keyboard':[[button('حالة البوت: '+('مدفوع' if info.get('plan')=='paid' else 'مجاني'),'noop')],[button('تشغيل',f'run_{bid}'),button('ايقاف',f'stop_{bid}')],[button('تغيير الاشتراك الاجباري',f'force_{bid}')],[button('تفعيل اشتراك','activate'),button('الاسعار','prices')],[button(SOURCE_NAME,url=f'https://t.me/{DEV_USERNAME}',style='danger')]]}

def reg(m):
    u=sid(m.from_user.id)
    if u not in data['users']:
        data['users'][u]={'name':m.from_user.first_name or '', 'username':m.from_user.username or '', 'joined':int(time.time())}
        save(data)

def make_code(plan):
    code='FADI-'+plan.upper()+'-'+''.join(random.choices(string.ascii_uppercase+string.digits,k=6))
    data['codes'][code]={'plan':plan,'days':PLANS[plan][1],'used':False,'created_at':int(time.time())}
    save(data); return code

def bot_info_from_token(token):
    try:
        r=requests.get(f'https://api.telegram.org/bot{token}/getMe',timeout=15).json()
        if r.get('ok'): return r['result']['username'], r['result'].get('first_name','Protection Bot')
    except: pass
    return None,None

def create_file(bid):
    info=data['bots'][bid]
    code=open('protection_template.py',encoding='utf-8').read()
    reps={'__BOT_TOKEN__':info['token'],'__OWNER_ID__':str(info['owner_id']),'__BOT_USERNAME__':info['username'],'__DEV_USERNAME__':DEV_USERNAME,'__BOT_ID__':bid,'__MAKER_DATA_FILE__':DATA_FILE,'__OWNER_FORCE_CHANNEL__':OWNER_FORCE_CHANNEL,'__SOURCE_NAME__':SOURCE_NAME}
    for a,b in reps.items(): code=code.replace(a,b)
    path=os.path.join(BOTS_DIR,bid+'.py')
    open(path,'w',encoding='utf-8').write(code)
    return path

def run_bot(bid):
    if bid in running and running[bid].poll() is None: return
    running[bid]=subprocess.Popen(['python',create_file(bid)])

def stop_bot(bid):
    p=running.get(bid)
    if p and p.poll() is None:
        try: p.terminate()
        except: pass
    running.pop(bid,None)

def expire_loop():
    while True:
        now=int(time.time()); ch=False
        for bid,info in data['bots'].items():
            if info.get('plan')=='paid' and info.get('expires_at') and now>info['expires_at']:
                info['plan']='free'; info['expires_at']=None; info['force_channel']=OWNER_FORCE_CHANNEL; ch=True
        if ch: save(data)
        time.sleep(3600)

@bot.message_handler(commands=['start'])
def start(m):
    reg(m)
    if m.from_user.id==OWNER_ID:
        txt=f"✦ لوحة المطور ✦\n\n• عدد المستخدمين : {len(data['users'])}\n• عدد الكروبات : {data.get('stats',{}).get('groups',0)}\n• عدد البوتات المصنوعة : {len(data['bots'])}\n• البوتات المدفوعة : {sum(1 for b in data['bots'].values() if b.get('plan')=='paid')}\n• البوتات المجانية : {sum(1 for b in data['bots'].values() if b.get('plan')=='free')}"
        return raw(m.chat.id,txt,owner_kb())
    raw(m.chat.id,'• هلا بك في صانع بوتات فادي\n\n• اصنع بوت حماية مجاني أو فعّل اشتراك مدفوع.',main_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    try: bot.answer_callback_query(c.id)
    except: pass
    uid=c.from_user.id; d=c.data
    if d=='noop': return
    if d=='prices': return raw(c.message.chat.id,PRICES_TEXT,main_kb())
    if d=='make': waiting[uid]={'step':'token'}; return raw(c.message.chat.id,'ارسل توكن بوت الحماية الجديد:')
    if d=='activate': waiting[uid]={'step':'activate'}; return raw(c.message.chat.id,'ارسل كود التفعيل:')
    if d=='mine':
        arr=[(bid,b) for bid,b in data['bots'].items() if b['owner_id']==uid]
        if not arr: return raw(c.message.chat.id,'ما عندك بوتات بعد.',main_kb())
        for bid,info in arr:
            exp='لا يوجد' if not info.get('expires_at') else time.strftime('%Y-%m-%d',time.localtime(info['expires_at']))
            raw(c.message.chat.id,f"• اسم البوت: {info.get('name')}\n• يوزر البوت: @{info.get('username')}\n• حالة البوت: {'مدفوع' if info.get('plan')=='paid' else 'مجاني'}\n• الاشتراك الإجباري: {info.get('force_channel')}\n• ينتهي: {exp}",bot_kb(bid))
        return
    if d.startswith('gen_') and uid==OWNER_ID:
        plan=d.replace('gen_',''); code=make_code(plan)
        return raw(c.message.chat.id,f"تم إنشاء كود {PLANS[plan][0]}:\n\n<code>{code}</code>\n\nارسله للمستخدم.")
    if d=='stats' and uid==OWNER_ID: return start(c.message)
    if d=='allbots' and uid==OWNER_ID:
        txt='• البوتات:\n\n'+'\n'.join([f"- @{b.get('username')} | {b.get('plan')} | {b.get('owner_id')}" for _,b in list(data['bots'].items())[:40]])
        return raw(c.message.chat.id,txt or 'ماكو بوتات')
    if d=='users' and uid==OWNER_ID:
        txt='• المستخدمين:\n\n'+'\n'.join([f"- {i.get('name')} | @{i.get('username') or 'ماكو'} | {u}" for u,i in list(data['users'].items())[:40]])
        return raw(c.message.chat.id,txt)
    if d.startswith('run_'):
        bid=d.replace('run_',''); info=data['bots'].get(bid)
        if info and (uid==info['owner_id'] or uid==OWNER_ID): run_bot(bid); return raw(c.message.chat.id,'تم تشغيل البوت.')
    if d.startswith('stop_'):
        bid=d.replace('stop_',''); info=data['bots'].get(bid)
        if info and (uid==info['owner_id'] or uid==OWNER_ID): stop_bot(bid); return raw(c.message.chat.id,'تم ايقاف البوت.')
    if d.startswith('force_'):
        bid=d.replace('force_',''); info=data['bots'].get(bid)
        if not info or info['owner_id']!=uid: return
        if info.get('plan')!='paid': return raw(c.message.chat.id,'هذه الميزة للمدفوع فقط. المجاني اشتراكه بقناة الصانع.')
        waiting[uid]={'step':'force','bot_id':bid}; return raw(c.message.chat.id,'ارسل معرف قناتك مع @ مثل:\n@channel')

@bot.message_handler(func=lambda m: True)
def text(m):
    reg(m); uid=m.from_user.id; txt=(m.text or '').strip()
    if uid not in waiting and txt.startswith('تفعيل '): waiting[uid]={'step':'activate'}; txt=txt.replace('تفعيل ','',1).strip()
    if uid not in waiting: return
    st=waiting[uid]
    if st['step']=='token':
        username,name=bot_info_from_token(txt)
        if not username: return raw(m.chat.id,'التوكن غير صحيح، ارسل توكن صحيح.')
        bid=str(int(time.time()))+str(random.randint(100,999))
        data['bots'][bid]={'owner_id':uid,'owner_name':m.from_user.first_name or '', 'owner_username':m.from_user.username or '', 'token':txt,'username':username,'name':name,'type':'protection','plan':'free','force_channel':OWNER_FORCE_CHANNEL,'expires_at':None,'created_at':int(time.time()),'active':True}
        save(data); create_file(bid); run_bot(bid); waiting.pop(uid,None)
        link=f"https://t.me/{m.from_user.username}" if m.from_user.username else f"tg://user?id={uid}"
        raw(OWNER_ID,f"🔔 تم صنع بوت جديد\n\n• الاسم: {m.from_user.first_name}\n• اليوزر: @{m.from_user.username or 'ماكو'}\n• الايدي: <code>{uid}</code>\n• حسابه: {link}\n\n• نوع البوت: حماية\n• اسم البوت: {name}\n• يوزر البوت: @{username}\n• الخطة: مجانية")
        return raw(m.chat.id,f"تم صنع بوت الحماية بنجاح.\n\n• يوزر البوت: @{username}\n• الحالة: مجاني\n• الاشتراك الإجباري: {OWNER_FORCE_CHANNEL}",bot_kb(bid))
    if st['step']=='activate':
        code=txt.replace('تفعيل ','',1).strip(); c=data['codes'].get(code)
        if not c: return raw(m.chat.id,'الكود غير صحيح.')
        if c.get('used'): return raw(m.chat.id,'الكود مستخدم سابقًا.')
        arr=[(bid,b) for bid,b in data['bots'].items() if b['owner_id']==uid]
        if not arr: return raw(m.chat.id,'ما عندك بوت. اصنع بوت أولاً.')
        bid,info=arr[-1]; now=int(time.time()); start=max(now,info.get('expires_at') or now)
        info['plan']='paid'; info['expires_at']=start+c['days']*86400; c['used']=True; c['used_by']=uid; c['used_at']=now
        save(data); waiting.pop(uid,None)
        return raw(m.chat.id,f"تم تفعيل الاشتراك.\n\n• البوت: @{info['username']}\n• المدة: {c['days']} يوم\n• الحالة: مدفوع\n\nتقدر الآن تضيف قناتك للاشتراك الإجباري.",bot_kb(bid))
    if st['step']=='force':
        if not txt.startswith('@'): return raw(m.chat.id,'ارسل معرف القناة مع @')
        bid=st['bot_id']; data['bots'][bid]['force_channel']=txt; save(data); waiting.pop(uid,None)
        return raw(m.chat.id,f'تم تغيير الاشتراك الإجباري إلى:\n{txt}',bot_kb(bid))

threading.Thread(target=expire_loop,daemon=True).start()
print('Maker bot running...')
bot.infinity_polling(skip_pending=True)
