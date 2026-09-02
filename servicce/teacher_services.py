from database.connection import get_connection

async def create_teacher(user_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        insert into teachers(user_id)
        values($1)
        """,user_id)
    except Exception as er:
        print("create teacher error:",er)
    finally:
        await conn.close()

async def get_teacher_by_user_id(user_id):
    conn=await get_connection()
    try:
        teacher=await conn.fetchrow("""
        select * from teachers
        where user_id=$1
        """,user_id)
        return teacher
    except Exception as er:
        print("get teacher by user id error:",er)
    finally:
        await conn.close()

async def get_teacher_by_id(teacher_id):
    conn=await get_connection()
    try:
        teacher=await conn.fetchrow("""
        select * from teachers
        where id=$1
        """,teacher_id)
        return teacher
    except Exception as er:
        print("get teacher by id error:",er)
    finally:
        await conn.close()

async def get_all_teachers():
    conn=await get_connection()
    try:
        teachers=await conn.fetch("""
        select * from teachers
        """)
        return teachers
    except Exception as er:
        print("get all teachers error:",er)
    finally:
        await conn.close()

async def assign_teacher_to_group(teacher_id,group_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        update groups set teacher_id=$1
        where id=$2
        """,teacher_id,group_id)
    except Exception as er:
        print("assign teacher to group error:",er)
    finally:
        await conn.close()

async def get_teacher_groups(teacher_id):
    conn=await get_connection()
    try:
        groups=await conn.fetch("""
        select g.id,g.name,g.course_id,c.name as course_name from groups g
        join courses c on g.course_id=c.id
        where g.teacher_id=$1
        """,teacher_id)
        return groups
    except Exception as er:
        print("get teacher groups error:",er)
    finally:
        await conn.close()