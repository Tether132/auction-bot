import telebot
import requests
from bs4 import BeautifulSoup
from telebot import types
from flask import Flask
from threading import Thread
import re

# --- الإعدادات ---
API_TOKEN = 'ضع_توكن_بوتك_هنا' # استبدل هذا النص بتوكن البوت الخاص بك
ADMIN_ID = 93037697
CHANNEL_ID = '@usbsbyy'

bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot is alive!"

def run(): app.run(host='0.0.0.0', port=8080)

# دالة سحب المعلومات من روابط تليجرام (t.me/nft)
def fetch_gift_info(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # سحب الاسم من العنوان
        title = soup.find('meta', property='og:title')
        full_title = title['content'] if title else "Gift"
        gift_name = full_title.replace('Telegram: Gift ', '').strip()
        
        # سحب السعر من الوصف
        desc = soup.find('meta', property='og:description')
        desc_text = desc['content'] if desc else ""
        
        price = "غير محدد"
        price_match = re.search(r'(\d+\.?\d*)\s?TON', desc_text)
        if price_match:
            price = f"{price_match.group(1)} TON"

        return gift_name, price
    except:
        return "Gift", "غير محدد"

def escape_md(text):
    for char in ['_', '*', '[', ']', '(', ')', '~', '`', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
        text = str(text).replace(char, f'\\{char}')
    return text

temp_data = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('إرسال طلب مزاد ➕'))
    bot.send_message(message.chat.id, "مرحباً بك في بوت المزادات الذكي!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'إرسال طلب مزاد ➕')
def ask_link(message):
    msg = bot.send_message(message.chat.id, "🔗 أرسل رابط الهدية فقط (t.me/nft/...) :")
    bot.register_next_step_handler(msg, process_link)

def process_link(message):
    url = message.text
    if "t.me/" not in url:
        bot.send_message(message.chat.id, "❌ يرجى إرسال رابط تليجرام صحيح.")
        return

    bot.send_message(message.chat.id, "⏳ جاري فحص الرابط وسحب البيانات...")
    name, price = fetch_gift_info(url)
    temp_data[message.chat.id] = {"name": name, "price": price, "url": url}
    
    admin_text = f"🚨 طلب مزاد جديد:\n\nالهدية: {name}\nالسعر: {price}\nالرابط: {url}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("قبول ✅", callback_data=f"accept_{message.chat.id}"),
               types.InlineKeyboardButton("رفض ❌", callback_data=f"reject_{message.chat.id}"))
    
    bot.send_message(ADMIN_ID, admin_text, reply_markup=markup)
    bot.send_message(message.chat.id, "✅ تم إرسال الطلب للإدارة.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('accept_'))
def handle_accept(call):
    u_id = int(call.data.split('_')[1])
    info = temp_data.get(u_id)
    if info:
        n = escape_md(info['name'])
        p = escape_md(info['price'])
        u = escape_md(info['url'])

        # التنسيق بنفس دقة الصورة التي أرسلتها
        auction_msg = (
            f"📊 *Gift details :*\n"
            f"**\n"
            f"> 🎁 *Gift 1:* {n}\n"
            f"> 🔗 *Link:* [اضغط هنا للرابط]({u})\n"
            f"**\n"
            f"💰 *Portal Price :* {p}"
        )
        sent = bot.send_message(CHANNEL_ID, auction_msg, parse_mode="MarkdownV2")
        
        # التعليق التلقائي الفوري
        comment = f"💬 *بداية المناقشة*\n**\n> جاري استقبال المزايدات هنا 👇"
        bot.reply_to(sent, comment, parse_mode="MarkdownV2")
        bot.answer_callback_query(call.id, "✅ تم النشر")

Thread(target=run).start()
bot.infinity_polling()
