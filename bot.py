import telebot
from yt_dlp import YoutubeDL
import os
from flask import Flask
from threading import Thread

# Flask server to keep the bot alive on Render
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

TOKEN = '7988731565:AAGzMDLZEVVBCmgv4oEkfBahbDSV351k5a8'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "রেণ্ডারে বটটি সফলভাবে চলছে! ইউটিউব লিঙ্ক দিন।")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text
    bot.reply_to(message, "ডাউনলোড হচ্ছে... একটু অপেক্ষা করুন।")
    try:
        ydl_opts = {
            'format': 'best[height<=480][ext=mp4]/best',
            'outtmpl': 'video.mp4',
            'noplaylist': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)
        os.remove('video.mp4')
    except Exception as e:
        bot.reply_to(message, "দুঃখিত, কোনো সমস্যা হয়েছে। ফাইলটি খুব বড় হতে পারে।")

if __name__ == "__main__":
    keep_alive() 
    bot.polling(none_stop=True)
