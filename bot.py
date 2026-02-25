import telebot
from telebot import types
from yt_dlp import YoutubeDL
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "Bot is Running!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

TOKEN = '7988731565:AAGzMDLZEVVBCmgv4oEkfBahbDSV351k5a8'
bot = telebot.TeleBot(TOKEN)
user_data = {}

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def handle_link(message):
    user_data[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎵 MP3", callback_data="mp3"))
    markup.add(types.InlineKeyboardButton("📺 360p", callback_data="360p"), 
               types.InlineKeyboardButton("🌟 720p", callback_data="720p"))
    bot.send_message(message.chat.id, "ফরম্যাট সিলেক্ট করুন:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    url = user_data.get(call.message.chat.id)
    bot.edit_message_text("ডাউনলোড হচ্ছে...", call.message.chat.id, call.message.message_id)
    try:
        if call.data == "mp3":
            opts = {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}], 'outtmpl': 'f.mp3'}
        else:
            q = "720" if call.data == "720p" else "360"
            opts = {'format': f'best[height<={q}][ext=mp4]/best', 'outtmpl': 'f.mp4'}
        with YoutubeDL(opts) as ydl: ydl.download([url])
        ext = 'mp3' if call.data == "mp3" else 'mp4'
        with open(f'f.{ext}', 'rb') as f:
            if ext == 'mp3': bot.send_audio(call.message.chat.id, f)
            else: bot.send_video(call.message.chat.id, f)
        os.remove(f'f.{ext}')
    except Exception:
        bot.send_message(call.message.chat.id, "ভুল হয়েছে! ফাইলটি ৫০ MB-র বেশি হতে পারে")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
    
