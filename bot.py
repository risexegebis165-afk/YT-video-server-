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

# লিঙ্ক সেভ করে রাখার জন্য একটি ডিকশনারি
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "ইউটিউব লিঙ্ক পাঠান। তারপর ফরম্যাট সিলেক্ট করুন।")

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def handle_link(message):
    url = message.text
    user_data[message.chat.id] = url
    
    # বাটন তৈরি
    markup = types.InlineKeyboardMarkup()
    btn_mp3 = types.InlineKeyboardButton("🎵 MP3 (Audio)", callback_data="mp3")
    btn_360p = types.InlineKeyboardButton("📺 360p (Video)", callback_data="360p")
    btn_480p = types.InlineKeyboardButton("📺 480p (Video)", callback_data="480p")
    
    markup.add(btn_mp3)
    markup.add(btn_360p, btn_480p)
    
    bot.send_message(message.chat.id, "আপনি কোন ফরম্যাটে ডাউনলোড করতে চান?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    url = user_data.get(call.message.chat.id)
    if not url:
        bot.answer_callback_query(call.id, "লিঙ্কটি আবার পাঠান।")
        return

    bot.edit_message_text("প্রসেসিং হচ্ছে... একটু অপেক্ষা করুন।", call.message.chat.id, call.message.message_id)
    
    try:
        if call.data == "mp3":
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                'outtmpl': 'downloaded_file.mp3'
            }
            ext = 'mp3'
        else:
            quality = "360" if call.data == "360p" else "480"
            ydl_opts = {
                'format': f'best[height<={quality}][ext=mp4]/best',
                'outtmpl': 'downloaded_file.mp4'
            }
            ext = 'mp4'

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open(f'downloaded_file.{ext}', 'rb') as f:
            if ext == 'mp3':
                bot.send_audio(call.message.chat.id, f)
            else:
                bot.send_video(call.message.chat.id, f)
                
        os.remove(f'downloaded_file.{ext}')
        
    except Exception as e:
        bot.send_message(call.message.chat.id, "সমস্যা হয়েছে! ফাইলটি খুব বড় হতে পারে।")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
    
