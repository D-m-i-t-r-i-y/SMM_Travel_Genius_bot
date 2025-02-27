from aiogram.fsm.state import State, StatesGroup

class ArticleStates(StatesGroup):
    # Основной процесс генерации

    choosing_destination = State()   # Выбор места\темы
    selecting_topic = State()        # Выбор темы
    waiting_generations = State()    # Получение генераций контента
    waiting_confirmation = State()   # Подтверждение публикации
    processing_article = State()     # Генерация статьи, защита от повтора
    sending_email = State()          # Отправка по почте

    # Настройки
    waiting_schedule = State()       # Настройка времени
    waiting_group = State()          # Настройка группы

    # Базовое состояние
    waiting_command = State()        # Основное состояние после /start
