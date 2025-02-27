# В файле handlers/confirmation_handler.py
import inspect
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from .email_handler import process_email


async def confirm_settings(message: types.Message, state: FSMContext):
    """После генерации статьи запускаем процесс подтверждения"""
    logging.info(f"\n\n[{inspect.currentframe().f_code.co_name}]:\n"
                 f"Состояние: {await state.get_state()}\n"
                 f"Данные: {await state.get_data()}\n")
    try:
        # Получаем данные из состояния (предполагаем, что они уже сохранены)
        user_data = await state.get_data()

        # Проверяем наличие обязательных данных
        if not user_data.get("content") or not user_data.get("image_path"):
            await message.answer("❌ Отсутствуют данные статьи")
            return

        # Запускаем процесс подтверждения
        await process_email(message, state)

    except Exception as e:
        await message.answer("❌ Ошибка при подготовке подтверждения")
