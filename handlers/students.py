from aiogram import Router, types, F
from servicce.user_services import get_user_tg_id
from servicce.student_service import get_student_by_user_id, get_student_group
from servicce.lesson_service import get_current_lesson, get_upcoming_lessons
from servicce.attendance_service import check_in,check_out,get_attendance_record,get_student_attendance,get_attendance_percentage
from servicce.notification_service import get_user_notifications
from servicce.ai_service import analyze_student_attendance

router=Router()

@router.message(F.text=="Check In")
async def check_in_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)
    student=await get_student_by_user_id(user["id"])
    if student is None:
        await message.answer("Student profile not found.")
        return
    group=await get_student_group(student["id"])
    if group is None:
        await message.answer("You are not assigned to a group yet.")
        return
    lesson=await get_current_lesson(group["id"])
    if lesson is None:
        await message.answer("There is no current lesson.")
        return
    attendance=await get_attendance_record(lesson["id"],student["id"])
    if attendance is None:
        await message.answer("Attendance record not found.")
        return
    result=await check_in(lesson["id"],student["id"])
    if result is False:
        await message.answer("You already checked in.")
        return
    await message.answer(f"Checked in successfully\n\nSubject: {lesson['subject']}")    

@router.message(F.text=="Check Out")
async def check_out_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)

    student=await get_student_by_user_id(user["id"])
    if student is None:
        await message.answer("Student profile not found.")
        return
    group=await get_student_group(student["id"])
    if group is None:
        await message.answer("You are not assigned to a group yet.")
        return
    lesson=await get_current_lesson(group["id"])
    if lesson is None:
        await message.answer("There is no current lesson.")
        return
    attendance=await get_attendance_record(lesson["id"],student["id"])
    if attendance is None:
        await message.answer("Attendance record not found.")
        return
    result=await check_out(lesson["id"],student["id"])
    if result is False:
        await message.answer("You must check in first or you already checked out.")
        return
    await message.answer(f"Checked out successfully\n\nSubject: {lesson['subject']}")       

@router.message(F.text=="Today's Lesson")
async def today_lesson_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)

    student=await get_student_by_user_id(user["id"])
    if student is None:
        await message.answer("Student profile not found.")
        return
    group=await get_student_group(student["id"])
    if group is None:
        await message.answer("You are not assigned to a group yet.")
        return
    lesson=await get_current_lesson(group["id"])
    if lesson is None:
        await message.answer("There is no current lesson.")
        return
    await message.answer(f"Today's Lesson\n\nSubject: {lesson['subject']}\nGroup: {lesson['group_name']}\nTeacher: {lesson['teacher_name']}\nRoom: {lesson['room_name']}\nTime: {lesson['start_time']} - {lesson['end_time']}")

@router.message(F.text=="Upcoming Lessons")
async def upcoming_lessons_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)

    student=await get_student_by_user_id(user["id"])
    if student is None:
        await message.answer("Student profile not found.")
        return
    group=await get_student_group(student["id"])
    if group is None:
        await message.answer("You are not assigned to a group yet.")
        return
    lessons=await get_upcoming_lessons(group["id"])
    if not lessons:
        await message.answer("There are no upcoming lessons.")
        return
    text="Upcoming Lessons\n\n"
    for lesson in lessons:
        text+=(f"Subject: {lesson['subject']}\nDate: {lesson['lesson_date']}\nTime: {lesson['start_time']} - {lesson['end_time']}\nTeacher: {lesson['teacher_name']}\nRoom: {lesson['room_name']}\n\n")
    await message.answer(text)
@router.message(F.text=="My Group")
async def my_group_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)

    student=await get_student_by_user_id(user["id"])
    if student is None:
        await message.answer("Student profile not found.")
        return
    group=await get_student_group(student["id"])
    if group is None:
        await message.answer("You are not assigned to a group yet.")
        return
    await message.answer(f"My Group\n\nGroup: {group['name']}\nCourse: {group['course_name']}")

@router.message(F.text=="My Attendance")
async def my_attendance_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)

    student=await get_student_by_user_id(user["id"])
    if student is None:
        await message.answer("Student profile not found.")
        return
    percentage=await get_attendance_percentage(student["id"])
    await message.answer(f"My Attendance\n\nAttendance percentage: {percentage}%")

@router.message(F.text=="Attendance History")
async def attendance_history_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)

    student=await get_student_by_user_id(user["id"])
    if student is None:
        await message.answer("Student profile not found.")
        return
    attendance=await get_student_attendance(student["id"])
    if not attendance:
        await message.answer("You don't have any attendance history yet.")
        return
    text="Attendance History\n\n"

    for row in attendance:
        text+=(f"Subject: {row['subject']}\nDate: {row['lesson_date']}\nStatus: {row['status']}\n")
    await message.answer(text)

@router.message(F.text=="Notifications")
async def notifications_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)

    notifications=await get_user_notifications(user["id"])
    if not notifications:
        await message.answer("You don't have any notifications.")
        return

    text="Notifications\n\n"
    for notification in notifications:
        text+=(f"{notification['message']}\nType: {notification['notification_type']}\nRead: {'Yes' if notification['is_read'] else 'No'}\n\n")
    await message.answer(text)

@router.message(F.text=="AI Attendance Analysis")
async def ai_attendance_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)

    student=await get_student_by_user_id(user["id"])
    if student is None:
        await message.answer("Student profile not found.")
        return
    await message.answer("Analyzing your attendance...")
    analysis=await analyze_student_attendance(student["id"])
    await message.answer(
        f"AI Attendance Analysis\n\n{analysis}"
    )