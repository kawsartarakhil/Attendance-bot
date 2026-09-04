from aiogram import Router,types,F
from aiogram.types import CallbackQuery
from servicce.user_services import get_user_tg_id
from servicce.teacher_services import get_teacher_by_user_id,get_teacher_groups
from servicce.lesson_service import get_teacher_today_lessons,get_lesson_by_id
from servicce.attendance_service import get_lesson_attendance
from servicce.analytics_service import get_group_statistics,get_weekly_group_report
from servicce.ai_service import analyze_group_attendance
from servicce.group_service import get_all_groups, get_group_students
from keyboards.inline import (
    groups_keyboard,
    attendance_lessons_keyboard,
    present_lessons_keyboard,
    late_lessons_keyboard,
    absent_lessons_keyboard,
    teacher_groups_keyboard,
)
from database.connection import get_connection

router=Router()


async def get_teacher_profile(telegram_id):
    user=await get_user_tg_id(telegram_id)
    if user is None:
        return None
    teacher=await get_teacher_by_user_id(user["id"])
    return teacher


@router.message(F.text=="My Groups")
async def my_groups_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None:
        await message.answer("User not found.")
        return
    teacher=await get_teacher_by_user_id(user["id"])
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    groups=await get_teacher_groups(teacher["id"])
    if not groups:
        await message.answer("You don't have any groups.")
        return
    await message.answer("My Groups:",reply_markup=groups_keyboard(groups, is_admin=False))

@router.message(F.text=="Present Students")
async def present_students_menu(message:types.Message):
    teacher=await get_teacher_profile(message.from_user.id)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You have no lessons today.")
        return
    await message.answer("Select a lesson:",reply_markup=present_lessons_keyboard(lessons))


@router.message(F.text=="Late Students")
async def late_students_menu(message:types.Message):
    teacher=await get_teacher_profile(message.from_user.id)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You have no lessons today.")
        return
    await message.answer("Select a lesson:",reply_markup=late_lessons_keyboard(lessons))


@router.message(F.text=="Absent Students")
async def absent_students_menu(message:types.Message):
    teacher=await get_teacher_profile(message.from_user.id)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You have no lessons today.")
        return
    await message.answer("Select a lesson:",reply_markup=absent_lessons_keyboard(lessons))


async def show_filtered_students(callback:CallbackQuery,lesson_id,status,label):
    user=await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"]=="student":
        await callback.answer("Access denied.",show_alert=True)
        return

    lesson=await get_lesson_by_id(lesson_id)

    if lesson is None:
        await callback.answer("Lesson not found.",show_alert=True)
        return

    if user["role"]=="teacher":
        teacher=await get_teacher_profile(callback.from_user.id)
        if teacher is None or lesson["teacher_id"]!=teacher["id"]:
            await callback.answer("This is not your lesson.",show_alert=True)
            return

    attendance=await get_lesson_attendance(lesson_id)
    filtered=[record for record in attendance if record["status"]==status]

    if not filtered:
        await callback.message.answer(f"No {label.lower()} students for {lesson['subject']}.")
        await callback.answer()
        return

    text=f"{label} Students\n\n{lesson['subject']}\n\n"

    for record in filtered:
        text+=f"👤 {record['full_name']}\n"
        if record["check_in_time"]:
            text+=f"Check in: {record['check_in_time']}\n"
        if record["late_minutes"]:
            text+=f"Late: {record['late_minutes']} min\n"
        text+="\n"

    await callback.message.answer(text)
    await callback.answer()

# F.data → data-e button ra megira.
# regexp → check mekona ke data ba yak pattern match shawa.
# ^ → az awal shuru shawa.
# group_ → bayad aynan group_ bashad.
# \d → raqam ast.
# + → yak ya chand raqam.
# $ → dar akhir tamam shawa.

@router.callback_query(F.data.regexp(r"^present_lesson_\d+$"))
async def present_lesson_handler(callback:CallbackQuery):
    lesson_id=int(callback.data.split("_")[2])
    await show_filtered_students(callback,lesson_id,"present","Present")


@router.callback_query(F.data.regexp(r"^late_lesson_\d+$"))
async def late_lesson_handler(callback:CallbackQuery):
    lesson_id=int(callback.data.split("_")[2])
    await show_filtered_students(callback,lesson_id,"late","Late")


@router.callback_query(F.data.regexp(r"^absent_lesson_\d+$"))
async def absent_lesson_handler(callback:CallbackQuery):
    lesson_id=int(callback.data.split("_")[2])
    await show_filtered_students(callback,lesson_id,"absent","Absent")



@router.message(F.text.in_(["Edit Attendance","Manual Attendance"]))
async def teacher_manual_attendance_menu(message:types.Message):
    teacher=await get_teacher_profile(message.from_user.id)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    lessons=await get_teacher_today_lessons(teacher["id"])
    if not lessons:
        await message.answer("You have no lessons today.")
        return
    await message.answer(
        "Select lesson for attendance correction:",
        reply_markup=attendance_lessons_keyboard(lessons)
    )



