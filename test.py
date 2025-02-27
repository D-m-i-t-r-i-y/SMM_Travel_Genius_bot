# test_api.py
import asyncio
from services.openai_service import generate_image, generate_titles

async def test():
    url = await generate_titles("Москва")
    print(url if url else "Ошибка")

asyncio.run(test())