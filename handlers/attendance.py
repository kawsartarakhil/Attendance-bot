from aiogram import Router,types,F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton
from servicce.user_services import get_user_tg_id
from servicce.teacher_services import get_teacher_by_user_id
from servicce.student_service import get_student_by_user_id,get_student_group
from servicce.lesson_service import get_teacher_today_lessons,get_current_lesson,get_upcoming_lessons,get_group_lessons,get_lesson_by_id
from servicce.attendance_service import check_in,check_out,get_attendance_record,get_student_attendance,get_lesson_attendance,get_attendance_percentage,edit_attendance
from servicce.group_service import get_group_students,get_teacher_groups
from datetime import date
from keyboards.inline import lessons_keyboard,present_lessons_keyboard,late_lessons_keyboard,absent_lessons_keyboard,attendance_lessons_keyboard,attendance_status_keyboard,confirmation_keyboard
from states import ManualAttendanceStates

router=Router()

def status_text(status):
    if status=="present":
        return "✅ Present"
    if status=="late":
        return "⏰ Late"
    if status=="absent":
        return "❌ Absent"
    if status=="excused":
        return "🟡 Excused"
    if status=="left_early":
        return "🚪 Left Early"
    return "⚪ Not marked"

def time_text(value):
    if value is None:
        return "-"
    if hasattr(value,"strftime"):
        return value.strftime("%H:%M")
    return str(value)

