from apscheduler.schedulers.asyncio import AsyncIOScheduler
from servicce.lesson_service import get_finished_lessons
from servicce.attendance_service import mark_absent_students
from servicce.notification_service import send_attendance_warnings, send_check_in_reminders, send_lesson_reminders

scheduler=AsyncIOScheduler()

async def absence_job():
    lessons=await get_finished_lessons()
    for lesson in lessons:
        await mark_absent_students(lesson["id"])

async def reminder_job(bot):
    await send_lesson_reminders(bot)

def start_scheduler(bot):
    scheduler.add_job(absence_job,"interval",minutes=1)
    scheduler.add_job(reminder_job,"interval",minutes=1,args=[bot])
    scheduler.add_job(check_in_reminder_job,"interval",minutes=1,args=[bot])
    scheduler.add_job(attendance_warning_job,"interval",hours=24,args=[bot])
    scheduler.start()


async def check_in_reminder_job(bot):
    await send_check_in_reminders(bot)


async def attendance_warning_job(bot):
    await send_attendance_warnings(bot)