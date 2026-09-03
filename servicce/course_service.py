from database.connection import get_connection

async def create_course(name,description):
    conn=await get_connection()
    try:
        await conn.execute("""
        insert into courses(name,description)
        values($1,$2)
        """,name,description)
    except Exception as er:
        print("create course error:",er)
    finally:
        await conn.close()

async def get_course_by_id(course_id):
    conn=await get_connection()
    try:
        course=await conn.fetchrow("""
        select * from courses
        where id=$1
        """,course_id)
        return course
    except Exception as er:
        print("get course by id error:",er)
    finally:
        await conn.close()

async def get_all_courses():
    conn=await get_connection()
    try:
        courses=await conn.fetch("""
        select * from courses
        """)
        return courses
    except Exception as er:
        print("get all courses error:",er)
    finally:
        await conn.close()

async def update_course(course_id,name,description):
    conn=await get_connection()
    try:
        await conn.execute("""
        update courses set name=$1,description=$2
        where id=$3
        """,name,description,course_id)
    except Exception as er:
        print("update course error:",er)
    finally:
        await conn.close()

async def delete_course(course_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        delete from courses
        where id=$1
        """,course_id)
    except Exception as er:
        print("delete course error:",er)
    finally:
        await conn.close()


