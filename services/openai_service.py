import logging
import aiohttp
from config import PROXYAPI_KEY, API_URL
import logging
from handlers.admin_utils import notify_admin
import inspect

async def generate_with_proxyapi(endpoint: str, payload: dict) -> dict:
    headers = {
        "Authorization": f"Bearer {PROXYAPI_KEY}",
        "Content-Type": "application/json"
    }
    func_name = inspect.currentframe().f_code.co_name
    logging.info(f"\n\n[{func_name}]:\n"
                 f"Endpoint: {endpoint}\n"
                 f"Payload: {payload}\n"
                 f"URL: {API_URL}/{endpoint}\n"
                 f"Headers: {headers}\n\n"
                 )
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"{API_URL}/{endpoint}",
                headers=headers,
                json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()


# async def generate_titles(prompt: str) -> list: # ЗАГЛУШКА
#     return [
#         "Открытие нового мира: путешествие по загадочной Кубе",
#         "В поисках настоящей кубинской жизни: исследуем остров с высоты птичьего полета",
#         "Куба: страна сигар и ритмов сальсы",
#         "Тайны и тайны Кубы: путешествие по улицам Гаваны",
#         "Погружение в колорит кубинской культуры: исследуем традиции и обычаи",
#         "Отдых на пляжах Кубы: наслаждаемся солнцем и морем в раю Карибского бассейна",
#         "Куба: история, культура и природа острова свободы",
#         "В поисках приключений на Кубе: джунгли, горы и водопады",
#         "Куба для истинных гурманов: кулинарное путешествие по лучшим ресторанам Гаваны",
#         "Куба: место, где время остановилось и начались приключения"
#     ]


async def generate_titles(prompt: str) -> list:
    func_name = "generate_titles"  # Определяем имя функции
    try:
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{
                "role": "user",
                "content": f"Сгенерируй 10 креативных заголовков до 150 символов для статьи о путешествиях на тему: {prompt}. Формат: 1. Заголовок 1\n2. Заголовок 2..."
            }],
            "temperature": 0.7
        }
        response = await generate_with_proxyapi("chat/completions", payload)
        logging.info("Генерация сервисом заголовков завершена")
        return [line.split('. ', 1)[1] for line in response['choices'][0]['message']['content'].split('\n') if line]
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        await notify_admin(f"Ошибка в {func_name}: {e}")
        return []




# async def generate_article_content(title: str) -> str:
#     return "Содержание статьи"

async def generate_article_content(title: str) -> str:
    func_name = 'generate_article_content'
    try:
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{
                "role": "user",
                "content": f"Напиши подробную статью для блога о путешествиях с заголовком: {title}. Максимум 1500 символов."
            }],
            "temperature": 0.7
        }
        response = await generate_with_proxyapi("chat/completions", payload)
        logging.info("Генерация сервисом содержания статьи завершена")
        return response['choices'][0]['message']['content']

    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        await notify_admin(f"Ошибка в {func_name}: {e}")
        return []

async def generate_prompt_image(title: str, content: str) -> str:
    try:
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                "role": "system",
                "content":  """Твоя задача написать промпт для генерации иллюстрации к статье. """
                            """В промпте нужно учесть, что иллюстрация должна быть реалистичной и привлекать внимание. """
                            """Стиль иллюстрации должен соответствовать стилю статьи. """
                            """Максимум 500 символов."""
                },
                {
                "role": "user",
                "content": f"""На основании заголовка {title} и текста {content} статьи """
                            """создай промпт для генерации иллюстрации к этой статье. """ 
                            """Максимум 500 символов."""
                }
            ],
            "temperature": 0.7
        }
        response = await generate_with_proxyapi("chat/completions", payload)
        logging.info("Генерация сервисом содержания статьи завершена")
        return response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Content generation error: {e}")
        return None

# async def generate_image(prompt: str) -> str:
#     return r"C:\Users\kosyg\PycharmProjects\Archive\SMM_Travel_Genius_draft\user_images\1860772250\yandexart-fbvgtcla7s15vtdqfhpg.jpeg"

async def generate_image(prompt: str) -> str:
    try:
        payload = {
            "model": "dall-e-3",
            "prompt": (f"Реалистичное фото для статьи о путешествиях: {prompt}."
                      "Цель: создать картинку, которая вызывает желание посетить эти места" 
                      "и она будет соответствовать статье. ")[:4000],
            "size": "1024x1024",
            "n": 1,
            "style": "natural"
            #"quality": "standard"
        }
        response = await generate_with_proxyapi("images/generations", payload)
        logging.info(f"Генерация сервисом иллюстрации завершена {response['data'][0]['url']}")
        return response['data'][0]['url']
    except Exception as e:
        logging.error(f"Image generation error: {e}")
        return None