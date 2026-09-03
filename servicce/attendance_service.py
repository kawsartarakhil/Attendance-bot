from database.connection import get_connection

async def check_in(lesson_id,student_id):
    conn=await get_connection()
    try:
        attendance=await conn.fetchrow("""
        select check_in_time
        from attendance_records
        where lesson_id=$1 and student_id=$2
        """,lesson_id,student_id)

        if attendance is None:
            await conn.execute("""
            insert into attendance_records(lesson_id,student_id,status)
            values($1,$2,null)
            """,lesson_id,student_id)

        else:
            if attendance["check_in_time"] is not None:
                return False

        await conn.execute("""
        update attendance_records
        set check_in_time=current_timestamp,status='present'
        where lesson_id=$1 and student_id=$2
        """,lesson_id,student_id)

        await calculate_late_minutes(lesson_id,student_id)
        return True

    except Exception as er:
        print("check in error:",er)
        return False

    finally:
        await conn.close()


async def check_out(lesson_id,student_id):
    conn=await get_connection()
    try:
        attendance=await conn.fetchrow("""
        select check_in_time,check_out_time
        from attendance_records
        where lesson_id=$1 and student_id=$2
        """,lesson_id,student_id)

        if attendance is None or attendance["check_in_time"] is None:
            return False

        if attendance["check_out_time"] is not None:
            return False

        await conn.execute("""
        update attendance_records
        set check_out_time=current_timestamp
        where lesson_id=$1 and student_id=$2
        """,lesson_id,student_id)

        await calculate_early_leave_minutes(lesson_id,student_id)
        await calculate_time_in_class(lesson_id,student_id)

        return True

    except Exception as er:
        print("check out error:",er)
        return False

    finally:
        await conn.close()


async def mark_attendance(lesson_id,student_id,status):
    conn=await get_connection()
    try:
        await conn.execute("""
        update attendance_records
        set status=$1
        where lesson_id=$2 and student_id=$3
        """,status,lesson_id,student_id)
        return True
    except Exception as er:
        print("mark attendance error:",er)
        return False
    finally:
        await conn.close()


async def get_attendance_record(lesson_id,student_id):
    conn=await get_connection()
    try:
        attendance=await conn.fetchrow("""
        select *
        from attendance_records
        where lesson_id=$1 and student_id=$2
        """,lesson_id,student_id)
        return attendance
    except Exception as er:
        print("get attendance record error:",er)
        return None
    finally:
        await conn.close()


async def get_student_attendance(student_id):
    conn=await get_connection()
    try:
        attendance=await conn.fetch("""
        select
        ar.id,
        ar.lesson_id,
        l.subject,
        l.lesson_date,
        l.start_time,
        l.end_time,
        ar.check_in_time,
        ar.check_out_time,
        ar.late_minutes,
        ar.early_leave_minutes,
        ar.time_in_class,
        ar.status
        from attendance_records ar
        join lessons l on ar.lesson_id=l.id
        where ar.student_id=$1
        order by l.lesson_date desc,l.start_time desc
        """,student_id)
        return attendance
    except Exception as er:
        print("get student attendance error:",er)
        return []
    finally:
        await conn.close()


async def get_lesson_attendance(lesson_id):
    conn=await get_connection()
    try:
        attendance=await conn.fetch("""
        select
        ar.id,
        ar.student_id,
        u.full_name,
        ar.check_in_time,
        ar.check_out_time,
        ar.late_minutes,
        ar.early_leave_minutes,
        ar.time_in_class,
        ar.status
        from attendance_records ar
        join students s on ar.student_id=s.id
        join users u on s.user_id=u.id
        where ar.lesson_id=$1
        order by u.full_name
        """,lesson_id)
        return attendance
    except Exception as er:
        print("get lesson attendance error:",er)
        return []
    finally:
        await conn.close()


async def get_group_attendance(group_id):
    conn=await get_connection()
    try:
        attendance=await conn.fetch("""
        select
        ar.id,
        ar.lesson_id,
        ar.student_id,
        u.full_name,
        l.subject,
        l.lesson_date,
        ar.check_in_time,
        ar.check_out_time,
        ar.late_minutes,
        ar.early_leave_minutes,
        ar.time_in_class,
        ar.status
        from attendance_records ar
        join lessons l on ar.lesson_id=l.id
        join students s on ar.student_id=s.id
        join users u on s.user_id=u.id
        where l.group_id=$1
        order by l.lesson_date desc,u.full_name
        """,group_id)
        return attendance
    except Exception as er:
        print("get group attendance error:",er)
        return []
    finally:
        await conn.close()


async def get_attendance_percentage(student_id):
    conn=await get_connection()
    try:
        result=await conn.fetchrow("""
        select
        count(*) as total_lessons,
        count(*) filter(
            where status in ('present','late','left_early')
        ) as attended_lessons
        from attendance_records
        where student_id=$1
        """,student_id)

        if result["total_lessons"]==0:
            return 0

        percentage=result["attended_lessons"]*100/result["total_lessons"]

        return round(percentage,2)

    except Exception as er:
        print("get attendance percentage error:",er)
        return 0

    finally:
        await conn.close()


async def calculate_late_minutes(lesson_id,student_id):
    conn=await get_connection()
    try:
        result=await conn.fetchrow("""
        select
        ar.check_in_time,
        l.start_time
        from attendance_records ar
        join lessons l on ar.lesson_id=l.id
        where ar.lesson_id=$1 and ar.student_id=$2
        """,lesson_id,student_id)

        if result is None or result["check_in_time"] is None:
            return 0

        check_in=result["check_in_time"].time()
        start_time=result["start_time"]

        late_minutes=(check_in.hour*60+check_in.minute)-(start_time.hour*60+start_time.minute)

        if late_minutes<0:
            late_minutes=0

        status="late" if late_minutes>0 else "present"

        await conn.execute("""
        update attendance_records
        set late_minutes=$1,status=$2
        where lesson_id=$3 and student_id=$4
        """,late_minutes,status,lesson_id,student_id)

        return late_minutes

    except Exception as er:
        print("calculate late minutes error:",er)
        return 0

    finally:
        await conn.close()


