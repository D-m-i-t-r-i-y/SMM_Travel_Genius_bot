import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from config import TELEGRAM_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
TOKEN = TELEGRAM_TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Добро пожаловать! Используйте /help для списка команд.")

# Настройка вебхука
async def on_startup(bot: Bot):
    await bot.set_webhook(
        url="https://smmtravelgenius.pythonanywhere.com/telegram-webhook",
        drop_pending_updates=True
    )

# Создание aiohttp-приложения
app = web.Application()
setup_application(app, dp, bot=bot)
webhook_handler = SimpleRequestHandler(dp, bot)
webhook_handler.register(app, path="/telegram-webhook")

if __name__ == "__main__":
    # Запуск сервера
    web.run_app(app, host="localhost", port=8888)