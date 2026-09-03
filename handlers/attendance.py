from aiogram import Router,types,F
from aiogram.fsm.context import FSMContext
from database.connection import get_connection
from servicce.user_services import get_user_tg_id
from servicce.lesson_service import get_today_lessons,get_lesson_by_id
from servicce.attendance_service import check_in,check_out,get_attendance_record,get_student_attendance,get_attendance_percentage,get_lesson_attendance,get_attendance_by_id,edit_attendance,get_attendance_edits,get_students_with_low_attendance,get_students_with_low_attendance_by_teacher
from keyboards.inline import attendance_lessons_keyboard, present_lessons_keyboard,lessons_keyboard,attendance_status_keyboard
from states import AttendanceStates,ManualAttendanceStates

router=Router()

def lesson_list_keyboard(lessons):
    keyboard=[]
    for lesson in lessons:
        keyboard.append([
            types.InlineKeyboardButton(
                text=f"{lesson['subject']} | {lesson['start_time']}-{lesson['end_time']}",
                callback_data=f"attendance_lesson_{lesson['id']}"
            )
        ])
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


def student_attendance_keyboard(lessons):
    keyboard=[]
    for lesson in lessons:
        keyboard.append([
            types.InlineKeyboardButton(
                text=f"📚 {lesson['subject']} | {lesson['start_time']}",
                callback_data=f"student_attendance_{lesson['id']}"
            )
        ])
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_student_id_by_telegram_id(telegram_id):
    conn=await get_connection()
    try:
        student=await conn.fetchrow("""
        select s.id
        from students s
        join users u on s.user_id=u.id
        where u.telegram_id=$1
        """,str(telegram_id))

        if student:
            return student["id"]

        return None

    except Exception as er:
        print("get student id error:",er)
        return None

    finally:
        await conn.close()


async def get_teacher_id_by_telegram_id(telegram_id):
    conn=await get_connection()
    try:
        teacher=await conn.fetchrow("""
        select t.id
        from teachers t
        join users u on t.user_id=u.id
        where u.telegram_id=$1
        """,int(telegram_id))

        if teacher:
            return teacher["id"]

        return None

    except Exception as er:
        print("get teacher id error:",er)
        return None

    finally:
        await conn.close()


async def get_student_today_lessons(student_id):
    conn=await get_connection()
    try:
        lessons=await conn.fetch("""
        select
        l.id,
        l.subject,
        l.lesson_date,
        l.start_time,
        l.end_time,
        l.group_id
        from lessons l
        join group_students gs on gs.group_id=l.group_id
        where gs.student_id=$1
        and l.lesson_date=current_date
        order by l.start_time
        """,student_id)

        return lessons

    except Exception as er:
        print("get student today lessons error:",er)
        return []

    finally:
        await conn.close()


async def get_teacher_today_lessons(teacher_id):
    conn=await get_connection()
    try:
        lessons=await conn.fetch("""
        select
        l.id,
        l.subject,
        l.lesson_date,
        l.start_time,
        l.end_time,
        l.group_id,
        g.name as group_name
        from lessons l
        join groups g on l.group_id=g.id
        where l.teacher_id=$1
        and l.lesson_date=current_date
        order by l.start_time
        """,teacher_id)

        return lessons

    except Exception as er:
        print("get teacher today lessons error:",er)
        return []

    finally:
        await conn.close()