async def calculate_early_leave_minutes(lesson_id,student_id):
    conn=await get_connection()
    try:
        result=await conn.fetchrow("""
        select
        ar.check_out_time,
        ar.status,
        l.end_time
        from attendance_records ar
        join lessons l on ar.lesson_id=l.id
        where ar.lesson_id=$1 and ar.student_id=$2
        """,lesson_id,student_id)

        if result is None or result["check_out_time"] is None:
            return 0

        end_time=result["end_time"]
        check_out=result["check_out_time"].time()

        early_leave_minutes=(end_time.hour*60+end_time.minute)-(check_out.hour*60+check_out.minute)

        if early_leave_minutes<0:
            early_leave_minutes=0

        if early_leave_minutes>0:
            status="left_early"
        elif result["status"]=="late":
            status="late"
        else:
            status="present"

        await conn.execute("""
        update attendance_records
        set early_leave_minutes=$1,status=$2
        where lesson_id=$3 and student_id=$4
        """,early_leave_minutes,status,lesson_id,student_id)

        return early_leave_minutes

    except Exception as er:
        print("calculate early leave minutes error:",er)
        return 0

    finally:
        await conn.close()


async def calculate_time_in_class(lesson_id,student_id):
    conn=await get_connection()
    try:
        result=await conn.fetchrow("""
        select check_in_time,check_out_time
        from attendance_records
        where lesson_id=$1 and student_id=$2
        """,lesson_id,student_id)

        if result is None:
            return 0

        if result["check_in_time"] is None or result["check_out_time"] is None:
            return 0

        check_in=result["check_in_time"]
        check_out=result["check_out_time"]

        time_in_class=(check_out.hour*60+check_out.minute)-(check_in.hour*60+check_in.minute)

        if time_in_class<0:
            time_in_class=0

        await conn.execute("""
        update attendance_records
        set time_in_class=$1
        where lesson_id=$2 and student_id=$3
        """,time_in_class,lesson_id,student_id)

        return time_in_class

    except Exception as er:
        print("calculate time in class error:",er)
        return 0

    finally:
        await conn.close()


async def mark_absent_students(lesson_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        update attendance_records
        set status='absent'
        where lesson_id=$1
        and check_in_time is null
        and status is null
        """,lesson_id)
    except Exception as er:
        print("mark absent students error:",er)
    finally:
        await conn.close()


async def edit_attendance(attendance_id,edited_by,old_status,new_status,edit_reason):
    conn=await get_connection()
    try:
        await conn.execute("""
        update attendance_records
        set status=$1
        where id=$2
        """,new_status,attendance_id)

        await conn.execute("""
        insert into attendance_edits(
            attendance_id,
            edited_by,
            old_status,
            new_status,
            edit_reason
        )
        values($1,$2,$3,$4,$5)
        """,attendance_id,edited_by,old_status,new_status,edit_reason)

        return True

    except Exception as er:
        print("edit attendance error:",er)
        return False

    finally:
        await conn.close()


async def get_attendance_edits(attendance_id):
    conn=await get_connection()
    try:
        edits=await conn.fetch("""
        select
        ae.id,
        ae.attendance_id,
        ae.edited_by,
        u.full_name as editor_name,
        ae.old_status,
        ae.new_status,
        ae.edit_reason,
        ae.edited_at
        from attendance_edits ae
        join users u on ae.edited_by=u.id
        where ae.attendance_id=$1
        order by ae.edited_at desc
        """,attendance_id)

        return edits

    except Exception as er:
        print("get attendance edits error:",er)
        return []

    finally:
        await conn.close()


async def get_attendance_by_id(attendance_id):
    conn=await get_connection()
    try:
        attendance=await conn.fetchrow("""
        select
        ar.id,
        ar.lesson_id,
        ar.student_id,
        u.full_name,
        ar.status
        from attendance_records ar
        join students s on ar.student_id=s.id
        join users u on s.user_id=u.id
        where ar.id=$1
        """,attendance_id)

        return attendance

    except Exception as er:
        print("get attendance by id error:",er)
        return None

    finally:
        await conn.close()


async def get_students_not_checked_in(lesson_id):
    conn=await get_connection()
    try:
        students=await conn.fetch("""
        select
        u.telegram_id,
        u.full_name
        from attendance_records ar
        join students s on ar.student_id=s.id
        join users u on s.user_id=u.id
        where ar.lesson_id=$1
        and ar.check_in_time is null
        """,lesson_id)

        return students

    except Exception as er:
        print("get students not checked in error:",er)
        return []

    finally:
        await conn.close()


async def get_students_with_low_attendance():
    conn=await get_connection()
    try:
        students=await conn.fetch("""
        select
        s.id,
        u.telegram_id,
        u.full_name,
        count(ar.id) as total_lessons,
        count(ar.id) filter(
            where ar.status in ('present','late','left_early')
        ) as attended
        from students s
        join users u on s.user_id=u.id
        join attendance_records ar on ar.student_id=s.id
        group by s.id,u.telegram_id,u.full_name
        having count(ar.id)>0
        and count(ar.id) filter(
            where ar.status in ('present','late','left_early')
        )*100.0/count(ar.id)<75
        """)

        return students

    except Exception as er:
        print("get low attendance students error:",er)
        return []

    finally:
        await conn.close()