import telebot
import yt_dlp
import os
from datetime import datetime

# ⚠️ لا تغير هذه الثوابت أبداً!
API_TOKEN = "8998965513:AAGH1xbEsqDcmds6BC0gGM9UhcV-YVBAOQ4"
CHANNEL_USERNAME = "@ZamanCartoon17"
ADMIN_ID = 8880835062

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

CARTOONS = [
    {"title": "الأسد الملك 🦁", "query": "the lion king"},
    {"title": "فروزن ❄️", "query": "frozen"},
    {"title": "موانا 🌊", "query": "moana"},
    {"title": "رابونزل 👸", "query": "tangled"},
]

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return True

def get_video_formats(url):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'فيديو'),
                'id': info.get('id', 'unknown'),
                'duration': info.get('duration', 0),
                'url': url
            }
    except Exception as e:
        return None

def get_quality_buttons(video_id, video_url):
    markup = telebot.types.InlineKeyboardMarkup()
    qualities = [
        ("1080p 🎬", f"dl_1080_{video_id}"),
        ("720p 📹", f"dl_720_{video_id}"),
        ("480p 📺", f"dl_480_{video_id}"),
        ("240p 📱", f"dl_240_{video_id}"),
        ("🎵 MP3", f"dl_mp3_{video_id}"),
    ]
    for text, callback in qualities:
        markup.add(telebot.types.InlineKeyboardButton(text, callback_data=callback))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    if not check_subscription(message.chat.id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            "🔗 اشترك في القناة", 
            url=f"https://t.me/{CHANNEL_USERNAME[1:]}"
        ))
        bot.send_message(
            message.chat.id,
            f"<b>👋 أهلاً وسهلاً!</b>\n\n"
            f"يجب أن تشترك في القناة أولاً:\n\n"
            f"<b>{CHANNEL_USERNAME}</b>",
            reply_markup=markup
        )
        return
    
    bot.send_message(
        message.chat.id,
        f"<b>🎬 أهلاً بك في SAM A17!</b>\n\n"
        f"<b>👇 اختر:</b>\n"
        f"• أرسل <b>رابط فيديو</b>\n"
        f"• أو اكتب <b>/cartoon</b> للاقتراحات",
        reply_markup=telebot.types.ReplyKeyboardMarkup([
            ["/cartoon", "/help"]
        ])
    )

@bot.message_handler(commands=['cartoon'])
def cartoon_suggestions(message):
    if not check_subscription(message.chat.id):
        bot.send_message(message.chat.id, "❌ اشترك أولاً")
        return
    
    markup = telebot.types.InlineKeyboardMarkup()
    for cartoon in CARTOONS:
        markup.add(telebot.types.InlineKeyboardButton(
            cartoon["title"],
            url=f"https://www.youtube.com/results?search_query={cartoon['query']}"
        ))
    bot.send_message(message.chat.id, "🎬 <b>اقترحاتنا:</b>", reply_markup=markup)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "<b>📖 الطريقة:</b>\n\n"
        "1️⃣ أرسل رابط الفيديو\n"
        "2️⃣ اختر الجودة\n"
        "3️⃣ انتظر التحميل\n\n"
        "<b>✅ يدعم:</b>\n"
        "• YouTube ✓\n"
        "• Facebook ✓"
    )

@bot.message_handler(func=lambda m: m.text and ('http' in m.text or 'www' in m.text))
def handle_url(message):
    if not check_subscription(message.chat.id):
        bot.send_message(message.chat.id, "❌ اشترك أولاً")
        return
    
    msg = bot.send_message(message.chat.id, "⏳ جاري فحص الرابط...")
    
    info = get_video_formats(message.text)
    if not info:
        bot.edit_message_text(
            "❌ خطأ: لم أستطع فتح الرابط",
            message.chat.id,
            msg.message_id
        )
        return
    
    text = f"<b>📹 {info['title']}</b>\n\n<b>⬇️ اختر الجودة:</b>"
    bot.edit_message_text(
        text,
        message.chat.id,
        msg.message_id,
        reply_markup=get_quality_buttons(info['id'], info['url'])
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def download_handler(call):
    bot.answer_callback_query(call.id, "⏳ جاري التحضير...")
    bot.send_message(
        call.message.chat.id,
        "⏳ <b>قد يستغرق بعض الوقت...</b>\n\n"
        "برجاء الانتظار 🙏"
    )

@bot.message_handler(func=lambda m: True)
def echo(message):
    if not check_subscription(message.chat.id):
        bot.send_message(message.chat.id, "❌ اشترك أولاً")
        return
    
    bot.send_message(
        message.chat.id,
        "❓ أرسل رابط فيديو أو اكتب /help"
    )

if __name__ == '__main__':
    print("🤖 البوت شغّال...")
    bot.infinity_polling()