async def get_student(message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None:
        return None
    return await get_student_by_user_id(user["id"])

async def get_teacher(message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None:
        return None
    return await get_teacher_by_user_id(user["id"])

@router.message(F.text=="Check In")
async def check_in_handler(message:types.Message):
    student=await get_student(message)
    if student is None:
        await message.answer("Student profile not found.")
        return
    group=await get_student_group(student["id"])
    if group is None:
        await message.answer("You are not assigned to any group.")
        return
    lesson=await get_current_lesson(group["id"])
    if lesson is None:
        await message.answer("There is no active lesson right now.")
        return
    result=await check_in(lesson["id"],student["id"])
    if result is False:
        await message.answer("You cannot check in. You may have already checked in.")
        return
    record=await get_attendance_record(lesson["id"],student["id"])
    await message.answer(
        f"✅ Check-in successful!\n\n"
        f"📚 Subject: {lesson['subject']}\n"
        f"👥 Group: {lesson['group_name']}\n"
        f"📥 Check in: {time_text(record['check_in_time'])}\n"
        f"Status: {status_text(record['status'])}\n"
        f"⏰ Late: {record['late_minutes'] or 0} minutes"
    )

@router.message(F.text=="Check Out")
async def check_out_handler(message:types.Message):
    student=await get_student(message)
    if student is None:
        await message.answer("Student profile not found.")
        return
    group=await get_student_group(student["id"])
    if group is None:
        await message.answer("You are not assigned to any group.")
        return
    lesson=await get_current_lesson(group["id"])
    if lesson is None:
        await message.answer("There is no active lesson right now.")
        return
    result=await check_out(lesson["id"],student["id"])
    if result is False:
        await message.answer("You cannot check out. Make sure you checked in first.")
        return
    record=await get_attendance_record(lesson["id"],student["id"])
    await message.answer(
        f"✅ Check-out successful!\n\n"
        f"📚 Subject: {lesson['subject']}\n"
        f"📥 Check in: {time_text(record['check_in_time'])}\n"
        f"📤 Check out: {time_text(record['check_out_time'])}\n"
        f"🚪 Early leave: {record['early_leave_minutes'] or 0} minutes\n"
        f"⏱ Time in class: {record['time_in_class'] or 0} minutes"
    )

@router.message(F.text=="Today's Lesson")
async def todays_lesson_handler(message:types.Message):
    student=await get_student(message)
    if student is None:
        await message.answer("Student profile not found.")
        return
    group=await get_student_group(student["id"])
    if group is None:
        await message.answer("You are not assigned to any group.")
        return
    lessons=await get_group_lessons(group["id"])
    if not lessons:
        await message.answer("You have no lessons today.")
        return
    lessons=[lesson for lesson in lessons if lesson["lesson_date"]==date.today()]    
    if not lessons:
        await message.answer("You have no lessons today.")
        return
    await message.answer("📅 Today's Lessons:",reply_markup=lessons_keyboard(lessons))

@router.message(F.text=="Upcoming Lessons")
async def upcoming_lessons_handler(message:types.Message):
    student=await get_student(message)
    if student is None:
        await message.answer("Student profile not found.")
        return
    group=await get_student_group(student["id"])
    if group is None:
        await message.answer("You are not assigned to any group.")
        return
    lessons=await get_upcoming_lessons(group["id"])
    if not lessons:
        await message.answer("There are no upcoming lessons.")
        return
    await message.answer("📚 Upcoming Lessons:",reply_markup=lessons_keyboard(lessons))

@router.callback_query(F.data.startswith("lesson_"))
async def lesson_handler(callback:types.CallbackQuery):
    lesson_id=int(callback.data.split("_")[1])
    lesson=await get_lesson_by_id(lesson_id)
    if lesson is None:
        await callback.answer("Lesson not found.",show_alert=True)
        return
    await callback.message.answer(
        f"📚 {lesson['subject']}\n"
        f"👥 Group: {lesson['group_name']}\n"
        f"👨‍🏫 Teacher: {lesson['teacher_name']}\n"
        f"🏫 Room: {lesson['room_name'] or '-'}\n"
        f"📅 Date: {lesson['lesson_date']}\n"
        f"🕐 Time: {time_text(lesson['start_time'])} - {time_text(lesson['end_time'])}\n"
        f"📌 Status: {lesson['status']}"
    )
    await callback.answer()

@router.message(F.text=="My Group")
async def my_group_handler(message:types.Message):
    student=await get_student(message)
    if student is None:
        await message.answer("Student profile not found.")
        return
    group=await get_student_group(student["id"])
    if group is None:
        await message.answer("You are not assigned to any group.")
        return
    await message.answer(
        f"👥 My Group\n\n"
        f"Group: {group['name']}\n"
        f"📚 Course: {group['course_name']}"
    )

@router.message(F.text=="My Attendance")
async def my_attendance_handler(message:types.Message):
    student=await get_student(message)
    if student is None:
        await message.answer("Student profile not found.")
        return
    records=await get_student_attendance(student["id"])
    percentage=await get_attendance_percentage(student["id"])
    present=0
    late=0
    absent=0
    excused=0
    left_early=0
    for record in records or []:
        if record["status"]=="present":
            present+=1
        elif record["status"]=="late":
            late+=1
        elif record["status"]=="absent":
            absent+=1
        elif record["status"]=="excused":
            excused+=1
        elif record["status"]=="left_early":
            left_early+=1
    await message.answer(
        f"📊 My Attendance\n\n"
        f"📚 Total lessons: {len(records or [])}\n"
        f"✅ Present: {present}\n"
        f"⏰ Late: {late}\n"
        f"❌ Absent: {absent}\n"
        f"🟡 Excused: {excused}\n"
        f"🚪 Left Early: {left_early}\n\n"
        f"📈 Attendance: {percentage}%"
    )

@router.message(F.text=="Attendance History")
async def attendance_history_handler(message:types.Message):
    student=await get_student(message)
    if student is None:
        await message.answer("Student profile not found.")
        return
    records=await get_student_attendance(student["id"])
    if not records:
        await message.answer("You have no attendance history.")
        return
    for record in records[:20]:
        await message.answer(
            f"📚 {record['subject']}\n"
            f"📅 {record['lesson_date']}\n"
            f"🕐 {time_text(record['start_time'])} - {time_text(record['end_time'])}\n"
            f"Status: {status_text(record['status'])}\n"
            f"⏰ Late: {record['late_minutes'] or 0} min\n"
            f"🚪 Early: {record['early_leave_minutes'] or 0} min\n"
            f"⏱ Time: {record['time_in_class'] or 0} min"
        )

@router.message(F.text=="My Groups")
async def my_groups_handler(message:types.Message):
    teacher=await get_teacher(message)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    groups=await get_teacher_groups(teacher["id"])
    if not groups:
        await message.answer("You have no assigned groups.")
        return
    for group in groups:
        students=await get_group_students(group["id"])
        await message.answer(
            f"👥 {group['name']}\n"
            f"📚 Course: {group['course_name']}\n"
            f"👨‍🎓 Students: {len(students)}"
        )

@router.message(F.text=="Today's Lessons")
async def teacher_today_lessons_handler(message:types.Message):
    teacher=await get_teacher(message)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You don't have any lessons today.")
        return
    await message.answer("📅 Today's Lessons:",reply_markup=lessons_keyboard(lessons))

@router.message(F.text=="Today's Attendance")
async def todays_attendance_handler(message:types.Message):
    teacher=await get_teacher(message)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You don't have any lessons today.")
        return
    await message.answer("📊 Select a lesson:",reply_markup=attendance_lessons_keyboard(lessons))

@router.message(F.text=="Present Students")
async def present_students_handler(message:types.Message):
    teacher=await get_teacher(message)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You don't have any lessons today.")
        return
    await message.answer("Select a lesson:",reply_markup=present_lessons_keyboard(lessons))

@router.callback_query(F.data.startswith("present_lesson_"))
async def present_lesson_handler(callback:types.CallbackQuery):
    lesson_id=int(callback.data.split("_")[2])
    attendance=await get_lesson_attendance(lesson_id)
    students=[row for row in attendance if row["status"] in ("present","left_early")]
    if not students:
        await callback.message.answer("There are no present students.")
        await callback.answer()
        return
    for row in students:
        await callback.message.answer(f"👤 {row['full_name']}\nStatus: {status_text(row['status'])}")
    await callback.answer()

@router.message(F.text=="Late Students")
async def late_students_handler(message:types.Message):
    teacher=await get_teacher(message)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You don't have any lessons today.")
        return
    await message.answer("Select a lesson:",reply_markup=late_lessons_keyboard(lessons))

@router.callback_query(F.data.startswith("late_lesson_"))
async def late_lesson_handler(callback:types.CallbackQuery):
    lesson_id=int(callback.data.split("_")[2])
    attendance=await get_lesson_attendance(lesson_id)
    students=[row for row in attendance if row["status"]=="late"]
    if not students:
        await callback.message.answer("There are no late students.")
        await callback.answer()
        return
    for row in students:
        await callback.message.answer(f"👤 {row['full_name']}\n⏰ Late: {row['late_minutes'] or 0} minutes")
    await callback.answer()

@router.message(F.text=="Absent Students")
async def absent_students_handler(message:types.Message):
    teacher=await get_teacher(message)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You don't have any lessons today.")
        return
    await message.answer("Select a lesson:",reply_markup=absent_lessons_keyboard(lessons))

@router.callback_query(F.data.startswith("absent_lesson_"))
async def absent_lesson_handler(callback:types.CallbackQuery):
    lesson_id=int(callback.data.split("_")[2])
    attendance=await get_lesson_attendance(lesson_id)
    students=[row for row in attendance if row["status"]=="absent"]
    if not students:
        await callback.message.answer("There are no absent students.")
        await callback.answer()
        return
    for row in students:
        await callback.message.answer(f"👤 {row['full_name']}\nStatus: ❌ Absent")
    await callback.answer()

@router.message(F.text=="Manual Attendance")
async def manual_attendance_handler(message:types.Message,state:FSMContext):
    teacher=await get_teacher(message)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You don't have any lessons today.")
        return
    await state.clear()
    await message.answer("📝 Select a lesson:",reply_markup=attendance_lessons_keyboard(lessons))

@router.callback_query(F.data.startswith("manual_lesson_"))
async def manual_lesson_handler(callback:types.CallbackQuery,state:FSMContext):
    lesson_id=int(callback.data.split("_")[2])
    attendance=await get_lesson_attendance(lesson_id)
    if not attendance:
        await callback.answer("No attendance records found.",show_alert=True)
        return
    keyboard=[]
    for row in attendance:
        keyboard.append([InlineKeyboardButton(text=row["full_name"],callback_data=f"manual_student_{row['id']}")])
    await state.update_data(lesson_id=lesson_id)
    await state.set_state(ManualAttendanceStates.student)
    await callback.message.answer("Select a student:",reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

@router.callback_query(F.data.startswith("manual_student_"))
async def manual_student_handler(callback:types.CallbackQuery,state:FSMContext):
    attendance_id=int(callback.data.split("_")[2])
    data=await state.get_data()
    attendance=await get_lesson_attendance(data["lesson_id"])
    selected=None
    for row in attendance:
        if row["id"]==attendance_id:
            selected=row
            break
    if selected is None:
        await callback.answer("Attendance record not found.",show_alert=True)
        return
    await state.update_data(
        attendance_id=attendance_id,
        student_id=selected["student_id"],
        old_status=selected["status"]
    )
    await state.set_state(ManualAttendanceStates.status)
    await callback.message.answer(
        f"👤 {selected['full_name']}\n"
        f"Current status: {status_text(selected['status'])}\n\n"
        f"Select new status:",
        reply_markup=attendance_status_keyboard(attendance_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("status_"))
async def status_handler(callback:types.CallbackQuery,state:FSMContext):
    parts=callback.data.split("_")
    status=parts[1]
    attendance_id=int(parts[2])
    data=await state.get_data()
    if data.get("attendance_id")!=attendance_id:
        await callback.answer("Invalid attendance record.",show_alert=True)
        return
    await state.update_data(new_status=status)
    await state.set_state(ManualAttendanceStates.reason)
    await callback.message.answer("Enter the reason:")
    await callback.answer()

@router.message(ManualAttendanceStates.reason)
async def attendance_reason_handler(message:types.Message,state:FSMContext):
    if not message.text:
        await message.answer("Please enter a reason.")
        return
    await state.update_data(reason=message.text)
    await state.set_state(ManualAttendanceStates.confirm)
    data=await state.get_data()
    await message.answer(
        f"Confirm attendance correction?\n\n"
        f"Old status: {status_text(data['old_status'])}\n"
        f"New status: {status_text(data['new_status'])}\n"
        f"Reason: {data['reason']}",
        reply_markup=confirmation_keyboard("attendance")
    )

@router.callback_query(F.data=="confirm_attendance")
async def confirm_attendance_handler(callback:types.CallbackQuery,state:FSMContext):
    data=await state.get_data()
    user=await get_user_tg_id(callback.from_user.id)
    if user is None:
        await callback.answer("User not found.",show_alert=True)
        return
    await edit_attendance(
        data["attendance_id"],
        user["id"],
        data["old_status"],
        data["new_status"],
        data["reason"]
    )
    await state.clear()
    await callback.message.answer("✅ Attendance updated successfully.")
    await callback.answer()

@router.callback_query(F.data=="cancel_attendance")
async def cancel_attendance_handler(callback:types.CallbackQuery,state:FSMContext):
    await state.clear()
    await callback.message.answer("❌ Attendance correction cancelled.")
    await callback.answer()