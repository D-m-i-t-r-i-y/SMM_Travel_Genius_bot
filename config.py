import os
from aiogram import Bot
from dotenv import load_dotenv
from asyncio import Semaphore

API_SEMAPHORE = Semaphore(2)  # Ограничение параллелизма
LOGGING_LEVEL = "DEBUG"
# Инициализировать логирование в точке входа:
# logging.basicConfig(level=config.LOGGING_LEVEL)
# Для работы логов уровня DEBUG запускайте бота с флагом:
# python -m bot_prev --log-level DEBUG

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_TOKEN_MYID = os.getenv("TELEGRAM_TOKEN_MYID")
PROXYAPI_KEY = os.getenv("PROXYAPI_KEY")
API_URL = "https://api.proxyapi.ru/openai/v1"
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = 465 # для yandex os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
IMAGE_STORAGE_PATH = "user_images"
FIXED_EMAIL = "dmitkos.gpt@gmail.com" #"smmtravelgenius@robot.zapier.com"
IMAGE_STORAGE_PATH = "user_images"
DEFAULT_IMAGE = "picture_without_generation.jpg"
TZ = os.getenv("TZ")
bot = Bot(token=TELEGRAM_TOKEN)