@router.callback_query(F.data.regexp(r"^checkin_lesson_\d+$"))
async def student_check_in_handler(callback:types.CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"]!="student":
        await callback.answer("Access denied.",show_alert=True)
        return

    student_id=await get_student_id_by_telegram_id(callback.from_user.id)

    if student_id is None:
        await callback.answer("Student profile not found.",show_alert=True)
        return

    lesson_id=int(callback.data.split("_")[2])

    lesson=await get_lesson_by_id(lesson_id)

    if lesson is None:
        await callback.answer("Lesson not found.",show_alert=True)
        return

    result=await check_in(lesson_id,student_id)

    if not result:
        await callback.answer("You have already checked in.",show_alert=True)
        return

    attendance=await get_attendance_record(lesson_id,student_id)
    late_minutes=attendance["late_minutes"] if attendance else 0

    if late_minutes and late_minutes>0:
        await callback.message.answer(
            f"✅ Check-in successful.\n\n"
            f"Lesson: {lesson['subject']}\n"
            f"⏰ Late by {late_minutes} minutes."
        )
    else:
        await callback.message.answer(
            f"✅ Check-in successful.\n\n"
            f"Lesson: {lesson['subject']}\n"
            f"On time."
        )

    await callback.answer()

@router.message(F.text=="Check Out")
async def student_check_out_menu(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)

    if user is None or user["role"]!="student":
        await message.answer("You don't have permission to use check-out.")
        return

    student_id=await get_student_id_by_telegram_id(message.from_user.id)

    if student_id is None:
        await message.answer("Student profile not found.")
        return

    lessons=await get_student_today_lessons(student_id)

    available=[]

    for lesson in lessons:
        attendance=await get_attendance_record(lesson["id"],student_id)

        if attendance and attendance["check_in_time"] and not attendance["check_out_time"]:
            available.append(lesson)

    if not available:
        await message.answer("There are no lessons available for check-out.")
        return

    await message.answer(
        "Select lesson:",
        reply_markup=lessons_keyboard(available)
    )

@router.callback_query(F.data.regexp(r"^checkout_lesson_\d+$"))
async def student_check_out_handler(callback:types.CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"]!="student":
        await callback.answer("Access denied.",show_alert=True)
        return

    student_id=await get_student_id_by_telegram_id(callback.from_user.id)

    if student_id is None:
        await callback.answer("Student profile not found.",show_alert=True)
        return

    lesson_id=int(callback.data.split("_")[2])

    lesson=await get_lesson_by_id(lesson_id)

    if lesson is None:
        await callback.answer("Lesson not found.",show_alert=True)
        return

    result=await check_out(lesson_id,student_id)

    if not result:
        await callback.answer(
            "You cannot check out from this lesson.",
            show_alert=True
        )
        return

    attendance=await get_attendance_record(lesson_id,student_id)

    await callback.message.answer(
        f"🚪 Check-out successful.\n\n"
        f"Lesson: {lesson['subject']}\n"
        f"⏱ Time in class: {attendance['time_in_class'] or 0} minutes\n"
        f"⏰ Late: {attendance['late_minutes'] or 0} minutes\n"
        f"🏃 Early leave: {attendance['early_leave_minutes'] or 0} minutes\n"
        f"Status: {attendance['status']}"
    )

    await callback.answer()


@router.message(F.text=="My Attendance")
async def student_attendance_menu(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)

    if user is None or user["role"]!="student":
        await message.answer("You don't have permission to view attendance.")
        return

    student_id=await get_student_id_by_telegram_id(message.from_user.id)

    if student_id is None:
        await message.answer("Student profile not found.")
        return

    attendance=await get_student_attendance(student_id)
    percentage=await get_attendance_percentage(student_id)

    if not attendance:
        await message.answer(
            f"📊 Attendance: {percentage}%\n\n"
            f"No attendance records yet."
        )
        return

    text=f"📊 Your Attendance\n\nAttendance: {percentage}%\n\n"

    for record in attendance[:20]:
        status=record["status"] or "Not marked"

        text+=(
            f"📚 {record['subject']}\n"
            f"📅 {record['lesson_date']}\n"
            f"⏰ {record['start_time']} - {record['end_time']}\n"
            f"Status: {status}\n"
            f"Late: {record['late_minutes'] or 0} min\n"
            f"Early leave: {record['early_leave_minutes'] or 0} min\n"
            f"Time in class: {record['time_in_class'] or 0} min\n\n"
        )

    await message.answer(text)


@router.message(F.text=="Today's Lessons")
async def today_lessons_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)

    if user is None:
        await message.answer("User not found.")
        return

    if user["role"]=="student":
        student_id=await get_student_id_by_telegram_id(message.from_user.id)

        if student_id is None:
            await message.answer("Student profile not found.")
            return

        lessons=await get_student_today_lessons(student_id)

        if not lessons:
            await message.answer("You have no lessons today.")
            return

        text="📚 Today's Lessons\n\n"

        for lesson in lessons:
            attendance=await get_attendance_record(lesson["id"],student_id)

            status="Not checked in"

            if attendance:
                if attendance["check_out_time"]:
                    status="Checked out"
                elif attendance["check_in_time"]:
                    status="Checked in"

            text+=(
                f"📖 {lesson['subject']}\n"
                f"⏰ {lesson['start_time']} - {lesson['end_time']}\n"
                f"Status: {status}\n\n"
            )

        await message.answer(text)
        return

    if user["role"]=="teacher":
        teacher_id=await get_teacher_id_by_telegram_id(message.from_user.id)

        if teacher_id is None:
            await message.answer("Teacher profile not found.")
            return

        lessons=await get_teacher_today_lessons(teacher_id)

        if not lessons:
            await message.answer("You have no lessons today.")
            return

        text="📚 Today's Lessons\n\n"

        for lesson in lessons:
            text+=(
                f"📖 {lesson['subject']}\n"
                f"👥 Group: {lesson['group_name']}\n"
                f"⏰ {lesson['start_time']} - {lesson['end_time']}\n\n"
            )

        await message.answer(text)
        return

    await message.answer("You don't have permission.")


@router.message(F.text.in_(["Attendance","Today's Attendance"]))
async def teacher_attendance_menu(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)

    if user is None:
        await message.answer("User not found.")
        return

    if user["role"]=="student":
        await student_attendance_menu(message)
        return

    if user["role"]=="teacher":
        teacher_id=await get_teacher_id_by_telegram_id(message.from_user.id)

        if teacher_id is None:
            await message.answer("Teacher profile not found.")
            return

        lessons=await get_teacher_today_lessons(teacher_id)

        if not lessons:
            await message.answer("You have no lessons today.")
            return

        await message.answer(
            "Select a lesson:",
            reply_markup=lesson_list_keyboard(lessons)
        )
        return

    if user["role"]=="admin":
        lessons=await get_today_lessons()

        if not lessons:
            await message.answer("There are no lessons today.")
            return

        await message.answer(
            "Select a lesson:",
            reply_markup=lesson_list_keyboard(lessons)
        )


@router.callback_query(F.data.regexp(r"^attendance_lesson_\d+$"))
async def attendance_lesson_handler(callback:types.CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)

    if user is None:
        await callback.answer("User not found.",show_alert=True)
        return

    if user["role"]=="student":
        return

    lesson_id=int(callback.data.split("_")[2])

    lesson=await get_lesson_by_id(lesson_id)

    if lesson is None:
        await callback.answer("Lesson not found.",show_alert=True)
        return

    attendance=await get_lesson_attendance(lesson_id)

    if not attendance:
        await callback.message.answer("No attendance records found.")
        await callback.answer()
        return

    text=f"📊 Attendance\n\n{lesson['subject']}\n\n"

    for record in attendance:
        status=record["status"] or "Not marked"

        text+=(
            f"👤 {record['full_name']}\n"
            f"Status: {status}\n"
            f"Check in: {record['check_in_time'] or 'Not checked in'}\n"
            f"Check out: {record['check_out_time'] or 'Not checked out'}\n"
            f"Late: {record['late_minutes'] or 0} min\n"
            f"Early leave: {record['early_leave_minutes'] or 0} min\n"
            f"Time in class: {record['time_in_class'] or 0} min\n\n"
        )

    await callback.message.answer(text)
    await callback.answer()


@router.message(F.text=="Attendance Corrections")
async def attendance_corrections_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)

    if user is None or user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return

    lessons=await get_today_lessons()

    if not lessons:
        await message.answer("There are no lessons today.")
        return

    await message.answer(
        "Select lesson for attendance correction:",
        reply_markup=attendance_lessons_keyboard(lessons)
    )


