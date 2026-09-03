from datetime import time
from database.connection import get_connection

async def create_schedule(group_id,weekday,start_time,end_time,room_id=None):
    conn=await get_connection()
    try:
        start_time=time.fromisoformat(start_time)
        end_time=time.fromisoformat(end_time)
        await conn.execute("""
        insert into schedules(group_id,weekday,start_time,end_time,room_id)
        values($1,$2,$3,$4,$5)
        """,group_id,weekday,start_time,end_time,room_id)
    except Exception as er:
        print("create schedule error:",er)
    finally:
        await conn.close()

async def get_schedule_by_id(schedule_id):
    conn=await get_connection()
    try:
        schedule=await conn.fetchrow("""
        select s.id,s.group_id,g.name as group_name,s.weekday,
        s.start_time,s.end_time,s.room_id,r.name as room_name,s.is_active from schedules s
        join groups g on s.group_id=g.id
        left join rooms r on s.room_id=r.id
        where s.id=$1
        """,schedule_id)
        return schedule
    except Exception as er:
        print("get schedule by id error:",er)
    finally:
        await conn.close()


# injo join kardm ba jadvali groups az ruye group_id mefahmem ki kadom group ast va bad join kardem ba jadvali rooms az ruye room_id mefahmem ki kadom room ast
async def get_group_schedules(group_id):
    conn=await get_connection()
    try:
        schedules=await conn.fetch("""
        select s.id,s.group_id,g.name as group_name,s.weekday,
        s.start_time,s.end_time,s.room_id,r.name as room_name,s.is_active from schedules s
        join groups g on s.group_id=g.id
        left join rooms r on s.room_id=r.id
        where s.group_id=$1
        order by s.weekday,s.start_time
        """,group_id)
        return schedules
    except Exception as er:
        print("get group schedules error:",er)
    finally:
        await conn.close()

async def get_all_schedules():
    conn=await get_connection()
    try:
        schedules=await conn.fetch("""
        select s.id,s.group_id,g.name as group_name,s.weekday,
        s.start_time,s.end_time,s.room_id,r.name as room_name,s.is_active from schedules s
        join groups g on s.group_id=g.id
        left join rooms r on s.room_id=r.id
        order by s.weekday,s.start_time
        """)
        return schedules
    except Exception as er:
        print("get all schedules error:",er)
    finally:
        await conn.close()


async def update_schedule(schedule_id,group_id,weekday,start_time,end_time,room_id=None):
    conn=await get_connection()
    try:
        start_time=time.fromisoformat(start_time)
        end_time=time.fromisoformat(end_time)
        await conn.execute("""
        update schedules set group_id=$1,weekday=$2,start_time=$3,end_time=$4,room_id=$5
        where id=$6
        """,group_id,weekday,start_time,end_time,room_id,schedule_id)
    except Exception as er:
        print("update schedule error:",er)
    finally:
        await conn.close()

async def deactivate_schedule(schedule_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        update schedules set is_active=false
        where id=$1
        """,schedule_id)
    except Exception as er:
        print("deactivate schedule error:",er)
    finally:
        await conn.close()

async def delete_schedule(schedule_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        delete from schedules
        where id=$1
        """,schedule_id)
    except Exception as er:
        print("delete schedule error:",er)
    finally:
        await conn.close()