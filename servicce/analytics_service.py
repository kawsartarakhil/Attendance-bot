from database.connection import get_connection


async def get_student_statistics(student_id):
    conn=await get_connection()
    try:
        statistics=await conn.fetch("""
        select status,late_minutes,early_leave_minutes,time_in_class
        from attendance_records
        where student_id=$1
        """,student_id)
        
        total_lessons=len(statistics)
        present=0
        late=0
        absent=0
        excused=0
        left_early=0
        total_late_minutes=0
        total_early_leave_minutes=0
        total_time_in_class=0

        for row in statistics:
            if row["status"]=="present":
                present+=1
            elif row["status"]=="late":
                late+=1
            elif row["status"]=="absent":
                absent+=1
            elif row["status"]=="excused":
                excused+=1
            elif row["status"]=="left_early":
                left_early+=1

            total_late_minutes+=row["late_minutes"]
            total_early_leave_minutes+=row["early_leave_minutes"]
            total_time_in_class+=row["time_in_class"]

        attended=present+late+left_early

        if total_lessons==0:
            attendance_percentage=0
        else:
            attendance_percentage=round(attended*100/total_lessons,2)
        return { "total_lessons":total_lessons, "present":present, "late":late,"absent":absent, "excused":excused, "left_early":left_early, "attendance_percentage":attendance_percentage, "total_late_minutes":total_late_minutes, "total_early_leave_minutes":total_early_leave_minutes, "total_time_in_class":total_time_in_class}
    except Exception as er:
        print("get student statistics error:",er)
    finally:
        await conn.close()


async def get_group_statistics(group_id):
    conn=await get_connection()
    try:
        statistics=await conn.fetch("""
        select ar.status
        from attendance_records ar
        join lessons l on ar.lesson_id=l.id
        where l.group_id=$1
        """,group_id)

        total=len(statistics)
        present=0
        late=0
        absent=0
        excused=0
        left_early=0

        for row in statistics:
            if row["status"]=="present":
                present+=1
            elif row["status"]=="late":
                late+=1
            elif row["status"]=="absent":
                absent+=1
            elif row["status"]=="excused":
                excused+=1
            elif row["status"]=="left_early":
                left_early+=1

        attended=present+late+left_early

        if total==0:
            attendance_percentage=0
        else:
            attendance_percentage=round(attended*100/total,2)

        return { "total_records":total, "present":present, "late":late, "absent":absent, "excused":excused, "left_early":left_early, "attendance_percentage":attendance_percentage}
    except Exception as er:
        print("get group statistics error:",er)
    finally:
        await conn.close()


async def get_teacher_statistics(teacher_id):
    conn=await get_connection()
    try:
        statistics=await conn.fetch("""
        select ar.status from attendance_records ar
        join lessons l on ar.lesson_id=l.id
        where l.teacher_id=$1
        """,teacher_id)

        total=len(statistics)
        present=0
        late=0
        absent=0
        excused=0
        left_early=0

        for row in statistics:
            if row["status"]=="present":
                present+=1
            elif row["status"]=="late":
                late+=1
            elif row["status"]=="absent":
                absent+=1
            elif row["status"]=="excused":
                excused+=1
            elif row["status"]=="left_early":
                left_early+=1
        attended=present+late+left_early
        if total==0:
            attendance_percentage=0
        else:
            attendance_percentage=round(attended*100/total,2)

        lessons=await conn.fetch("""
        select id,group_id from lessons
        where teacher_id=$1
        """,teacher_id)

        groups=[]

        for lesson in lessons:
            if lesson["group_id"] not in groups:
                groups.append(lesson["group_id"])
        statistics={"total_lessons":len(lessons),"total_groups":len(groups),"total_attendance_records":total,"present":present,"late":late, "absent":absent, "excused":excused, "left_early":left_early, "attendance_percentage":attendance_percentage}
        return statistics
    except Exception as er:
        print("get teacher statistics error:",er)
    finally:
        await conn.close()

async def get_weekly_group_report(group_id):
    conn=await get_connection()
    try:
        report=await conn.fetch("""
        select l.lesson_date,l.subject, ar.status from lessons l
        left join attendance_records ar on l.id=ar.lesson_id
        where l.group_id=$1
        and l.lesson_date>=current_date-6
        order by l.lesson_date
        """,group_id)

        return report
    except Exception as er:
        print("get weekly group report error:",er)
    finally:
        await conn.close()


async def get_monthly_report():
    conn=await get_connection()
    try:
        report=await conn.fetch("""
        select l.lesson_date,l.subject, ar.status from lessons l
        left join attendance_records ar on l.id=ar.lesson_id
        where l.lesson_date>=current_date-29
        order by l.lesson_date
        """)
        return report
    except Exception as er:
        print("get monthly report error:",er)
    finally:
        await conn.close()


async def get_students_at_risk():
    conn=await get_connection()
    try:
        students=await conn.fetch("""
        select s.id,u.full_name from students s
        join users u on s.user_id=u.id
        """)
        at_risk=[]

        for student in students:
            statistics=await get_student_statistics(student["id"])
            monthly=await conn.fetch("""
            select status from attendance_records
            where student_id=$1
            and created_at>=current_date-29
            """,student["id"])
            monthly_absent=0
            monthly_late=0
            for row in monthly:
                if row["status"]=="absent":
                    monthly_absent+=1
                elif row["status"]=="late":
                    monthly_late+=1
            if statistics["attendance_percentage"]<75:
                at_risk.append(student)
            elif monthly_absent>=3:
                at_risk.append(student)
            elif monthly_late>=5:
                at_risk.append(student)
        return at_risk
    except Exception as er:
        print("get students at risk error:",er)
    finally:
        await conn.close()


async def get_most_missed_day():
    conn=await get_connection()
    try:
        attendance=await conn.fetch("""
        select l.lesson_date from attendance_records ar
        join lessons l on ar.lesson_id=l.id
        where ar.status='absent'
        """)
        days={}

        for row in attendance:
            day=row["lesson_date"].strftime("%A")
            if day not in days:
                days[day]=0
            days[day]+=1
        if not days:
            return None
        most_missed_day=""
        most_missed_count=0
        for day,count in days.items():
            if count>most_missed_count:
                most_missed_day=day
                most_missed_count=count

        result={"day":most_missed_day,"missed_count":most_missed_count}
        return result
    except Exception as er:
        print("get most missed day error:",er)
    finally:
        await conn.close()


async def get_attendance_trend(student_id):
    conn=await get_connection()
    try:
        trend=await conn.fetch("""
        select l.lesson_date,ar.status from attendance_records ar
        join lessons l on ar.lesson_id=l.id
        where ar.student_id=$1
        order by l.lesson_date
        """,student_id)
        return trend
    except Exception as er:
        print("get attendance trend error:",er)
    finally:
        await conn.close()