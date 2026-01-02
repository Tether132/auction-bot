import telebot
import requests
import os
from telebot import types
from flask import Flask
from threading import Thread

# --- إعداداتك الخاصة ---
BOT_TOKEN = "8257393953:AAFqii_USR1h7fe2kj4IoSS31e0PDaDikGc"
ADMIN_ID = 93037697
DEV_USER = "@M_9_C"
CHANNEL_ID = "@usbsbyy"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- نظام التشغيل المستمر المتوافق مع Railway ---
@app.route('/')
def home(): 
    return "Bot is Running!"

def run():
    # Railway يحدد المنفذ تلقائياً عبر متغير البيئة PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- واجهة البوت ---
def main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("إرسال طلب مزاد ➕")
    markup.row("طلباتي 📋", "الدعم الفني 🛠")
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, f"أهلاً بك في بوت المزاد.\nالمطور: {DEV_USER}", reply_markup=main_markup())

@bot.message_handler(func=lambda m: m.text == "إرسال طلب مزاد ➕")
def ask_auction(m):
    msg = bot.send_message(m.chat.id, "أرسل رابط الهدية أو معرف اليوزر الآن:")
    bot.register_next_step_handler(msg, send_to_admin)

def send_to_admin(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("قبول ✅", callback_data=f"accept_{m.from_user.id}"),
               types.InlineKeyboardButton("رفض ❌", callback_data=f"reject_{m.from_user.id}"))
    
    bot.send_message(ADMIN_ID, f"👤 طلب من: @{m.from_user.username}\n📝 المحتوى: {m.text}", reply_markup=markup)
    bot.reply_to(m, "✅ تم إرسال طلبك للأدمن.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('accept_'))
def accept(call):
    user_id = call.data.split('_')[1]
    # تنسيق المنشور كما في الصورة
    text = (
        "📊 **New Auction Entry**\n\n"
        f"Gift - Auction offers • [Click]({call.message.text.split(': ')[-1]})\n\n"
        "❞ زايد تدريجيًا ( 1as / 1ton / 1us / 30egp ) ❝\n"
        f"❞ Auction ch : {CHANNEL_ID} ❝"
    )
    
    # النشر في القناة
    pub = bot.send_message(CHANNEL_ID, text, parse_mode="Markdown", disable_web_page_preview=False)
    
    # إشعار للمستخدم
    bot.send_message(user_id, f"🥳 تم قبول طلبك بنجاح!\nرابط المزاد: https://t.me/{CHANNEL_ID[1:]}/{pub.message_id}")
    bot.edit_message_text("✅ تم النشر في القناة.", call.message.chat.id, call.message.message_id)

# --- تشغيل البوت ---
if __name__ == "__main__":
    keep_alive()
    print("Bot started...")
    bot.infinity_polling()