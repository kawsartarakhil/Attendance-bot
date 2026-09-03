from database.connection import get_connection

async def create_notification(user_id,message,notification_type):
    conn=await get_connection()
    try:
        await conn.execute("""
        insert into notifications(user_id,message,notification_type)
        values($1,$2,$3)
        """,user_id,message,notification_type)
    except Exception as er:
        print("create notification error:",er)
    finally:
        await conn.close()


async def get_user_notifications(user_id):
    conn=await get_connection()
    try:
        notifications=await conn.fetch("""
        select * from notifications
        where user_id=$1
        order by created_at desc
        """,user_id)
        return notifications
    except Exception as er:
        print("get user notifications error:",er)
    finally:
        await conn.close()

async def get_unread_notifications(user_id):
    conn=await get_connection()
    try:
        notifications=await conn.fetch("""
        select * from notifications
        where user_id=$1 and is_read=false
        order by created_at desc
        """,user_id)
        return notifications
    except Exception as er:
        print("get unread notifications error:",er)
    finally:
        await conn.close()


async def mark_notification_read(notification_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        update notifications set is_read=true
        where id=$1
        """,notification_id)
    except Exception as er:
        print("mark notification read error:",er)
    finally:
        await conn.close()



from servicce.lesson_service import get_upcoming_lessons_for_reminder
from servicce.student_service import get_group_student_users

async def send_lesson_reminders(bot):
    lessons=await get_upcoming_lessons_for_reminder()
    for lesson in lessons:
        students=await get_group_student_users(lesson["group_id"])
        for student in students:
            await bot.send_message(
                student["telegram_id"],
                f"🔔 Lesson Reminder\n\n"
                f"📚 {lesson['subject']}\n"
                f"🕐 Starts at: {lesson['start_time'].strftime('%H:%M')}\n"
                f"🏫 Room: {lesson['room_name'] or '-'}"
            )




from servicce.lesson_service import get_started_lessons
from servicce.attendance_service import get_students_not_checked_in

async def send_check_in_reminders(bot):
    lessons=await get_started_lessons()
    for lesson in lessons:
        students=await get_students_not_checked_in(lesson["id"])
        for student in students:
            await bot.send_message(
                student["telegram_id"],
                f"⚠️ Your lesson has started!\n\n"
                f"📚 {lesson['subject']}\n"
                f"🕐 Start: {lesson['start_time'].strftime('%H:%M')}\n"
                f"🏫 Room: {lesson['room_name'] or '-'}\n\n"
                f"Please check in."
            )


from servicce.attendance_service import get_students_with_low_attendance

async def send_attendance_warnings(bot):
    students=await get_students_with_low_attendance()
    for student in students:
        percentage=round(student["attended"]*100/student["total_lessons"],2)
        await bot.send_message(
            student["telegram_id"],
            f"⚠️ Attendance Warning\n\n"
            f"Your attendance is {percentage}%.\n"
            f"Total lessons: {student['total_lessons']}\n"
            f"Attended: {student['attended']}\n\n"
            f"Please try to improve your attendance."
        )