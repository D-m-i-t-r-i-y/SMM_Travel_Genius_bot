import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from flask import Flask, request
from config import TELEGRAM_TOKEN
from handlers import setup_handlers  # Импорт setup_handlers
import threading

# Инициализация бота и хранилища
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация обработчиков
setup_handlers(dp)

# Вебхук для Albato
app = Flask(__name__)

@app.route('/albato-webhook', methods=['POST'])
def albato_webhook():
    data = request.json
    user_id = data.get("user_id")
    status = data.get("status")

    async def send_notification():
        if status == "success":
            await bot.send_message(user_id, text="↗ Пост опубликован!")
        elif status == "error":
            await bot.send_message(user_id, text="× Ошибка публикации.")

    # Запуск асинхронной функции в синхронном контексте
    asyncio.run(send_notification())
    return "OK"

# Запуск Flask в отдельном потоке
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Запуск бота
async def run_bot():
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Запуск Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    asyncio.run(run_bot())