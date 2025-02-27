# Файл: handlers/content_handler.py <- Исправленный Файл: handlers/title_handler.py
from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from states.article_states import ArticleStates
from services.openai_service import generate_titles, generate_image
from handlers.admin_utils import notify_admin
import inspect
import logging
import re

def escape_markdown(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


async def process_content(message: types.Message, state: FSMContext, bot: Bot):
    func_name = inspect.currentframe().f_code.co_name
    current_state = await state.get_state()
    user_data = await state.get_data()
    logging.info(f"\n\n[{func_name}]:\n"
                 f"Состояние: {await state.get_state()}\n"
                 f"Данные: {await state.get_data()}\n")

    try:
        if current_state == ArticleStates.choosing_destination:
            destination = escape_markdown(message.text.strip())

            # Явное сохранение данных
            await state.update_data(destination=destination)

            logging.info(f"\n\n[{func_name}] Фиксация заголовка в состоянии:\n"
                         f"Текущие состояния: {await state.get_state()}\n"
                         f"Текущие данные: {await state.get_data()}\n")

            # Генерируем темы через generate_titles
            titles = await generate_titles(destination)
            if not titles:
                await message.answer("❌ Не удалось сгенерировать темы. Пробуйте еще...")
                return
            else:
                await state.update_data(titles=titles)

            # Форматируем список тем
            titles_list = "\n".join(
                escape_markdown(f"🌴 {idx + 1}. {title}")
                # Используем escape_markdown для обработки специальных символов в темах "{titles}"
                for idx, title in enumerate(titles)
            )

            # Отправляем сообщение
            await message.answer(
                f"🎯 Выберите номер заголовка:\n\n{titles_list}",
                parse_mode="MarkdownV2"
            )
            logging.info(f"\n\n[{func_name}] Сообщение о выборе заголовка:\n"
                         f"Текущие состояния: {await state.get_state()}\n"
                         f"Текущие данные: {await state.get_data()}\n")
            await state.set_state(ArticleStates.waiting_generations)

        else:
            await message.answer("❌ Произошла ошибка. Попробуйте снова.")

    except ValueError:
        await message.answer("❌ Введи число.")
    except Exception as e:
        error_msg = f"Ошибка в {func_name}: {e}"
        logging.error(error_msg)
        await notify_admin(bot, error_msg=error_msg)  # Вызываем функцию уведомления администратора
        await message.answer("❌ Произошла ошибка. Попробуйте снова.")
