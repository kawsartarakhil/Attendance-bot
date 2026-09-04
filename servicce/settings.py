from database.connection import get_connection

async def get_setting(key):
    conn=await get_connection()
    try:
        row=await conn.fetchrow("""
        select value from settings where key=$1
        """,key)
        if row is None:
            return None
        return row["value"]
    except Exception as er:
        print("get setting error:",er)
        return None
    finally:
        await conn.close()


async def get_all_settings():
    conn=await get_connection()
    try:
        rows=await conn.fetch("""
        select key,value from settings order by key
        """)
        return rows
    except Exception as er:
        print("get all settings error:",er)
        return []
    finally:
        await conn.close()


async def set_setting(key,value):
    conn=await get_connection()
    try:
        await conn.execute("""
        insert into settings(key,value) values($1,$2)
        on conflict (key) do update set value=$2
        """,key,value)
        return True
    except Exception as er:
        print("set setting error:",er)
        return False
    finally:
        await conn.close()