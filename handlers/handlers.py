from aiogram import Dispatcher,Router
from aiogram.filters import CommandStart
from aiogram.types import Message



router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("""
    Welcome to Attendance Bot 📚

    Attendance Bot is a Telegram-based student management system designed to make attendance and academic tracking easier.

    Students can check their attendance, grades, lessons, and academic performance. Teachers can manage lessons, record attendance, and add grades. Administrators can manage users and monitor the overall system.

    The bot also includes automatic attendance notifications, reminders, weekly reports, and AI-powered assistance to help students stay informed about their academic progress.""")