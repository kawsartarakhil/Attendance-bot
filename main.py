import asyncio
from aiogram import Bot, Dispatcher
from database.connection import init_tables
import handlers.handlers
from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()



async def main():
    await init_tables()
    dp.include_router(handlers.handlers.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())