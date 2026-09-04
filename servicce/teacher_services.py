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
        select t.id,t.user_id,u.full_name from teachers t
        join users u on t.user_id=u.id
        order by u.full_name
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


from database.connection import get_connection


async def create_teacher_user(tg_id, full_name):
    conn = await get_connection()

    try:
        # Check if user already exists
        user = await conn.fetchrow("""
        select * from users
        where telegram_id=$1
        """, tg_id)

        if user:
            # Check if already a teacher
            teacher = await conn.fetchrow("""
            select * from teachers
            where user_id=$1
            """, user["id"])

            if teacher:
                return None

    
            await conn.execute("""
            update users
            set role='teacher', full_name=$1
            where id=$2
            """, full_name, user["id"])

            await conn.execute("""
            insert into teachers(user_id)
            values($1)
            """, user["id"])

            return user

    
        user = await conn.fetchrow("""
        insert into users(telegram_id, full_name, role)
        values($1, $2, 'teacher')
        returning *
        """, tg_id, full_name)

        await conn.execute("""
        insert into teachers(user_id)
        values($1)
        """, user["id"])

        return user

    except Exception as er:
        print("create teacher user error:", er)
        return None

    finally:
        await conn.close()




async def update_teacher_user(teacher_id, full_name, telegram_id):
    conn = await get_connection()

    try:
        teacher = await conn.fetchrow("""
        select t.id, t.user_id
        from teachers t
        where t.id=$1
        """, teacher_id)

        if teacher is None:
            return False

        await conn.execute("""
        update users
        set full_name=$1, telegram_id=$2
        where id=$3
        """, full_name, telegram_id, teacher["user_id"])

        return True

    except Exception as er:
        print("update teacher user error:", er)
        return False

    finally:
        await conn.close()


async def delete_teacher(teacher_id):
    conn = await get_connection()

    try:
        teacher = await conn.fetchrow("""
        select user_id
        from teachers
        where id=$1
        """, teacher_id)

        if teacher is None:
            return False

        await conn.execute("""
        delete from users
        where id=$1
        """, teacher["user_id"])

        return True

    except Exception as er:
        print("delete teacher error:", er)
        return False

    finally:
        await conn.close()



async def create_teacher_user(tg_id, full_name):
    conn = await get_connection()

    try:
        user = await conn.fetchrow("""
        select * from users
        where telegram_id=$1
        """, tg_id)

        if user:
            teacher = await conn.fetchrow("""
            select * from teachers
            where user_id=$1
            """, user["id"])

            if teacher:
                return None

            await conn.execute("""
            update users
            set role='teacher', full_name=$1
            where id=$2
            """, full_name, user["id"])

            await conn.execute("""
            insert into teachers(user_id)
            values($1)
            """, user["id"])

            return user

        user = await conn.fetchrow("""
        insert into users(telegram_id, full_name, role)
        values($1, $2, 'teacher')
        returning *
        """, tg_id, full_name)

        await conn.execute("""
        insert into teachers(user_id)
        values($1)
        """, user["id"])

        return user

    except Exception as er:
        print("create teacher user error:", er)
        return None

    finally:
        await conn.close()


