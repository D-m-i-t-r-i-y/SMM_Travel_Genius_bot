from aiogram import types
from aiogram.fsm.context import FSMContext
from states.article_states import ArticleStates
from handlers.break_circles import  load_config, is_bot_user
from handlers.admin_utils import notify_admin
from handlers.stop_handler import stop_handler
import logging
import inspect

async def handle_generate(message: types.Message, state: FSMContext):
    func_name = inspect.currentframe().f_code.co_name
    logging.info(f"[{func_name}] Текущие данные состояния: {await state.get_data()}")
    if not is_bot_user(message.from_user.username):
        await message.answer("⚠️ Вас нет в списке пользователей бота ⚠️")
        await stop_handler(message, state)
    else:
        try:
            # Проверка наличия группы
            config = load_config(message.from_user.id)
            if not config.get("group_id"):
                await message.answer("❌ Группа не настроена! Используйте /set_group")
                return
            # Начало цикла генерации
            await message.answer("🏞️ Напиши название места, например: <i>Бали, Индонезия</i>", parse_mode="HTML")

            await state.set_state(ArticleStates.choosing_destination)

        except Exception as e:
            logging.error(f"Ошибка в {func_name}: {e}")
            await message.answer("❌ Не удалось загрузить конфигурацию для пользователя (из user_configs.json)")
