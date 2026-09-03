from aiogram import Router, types, F
from servicce.user_services import get_user_tg_id
from servicce.teacher_services import get_teacher_by_user_id,get_teacher_groups
from keyboards.inline import groups_keyboard
from database.connection import get_connection
router=Router()
@router.message(F.text=="My Groups")
async def my_groups_handler(message: types.Message):
    user=await get_user_tg_id(message.from_user.id)
    teacher=await get_teacher_by_user_id(user["id"])
    if teacher is None:
        await message.answer("Teacher profile not found.")
        return
    groups=await get_teacher_groups(teacher["id"])
    if not groups:
        await message.answer("You don't have any groups.")
        return
    await message.answer("My Groups:", reply_markup=groups_keyboard(groups))

@router.callback_query(F.data.startswith("group_"))
async def teacher_group_handler(callback: types.CallbackQuery):
    group_id = int(callback.data.split("_")[1])
    conn = await get_connection()
    try:
        group = await conn.fetchrow("""
        select g.id,g.name,c.name as course_name from groups g
        join courses c on g.course_id=c.id
        where g.id=$1
        """,group_id)
        if group is None:
            await callback.message.answer("group not found.")
            await callback.answer()
            return
        students_count = await conn.fetchval("""
        select count(*) from group_students
        where group_id=$1
        """,group_id)
    except Exception as er:
        print("teacher group error:",er)
        await callback.message.answer("something went wrong.")
        await callback.answer()
        return
    finally:
        await conn.close()
    await callback.message.answer("group: "+group["name"]+"\ncourse: "+group["course_name"]+"\n"+"students: "+str(students_count))
    await callback.answer()