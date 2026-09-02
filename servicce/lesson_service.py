from database.connection import get_connection

# groups ro ba lessons join kardem ta nomi group ro girifta tavonem
# teachers ro ba lessons join kardem ta malumot dar borai teacher ro girifta tavonem
# users ro ba teachers join kardem ta full name  teacher ro girifta tavonem
# rooms ro ba lessons join kardem ta nomi room ro girifta tavonem

async def create_lesson(group_id,teacher_id,room_id,subject,lesson_date,start_time,end_time):
    conn=await get_connection()
    try:
        await conn.execute("""
        insert into lessons(group_id,teacher_id,room_id,subject,lesson_date,start_time,end_time)
        values($1,$2,$3,$4,$5,$6,$7)
        """,group_id,teacher_id,room_id,subject,lesson_date,start_time,end_time)
    except Exception as er:
        print("create lesson error:",er)
    finally:
        await conn.close()

async def get_lesson_by_id(lesson_id):
    conn=await get_connection()
    try:
        lesson=await conn.fetchrow("""
        select l.id,l.group_id,g.name as group_name,l.teacher_id,
        u.full_name as teacher_name,l.room_id,r.name as room_name,
        l.subject,l.lesson_date,l.start_time,l.end_time,l.status from lessons l
        join groups g on l.group_id=g.id
        join teachers t on l.teacher_id=t.id
        join users u on t.user_id=u.id
        left join rooms r on l.room_id=r.id
        where l.id=$1
        """,lesson_id)
        return lesson
    except Exception as er:
        print("get lesson by id error:",er)
    finally:
        await conn.close()

async def get_today_lessons():
    conn=await get_connection()
    try:
        lessons=await conn.fetch("""
        select l.id,l.group_id,g.name as group_name,l.teacher_id,
        u.full_name as teacher_name,l.room_id,r.name as room_name,
        l.subject,l.lesson_date,l.start_time,l.end_time,l.status from lessons l
        join groups g on l.group_id=g.id
        join teachers t on l.teacher_id=t.id
        join users u on t.user_id=u.id
        left join rooms r on l.room_id=r.id
        where l.lesson_date=current_date
        order by l.start_time
        """)
        return lessons
    except Exception as er:
        print("get today lessons error:",er)
    finally:
        await conn.close()

async def get_current_lesson(group_id):
    conn=await get_connection()
    try:
        lesson=await conn.fetchrow("""
        select l.id,l.group_id,g.name as group_name,l.teacher_id,
        u.full_name as teacher_name,l.room_id,r.name as room_name,
        l.subject,l.lesson_date,l.start_time,l.end_time,l.status from lessons l
        join groups g on l.group_id=g.id
        join teachers t on l.teacher_id=t.id
        join users u on t.user_id=u.id
        left join rooms r on l.room_id=r.id
        where l.group_id=$1 and l.lesson_date=current_date and current_time between l.start_time and l.end_time and l.status!='cancelled'
        limit 1
        """,group_id)
        return lesson
    except Exception as er:
        print("get current lesson error:",er)
    finally:
        await conn.close()

async def get_upcoming_lessons(group_id):
    conn=await get_connection()
    try:
        lessons=await conn.fetch("""
        select l.id,l.group_id,g.name as group_name,l.teacher_id,
        u.full_name as teacher_name,l.room_id,r.name as room_name,
        l.subject,l.lesson_date,l.start_time,l.end_time,l.status from lessons l
        join groups g on l.group_id=g.id
        join teachers t on l.teacher_id=t.id
        join users u on t.user_id=u.id
        left join rooms r on l.room_id=r.id
        where l.group_id=$1 and (l.lesson_date>current_date or (l.lesson_date=current_date and l.start_time>current_time)) and l.status!='cancelled'
        order by l.lesson_date,l.start_time
        """,group_id)
        return lessons
    except Exception as er:
        print("get upcoming lessons error:",er)
    finally:
        await conn.close()

async def get_teacher_lessons(teacher_id):
    conn=await get_connection()
    try:
        lessons=await conn.fetch("""
        select l.id,l.group_id,g.name as group_name,l.teacher_id,
        u.full_name as teacher_name,l.room_id,r.name as room_name,
        l.subject,l.lesson_date,l.start_time,l.end_time,l.status from lessons l
        join groups g on l.group_id=g.id
        join teachers t on l.teacher_id=t.id
        join users u on t.user_id=u.id
        left join rooms r on l.room_id=r.id
        where l.teacher_id=$1
        order by l.lesson_date,l.start_time
        """,teacher_id)
        return lessons
    except Exception as er:
        print("get teacher lessons error:",er)
    finally:
        await conn.close()

async def get_group_lessons(group_id):
    conn=await get_connection()
    try:
        lessons=await conn.fetch("""
        select l.id,l.group_id,g.name as group_name,l.teacher_id,
        u.full_name as teacher_name,l.room_id,r.name as room_name,
        l.subject,l.lesson_date,l.start_time,l.end_time,l.status from lessons l
        join groups g on l.group_id=g.id
        join teachers t on l.teacher_id=t.id
        join users u on t.user_id=u.id
        left join rooms r on l.room_id=r.id
        where l.group_id=$1
        order by l.lesson_date,l.start_time
        """,group_id)
        return lessons
    except Exception as er:
        print("get group lessons error:",er)
    finally:
        await conn.close()

async def update_lesson_status(lesson_id,status):
    conn=await get_connection()
    try:
        await conn.execute("""
        update lessons set status=$1
        where id=$2
        """,status,lesson_id)
    except Exception as er:
        print("update lesson status error:",er)
    finally:
        await conn.close()

async def cancel_lesson(lesson_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        update lessons set status='cancelled'
        where id=$1
        """,lesson_id)
    except Exception as er:
        print("cancel lesson error:",er)
    finally:
        await conn.close()