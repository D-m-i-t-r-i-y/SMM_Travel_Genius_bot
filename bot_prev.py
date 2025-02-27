import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from config import TELEGRAM_TOKEN
from handlers import setup_handlers
import logging

# Настройка логирования (добавьте в начало файла)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def main():
    bot = Bot(token=TELEGRAM_TOKEN, session=AiohttpSession())
    dp = Dispatcher()

    # Настройка обработчиков
    setup_handlers(dp)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())