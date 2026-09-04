from database.connection import get_connection

async def create_student(user_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        insert into students(user_id)
        values($1)
        """,user_id)
    except Exception as er:
        print("create student error:",er)
    finally:
        await conn.close()

async def get_student_by_user_id(user_id):
    conn=await get_connection()
    try:
        student=await conn.fetchrow("""
        select * from students
        where user_id=$1
        """,user_id)
        return student
    except Exception as er:
        print("get student by user id error:",er)
    finally:
        await conn.close()

async def get_student_by_id(student_id):
    conn=await get_connection()
    try:
        student=await conn.fetchrow("""
        select * from students
        where id=$1
        """,student_id)
        return student
    except Exception as er:
        print("get student by id error:",er)
    finally:
        await conn.close()

async def get_all_students():
    conn=await get_connection()
    try:
        students=await conn.fetch("""
        select s.id,s.user_id,u.full_name from students s
        join users u on s.user_id=u.id
        order by u.full_name
        """)
        return students
    except Exception as er:
        print("get all students error:",er)
    finally:
        await conn.close()

async def add_student_to_group(student_id,group_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        insert into group_students(student_id,group_id)
        values($1,$2)
        """,student_id,group_id)
    except Exception as er:
        print("add student to group error:",er)
    finally:
        await conn.close()

async def remove_student_from_group(student_id,group_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        delete from group_students
        where student_id=$1 and group_id=$2
        """,student_id,group_id)
    except Exception as er:
        print("remove student from group error:",er)
    finally:
        await conn.close()

async def get_student_group(student_id):
    conn=await get_connection()
    try:
        group=await conn.fetchrow("""
        select g.id,g.name,g.course_id,c.name as course_name from group_students gs
        join groups g on gs.group_id=g.id
        join courses c on g.course_id=c.id
        where gs.student_id=$1
        """,student_id)
        return group
    except Exception as er:
        print("get student group error:",er)
    finally:
        await conn.close()




async def get_group_student_users(group_id):
    conn=await get_connection()
    try:
        students=await conn.fetch("""
        select u.id,u.telegram_id,u.full_name
        from group_students gs
        join students s on gs.student_id=s.id
        join users u on s.user_id=u.id
        where gs.group_id=$1
        """,group_id)
        return students
    except Exception as er:
        print("get group student users error:",er)
    finally:
        await conn.close()


async def create_student_user(tg_id, full_name):
    conn = await get_connection()

    try:
        user = await conn.fetchrow("""
        select * from users
        where telegram_id=$1
        """, tg_id)

        if user:
            student = await conn.fetchrow("""
            select * from students
            where user_id=$1
            """, user["id"])

            if student:
                return None

            await conn.execute("""
            update users
            set role='student', full_name=$1
            where id=$2
            """, full_name, user["id"])

            await conn.execute("""
            insert into students(user_id)
            values($1)
            """, user["id"])

            return user

        user = await conn.fetchrow("""
        insert into users(telegram_id, full_name, role)
        values($1, $2, 'student')
        returning *
        """, tg_id, full_name)

        await conn.execute("""
        insert into students(user_id)
        values($1)
        """, user["id"])

        return user

    except Exception as er:
        print("create student user error:", er)
        return None

    finally:
        await conn.close()


async def update_student_user(student_id, full_name, telegram_id):
    conn = await get_connection()

    try:
        student = await conn.fetchrow("""
        select s.id, s.user_id
        from students s
        where s.id=$1
        """, student_id)

        if student is None:
            return False

        await conn.execute("""
        update users
        set full_name=$1, telegram_id=$2
        where id=$3
        """, full_name, telegram_id, student["user_id"])

        return True

    except Exception as er:
        print("update student user error:", er)
        return False

    finally:
        await conn.close()


async def delete_student(student_id):
    conn = await get_connection()

    try:
        student = await conn.fetchrow("""
        select user_id
        from students
        where id=$1
        """, student_id)

        if student is None:
            return False

        await conn.execute("""
        delete from users
        where id=$1
        """, student["user_id"])

        return True

    except Exception as er:
        print("delete student error:", er)
        return False

    finally:
        await conn.close()