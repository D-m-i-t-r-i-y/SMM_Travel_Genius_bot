from aiogram import Bot
import os
import logging
from config import bot

async def notify_admin(error_msg: str, bot: Bot = bot):
    try:
        admin_id = os.getenv("ADMIN_TELEGRAM_ID")
        if not admin_id:
            logging.error("ADMIN_TELEGRAM_ID не установлен в окружении")
            return

        await bot.send_message(
            chat_id=int(admin_id),
            text=f"🚨 Ошибка: {error_msg}"
        )
    except Exception as e:
        logging.error(f"Ошибка уведомления администратора: {e}")