from datetime import datetime, timedelta
from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states.article_states import ArticleStates
import logging
import pytz
import inspect

from config import FIXED_EMAIL, TZ, bot
from services.email_service import send_email
from .admin_utils import notify_admin
from .break_circles import load_config


async def process_email(message: types.Message, state: FSMContext):
    func_name = inspect.currentframe().f_code.co_name
    logging.info(f"\n\n[{func_name}]:\n"
                 f"Текущие состояния: {await state.get_state()}\n"
                 f"Текущие данные: {await state.get_data()}\n")
    try:
        user_data = await state.get_data()

        # Если время не установлено - рассчитываем автоматически
        if not user_data.get("schedule_time"):
            timezone = pytz.timezone("Europe/Moscow")
            schedule_time = (datetime.now(timezone) + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
            await state.update_data(schedule_time=schedule_time)  # <-- Сохраняе

        if not user_data.get("image_path") or not user_data.get("content"):
            await message.answer("❌ Отсутствуют необходимые данные (изображение или текст)")
            return

        user_id = message.from_user.id
        config = load_config(user_id)

        # Обработка времени
        schedule_time = user_data.get("schedule_time")  # Берем время только из состояния
        timezone = pytz.timezone(TZ)
        min_time = (datetime.now(pytz.utc) + timedelta(minutes=5)).astimezone(timezone)

        if isinstance(schedule_time, str):
            schedule_time = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M:%S")
            schedule_time = timezone.localize(schedule_time)

        if not schedule_time or schedule_time <= min_time:
            schedule_time = min_time

        formatted_time = schedule_time.strftime("%Y-%m-%d %H:%M:%S")

        final_data = {
            **user_data,
            "email": FIXED_EMAIL,
            "schedule_time": formatted_time,
            "telegram_group": config.get("group_id", "Не указана")
        }

        logging.info(f"['{func_name}']:\n"
                     f"Данные final_data для отправки: {final_data}")

        await state.update_data(final_data=final_data)

        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text="✅ Да, отправить", callback_data="confirm_yes"),
            types.InlineKeyboardButton(text="❌ Отменить", callback_data="confirm_no")
        )

        confirm_message = (
            "⚠️ Подтвердите отправку статьи:\n\n"
            f"📅 Дата публикации: {formatted_time}\n"
            f"👥 Целевая группа: {final_data['telegram_group']}\n\n"
            "Отправить статью в рассылку?"
        )

        await message.answer(confirm_message, reply_markup=builder.as_markup())

    except Exception as e:
        logging.error(f"Ошибка подготовки письма: {str(e)}")
        await notify_admin(f"Ошибка в process_email: {str(e)}")
        await message.answer("❌ Произошла ошибка при подготовке данных")
        await state.clear()


async def handle_confirmation(callback: types.CallbackQuery, state: FSMContext):
    try:
        if callback.data == "confirm_yes":
            user_data = await state.get_data()
            final_data = user_data.get("final_data", {})  # Получаем final_data

            if not final_data:
                await callback.message.edit_text("❌ Данные для отправки утеряны.")
                return

            # Передаем final_data в send_email
            if await send_email(final_data, final_data.get("image_path", "")):
                await callback.message.edit_text(
                    "✅ Статья отправлена!\n"
                    f"📅 Дата: {final_data.get('schedule_time', 'Не указано')}\n"
                    f"👥 Группа: {final_data.get('telegram_group', 'Не указана')}"
                )
            else:
                await callback.message.edit_text("❌ Ошибка отправки!")

        elif callback.data == "confirm_no":
            await state.clear()
            await callback.message.edit_text("❌ Отправка отменена. Состояние сброшено.")

        await callback.answer()

    except Exception as e:
        logging.error(f"Ошибка подтверждения: {str(e)}")
        await notify_admin(f"Ошибка в handle_confirmation: {str(e)}")
        await callback.message.answer("❌ Произошла системная ошибка")
        await state.clear()