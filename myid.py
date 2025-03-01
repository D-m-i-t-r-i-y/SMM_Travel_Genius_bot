from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import TELEGRAM_TOKEN_MYID

# Запустите бота и отправьте ему команду /myid. Бот вернет ваш ID. t.me/Travel_Genius_MyIdBot
bot = Bot(token=TELEGRAM_TOKEN_MYID)
dp = Dispatcher()

@dp.message(Command("myid"))
async def get_user_id(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await message.answer(f"Ваш ID: {user_id}, @{username}")

if __name__ == '__main__':
    dp.run_polling(bot)