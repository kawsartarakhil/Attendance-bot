from datetime import date, time

from aiogram import Router,types,F
from aiogram.fsm.context import FSMContext
from servicce.analytics_service import get_monthly_report,get_weekly_report,get_teacher_statistics
from servicce.user_services import get_user_tg_id
from servicce.student_service import delete_student, get_all_students,get_student_by_id,get_student_group,create_student_user, update_student_user
from servicce.teacher_services import create_teacher_user, get_all_teachers,get_teacher_by_id,get_teacher_groups
from servicce.course_service import get_all_courses,get_course_by_id,create_course,update_course,delete_course
from servicce.room_service import get_all_rooms,get_room_by_id,create_room,update_room,delete_room
from servicce.schedule_service import get_all_schedules,get_schedule_by_id,create_schedule,delete_schedule,update_schedule
from keyboards.inline import lesson_groups_keyboard, rooms_keyboard,room_actions_keyboard, schedule_groups_keyboard, schedule_rooms_keyboard,students_keyboard,courses_keyboard,course_actions_keyboard,groups_keyboard,group_courses_keyboard,group_teachers_keyboard,group_actions_keyboard,edit_group_courses_keyboard,edit_group_teachers_keyboard,schedules_keyboard,schedule_actions_keyboard,lessons_keyboard,lesson_actions_keyboard, teachers_keyboard
from servicce.lesson_service import create_lesson,get_lesson_by_id,get_today_lessons,update_lesson_status,cancel_lesson
from servicce.teacher_services import get_all_teachers, create_teacher_user
from states import (
    AddCourseStates,
    CreateCourseStates,
    CreateLessonStates,
    CreateTeacherStates,
    DeleteStudentStates,
    EditCourseStates,
    DeleteCourseStates,
    CreateGroupStates,
    EditGroupStates,
    DeleteGroupStates,
    CreateRoomStates,
    EditRoomStates,
    DeleteRoomStates,
    CreateScheduleStates,
    EditScheduleStates,
    DeleteScheduleStates,
    CreateStudentStates,
    EditStudentStates
)
from servicce.group_service import get_all_groups,get_group_by_id,create_group,update_group,delete_group,get_group_students
from servicce.analytics_service import get_group_statistics
from servicce.attendance_service import get_students_with_low_attendance
from servicce.settings import get_setting,set_setting,get_all_settings
from servicce.ai_service import generate_monthly_summary,analyze_attendance_risk
from keyboards.inline import teacher_groups_keyboard
from states import SettingsStates
from aiogram.types import CallbackQuery
router=Router()


@router.callback_query(
    F.data.regexp(r"^create_lesson_group_\d+$"),
    CreateLessonStates.group
)
async def lesson_group_handler(callback: types.CallbackQuery, state: FSMContext):

    group_id = int(callback.data.split("_")[3])

    await state.update_data(group=group_id)

    teachers = await get_all_teachers()

    if not teachers:
        await callback.answer("No teachers found")
        return

    await state.set_state(CreateLessonStates.teacher)

    await callback.message.answer(
        "Select teacher:",
        reply_markup=teachers_keyboard(teachers)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("teacher_"), CreateLessonStates.teacher)
async def lesson_teacher_handler(callback: types.CallbackQuery,state: FSMContext):

    teacher_id=int(callback.data.split("_")[1])

    await state.update_data(teacher=teacher_id)

    rooms=await get_all_rooms()

    if not rooms:
        await callback.answer("No rooms found")
        return

    await state.set_state(CreateLessonStates.room)

    await callback.message.answer(
        "Select room:",
        reply_markup=rooms_keyboard(rooms)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("room_"), CreateLessonStates.room)
async def lesson_room_handler(callback: types.CallbackQuery,state: FSMContext):
    room_id=int(callback.data.split("_")[1])

    await state.update_data(room=room_id)

    await state.set_state(CreateLessonStates.subject)

    await callback.message.answer("Enter lesson subject:")

    await callback.answer()

@router.message(F.text=="Students")
async def admin_students_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)

    if user is None:
        await message.answer("User not found.")
        return

    if user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return

    students=await get_all_students()

    await message.answer(
        "Students:",
        reply_markup=students_keyboard(students)
    )



@router.message(F.text=="Courses")
async def admin_courses_handler(message:types.Message,state:FSMContext):
    await state.clear()
    user=await get_user_tg_id(message.from_user.id)
    if user is None:
        await message.answer("User not found.")
        return
    if user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return
    courses=await get_all_courses()
    await message.answer("Courses:",reply_markup=courses_keyboard(courses))

@router.callback_query(F.data.startswith("course_"))
async def admin_course_handler(callback: types.CallbackQuery):
    course_id=int(callback.data.split("_")[1])
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.message.answer("You don't have permission to access this.")
        await callback.answer()
        return
    course=await get_course_by_id(course_id)
    if course is None:
        await callback.message.answer("Course not found.")
        await callback.answer()
        return
    await callback.message.answer("Course Details\n\nCourse ID: "+str(course["id"])+"\nName: "+course["name"]+"\nDescription: "+str(course["description"]),reply_markup=course_actions_keyboard(course_id))
    await callback.answer()

