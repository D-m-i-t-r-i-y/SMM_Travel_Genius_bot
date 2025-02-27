from aiogram import types
from aiogram.fsm.context import FSMContext

async def stop_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🛑 Сеанс завершен. Для начала работы используйте /start.")