@router.callback_query(F.data.regexp(r"^manual_lesson_\d+$"))
async def manual_lesson_handler(callback:types.CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"] not in ("admin","teacher"):
        await callback.answer("Access denied.",show_alert=True)
        return

    lesson_id=int(callback.data.split("_")[2])

    if user["role"]=="teacher":
        lesson=await get_lesson_by_id(lesson_id)
        teacher_id=await get_teacher_id_by_telegram_id(callback.from_user.id)
        if lesson is None or teacher_id is None or lesson["teacher_id"]!=teacher_id:
            await callback.answer("This is not your lesson.",show_alert=True)
            return

    attendance=await get_lesson_attendance(lesson_id)

    if not attendance:
        await callback.answer("No attendance records.",show_alert=True)
        return

    await state.update_data(lesson_id=lesson_id)

    text="Select student:\n\n"

    keyboard=[]

    for record in attendance:
        keyboard.append([
            types.InlineKeyboardButton(
                text=record["full_name"],
                callback_data=f"manual_attendance_{record['id']}"
            )
        ])

    await callback.message.answer(
        text,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

    await callback.answer()


@router.callback_query(F.data.regexp(r"^manual_attendance_\d+$"))
async def manual_attendance_handler(callback:types.CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"] not in ("admin","teacher"):
        await callback.answer("Access denied.",show_alert=True)
        return

    attendance_id=int(callback.data.split("_")[2])

    attendance=await get_attendance_by_id(attendance_id)

    if attendance is None:
        await callback.answer("Attendance record not found.",show_alert=True)
        return

    if user["role"]=="teacher":
        lesson=await get_lesson_by_id(attendance["lesson_id"])
        teacher_id=await get_teacher_id_by_telegram_id(callback.from_user.id)
        if lesson is None or teacher_id is None or lesson["teacher_id"]!=teacher_id:
            await callback.answer("This is not your lesson.",show_alert=True)
            return

    await state.update_data(
        attendance_id=attendance_id,
        old_status=attendance["status"]
    )

    await state.set_state(ManualAttendanceStates.status)

    await callback.message.answer(
        f"Student: {attendance['full_name']}\n"
        f"Current status: {attendance['status']}\n\n"
        f"Select new status:",
        reply_markup=attendance_status_keyboard(attendance_id)
    )

    await callback.answer()


@router.callback_query(F.data.regexp(r"^status_(present|late|absent|excused|left_early)_\d+$"))
async def manual_status_handler(callback:types.CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"] not in ("admin","teacher"):
        await callback.answer("Access denied.",show_alert=True)
        return

    parts=callback.data.split("_")

    attendance_id=int(parts[-1])
    status="_".join(parts[1:-1])

    attendance=await get_attendance_by_id(attendance_id)

    if attendance is None:
        await callback.answer("Attendance record not found.",show_alert=True)
        return

    await state.update_data(
        attendance_id=attendance_id,
        old_status=attendance["status"],
        new_status=status
    )

    await state.set_state(ManualAttendanceStates.reason)

    await callback.message.answer(
        f"Old status: {attendance['status']}\n"
        f"New status: {status}\n\n"
        f"Enter the reason for this correction:"
    )

    await callback.answer()


@router.message(ManualAttendanceStates.reason)
async def manual_reason_handler(message:types.Message,state:FSMContext):
    user=await get_user_tg_id(message.from_user.id)

    if user is None or user["role"] not in ("admin","teacher"):
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return

    if not message.text:
        await message.answer("Please enter a reason.")
        return

    await state.update_data(reason=message.text)

    data=await state.get_data()

    await state.set_state(ManualAttendanceStates.confirm)

    await message.answer(
        f"Attendance correction\n\n"
        f"Old status: {data['old_status']}\n"
        f"New status: {data['new_status']}\n"
        f"Reason: {data['reason']}\n\n"
        f"Send Yes to confirm or No to cancel."
    )


@router.message(ManualAttendanceStates.confirm)
async def manual_confirm_handler(message:types.Message,state:FSMContext):
    user=await get_user_tg_id(message.from_user.id)

    if user is None or user["role"] not in ("admin","teacher"):
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return

    if message.text=="No":
        await state.clear()
        await message.answer("Attendance correction cancelled.")
        return

    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return

    data=await state.get_data()

    editor=await get_user_tg_id(message.from_user.id)

    await edit_attendance(
        data["attendance_id"],
        editor["id"],
        data["old_status"],
        data["new_status"],
        data["reason"]
    )

    await state.clear()

    await message.answer("Attendance corrected successfully.")


@router.message(F.text=="Students at Risk")
async def students_at_risk_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)

    if user is None or user["role"] not in ("admin","teacher"):
        await message.answer("You don't have permission to access this.")
        return

    if user["role"]=="teacher":
        teacher_id=await get_teacher_id_by_telegram_id(message.from_user.id)
        if teacher_id is None:
            await message.answer("Teacher profile not found.")
            return
        students=await get_students_with_low_attendance_by_teacher(teacher_id)
    else:
        students=await get_students_with_low_attendance()

    if not students:
        await message.answer("No students are currently below 75% attendance.")
        return

    text="⚠️ Students At Risk\n\n"

    for student in students:
        total=student["total_lessons"] or 0
        attended=student["attended"] or 0

        percentage=round(attended*100/total,2) if total else 0

        text+=(
            f"👤 {student['full_name']}\n"
            f"📚 Lessons: {total}\n"
            f"✅ Attended: {attended}\n"
            f"📈 Attendance: {percentage}%\n\n"
        )

    await message.answer(text)


@router.callback_query(F.data.regexp(r"^attendance_history_\d+$"))
async def attendance_history_handler(callback:types.CallbackQuery):
    student_id=int(callback.data.split("_")[2])

    attendance=await get_student_attendance(student_id)
    percentage=await get_attendance_percentage(student_id)

    if not attendance:
        await callback.message.answer(
            f"Attendance: {percentage}%\n\nNo attendance records."
        )
        await callback.answer()
        return

    text=f"📊 Attendance: {percentage}%\n\n"

    for record in attendance[:20]:
        text+=(
            f"📚 {record['subject']}\n"
            f"📅 {record['lesson_date']}\n"
            f"Status: {record['status'] or 'Not marked'}\n"
            f"Late: {record['late_minutes'] or 0} min\n"
            f"Early leave: {record['early_leave_minutes'] or 0} min\n"
            f"Time in class: {record['time_in_class'] or 0} min\n\n"
        )

    await callback.message.answer(text)
    await callback.answer()