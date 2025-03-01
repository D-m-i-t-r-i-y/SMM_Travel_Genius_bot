from aiogram import types
from aiogram.fsm.context import FSMContext
from states.article_states import ArticleStates
from handlers.break_circles import load_config, is_bot_user
from handlers.stop_handler import stop_handler
import logging
import inspect

async def start_handler(message: types.Message, state: FSMContext):
    # Сброс данных
    await state.clear()
    logging.info(f"\n\n[{inspect.currentframe().f_code.co_name}]:\n"
                 f"Состояние: {await state.get_state()}\n"
                 f"Данные: {await state.get_data()}\n")

    # Загрузка конфигурации
    user_id = message.from_user.id
    username = message.from_user.username
    if not is_bot_user(username):
        await message.answer("⚠️ Вас нет в списке пользователей бота ⚠️")
        await stop_handler(message, state)
    else:
        config = load_config(user_id)

        intro =("Привет!\n\n"
            "🌟 <b>Я - SMM-ассистент TRAVEL-блогера</b> 🌟\n\n"
            "📋 <b>Ты можешь задать следующие команды:</b>\n"
            "• /start — начать сеанс работы (перезапуск бота).\n"
            "• /set_group — задать ID-телеграм блога(группы).\n"
            "• /set_schedule — установить время публикации.\n"
            "• /generate — начать авто-генерацию контента.\n"
            "• /stop — завершить сеанс работы.\n\n"
            )
        #await message.answer(intro, parse_mode="HTML")
        # Формирование сообщения с командами и конфигом
        config_text = intro +  (
            f"⚙️ <b>Текущие настройки:</b>\n"
            f"• Группа: {config.get('group_id', 'не задана')}\n"
            f"• Время публикации: {config.get('schedule_time', 'автоматически')}\n\n"
            "📋 <b>Доступные команды:</b>\n"
            "/start\n"
            "/set_group\n"
            "/set_schedule\n"
            "/generate \n"
            "/stop"
        )

        await message.answer(config_text, parse_mode="HTML")
        await state.set_state(ArticleStates.waiting_command)