import asyncio
from aiogram import Bot, Dispatcher
from database.connection import init_tables
import handlers.start,handlers.students,handlers.attendance,handlers.teacher,handlers.admin
from config import BOT_TOKEN
from scheduler import start_scheduler

bot=Bot(token=BOT_TOKEN)
dp=Dispatcher()

async def main():
    await init_tables()
    dp.include_router(handlers.start.router)
    dp.include_router(handlers.students.router)
    dp.include_router(handlers.attendance.router)
    dp.include_router(handlers.admin.router)
    dp.include_router(handlers.teacher.router)
    start_scheduler(bot)
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())