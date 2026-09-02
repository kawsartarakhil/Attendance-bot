from database.connection import get_connection

async def create_group(name,course_id,teacher_id=None):
    conn=await get_connection()
    try:
        await conn.execute("""
        insert into groups(name,course_id,teacher_id)
        values($1,$2,$3)
        """,name,course_id,teacher_id)
    except Exception as er:
        print("create group error:",er)
    finally:
        await conn.close()

async def get_group_by_id(group_id):
    conn=await get_connection()
    try:
        group=await conn.fetchrow("""
        select g.id,g.name,g.course_id,g.teacher_id,c.name as course_name from groups g
        join courses c on g.course_id=c.id
        where g.id=$1
        """,group_id)
        return group
    except Exception as er:
        print("get group by id error:",er)
    finally:
        await conn.close()

async def get_all_groups():
    conn=await get_connection()
    try:
        groups=await conn.fetch("""
        select g.id,g.name,g.course_id,g.teacher_id,c.name as course_name from groups g
        join courses c on g.course_id=c.id
        """)
        return groups
    except Exception as er:
        print("get all groups error:",er)
    finally:
        await conn.close()

async def update_group(group_id,name,course_id,teacher_id=None):
    conn=await get_connection()
    try:
        await conn.execute("""
        update groups set name=$1,course_id=$2,teacher_id=$3
        where id=$4
        """,name,course_id,teacher_id,group_id)
    except Exception as er:
        print("update group error:",er)
    finally:
        await conn.close()

async def delete_group(group_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        delete from groups
        where id=$1
        """,group_id)
    except Exception as er:
        print("delete group error:",er)
    finally:
        await conn.close()

async def add_student_to_group(student_id,group_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        insert into group_students(group_id,student_id)
        values($1,$2)
        """,group_id,student_id)
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

async def get_group_students(group_id):
    conn=await get_connection()
    try:
        students=await conn.fetch("""
        select s.id,s.user_id,u.full_name,u.username,u.phone from group_students gs
        join students s on gs.student_id=s.id
        join users u on s.user_id=u.id
        where gs.group_id=$1
        """,group_id)
        return students
    except Exception as er:
        print("get group students error:",er)
    finally:
        await conn.close()

async def assign_teacher(teacher_id,group_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        update groups set teacher_id=$1
        where id=$2
        """,teacher_id,group_id)
    except Exception as er:
        print("assign teacher error:",er)
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