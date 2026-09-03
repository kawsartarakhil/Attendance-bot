from apscheduler.schedulers.asyncio import AsyncIOScheduler
from servicce.lesson_service import get_finished_lessons
from servicce.attendance_service import mark_absent_students

scheduler=AsyncIOScheduler()

async def absence_job():
    lessons=await get_finished_lessons()
    for lesson in lessons:
        await mark_absent_students(lesson["id"])

def start_scheduler():
    scheduler.add_job(absence_job,"interval",minutes=1)
    scheduler.start()