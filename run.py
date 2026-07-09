#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from backend.bot import bot
from app import app
import threading

load_dotenv()

def run_bot():
    """Chạy Telegram Bot"""
    print("🤖 Khởi động Telegram Bot...")
    bot.run()

def run_flask():
    """Chạy Flask Server"""
    print("🚀 Khởi động Flask Server...")
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Chạy bot và flask cùng lúc
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    flask_thread = threading.Thread(target=run_flask, daemon=False)
    
    bot_thread.start()
    flask_thread.start()
    
    # Giữ chương trình chạy
    try:
        flask_thread.join()
    except KeyboardInterrupt:
        print("\n⛔ Tắt chương trình...")
        sys.exit(0)
