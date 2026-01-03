import telebot
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# --- إعدادات البوت ---
API_TOKEN = '8257393953:AAFqii_USR1h_Yf334r5L0LqOAsNIn5G_jU'
ADMIN_ID = 7447432029  # معرف الآدمن (أنت)
CHANNEL_USERNAME = '@usbsbyy'  # يوزر قناتك

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- وظيفة سحب بيانات الهدية ---
def fetch_gift_info(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # محاولة العثور على اسم المقتنى (الهدية)
            title = soup.find('meta', property='og:title')
            description = soup.find('meta', property='og:description')
            
            name = title['content'] if title else "غير معروف"
            details = description['content'] if description else "لا يوجد وصف"
            
            return f"🎁 **بيانات المقتنى المستخرجة:**\n\n**الاسم:** {name}\n**الوصف:** {details}"
    except Exception as e:
        return f"❌ خطأ أثناء سحب البيانات: {e}"
    return "❌ تعذر العثور على بيانات في هذا الرابط."

# --- أوامر البوت ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "مرحباً بك في بوت مزادات القناة!\n\n"
        "لإرسال طلب مزاد، فقط أرسل رابط الهدية (t.me/nft/...) وسأقوم بسحب بياناتها لك تلقائياً."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: "t.me/nft/" in message.text or "t.me/gift/" in message.text)
def handle_link(message):
    url = message.text.strip()
    bot.reply_to(message, "⏳ جاري فحص الرابط وسحب البيانات...")
    
    gift_data = fetch_gift_info(url)
    
    # إرسال البيانات للمستخدم مع خيار التأكيد
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("إرسال للمراجعة ✅", callback_data="send_to_admin"))
    
    bot.send_message(message.chat.id, gift_data, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "send_to_admin")
def send_to_admin(call):
    bot.forward_message(ADMIN_ID, call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "تم إرسال طلبك للآدمن بنجاح!")
    bot.edit_message_text("✅ تم إرسال المزاد للمراجعة.", call.message.chat.id, call.message.message_id)

# --- تشغيل Flask ليبقى البوت حياً ---
@app.route('/')
def home():
    return "Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    # تشغيل السيرفر في خلفية
    t = Thread(target=run)
    t.start()
    # تشغيل البوت
    bot.polling(non_stop=True)
