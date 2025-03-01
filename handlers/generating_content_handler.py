import aiohttp
import aiofiles
import asyncio
import logging
import os
import uuid
import inspect
from urllib.parse import unquote
from typing import Optional, Tuple
from pathlib import Path

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.markdown import bold

from services.openai_service import generate_image, generate_article_content
from states.article_states import ArticleStates
from handlers.break_circles import load_config
from handlers.email_handler import process_email
from handlers.admin_utils import notify_admin
from config import PROXYAPI_KEY, IMAGE_STORAGE_PATH, LOGGING_LEVEL, API_SEMAPHORE, DEFAULT_IMAGE

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL)

MAX_STORED_IMAGES = 50

async def download_image(url: str, user_id: int) -> Optional[str]:
    """Загружает и сохраняет изображение с указанного URL"""
    try:
        async with API_SEMAPHORE:
            decoded_url = url #unquote(url)

            if not decoded_url.startswith(('http://', 'https://')):
                logger.error(f"Invalid URL: {decoded_url}")
                return None

            async with aiohttp.ClientSession() as session:
                async with session.get(decoded_url) as response:
                    if response.status != 200:
                        logger.error(f"HTTP Error {response.status} for URL {decoded_url}")
                        return None
                    content = await response.read()

            user_dir = Path(IMAGE_STORAGE_PATH) / str(user_id)
            user_dir.mkdir(parents=True, exist_ok=True)

            file_name = f"{uuid.uuid4()}.jpg"
            file_path = user_dir / file_name

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)

            await _cleanup_old_images(user_dir)
            logger.info(f"Изображение сохранено: {file_path}")
            return str(file_path)

    except Exception as e:
        logger.error(f"Ошибка загрузки: {str(e)}", exc_info=True)
        await notify_admin(f"🖼️ Ошибка загрузки изображения: {str(e)}")
        return None


async def _cleanup_old_images(directory: Path) -> None:
    """Удаляет старые файлы, сохраняя последние MAX_STORED_IMAGES"""
    try:
        images = sorted(directory.glob("*.jpg"), key=os.path.getmtime, reverse=True)
        for old_file in images[MAX_STORED_IMAGES:]:
            old_file.unlink()
            logger.debug(f"Удален устаревший файл: {old_file}")
    except Exception as e:
        logger.warning(f"Ошибка очистки: {str(e)}")


async def _validate_choice(choice: str, titles: list) -> Tuple[bool, Optional[int]]:
    """Проверяет корректность выбора пользователя"""
    try:
        index = int(choice) - 1
        return (True, index) if 0 <= index < len(titles) else (False, None)
    except ValueError:
        return False, None


async def _generate_image_data(title: str, user_id: int) -> Optional[str]:
    """Генерирует и сохраняет изображение, возвращает путь"""
    try:
        async with API_SEMAPHORE:
            image_url = await generate_image(title)
            if not image_url:
                await notify_admin(f"⚠️ Не удалось сгенерировать изображение для: {title}")
                logger.warning("Используется изображение по умолчанию")
                return DEFAULT_IMAGE  # Возвращаем дефолтное изображение

            downloaded_path = await download_image(image_url, user_id)
            return downloaded_path if downloaded_path else DEFAULT_IMAGE  # Запасной вариант

    except Exception as e:
        logger.error(f"Ошибка генерации изображения: {str(e)}")
        await notify_admin(f"🖼️ Критическая ошибка генерации: {str(e)}")
        return DEFAULT_IMAGE


async def _generate_content_data(title: str) -> Optional[str]:
    """Генерирует текст статьи"""
    try:
        async with API_SEMAPHORE:
            content = await generate_article_content(title)
            return content if content else None
    except Exception as e:
        logger.error(f"Ошибка генерации текста: {str(e)}")
        await notify_admin(f"📝 Критическая ошибка генерации: {str(e)}")
        return None


async def process_title(message: types.Message, state: FSMContext):
    """Обработчик выбора заголовка и генерации контента"""
    func_name = inspect.currentframe().f_code.co_name
    logging.info(f"\n\n[{func_name}]:\n"
                 f"Текущие состояния: {await state.get_state()}\n"
                 f"Текущие данные: {await state.get_data()}\n")
    try:
        current_state = await state.get_state()
        user_data = await state.get_data()
        if current_state == ArticleStates.processing_article:
            await message.answer("⏳ Дождитесь завершения текущей генерации!")
            return


        if not (titles := user_data.get("titles")):
            await message.answer("❌ Данные заголовков отсутствуют. Начните заново (/start).")
            await state.clear()
            return

        logging.info(f"\n\n[{func_name}] Выбор заголовка:\n"
                     f"Текущие состояния: {await state.get_state()}\n"
                     f"Текущие данные: {await state.get_data()}\n")

        is_valid, idx = await _validate_choice(message.text, titles)
        if not is_valid:
            await message.answer("🔢 Введите корректный номер из списка (1-10)")
            await state.set_state(ArticleStates.waiting_generations)
            return

        await state.set_state(ArticleStates.processing_article)
        selected_title = titles[idx]
        await state.update_data(selected_title=selected_title)

        logging.info(f"\n\n[{func_name}] Фиксация заголовка в состоянии:\n"
                     f"Текущие состояния: {await state.get_state()}\n"
                     f"Текущие данные: {await state.get_data()}\n")


        # Последовательная генерация
        user_id = message.from_user.id

        # 1. Генерация изображения
        image_path = await _generate_image_data(selected_title, user_id)
        if image_path:
            await message.answer_photo(
                FSInputFile(image_path),
                caption=bold(selected_title),
                parse_mode="MarkdownV2"
            )
            await state.update_data(image_path=image_path)
        else:
            await state.update_data(image_path=DEFAULT_IMAGE)  # Используем дефолтное изображение
            await message.answer("⚠️ Изображение заменено на стандартное")

        # 2. Генерация текста
        content = await _generate_content_data(selected_title)
        if content:
            await message.answer(content[:4000])
            await state.update_data(content=content)
        else:
            await message.answer("⚠️ Текст не сгенерирован. Попробуйте другой запрос.")

        # Завершение процесса
        await state.set_state(ArticleStates.sending_email)
        await message.answer("✅ Генерация завершена! Ознакомьтесь с постом.")
        await process_email(message, state)


        # Параллельная генерация
        # user_id = message.from_user.id
        # image_task = asyncio.create_task(_generate_image_data(selected_title, user_id))
        # content_task = asyncio.create_task(_generate_content_data(selected_title))
        # image_path, content = await asyncio.gather(image_task, content_task)
        #
        # # Отправка результата пользователю
        # if image_path:
        #     await message.answer_photo(
        #         FSInputFile(image_path),
        #         caption=bold(selected_title),
        #         parse_mode="MarkdownV2"
        #     )
        #     await state.update_data(image_path=image_path)
        # else:
        #     await state.update_data(image_path=DEFAULT_IMAGE)
        #     await message.answer("⚠️ Не удалось сгенерировать изображение")
        #
        # await asyncio.sleep(2)  # Пауза для UX
        #
        # if content:
        #     await message.answer(content[:4000])
        #     await state.update_data(content=content)
        # else:
        #     await message.answer("⚠️ Не удалось сгенерировать текст")
        #
        # # Завершение генерации
        # await state.set_state(ArticleStates.sending_email)
        # await message.answer("✅ Генерация завершена! Ознакомьтесь с постом.")
        # await process_email(message, state)  # Передаем управление в email_handler

    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
        await state.clear()
        await message.answer("❌ Произошла ошибка. Попробуйте снова.")