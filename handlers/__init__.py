from aiogram.filters import Command, StateFilter
from aiogram import Dispatcher, types
import logging
from states.article_states import ArticleStates
from handlers.start_handler import start_handler
from handlers.generate_handler import handle_generate
from handlers.stop_handler import stop_handler
from handlers.config_handler import (
    set_group_command,
    set_schedule_command,
    process_group,
    process_schedule
)
from handlers.generating_content_handler import process_title, _validate_choice
from handlers.content_handler import process_content
from handlers.email_handler import handle_confirmation, process_email

logger = logging.getLogger(__name__)

# блокировка команд во время генерации
async def _block_commands_during_processing(message: types.Message):
    await message.answer("⏳ Дождитесь завершения генерации!")

def setup_handlers(dp: Dispatcher):
    # Основные команды (доступны всегда)
    dp.message.register(start_handler, Command("start"))
    logger.debug("Обработчик start_handler зарегистрирован для /start")

    dp.message.register(stop_handler, Command("stop"))
    logger.debug("Обработчик stop_handler зарегистрирован для /stop")

    # Команды генерации
    dp.message.register(
        handle_generate,
        Command("generate")
    )
    logger.debug("Обработчик handle_generate зарегистрирован для /generate")

    # Настройки группы
    dp.message.register(
        set_group_command,
        Command("set_group")
    )
    logger.debug("Обработчик set_group_command зарегистрирован для /set_group")

    # Настройки расписания
    dp.message.register(
        set_schedule_command,
        Command("set_schedule")
    )
    logger.debug("Обработчик set_schedule_command зарегистрирован для /set_schedule")

    # Обработка выбора группы
    dp.message.register(
        process_group,
        StateFilter(ArticleStates.waiting_group)
    )
    logger.debug("Обработчик process_group зарегистрирован для waiting_group")

    # Обработка расписания
    dp.message.register(
        process_schedule,
        StateFilter(ArticleStates.waiting_schedule)
    )
    logger.debug("Обработчик process_schedule зарегистрирован для waiting_schedule")

    # Обработка контента (2 состояния)
    dp.message.register(
        process_content,
        StateFilter(ArticleStates.choosing_destination)
    )
    logger.debug("Обработчик process_content зарегистрирован для choosing_destination")


    # Основной обработчик генерации
    dp.message.register(
        process_title,
        StateFilter(ArticleStates.waiting_generations)
    )
    logger.debug("Обработчик process_title зарегистрирован для waiting_generations")

    # Повторная генерация
    dp.message.register(
        process_title,
        StateFilter(ArticleStates.waiting_command),
        Command("retry_generation")
    )
    logger.debug("Обработчик process_title зарегистрирован для retry_generation")

    # Генерация контента
    dp.message.register(
        process_title,
        StateFilter(ArticleStates.processing_article)
    )
    logger.debug("Обработчик process_title зарегистрирован для processing_article")

    # Отправка по почте
    dp.callback_query.register(
        handle_confirmation,
        StateFilter(ArticleStates.sending_email)
    )
    logger.debug("Обработчик handle_confirmation зарегистрирован для sending_email")

    # Блокировка всех команд, кроме /stop, во время генерации
    dp.message.register(
        _block_commands_during_processing,
        lambda msg: msg.text not in ["/stop"],
        StateFilter(ArticleStates.processing_article)
    )
    logger.debug("Обработчик _block_commands_during_processing зарегистрирован для processing_article")

    # В разделе "Отправка по почте":
    dp.message.register(
        process_email,
        StateFilter(ArticleStates.sending_email)
    )
    logger.debug("Обработчик process_email зарегистрирован для sending_email")