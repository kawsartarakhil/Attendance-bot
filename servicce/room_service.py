from database.connection import get_connection

async def create_room(name,capacity):
    conn=await get_connection()
    try:
        await conn.execute("""
        insert into rooms(name,capacity)
        values($1,$2)
        """,name,capacity)
    except Exception as er:
        print("create room error:",er)
    finally:
        await conn.close()

async def get_room_by_id(room_id):
    conn=await get_connection()
    try:
        room=await conn.fetchrow("""
        select * from rooms
        where id=$1
        """,room_id)
        return room
    except Exception as er:
        print("get room by id error:",er)
    finally:
        await conn.close()

async def get_all_rooms():
    conn=await get_connection()
    try:
        rooms=await conn.fetch("""
        select * from rooms
        """)
        return rooms
    except Exception as er:
        print("get all rooms error:",er)
    finally:
        await conn.close()

async def update_room(room_id,name,capacity):
    conn=await get_connection()
    try:
        await conn.execute("""
        update rooms set name=$1,capacity=$2
        where id=$3
        """,name,capacity,room_id)
    except Exception as er:
        print("update room error:",er)
    finally:
        await conn.close()

async def delete_room(room_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        delete from rooms
        where id=$1
        """,room_id)
    except Exception as er:
        print("delete room error:",er)
    finally:
        await conn.close()