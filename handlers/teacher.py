from aiogram import Router,types,F
from aiogram.types import CallbackQuery
from servicce.user_services import get_user_tg_id
from servicce.teacher_services import get_teacher_by_user_id,get_teacher_groups
from keyboards.inline import groups_keyboard
from database.connection import get_connection

router=Router()

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
    await message.answer("My Groups:",reply_markup=groups_keyboard(groups))
# F.data → data-e button ra megira.
# regexp → check mekona ke data ba yak pattern match shawa.
# ^ → az awal shuru shawa.
# group_ → bayad aynan group_ bashad.
# \d → raqam ast.
# + → yak ya chand raqam.
# $ → dar akhir tamam shawa.
@router.callback_query(F.data.regexp(r"^group_\d+$"))
async def teacher_group_handler(callback:CallbackQuery):
    group_id=int(callback.data.split("_")[1])
    conn=await get_connection()
    try:
        group=await conn.fetchrow("""
        select g.id,g.name,c.name as course_name from groups g
        join courses c on g.course_id=c.id
        where g.id=$1
        """,group_id)
        if group is None:
            await callback.message.answer("Group not found.")
            await callback.answer()
            return
        students_count=await conn.fetchval("""
        select count(*) from group_students
        where group_id=$1
        """,group_id)
    except Exception as er:
        print("teacher group error:",er)
        await callback.message.answer("Something went wrong.")
        await callback.answer()
        return
    finally:
        await conn.close()
    await callback.message.answer(
        "Group: "+group["name"]+
        "\nCourse: "+group["course_name"]+
        "\nStudents: "+str(students_count)
    )
    await callback.answer()