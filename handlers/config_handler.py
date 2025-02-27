# config_handler.py
import json
import logging
import re
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.article_states import ArticleStates
from handlers.break_circles import load_config, save_config
import inspect
from datetime import datetime, timedelta


async def set_group_command(message: types.Message, state: FSMContext):
    func_name = inspect.currentframe().f_code.co_name
    logging.info(f"[{func_name}] Текущие данные состояния: {await state.get_data()}")
    await message.answer("🖋️ Введите ID группы:")
    await state.set_state(ArticleStates.waiting_group)

async def process_group(message: types.Message, state: FSMContext):
    func_name = inspect.currentframe().f_code.co_name
    logging.info(f"[{func_name}] Текущие данные состояния: {await state.get_data()}")

    group_id = message.text.strip()
    if not re.match(r"^-\d+$", group_id):
        await message.answer("❌ Неверный формат! Пример: -100123456789")
        return

    try:
        # Сохраняем данные в состояние
        await state.update_data(group_id=str(group_id))
        user_id = message.from_user.id
        config = load_config(user_id)
        config["group_id"] = str(group_id)  # Сохраняем как строку
        save_config(user_id, config)

        logging.info(f"[{func_name}] Текущие данные состояния: {await state.get_data()}")

        # Проверка сохранения
        updated_config = load_config(user_id)
        if updated_config.get("group_id") != group_id:
            raise Exception("Группа не сохранилась в конфигурации.")

        await message.answer(
            f"✅ Группа <b>{group_id}</b> сохранена!\n\n"
            "Доступные команды:\n"
            "Изменить группу: /set_group\n"
            "Изменить время: /set_schedule\n"
            "Начать генерацию контента: /generate"
            , parse_mode="HTML"
        )
        # Возвращаемся в основное состояние
        await state.set_state(ArticleStates.waiting_command)

    except Exception as e:
        logging.error(f"Ошибка сохранения группы: {e}")
        #await notify_admin(bot, f"Ошибка в {func_name}: {e}")
        await message.answer("❌ Не удалось сохранить группу. Попробуйте позже.")

async def set_schedule_command(message: types.Message, state: FSMContext):
    func_name = inspect.currentframe().f_code.co_name
    logging.info(f"[{func_name}] Текущие данные состояния: {await state.get_data()}")
    await message.answer(
         "⏰ Введите время публикации\n  в формате: ГГГГ-ММ-ДД ЧЧ:ММ:СС\n"
     )
    await state.set_state(ArticleStates.waiting_schedule)


import dateparser
import pytz
from states.article_states import ArticleStates
from handlers.break_circles import load_config, save_config
import logging
from config import TZ

async def process_schedule(message: types.Message, state: FSMContext):
    try:
        user_input = message.text.strip()
        user_id = message.from_user.id
        timezone = pytz.timezone(TZ)  # Указываем нужный часовой пояс

        # Парсим время с учетом часового пояса
        parsed_time = dateparser.parse(
            user_input,
            settings={'TIMEZONE': TZ, 'PREFER_DAY_OF_MONTH': 'first'}
        )

        if not parsed_time:
            raise ValueError("NOT_VALID_TIME")

        # Привязываем время к часовому поясу
        localized_time = timezone.localize(parsed_time)

        # Проверяем, что время в будущем (минимум на 5 минут вперед)
        current_time = datetime.now(timezone)
        if localized_time < current_time + timedelta(minutes=5):
            raise ValueError("OLD_TIME")

        # Сохраняем время в конфиг
        config = load_config(user_id)
        config["schedule_time"] = localized_time.strftime("%Y-%m-%d %H:%M:%S")
        save_config(user_id, config)


        # Отправляем подтверждение
        await message.answer(
            f"✅ Время публикации сохранено:\n"
            f"<b>{localized_time.strftime('%Y-%m-%d %H:%M:%S')}</b>\n"
            "Изменить группу: /set_group\n"
            "Изменить время: /set_schedule\n"
            "Начать генерацию контента: /generate"
            ,parse_mode="HTML"
        )
        # Возвращаемся в основное состояние
        await state.set_state(ArticleStates.waiting_command)


    except ValueError as e:
        error_msg = {
            "NOT_VALID_TIME": "❌ Неверный формат времени:\n⏳ <code>ГГГГ-ММ-ДД ЧЧ:ММ:СС</code>",
            "OLD_TIME": "❌ Время должно быть в будущем:\n⏳ минимум = текущее +5 минут"
        }.get(str(e), "❌ Некорректное значение")
        logging.info(f"Ошибка {e} установки времени: {error_msg}")
        await message.answer(error_msg, parse_mode="HTML")

    except Exception as e:
        logging.error(f"⚠️ Ошибка установки времени: {e}")
        await message.answer("⚠️ Произошла системная ошибка. Попробуйте позже.")