@router.callback_query(F.data=="create_course")
async def create_course_handler(callback:CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("You don't have permission.",show_alert=True)
        return
    await state.set_state(CreateCourseStates.name)
    await callback.message.answer("Enter course name:")
    await callback.answer()

@router.message(CreateCourseStates.name)
async def course_name_handler(message: types.Message,state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CreateCourseStates.description)
    await message.answer("Enter course description:")

@router.message(CreateCourseStates.description)
async def course_description_handler(message: types.Message,state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(CreateCourseStates.confirm)
    data=await state.get_data()
    await message.answer("Create this course?\n\nName: "+data["name"]+"\nDescription: "+data["description"]+"\n\nSend Yes to confirm or No to cancel.")

@router.message(CreateCourseStates.confirm)
async def course_confirm_handler(message: types.Message,state: FSMContext):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return
    if message.text=="No":
        await state.clear()
        await message.answer("Course creation cancelled.")
        return
    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return
    data=await state.get_data()
    await create_course(data["name"],data["description"])
    await state.clear()
    await message.answer("Course created successfully.")

@router.callback_query(F.data.startswith("edit_course_"))
async def edit_course_handler(callback: types.CallbackQuery,state: FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.message.answer("You don't have permission to access this.")
        await callback.answer()
        return
    course_id=int(callback.data.split("_")[2])
    course=await get_course_by_id(course_id)
    if course is None:
        await callback.message.answer("Course not found.")
        await callback.answer()
        return
    await state.update_data(course_id=course_id)
    await state.set_state(EditCourseStates.name)
    await callback.message.answer("Enter new course name:")
    await callback.answer()

@router.message(EditCourseStates.name)
async def edit_course_name_handler(message: types.Message,state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(EditCourseStates.description)
    await message.answer("Enter new course description:")

@router.message(EditCourseStates.description)
async def edit_course_description_handler(message: types.Message,state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(EditCourseStates.confirm)
    data=await state.get_data()
    await message.answer("Update this course?\n\nName: "+data["name"]+"\nDescription: "+data["description"]+"\n\nSend Yes to confirm or No to cancel.")


@router.message(EditCourseStates.confirm)
async def edit_course_confirm_handler(message: types.Message,state: FSMContext):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return
    if message.text=="No":
        await state.clear()
        await message.answer("Course update cancelled.")
        return
    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return
    data=await state.get_data()
    await update_course(data["course_id"],data["name"],data["description"])
    await state.clear()
    await message.answer("Course updated successfully.")



@router.callback_query(F.data.startswith("delete_course_"))
async def delete_course_handler(callback: types.CallbackQuery,state: FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.message.answer("You don't have permission to access this.")
        await callback.answer()
        return
    course_id=int(callback.data.split("_")[2])
    course=await get_course_by_id(course_id)
    if course is None:
        await callback.message.answer("Course not found.")
        await callback.answer()
        return
    await state.update_data(course_id=course_id)
    await state.set_state(DeleteCourseStates.confirm)
    await callback.message.answer("Delete this course?\n\nName: "+course["name"]+"\n\nSend Yes to confirm or No to cancel.")
    await callback.answer()


@router.message(DeleteCourseStates.confirm)
async def delete_course_confirm_handler(message: types.Message,state: FSMContext):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return
    if message.text=="No":
        await state.clear()
        await message.answer("Course deletion cancelled.")
        return
    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return
    data=await state.get_data()
    await delete_course(data["course_id"])
    await state.clear()
    await message.answer("Course deleted successfully.")

@router.message(F.text == "Groups")
async def admin_groups_handler(message: types.Message, state: FSMContext):
    await state.clear()

    user = await get_user_tg_id(message.from_user.id)

    if user is None:
        await message.answer("User not found.")
        return

    if user["role"] != "admin":
        await message.answer("You don't have permission to access this.")
        return

    groups = await get_all_groups()

    if not groups:
        await message.answer(
            "There are no groups yet.",
            reply_markup=groups_keyboard([], is_admin=True)
        )
        return

    await message.answer(
        "Groups:",
        reply_markup=groups_keyboard(groups, is_admin=True)
    )

@router.callback_query(F.data.regexp(r"^group_\d+$"))
async def admin_group_handler(callback: types.CallbackQuery):

    user = await get_user_tg_id(callback.from_user.id)

    if user is None:
        await callback.answer(
            "User not found.",
            show_alert=True
        )
        return

    if user["role"] != "admin":
        await callback.answer(
            "You don't have permission to access this.",
            show_alert=True
        )
        return

    group_id = int(callback.data.split("_")[1])

    group = await get_group_by_id(group_id)

    if group is None:
        await callback.answer(
            "Group not found.",
            show_alert=True
        )
        return

    students = await get_group_students(group_id)

    if students:
        student_text = ""

        for student in students:
            student_text += f"👤 {student['full_name']}\n"
    else:
        student_text = "No students assigned"

    if group["teacher_id"] is None:
        teacher_text = "Not assigned"
    else:
        teacher_text = str(group["teacher_id"])

    await callback.message.answer(
        "👥 Group Details\n\n"
        f"Group ID: {group['id']}\n"
        f"Name: {group['name']}\n"
        f"Course: {group['course_name']}\n"
        f"Teacher ID: {teacher_text}\n\n"
        f"Students:\n{student_text}",
        reply_markup=group_actions_keyboard(group_id)
    )

    await callback.answer()

@router.callback_query(F.data=="create_group")
async def create_group_handler(callback:CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("You don't have permission.",show_alert=True)
        return
    courses=await get_all_courses()
    if not courses:
        await callback.message.answer("There are no courses. Create a course first.")
        await callback.answer()
        return
    await state.set_state(CreateGroupStates.group_name)
    await callback.message.answer("Enter group name:")
    await callback.answer()


@router.message(CreateGroupStates.group_name)
async def group_name_handler(message: types.Message,state: FSMContext):
    await state.update_data(name=message.text)
    courses=await get_all_courses()
    if not courses:
        await state.clear()
        await message.answer("There are no courses. Create a course first.")
        return
    await state.set_state(CreateGroupStates.course)
    await message.answer("Select a course:",reply_markup=group_courses_keyboard(courses))


@router.callback_query(F.data.startswith("group_course_"))
async def group_course_handler(callback: types.CallbackQuery,state: FSMContext):
    course_id=int(callback.data.split("_")[2])
    course=await get_course_by_id(course_id)
    if course is None:
        await callback.message.answer("Course not found.")
        await callback.answer()
        return
    teachers=await get_all_teachers()
    if not teachers:
        await callback.message.answer("There are no teachers. Create a teacher first.")
        await callback.answer()
        return
    await state.update_data(course_id=course_id)
    await state.set_state(CreateGroupStates.teacher)
    await callback.message.answer("Select a teacher:",reply_markup=group_teachers_keyboard(teachers))
    await callback.answer()


@router.callback_query(F.data.startswith("group_teacher_"))
async def group_teacher_handler(callback: types.CallbackQuery,state: FSMContext):
    teacher_id=int(callback.data.split("_")[2])
    teacher=await get_teacher_by_id(teacher_id)
    if teacher is None:
        await callback.message.answer("Teacher not found.")
        await callback.answer()
        return
    data=await state.get_data()
    await create_group(data["name"],data["course_id"],teacher_id)
    await state.clear()
    await callback.message.answer("Group created successfully.")
    await callback.answer()



@router.callback_query(F.data.startswith("edit_group_"))
async def edit_group_handler(callback: types.CallbackQuery,state: FSMContext):
    if not callback.data.split("_")[2].isdigit():
        return
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.message.answer("You don't have permission to access this.")
        await callback.answer()
        return
    group_id=int(callback.data.split("_")[2])
    group=await get_group_by_id(group_id)
    if group is None:
        await callback.message.answer("Group not found.")
        await callback.answer()
        return
    await state.update_data(group_id=group_id,old_name=group["name"],old_course_id=group["course_id"],old_teacher_id=group["teacher_id"])
    await state.set_state(EditGroupStates.name)
    await callback.message.answer("Enter new group name:")
    await callback.answer()


@router.message(EditGroupStates.name)
async def edit_group_name_handler(message: types.Message,state: FSMContext):
    await state.update_data(name=message.text)
    courses=await get_all_courses()
    if not courses:
        await state.clear()
        await message.answer("There are no courses.")
        return
    await state.set_state(EditGroupStates.course)
    await message.answer("Select a course:",reply_markup=edit_group_courses_keyboard(courses))


@router.callback_query(F.data.startswith("edit_group_course_"))
async def edit_group_course_handler(callback: types.CallbackQuery,state: FSMContext):
    course_id=int(callback.data.split("_")[3])
    course=await get_course_by_id(course_id)
    if course is None:
        await callback.message.answer("Course not found.")
        await callback.answer()
        return
    teachers=await get_all_teachers()
    if not teachers:
        await callback.message.answer("There are no teachers.")
        await callback.answer()
        return
    await state.update_data(course_id=course_id)
    await state.set_state(EditGroupStates.teacher)
    await callback.message.answer("Select a teacher:",reply_markup=edit_group_teachers_keyboard(teachers))
    await callback.answer()


@router.callback_query(F.data.startswith("edit_group_teacher_"))
async def edit_group_teacher_handler(callback: types.CallbackQuery,state: FSMContext):
    teacher_id=int(callback.data.split("_")[3])
    teacher=await get_teacher_by_id(teacher_id)
    if teacher is None:
        await callback.message.answer("Teacher not found.")
        await callback.answer()
        return
    await state.update_data(teacher_id=teacher_id)
    data=await state.get_data()
    await state.set_state(EditGroupStates.confirm)
    await callback.message.answer("Update this group?\n\n""Name: "+data["name"]+"\nCourse ID: "+str(data["course_id"])+"\nTeacher ID: "+str(data["teacher_id"])+"\n\nSend Yes to confirm or No to cancel.")
    await callback.answer()

@router.message(EditGroupStates.confirm)
async def edit_group_confirm_handler(message: types.Message,state: FSMContext):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return
    if message.text=="No":
        await state.clear()
        await message.answer("Group update cancelled.")
        return
    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return
    data=await state.get_data()
    await update_group(data["group_id"],data["name"],data["course_id"],data["teacher_id"])
    await state.clear()
    await message.answer("Group updated successfully.")



@router.callback_query(F.data.startswith("delete_group_"))
async def delete_group_handler(callback: types.CallbackQuery,state: FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.message.answer("You don't have permission to access this.")
        await callback.answer()
        return
    group_id=int(callback.data.split("_")[2])
    group=await get_group_by_id(group_id)
    if group is None:
        await callback.message.answer("Group not found.")
        await callback.answer()
        return
    await state.update_data(group_id=group_id)
    await state.set_state(DeleteGroupStates.confirm)
    await callback.message.answer("Delete this group?\n\n"+"Name: "+group["name"]+"\n"+"Course: "+group["course_name"]+"\n\n"+"Send Yes to confirm or No to cancel.")
    await callback.answer()


@router.message(DeleteGroupStates.confirm)
async def delete_group_confirm_handler(message: types.Message,state: FSMContext):
    user=await get_user_tg_id(message.from_user.id)

    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return
    if message.text=="No":
        await state.clear()
        await message.answer("Group deletion cancelled.")
        return
    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return
    data=await state.get_data()
    await delete_group(data["group_id"])
    await state.clear()
    await message.answer("Group deleted successfully.")

@router.message(F.text=="Rooms")
async def admin_rooms_handler(message:types.Message,state:FSMContext):
    await state.clear()
    user=await get_user_tg_id(message.from_user.id)
    if user is None:
        await message.answer("User not found.")
        return
    if user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return
    rooms=await get_all_rooms()
    await message.answer("Rooms:",reply_markup=rooms_keyboard(rooms))


@router.callback_query(F.data.regexp(r"^room_\d+$"))
async def admin_room_handler(callback:types.CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("You don't have permission.",show_alert=True)
        return
    room_id=int(callback.data.split("_")[1])
    room=await get_room_by_id(room_id)
    if room is None:
        await callback.message.answer("Room not found.")
        await callback.answer()
        return
    await callback.message.answer(
        "Room Details\n\n"+
        "Room ID: "+str(room["id"])+"\n"+
        "Name: "+room["name"]+"\n"+
        "Capacity: "+str(room["capacity"]),
        reply_markup=room_actions_keyboard(room_id)
    )
    await callback.answer()


@router.callback_query(F.data=="create_room")
async def create_room_handler(callback:types.CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("You don't have permission.",show_alert=True)
        return
    await state.set_state(CreateRoomStates.name)
    await callback.message.answer("Enter room name:")
    await callback.answer()


@router.message(CreateRoomStates.name)
async def room_name_handler(message:types.Message,state:FSMContext):
    if not message.text:
        await message.answer("Please enter a room name.")
        return
    await state.update_data(name=message.text)
    await state.set_state(CreateRoomStates.capacity)
    await message.answer("Enter room capacity:")


@router.message(CreateRoomStates.capacity)
async def room_capacity_handler(message:types.Message,state:FSMContext):
    if not message.text.isdigit():
        await message.answer("Please enter a number.")
        return
    capacity=int(message.text)
    if capacity<=0:
        await message.answer("Capacity must be greater than 0.")
        return
    await state.update_data(capacity=capacity)
    await state.set_state(CreateRoomStates.confirm)
    data=await state.get_data()
    await message.answer(
        "Create this room?\n\n"+
        "Name: "+data["name"]+"\n"+
        "Capacity: "+str(data["capacity"])+"\n\n"+
        "Send Yes to confirm or No to cancel."
    )


@router.message(CreateRoomStates.confirm)
async def room_confirm_handler(message:types.Message,state:FSMContext):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return
    if message.text=="No":
        await state.clear()
        await message.answer("Room creation cancelled.")
        return
    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return
    data=await state.get_data()
    await create_room(data["name"],data["capacity"])
    await state.clear()
    await message.answer("Room created successfully.")


@router.callback_query(F.data.regexp(r"^edit_room_\d+$"))
async def edit_room_handler(callback:types.CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("You don't have permission.",show_alert=True)
        return
    room_id=int(callback.data.split("_")[2])
    room=await get_room_by_id(room_id)
    if room is None:
        await callback.message.answer("Room not found.")
        await callback.answer()
        return
    await state.update_data(room_id=room_id)
    await state.set_state(EditRoomStates.name)
    await callback.message.answer(
        "Enter new room name:\n\nCurrent name: "+room["name"]
    )
    await callback.answer()


@router.message(EditRoomStates.name)
async def edit_room_name_handler(message:types.Message,state:FSMContext):
    if not message.text:
        await message.answer("Please enter a room name.")
        return
    await state.update_data(name=message.text)
    await state.set_state(EditRoomStates.capacity)
    await message.answer("Enter new room capacity:")


@router.message(EditRoomStates.capacity)
async def edit_room_capacity_handler(message:types.Message,state:FSMContext):
    if not message.text.isdigit():
        await message.answer("Please enter a number.")
        return
    capacity=int(message.text)
    if capacity<=0:
        await message.answer("Capacity must be greater than 0.")
        return
    await state.update_data(capacity=capacity)
    await state.set_state(EditRoomStates.confirm)
    data=await state.get_data()
    await message.answer(
        "Update this room?\n\n"+
        "Name: "+data["name"]+"\n"+
        "Capacity: "+str(data["capacity"])+"\n\n"+
        "Send Yes to confirm or No to cancel."
    )


@router.message(EditRoomStates.confirm)
async def edit_room_confirm_handler(message:types.Message,state:FSMContext):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return
    if message.text=="No":
        await state.clear()
        await message.answer("Room update cancelled.")
        return
    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return
    data=await state.get_data()
    await update_room(
        data["room_id"],
        data["name"],
        data["capacity"]
    )
    await state.clear()
    await message.answer("Room updated successfully.")


@router.callback_query(F.data.regexp(r"^delete_room_\d+$"))
async def delete_room_handler(callback:types.CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("You don't have permission.",show_alert=True)
        return
    room_id=int(callback.data.split("_")[2])
    room=await get_room_by_id(room_id)
    if room is None:
        await callback.message.answer("Room not found.")
        await callback.answer()
        return
    await state.update_data(room_id=room_id)
    await state.set_state(DeleteRoomStates.confirm)
    await callback.message.answer(
        "Delete this room?\n\n"+
        "Name: "+room["name"]+"\n"+
        "Capacity: "+str(room["capacity"])+"\n\n"+
        "Send Yes to confirm or No to cancel."
    )
    await callback.answer()


@router.message(DeleteRoomStates.confirm)
async def delete_room_confirm_handler(message:types.Message,state:FSMContext):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return
    if message.text=="No":
        await state.clear()
        await message.answer("Room deletion cancelled.")
        return
    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return
    data=await state.get_data()
    await delete_room(data["room_id"])
    await state.clear()
    await message.answer("Room deleted successfully.")


@router.message(F.text=="Schedules")
async def admin_schedules_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return
    schedules=await get_all_schedules()
    if not schedules:
        await message.answer("There are no schedules yet.",reply_markup=schedules_keyboard([]))
        return
    await message.answer("Schedules:",reply_markup=schedules_keyboard(schedules))


@router.callback_query(F.data.regexp(r"^schedule_\d+$"))
async def admin_schedule_handler(callback:types.CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.message.answer("You don't have permission to access this.")
        await callback.answer()
        return
    schedule_id=int(callback.data.split("_")[1])
    schedule=await get_schedule_by_id(schedule_id)
    if schedule is None:
        await callback.message.answer("Schedule not found.")
        await callback.answer()
        return
    room_name=schedule["room_name"] if schedule["room_name"] else "No room"
    await callback.message.answer(
        "Schedule Details\n\n"+
        "Group: "+schedule["group_name"]+"\n"+
        "Weekday: "+schedule["weekday"]+"\n"+
        "Start Time: "+str(schedule["start_time"])+"\n"+
        "End Time: "+str(schedule["end_time"])+"\n"+
        "Room: "+room_name+"\n"+
        "Active: "+str(schedule["is_active"]),
        reply_markup=schedule_actions_keyboard(schedule_id)
    )
    await callback.answer()


@router.callback_query(F.data=="create_schedule")
async def create_schedule_handler(callback:types.CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("You don't have permission.",show_alert=True)
        return
    groups=await get_all_groups()
    if not groups:
        await callback.answer("There are no groups.")
        return
    await state.set_state(CreateScheduleStates.group)
    await callback.message.answer(
        "Select group:",
        reply_markup=schedule_groups_keyboard(groups)
    )
    await callback.answer()


@router.callback_query(CreateScheduleStates.group,F.data.regexp(r"^schedule_group_\d+$"))
async def schedule_group_handler(callback:types.CallbackQuery,state:FSMContext):
    group_id=int(callback.data.split("_")[2])
    await state.update_data(group_id=group_id)
    await state.set_state(CreateScheduleStates.weekday)
    await callback.message.answer("Enter weekday:\n\nMonday\nTuesday\nWednesday\nThursday\nFriday\nSaturday\nSunday")
    await callback.answer()


@router.message(CreateScheduleStates.weekday)
async def schedule_weekday_handler(message:types.Message,state:FSMContext):
    weekdays=[
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]
    if message.text not in weekdays:
        await message.answer("Please enter a valid weekday.")
        return
    await state.update_data(weekday=message.text)
    await state.set_state(CreateScheduleStates.start_time)
    await message.answer("Enter start time:\nExample: 09:00")


@router.message(CreateScheduleStates.start_time)
async def schedule_start_time_handler(message:types.Message,state:FSMContext):
    await state.update_data(start_time=message.text)
    await state.set_state(CreateScheduleStates.end_time)
    await message.answer("Enter end time:\nExample: 10:30")


@router.message(CreateScheduleStates.end_time)
async def schedule_end_time_handler(message:types.Message,state:FSMContext):
    await state.update_data(end_time=message.text)
    rooms=await get_all_rooms()
    if not rooms:
        await state.update_data(room_id=None)
        await state.set_state(CreateScheduleStates.confirm)
        data=await state.get_data()
        await message.answer(
            "Create this schedule?\n\n"+
            "Weekday: "+data["weekday"]+"\n"+
            "Start Time: "+data["start_time"]+"\n"+
            "End Time: "+data["end_time"]+"\n"+
            "Room: No room\n\n"+
            "Send Yes to confirm or No to cancel."
        )
        return
    await state.set_state(CreateScheduleStates.room)
    await message.answer(
        "Select room:",
        reply_markup=schedule_rooms_keyboard(rooms)
    )


@router.callback_query(CreateScheduleStates.room,F.data.regexp(r"^schedule_room_\d+$"))
async def schedule_room_handler(callback:types.CallbackQuery,state:FSMContext):
    room_id=int(callback.data.split("_")[2])
    await state.update_data(room_id=room_id)
    await state.set_state(CreateScheduleStates.confirm)
    data=await state.get_data()
    room=await get_room_by_id(room_id)
    if room is None:
        await callback.answer("Room not found.",show_alert=True)
        return
    await callback.message.answer(
        "Create this schedule?\n\n"+
        "Weekday: "+data["weekday"]+"\n"+
        "Start Time: "+data["start_time"]+"\n"+
        "End Time: "+data["end_time"]+"\n"+
        "Room: "+room["name"]+"\n\n"+
        "Send Yes to confirm or No to cancel."
    )
    await callback.answer()


@router.message(CreateScheduleStates.confirm)
async def create_schedule_confirm_handler(message:types.Message,state:FSMContext):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return
    if message.text=="No":
        await state.clear()
        await message.answer("Schedule creation cancelled.")
        return
    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return
    data=await state.get_data()
    await create_schedule(
        data["group_id"],
        data["weekday"],
        data["start_time"],
        data["end_time"],
        data.get("room_id")
    )
    await state.clear()
    await message.answer("Schedule created successfully.")


@router.callback_query(F.data.regexp(r"^delete_schedule_\d+$"))
async def delete_schedule_handler(callback:types.CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.message.answer("You don't have permission to access this.")
        await callback.answer()
        return
    schedule_id=int(callback.data.split("_")[2])
    schedule=await get_schedule_by_id(schedule_id)
    if schedule is None:
        await callback.message.answer("Schedule not found.")
        await callback.answer()
        return
    await state.update_data(schedule_id=schedule_id)
    await state.set_state(DeleteScheduleStates.confirm)
    await callback.message.answer(
        "Delete this schedule?\n\n"+
        "Group: "+schedule["group_name"]+"\n"+
        "Weekday: "+schedule["weekday"]+"\n"+
        "Time: "+str(schedule["start_time"])+" - "+str(schedule["end_time"])+"\n\n"+
        "Send Yes to confirm or No to cancel."
    )
    await callback.answer()


@router.message(DeleteScheduleStates.confirm)
async def delete_schedule_confirm_handler(message:types.Message,state:FSMContext):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return
    if message.text=="No":
        await state.clear()
        await message.answer("Schedule deletion cancelled.")
        return
    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return
    data=await state.get_data()
    await delete_schedule(data["schedule_id"])
    await state.clear()
    await message.answer("Schedule deleted successfully.")


@router.callback_query(F.data.regexp(r"^edit_schedule_\d+$"))
async def edit_schedule_handler(callback:types.CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.message.answer("You don't have permission to access this.")
        await callback.answer()
        return
    schedule_id=int(callback.data.split("_")[2])
    schedule=await get_schedule_by_id(schedule_id)
    if schedule is None:
        await callback.message.answer("Schedule not found.")
        await callback.answer()
        return
    await state.update_data(schedule_id=schedule_id)
    await state.set_state(EditScheduleStates.group)
    groups=await get_all_groups()
    if not groups:
        await callback.answer("There are no groups.",show_alert=True)
        return
    await callback.message.answer(
        "Select new group:",
        reply_markup=groups_keyboard(groups)
    )
    await callback.answer()


@router.callback_query(EditScheduleStates.group,F.data.regexp(r"^group_\d+$"))
async def edit_schedule_group_handler(callback:types.CallbackQuery,state:FSMContext):
    group_id=int(callback.data.split("_")[1])
    await state.update_data(group_id=group_id)
    await state.set_state(EditScheduleStates.weekday)
    await callback.message.answer(
        "Enter weekday:\n\n"+
        "Monday\n"+
        "Tuesday\n"+
        "Wednesday\n"+
        "Thursday\n"+
        "Friday\n"+
        "Saturday\n"+
        "Sunday"
    )
    await callback.answer()


@router.message(EditScheduleStates.weekday)
async def edit_schedule_weekday_handler(message:types.Message,state:FSMContext):
    weekdays=[
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]
    if message.text not in weekdays:
        await message.answer("Please enter a valid weekday.")
        return
    await state.update_data(weekday=message.text)
    await state.set_state(EditScheduleStates.start_time)
    await message.answer("Enter new start time:\nExample: 09:00")


@router.message(EditScheduleStates.start_time)
async def edit_schedule_start_time_handler(message:types.Message,state:FSMContext):
    await state.update_data(start_time=message.text)
    await state.set_state(EditScheduleStates.end_time)
    await message.answer("Enter new end time:\nExample: 10:30")


@router.message(EditScheduleStates.end_time)
async def edit_schedule_end_time_handler(message:types.Message,state:FSMContext):
    await state.update_data(end_time=message.text)
    rooms=await get_all_rooms()
    if not rooms:
        await state.update_data(room_id=None)
        await state.set_state(EditScheduleStates.confirm)
        data=await state.get_data()
        await message.answer(
            "Update this schedule?\n\n"+
            "Weekday: "+data["weekday"]+"\n"+
            "Start Time: "+data["start_time"]+"\n"+
            "End Time: "+data["end_time"]+"\n"+
            "Room: No room\n\n"+
            "Send Yes to confirm or No to cancel."
        )
        return
    await state.set_state(EditScheduleStates.room)
    await message.answer(
        "Select new room:",
        reply_markup=schedule_rooms_keyboard(rooms)
    )


@router.callback_query(EditScheduleStates.room,F.data.regexp(r"^room_\d+$"))
async def edit_schedule_room_handler(callback:types.CallbackQuery,state:FSMContext):
    room_id=int(callback.data.split("_")[1])
    await state.update_data(room_id=room_id)
    await state.set_state(EditScheduleStates.confirm)
    data=await state.get_data()
    room=await get_room_by_id(room_id)
    if room is None:
        await callback.answer("Room not found.",show_alert=True)
        return
    await callback.message.answer(
        "Update this schedule?\n\n"+
        "Weekday: "+data["weekday"]+"\n"+
        "Start Time: "+data["start_time"]+"\n"+
        "End Time: "+data["end_time"]+"\n"+
        "Room: "+room["name"]+"\n\n"+
        "Send Yes to confirm or No to cancel."
    )
    await callback.answer()


@router.message(EditScheduleStates.confirm)
async def edit_schedule_confirm_handler(message:types.Message,state:FSMContext):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return
    if message.text=="No":
        await state.clear()
        await message.answer("Schedule update cancelled.")
        return
    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return
    data=await state.get_data()
    await update_schedule(
        data["schedule_id"],
        data["group_id"],
        data["weekday"],
        data["start_time"],
        data["end_time"],
        data.get("room_id")
    )
    await state.clear()
    await message.answer("Schedule updated successfully.")



@router.message(F.text == "Lessons")
async def admin_lessons_handler(message: types.Message, state: FSMContext):
    user = await get_user_tg_id(message.from_user.id)

    if user is None or user["role"] != "admin":
        await message.answer("You don't have permission to access this.")
        return

    # Clear any previous FSM state
    await state.clear()

    lessons = await get_today_lessons()

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="➕ Create Lesson",
                    callback_data="create_lesson"
                )
            ]
        ]
    )

    if lessons:
        lesson_keyboard = lessons_keyboard(lessons)

        keyboard.inline_keyboard.extend(
            lesson_keyboard.inline_keyboard
        )

    await message.answer("Today's lessons:",reply_markup=keyboard)


@router.callback_query(F.data.startswith("lesson_"))
async def admin_lesson_handler(callback: types.CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"]!="admin":
        await callback.message.answer("You don't have permission to access this.")
        await callback.answer()
        return

    lesson_id=int(callback.data.split("_")[1])
    lesson=await get_lesson_by_id(lesson_id)

    if lesson is None:
        await callback.answer("Lesson not found")
        return

    room_name=lesson["room_name"] if lesson["room_name"] else "No room"

    text="Lesson\n\n"
    text+="Lesson ID: "+str(lesson["id"])+"\n"
    text+="Subject: "+str(lesson["subject"])+"\n"
    text+="Group: "+str(lesson["group_name"])+"\n"
    text+="Teacher: "+str(lesson["teacher_name"])+"\n"
    text+="Room: "+room_name+"\n"
    text+="Date: "+str(lesson["lesson_date"])+"\n"
    text+="Time: "+str(lesson["start_time"])+" - "+str(lesson["end_time"])+"\n"
    text+="Status: "+str(lesson["status"])

    await callback.message.answer(text,reply_markup=lesson_actions_keyboard(lesson_id))

    await callback.answer()



@router.callback_query(F.data.startswith("cancel_lesson_"))
async def admin_cancel_lesson_handler(callback: types.CallbackQuery):

    user=await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"]!="admin":
        await callback.message.answer("You don't have permission to access this.")
        await callback.answer()
        return

    lesson_id=int(callback.data.split("_")[2])

    lesson=await get_lesson_by_id(lesson_id)

    if lesson is None:
        await callback.answer("Lesson not found")
        return

    await cancel_lesson(lesson_id)

    await callback.message.answer("Lesson cancelled successfully.")

    await callback.answer()



@router.callback_query(F.data.startswith("complete_lesson_"))
async def admin_complete_lesson_handler(callback: types.CallbackQuery):

    user=await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"]!="admin":
        await callback.message.answer("You don't have permission to access this.")
        await callback.answer()
        return

    lesson_id=int(callback.data.split("_")[2])

    lesson=await get_lesson_by_id(lesson_id)

    if lesson is None:
        await callback.answer("Lesson not found")
        return

    await update_lesson_status(lesson_id,"completed")

    await callback.message.answer("Lesson marked as completed.")

    await callback.answer()
    
@router.callback_query(F.data == "create_lesson")
async def create_lesson_handler(callback: types.CallbackQuery, state: FSMContext):

    user = await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"] != "admin":
        await callback.answer("Access denied")
        return

    groups = await get_all_groups()

    if not groups:
        await callback.answer("No groups found")
        return

    await state.set_state(CreateLessonStates.group)

    await callback.message.answer(
        "Select group:",
        reply_markup=lesson_groups_keyboard(groups)
    )

    await callback.answer()


@router.message(CreateLessonStates.subject)
async def lesson_subject_handler(message: types.Message,state: FSMContext):

    await state.update_data(subject=message.text)

    await state.set_state(CreateLessonStates.lesson_date)

    await message.answer("Enter lesson date (YYYY-MM-DD):")





@router.message(CreateLessonStates.lesson_date)
async def lesson_date_handler(message:types.Message,state:FSMContext):
    try:
        lesson_date=date.fromisoformat(message.text)
    except ValueError:
        await message.answer("Please enter the date like 2026-09-03.")
        return
    await state.update_data(lesson_date=lesson_date)
    await state.set_state(CreateLessonStates.start_time)
    await message.answer("Enter start time (HH:MM):")

@router.message(CreateLessonStates.start_time)
async def lesson_start_time_handler(message:types.Message,state:FSMContext):
    try:
        start_time=time.fromisoformat(message.text)
    except ValueError:
        await message.answer("Please enter the time like 09:00.")
        return
    await state.update_data(start_time=start_time)
    await state.set_state(CreateLessonStates.end_time)
    await message.answer("Enter end time (HH:MM):")

@router.message(CreateLessonStates.end_time)
async def lesson_end_time_handler(
    message: types.Message,
    state: FSMContext
):
    try:
        end_time = time.fromisoformat(message.text)
    except ValueError:
        await message.answer("Please enter the time like 12:30.")
        return

    data = await state.get_data()

    start_time = data["start_time"]

    if end_time <= start_time:
        await message.answer(
            "End time must be later than start time.\n\n"
            f"Start time: {start_time.strftime('%H:%M')}\n"
            "Please enter another end time:"
        )
        return

    await state.update_data(end_time=end_time)

    await state.set_state(CreateLessonStates.confirm)

    data = await state.get_data()

    await message.answer(
        "Create this lesson?\n\n"
        f"Group ID: {data['group']}\n"
        f"Teacher ID: {data['teacher']}\n"
        f"Room ID: {data['room']}\n"
        f"Subject: {data['subject']}\n"
        f"Date: {data['lesson_date']}\n"
        f"Time: {data['start_time'].strftime('%H:%M')} - "
        f"{data['end_time'].strftime('%H:%M')}\n\n"
        "Send Yes to confirm or No to cancel."
    )
@router.message(CreateLessonStates.confirm)
async def create_lesson_confirm_handler(message: types.Message,state: FSMContext):

    user=await get_user_tg_id(message.from_user.id)

    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return

    if message.text=="No":
        await state.clear()
        await message.answer("Lesson creation cancelled.")
        return

    if message.text!="Yes":
        await message.answer("Please send Yes or No.")
        return

    data=await state.get_data()

    await create_lesson(
        data["group"],
        data["teacher"],
        data["room"],
        data["subject"],
        data["lesson_date"],
        data["start_time"],
        data["end_time"]
    )

    await state.clear()

    await message.answer("Lesson created successfully.")

@router.message(F.text=="Monthly Reports")
async def monthly_report_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return
    report=await get_monthly_report()
    total=report["total_records"] or 0
    attended=report["attended"] or 0
    late=report["late"] or 0
    absent=report["absent"] or 0
    excused=report["excused"] or 0
    percentage=round(attended*100/total,2) if total else 0
    await message.answer(
        f"📊 Monthly Attendance Report\n\n"
        f"📚 Lessons: {report['lessons'] or 0}\n"
        f"👥 Attendance records: {total}\n"
        f"✅ Attended: {attended}\n"
        f"⏰ Late: {late}\n"
        f"❌ Absent: {absent}\n"
        f"🟡 Excused: {excused}\n\n"
        f"📈 Attendance: {percentage}%"
    )


@router.message(F.text=="Weekly Reports")
async def weekly_report_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return
    report=await get_weekly_report()
    total=report["total_records"] or 0
    attended=report["attended"] or 0
    late=report["late"] or 0
    absent=report["absent"] or 0
    excused=report["excused"] or 0
    percentage=round(attended*100/total,2) if total else 0
    await message.answer(
        f"📊 Weekly Attendance Report\n\n"
        f"📚 Lessons: {report['lessons'] or 0}\n"
        f"👥 Attendance records: {total}\n"
        f"✅ Attended: {attended}\n"
        f"⏰ Late: {late}\n"
        f"❌ Absent: {absent}\n"
        f"🟡 Excused: {excused}\n\n"
        f"📈 Attendance: {percentage}%"
    )



@router.message(F.text=="Teacher Statistics")
async def teacher_statistics_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return
    teachers=await get_teacher_statistics()
    if not teachers:
        await message.answer("No teacher statistics available.")
        return
    text="👨‍🏫 Teacher Statistics\n\n"
    for teacher in teachers:
        total=teacher["total_records"] or 0
        attended=teacher["attended"] or 0
        late=teacher["late"] or 0
        absent=teacher["absent"] or 0
        percentage=round(attended*100/total,2) if total else 0
        text+=(
            f"👤 {teacher['full_name']}\n"
            f"📚 Lessons: {teacher['lessons'] or 0}\n"
            f"👥 Records: {total}\n"
            f"✅ Attended: {attended}\n"
            f"⏰ Late: {late}\n"
            f"❌ Absent: {absent}\n"
            f"📈 Attendance: {percentage}%\n\n"
        )
    await message.answer(text)



@router.message(F.text=="Reports")
async def reports_hub_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return

    keyboard=types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Weekly Report",callback_data="rep_weekly")],
        [types.InlineKeyboardButton(text="Monthly Report",callback_data="rep_monthly")],
        [types.InlineKeyboardButton(text="Teacher Statistics",callback_data="rep_teacher")],
        [types.InlineKeyboardButton(text="Students at Risk",callback_data="rep_risk")],
    ])

    await message.answer("Select a report:",reply_markup=keyboard)


@router.callback_query(F.data=="rep_weekly")
async def reports_hub_weekly(callback:CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("Access denied.",show_alert=True)
        return

    report=await get_weekly_report()
    total=report["total_records"] or 0
    attended=report["attended"] or 0
    late=report["late"] or 0
    absent=report["absent"] or 0
    excused=report["excused"] or 0
    percentage=round(attended*100/total,2) if total else 0

    await callback.message.answer(
        f"📊 Weekly Attendance Report\n\n"
        f"📚 Lessons: {report['lessons'] or 0}\n"
        f"👥 Attendance records: {total}\n"
        f"✅ Attended: {attended}\n"
        f"⏰ Late: {late}\n"
        f"❌ Absent: {absent}\n"
        f"🟡 Excused: {excused}\n\n"
        f"📈 Attendance: {percentage}%"
    )
    await callback.answer()


@router.callback_query(F.data=="rep_monthly")
async def reports_hub_monthly(callback:CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("Access denied.",show_alert=True)
        return

    report=await get_monthly_report()
    total=report["total_records"] or 0
    attended=report["attended"] or 0
    late=report["late"] or 0
    absent=report["absent"] or 0
    excused=report["excused"] or 0
    percentage=round(attended*100/total,2) if total else 0

    await callback.message.answer(
        f"📊 Monthly Attendance Report\n\n"
        f"📚 Lessons: {report['lessons'] or 0}\n"
        f"👥 Attendance records: {total}\n"
        f"✅ Attended: {attended}\n"
        f"⏰ Late: {late}\n"
        f"❌ Absent: {absent}\n"
        f"🟡 Excused: {excused}\n\n"
        f"📈 Attendance: {percentage}%"
    )
    await callback.answer()


@router.callback_query(F.data=="rep_teacher")
async def reports_hub_teacher(callback:CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("Access denied.",show_alert=True)
        return

    teachers=await get_teacher_statistics()

    if not teachers:
        await callback.message.answer("No teacher statistics available.")
        await callback.answer()
        return

    text="👨‍🏫 Teacher Statistics\n\n"
    for teacher in teachers:
        total=teacher["total_records"] or 0
        attended=teacher["attended"] or 0
        late=teacher["late"] or 0
        absent=teacher["absent"] or 0
        percentage=round(attended*100/total,2) if total else 0
        text+=(
            f"👤 {teacher['full_name']}\n"
            f"📚 Lessons: {teacher['lessons'] or 0}\n"
            f"👥 Records: {total}\n"
            f"✅ Attended: {attended}\n"
            f"⏰ Late: {late}\n"
            f"❌ Absent: {absent}\n"
            f"📈 Attendance: {percentage}%\n\n"
        )

    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data=="rep_risk")
async def reports_hub_risk(callback:CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("Access denied.",show_alert=True)
        return

    students=await get_students_with_low_attendance()

    if not students:
        await callback.message.answer("No students currently at risk.")
        await callback.answer()
        return

    text="⚠️ Students at Risk\n\n"
    for student in students:
        total=student["total_lessons"] or 0
        attended=student["attended"] or 0
        percentage=round(attended*100/total,2) if total else 0
        text+=f"👤 {student['full_name']} — {percentage}%\n"

    await callback.message.answer(text)
    await callback.answer()



@router.message(F.text=="AI Analytics")
async def ai_analytics_hub_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return

    keyboard=types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Monthly AI Summary",callback_data="ai_monthly_summary")],
        [types.InlineKeyboardButton(text="Attendance Risk Analysis",callback_data="ai_risk_analysis")],
    ])

    await message.answer("Select AI analysis:",reply_markup=keyboard)


@router.callback_query(F.data=="ai_monthly_summary")
async def ai_monthly_summary_handler(callback:CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("Access denied.",show_alert=True)
        return

    await callback.message.answer("Generating monthly summary...")
    summary=await generate_monthly_summary()
    await callback.message.answer(f"🤖 AI Monthly Summary\n\n{summary}")
    await callback.answer()


@router.callback_query(F.data=="ai_risk_analysis")
async def ai_risk_analysis_handler(callback:CallbackQuery):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("Access denied.",show_alert=True)
        return

    await callback.message.answer("Analyzing attendance risk...")
    analysis=await analyze_attendance_risk()
    await callback.message.answer(f"🤖 AI Risk Analysis\n\n{analysis}")
    await callback.answer()



RULE_LABELS={
    "late_minutes":"Allowed late minutes before a check-in counts as Late",
    "early_leave_minutes":"Allowed early-leave minutes before it counts as Left Early",
    "absence_check_minutes":"Minutes after lesson start before a no-show may be checked (not yet applied automatically — the absence scheduler currently marks students absent once the lesson is finished)",
}


def rule_keyboard(key):
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Change value",callback_data=f"setrule_{key}")]
    ])


@router.message(F.text=="Attendance Rules")
async def attendance_rules_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return

    settings=await get_all_settings()

    if not settings:
        await message.answer("No rules configured yet.")
        return

    text="⚙️ Attendance Rules\n\n"
    for row in settings:
        label=RULE_LABELS.get(row["key"],row["key"])
        text+=f"{label}: {row['value']} min\n\n"

    await message.answer(text)


@router.message(F.text=="Late Rules")
async def late_rules_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return

    value=await get_setting("late_minutes")
    await message.answer(
        f"Allowed late minutes: {value}\n\n"
        f"Students who check in within this many minutes of the lesson start are marked Present, otherwise Late.",
        reply_markup=rule_keyboard("late_minutes")
    )


@router.message(F.text=="Absence Rules")
async def absence_rules_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return

    value=await get_setting("absence_check_minutes")
    await message.answer(
        f"Absence check window: {value} minutes after lesson start.\n\n"
        f"Note: the automatic absence scheduler currently marks a student absent once their lesson is finished, "
        f"not at this exact minute mark yet — this value is stored for future use.",
        reply_markup=rule_keyboard("absence_check_minutes")
    )


@router.message(F.text=="Early Leave Rules")
async def early_leave_rules_handler(message:types.Message):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await message.answer("You don't have permission to access this.")
        return

    value=await get_setting("early_leave_minutes")
    await message.answer(
        f"Allowed early leave: {value} minutes.\n\n"
        f"Students who check out within this many minutes of the lesson end keep their normal status, "
        f"otherwise they're marked Left Early.",
        reply_markup=rule_keyboard("early_leave_minutes")
    )


@router.callback_query(F.data.startswith("setrule_"))
async def setrule_start_handler(callback:CallbackQuery,state:FSMContext):
    user=await get_user_tg_id(callback.from_user.id)
    if user is None or user["role"]!="admin":
        await callback.answer("Access denied.",show_alert=True)
        return

    key=callback.data.split("_",1)[1]

    await state.update_data(rule_key=key)
    await state.set_state(SettingsStates.value)

    await callback.message.answer("Send the new value in minutes (a whole number):")
    await callback.answer()


@router.message(SettingsStates.value)
async def setrule_value_handler(message:types.Message,state:FSMContext):
    user=await get_user_tg_id(message.from_user.id)
    if user is None or user["role"]!="admin":
        await state.clear()
        await message.answer("You don't have permission to access this.")
        return

    if not message.text.isdigit():
        await message.answer("Please send a whole number.")
        return

    data=await state.get_data()
    key=data.get("rule_key")

    await set_setting(key,int(message.text))

    await state.clear()

    label=RULE_LABELS.get(key,key)
    await message.answer(f"Updated.\n\n{label}: {message.text} min")


@router.callback_query(F.data == "create_student")
async def create_student_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    user = await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"] != "admin":
        await callback.message.answer(
            "You don't have permission."
        )
        return

    await state.set_state(CreateStudentStates.full_name)

    await callback.message.answer(
        "Enter student's full name:"
    )



@router.message(CreateStudentStates.full_name)
async def student_full_name_handler(
    message: types.Message,
    state: FSMContext
):
    await state.update_data(full_name=message.text)

    await state.set_state(CreateStudentStates.telegram_id)

    await message.answer(
        "Enter student's Telegram ID:"
    )


@router.message(CreateStudentStates.telegram_id)
async def student_telegram_id_handler(
    message: types.Message,
    state: FSMContext
):
    if not message.text.isdigit():
        await message.answer("Telegram ID must be a number.")
        return

    await state.update_data(
        telegram_id=int(message.text)
    )

    await state.set_state(CreateStudentStates.confirm)

    data = await state.get_data()

    await message.answer(
        "Create this student?\n\n"
        f"Full name: {data['full_name']}\n"
        f"Telegram ID: {data['telegram_id']}\n\n"
        "Send Yes to confirm or No to cancel."
    )

@router.message(CreateStudentStates.confirm)
async def create_student_confirm_handler(
    message: types.Message,
    state: FSMContext
):
    user = await get_user_tg_id(message.from_user.id)

    if user is None or user["role"] != "admin":
        await state.clear()
        await message.answer(
            "You don't have permission to access this."
        )
        return

    if message.text == "No":
        await state.clear()
        await message.answer(
            "Student creation cancelled."
        )
        return

    if message.text != "Yes":
        await message.answer(
            "Please send Yes or No."
        )
        return

    data = await state.get_data()

    student = await create_student_user(
        data["telegram_id"],
        data["full_name"]
    )

    if student is None:
        await state.clear()
        await message.answer(
            "Student already exists or could not be created."
        )
        return

    await state.clear()

    await message.answer(
        "Student created successfully."
    )




@router.callback_query(F.data == "create_teacher")
async def create_teacher_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    user = await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"] != "admin":
        await callback.message.answer(
            "You don't have permission."
        )
        return

    await state.set_state(CreateTeacherStates.full_name)

    await callback.message.answer(
        "Enter teacher's full name:"
    )


@router.message(CreateTeacherStates.full_name)
async def teacher_full_name_handler(
    message: types.Message,
    state: FSMContext
):
    await state.update_data(
        full_name=message.text
    )

    await state.set_state(
        CreateTeacherStates.telegram_id
    )

    await message.answer(
        "Enter teacher's Telegram ID:"
    )



@router.callback_query(F.data.regexp(r"^edit_student_\d+$"))
async def edit_student_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    user = await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"] != "admin":
        await callback.answer(
            "You don't have permission.",
            show_alert=True
        )
        return

    student_id = int(callback.data.split("_")[2])

    student = await get_student_by_id(student_id)

    if student is None:
        await callback.answer(
            "Student not found.",
            show_alert=True
        )
        return

    await state.update_data(
        student_id=student_id
    )

    await state.set_state(
        EditStudentStates.full_name
    )

    await callback.message.answer(
        "Enter new student's full name:"
    )

    await callback.answer()


@router.message(EditStudentStates.full_name)
async def edit_student_full_name_handler(
    message: types.Message,
    state: FSMContext
):
    await state.update_data(
        full_name=message.text
    )

    await state.set_state(
        EditStudentStates.telegram_id
    )

    await message.answer(
        "Enter new student's Telegram ID:"
    )


@router.message(EditStudentStates.telegram_id)
async def edit_student_telegram_id_handler(
    message: types.Message,
    state: FSMContext
):
    if not message.text.isdigit():
        await message.answer(
            "Telegram ID must be a number."
        )
        return

    await state.update_data(
        telegram_id=int(message.text)
    )

    await state.set_state(
        EditStudentStates.confirm
    )

    data = await state.get_data()

    await message.answer(
        "Update this student?\n\n"
        f"Full name: {data['full_name']}\n"
        f"Telegram ID: {data['telegram_id']}\n\n"
        "Send Yes to confirm or No to cancel."
    )


@router.message(EditStudentStates.confirm)
async def edit_student_confirm_handler(
    message: types.Message,
    state: FSMContext
):
    user = await get_user_tg_id(message.from_user.id)

    if user is None or user["role"] != "admin":
        await state.clear()
        await message.answer(
            "You don't have permission to access this."
        )
        return

    if message.text == "No":
        await state.clear()
        await message.answer(
            "Student update cancelled."
        )
        return

    if message.text != "Yes":
        await message.answer(
            "Please send Yes or No."
        )
        return

    data = await state.get_data()

    result = await update_student_user(
        data["student_id"],
        data["full_name"],
        data["telegram_id"]
    )

    await state.clear()

    if not result:
        await message.answer(
            "Student could not be updated."
        )
        return

    await message.answer(
        "Student updated successfully."
    )


@router.callback_query(F.data.regexp(r"^delete_student_\d+$"))
async def delete_student_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    user = await get_user_tg_id(callback.from_user.id)

    if user is None or user["role"] != "admin":
        await callback.answer(
            "You don't have permission.",
            show_alert=True
        )
        return

    student_id = int(callback.data.split("_")[2])

    student = await get_student_by_id(student_id)

    if student is None:
        await callback.answer(
            "Student not found.",
            show_alert=True
        )
        return

    await state.update_data(
        student_id=student_id
    )

    await state.set_state(
        DeleteStudentStates.confirm
    )

    await callback.message.answer(
        "⚠️ Delete this student?\n\n"
        f"Student ID: {student['id']}\n\n"
        "This will also remove the student's "
        "group membership and attendance records.\n\n"
        "Send Yes to confirm or No to cancel."
    )

    await callback.answer()


@router.message(DeleteStudentStates.confirm)
async def delete_student_confirm_handler(
    message: types.Message,
    state: FSMContext
):
    user = await get_user_tg_id(message.from_user.id)

    if user is None or user["role"] != "admin":
        await state.clear()
        await message.answer(
            "You don't have permission to access this."
        )
        return

    if message.text == "No":
        await state.clear()
        await message.answer(
            "Student deletion cancelled."
        )
        return

    if message.text != "Yes":
        await message.answer(
            "Please send Yes or No."
        )
        return

    data = await state.get_data()

    result = await delete_student(
        data["student_id"]
    )

    await state.clear()

    if not result:
        await message.answer(
            "Student could not be deleted."
        )
        return

    await message.answer(
        "Student deleted successfully."
    )


@router.message(F.text == "Teachers")
async def admin_teachers_handler(message: types.Message):
    user = await get_user_tg_id(message.from_user.id)

    if user is None:
        await message.answer("User not found.")
        return

    if user["role"] != "admin":
        await message.answer("You don't have permission to access this.")
        return

    teachers = await get_all_teachers()

    await message.answer(
        "Teachers:",
        reply_markup=teachers_keyboard(teachers)
    )



@router.message(CreateTeacherStates.telegram_id)
async def teacher_telegram_id_handler(
    message: types.Message,
    state: FSMContext
):
    if not message.text.isdigit():
        await message.answer(
            "Telegram ID must be a number."
        )
        return

    await state.update_data(
        telegram_id=int(message.text)
    )

    await state.set_state(
        CreateTeacherStates.confirm
    )

    data = await state.get_data()

    await message.answer(
        "Create this teacher?\n\n"
        f"Full name: {data['full_name']}\n"
        f"Telegram ID: {data['telegram_id']}\n\n"
        "Send Yes to confirm or No to cancel."
    )


@router.message(CreateTeacherStates.confirm)
async def create_teacher_confirm_handler(
    message: types.Message,
    state: FSMContext
):
    user = await get_user_tg_id(
        message.from_user.id
    )

    if user is None or user["role"] != "admin":
        await state.clear()

        await message.answer(
            "You don't have permission to access this."
        )
        return

    if message.text == "No":
        await state.clear()

        await message.answer(
            "Teacher creation cancelled."
        )
        return

    if message.text != "Yes":
        await message.answer(
            "Please send Yes or No."
        )
        return

    data = await state.get_data()

    teacher = await create_teacher_user(
        data["telegram_id"],
        data["full_name"]
    )

    if teacher is None:
        await state.clear()

        await message.answer(
            "Teacher already exists or could not be created."
        )
        return

    await state.clear()

    await message.answer(
        "Teacher created successfully."
    )