@router.message(F.text=="Weekly Report")
async def weekly_report_menu(message:types.Message):
    teacher=await get_teacher_profile(message.from_user.id)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    groups=await get_teacher_groups(teacher["id"])
    if not groups:
        await message.answer("You don't have any groups.")
        return
    await message.answer(
        "Select a group for the weekly report:",
        reply_markup=teacher_groups_keyboard(groups,"wreport")
    )


@router.callback_query(F.data.regexp(r"^wreport_\d+$"))
async def weekly_report_handler(callback:CallbackQuery):
    group_id=int(callback.data.split("_")[1])

    report=await get_weekly_group_report(group_id)

    if not report:
        await callback.message.answer("No lessons in the last 7 days for this group.")
        await callback.answer()
        return

    total=len(report)
    attended=sum(1 for row in report if row["status"] in ("present","late","left_early"))
    late=sum(1 for row in report if row["status"]=="late")
    absent=sum(1 for row in report if row["status"]=="absent")
    percentage=round(attended*100/total,2) if total else 0

    text=(
        f"📊 Weekly Attendance Report\n\n"
        f"Records: {total}\n"
        f"Attended: {attended}\n"
        f"Late: {late}\n"
        f"Absent: {absent}\n"
        f"Attendance: {percentage}%\n"
    )

    await callback.message.answer(text)
    await callback.answer()



@router.message(F.text=="Group Statistics")
async def group_statistics_menu(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)

    if user is None:
        await message.answer("User not found.")
        return

    if user["role"]=="admin":
        groups=await get_all_groups()
    elif user["role"]=="teacher":
        teacher=await get_teacher_profile(message.from_user.id)
        if teacher is None:
            await message.answer("Teacher profile not found.")
            return
        groups=await get_teacher_groups(teacher["id"])
    else:
        await message.answer("You don't have permission to access this.")
        return

    if not groups:
        await message.answer("There are no groups to show.")
        return

    await message.answer(
        "Select a group:",
        reply_markup=teacher_groups_keyboard(groups,"gstat")
    )


@router.callback_query(F.data.regexp(r"^gstat_\d+$"))
async def group_statistics_handler(callback:CallbackQuery):
    group_id=int(callback.data.split("_")[1])

    statistics=await get_group_statistics(group_id)

    if statistics is None or statistics["total_records"]==0:
        await callback.message.answer("No attendance records for this group yet.")
        await callback.answer()
        return

    text=(
        f"📊 Group Statistics\n\n"
        f"Total records: {statistics['total_records']}\n"
        f"Present: {statistics['present']}\n"
        f"Late: {statistics['late']}\n"
        f"Absent: {statistics['absent']}\n"
        f"Excused: {statistics['excused']}\n"
        f"Left early: {statistics['left_early']}\n"
        f"Attendance: {statistics['attendance_percentage']}%\n"
    )

    await callback.message.answer(text)
    await callback.answer()


@router.message(F.text=="AI Group Analysis")
async def ai_group_analysis_menu(message:types.Message):
    teacher=await get_teacher_profile(message.from_user.id)
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    groups=await get_teacher_groups(teacher["id"])
    if not groups:
        await message.answer("You don't have any groups.")
        return
    await message.answer(
        "Select a group for AI analysis:",
        reply_markup=teacher_groups_keyboard(groups,"aigroup")
    )


@router.callback_query(F.data.regexp(r"^aigroup_\d+$"))
async def ai_group_analysis_handler(callback: CallbackQuery):
    await callback.answer("🤖 Analyzing...")
    group_id = int(callback.data.split("_")[1])
    await callback.message.answer("🤖 Analyzing group attendance...")
    analysis = await analyze_group_attendance(group_id)
    await callback.message.answer(f"🤖 AI Group Analysis\n\n{analysis}")

@router.callback_query(F.data.regexp(r"^teacher_group_\d+$"))
async def teacher_group_handler(callback: CallbackQuery):
    group_id = int(callback.data.split("_")[2])

    teacher = await get_teacher_profile(callback.from_user.id)

    if teacher is None:
        await callback.answer(
            "Teacher profile not found.",
            show_alert=True
        )
        return

    groups = await get_teacher_groups(teacher["id"])

    group = None

    for item in groups:
        if item["id"] == group_id:
            group = item
            break

    if group is None:
        await callback.answer(
            "You don't have permission to access this group.",
            show_alert=True
        )
        return

    students = await get_group_students(group_id)

    await callback.message.answer(
        f"👥 Group Details\n\n"
        f"Group: {group['name']}\n"
        f"Course: {group['course_name']}\n"
        f"Students: {len(students)}"
    )

    await callback.answer()