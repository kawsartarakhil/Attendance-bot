from aiogram import Router,types,F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton
from database.connection import get_connection
from servicce.user_services import get_user_tg_id
from servicce.teacher_services import get_teacher_by_user_id
from servicce.lesson_service import get_teacher_today_lessons
from servicce.attendance_service import get_lesson_attendance,edit_attendance
from keyboards.inline import present_lessons_keyboard,late_lessons_keyboard,absent_lessons_keyboard,attendance_lessons_keyboard,attendance_status_keyboard,confirmation_keyboard
from states import ManualAttendanceStates

router=Router()

@router.message(F.text=="Today's Attendance")
async def todays_attendance_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None:
        await message.answer("User not found. Please use /start first.")
        return
    teacher=await get_teacher_by_user_id(user["id"])
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You don't have any lessons today.")
        return
    await message.answer("Select a lesson:",reply_markup=attendance_lessons_keyboard(lessons))

@router.message(F.text=="Present Students")
async def present_students_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None:
        await message.answer("User not found. Please use /start first.")
        return
    teacher=await get_teacher_by_user_id(user["id"])
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You don't have any lessons today.")
        return
    await message.answer("Select a lesson:",reply_markup=present_lessons_keyboard(lessons))

@router.callback_query(F.data.startswith("present_lesson_"))
async def present_lesson_handler(callback: types.CallbackQuery):
    lesson_id=int(callback.data.split("_")[2])
    attendance=await get_lesson_attendance(lesson_id)
    students=[]
    for row in attendance:
        if row["status"] in ("present","left_early"):
            students.append(row)
    if not students:
        await callback.message.answer("There are no present students.")
        await callback.answer()
        return
    for row in students:
        await callback.message.answer(f"Student: {row['full_name']}\nStatus: {row['status']}")
    await callback.answer()

@router.message(F.text=="Late Students")
async def late_students_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None:
        await message.answer("User not found. Please use /start first.")
        return
    teacher=await get_teacher_by_user_id(user["id"])
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You don't have any lessons today.")
        return
    await message.answer("Select a lesson:",reply_markup=late_lessons_keyboard(lessons))

@router.callback_query(F.data.startswith("late_lesson_"))
async def late_lesson_handler(callback: types.CallbackQuery):
    lesson_id=int(callback.data.split("_")[2])
    attendance=await get_lesson_attendance(lesson_id)
    students=[]
    for row in attendance:
        if row["status"]=="late":
            students.append(row)
    if not students:
        await callback.message.answer("There are no late students.")
        await callback.answer()
        return
    for row in students:
        await callback.message.answer(f"Student: {row['full_name']}\nLate: {row['late_minutes']} minutes")
    await callback.answer()

@router.message(F.text=="Absent Students")
async def absent_students_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None:
        await message.answer("User not found. Please use /start first.")
        return
    teacher=await get_teacher_by_user_id(user["id"])
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You don't have any lessons today.")
        return
    await message.answer("Select a lesson:",reply_markup=absent_lessons_keyboard(lessons))

@router.callback_query(F.data.startswith("absent_lesson_"))
async def absent_lesson_handler(callback: types.CallbackQuery):
    lesson_id=int(callback.data.split("_")[2])
    attendance=await get_lesson_attendance(lesson_id)
    students=[]
    for row in attendance:
        if row["status"]=="absent":
            students.append(row)
    if not students:
        await callback.message.answer("There are no absent students.")
        await callback.answer()
        return
    for row in students:
        await callback.message.answer(f"Student: {row['full_name']}\nStatus: {row['status']}" )
    await callback.answer()

@router.callback_query(F.data.startswith("manual_lesson_"))
async def attendance_students_handler(callback: types.CallbackQuery,state: FSMContext):
    lesson_id=int(callback.data.split("_")[2])
    user=await get_user_tg_id(callback.from_user.id)
    if user is None:
        await callback.message.answer("User not found.")
        await callback.answer()
        return
    teacher=await get_teacher_by_user_id(user["id"])
    if teacher is None:
        await callback.message.answer("Teacher profile not found.")
        await callback.answer()
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    allowed=False
    for lesson in lessons:
        if lesson["id"]==lesson_id:
            allowed=True
            break
    if not allowed:
        await callback.message.answer("You cannot edit this lesson.")
        await callback.answer()
        return
    attendance=await get_lesson_attendance(lesson_id)
    if not attendance:
        await callback.message.answer("No attendance records found.")
        await callback.answer()
        return
    keyboard=[]
    for row in attendance:
        keyboard.append([InlineKeyboardButton(text=row["full_name"],callback_data=f"manual_student_{row['id']}")])
    await state.update_data(lesson_id=lesson_id)
    await state.set_state(ManualAttendanceStates.student)
    await callback.message.answer("Select a student:",reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

@router.callback_query(F.data.startswith("manual_student_"))
async def manual_student_handler(callback: types.CallbackQuery,state: FSMContext):
    attendance_id=int(callback.data.split("_")[2])
    await state.update_data(attendance_id=attendance_id)
    await state.set_state(ManualAttendanceStates.status)
    await callback.message.answer("Select status:",reply_markup=attendance_status_keyboard(attendance_id))
    await callback.answer()

@router.callback_query(F.data.startswith("status_"))
async def change_attendance_status_handler(callback: types.CallbackQuery,state: FSMContext):
    parts=callback.data.split("_")
    status=parts[1]
    attendance_id=int(parts[2])
    await state.update_data(status=status,attendance_id=attendance_id)
    await state.set_state(ManualAttendanceStates.reason)
    await callback.message.answer("Enter the reason:")
    await callback.answer()

@router.message(ManualAttendanceStates.reason)
async def attendance_reason_handler(message: types.Message,state: FSMContext):
    await state.update_data(reason=message.text)
    await state.set_state(ManualAttendanceStates.confirm)
    await message.answer("Confirm attendance correction?",reply_markup=confirmation_keyboard("attendance"))

@router.callback_query(F.data=="confirm_attendance")
async def confirm_attendance_handler(callback: types.CallbackQuery,state: FSMContext):
    data=await state.get_data()
    conn=await get_connection()
    try:
        attendance=await conn.fetchrow("""
        select * from attendance_records
        where id=$1
        """,data["attendance_id"])
    except Exception as er:
        print("get attendance for edit error:",er)
        attendance=None
    finally:
        await conn.close()
    if attendance is None:
        await callback.message.answer("Attendance record not found.")
        await state.clear()
        await callback.answer()
        return
    user=await get_user_tg_id(callback.from_user.id)
    if user is None:
        await callback.message.answer("User not found.")
        await state.clear()
        await callback.answer()
        return
    teacher=await get_teacher_by_user_id(user["id"])
    if teacher is None:
        await callback.message.answer("Teacher profile not found.")
        await state.clear()
        await callback.answer()
        return
    await edit_attendance(data["attendance_id"],user["id"],attendance["status"],data["status"],data["reason"])
    await callback.message.answer(f"Attendance updated successfully.\n\nOld status: {attendance['status']}\nNew status: {data['status']}\nReason: {data['reason']}")
    await state.clear()
    await callback.answer()

@router.callback_query(F.data=="cancel_attendance")
async def cancel_attendance_handler(callback: types.CallbackQuery,state: FSMContext):
    await state.clear()
    await callback.message.answer("Attendance correction cancelled.")
    await callback.answer()