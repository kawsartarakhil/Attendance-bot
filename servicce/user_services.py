from database.connection import get_connection

async def register(tg_id,name):
    conn=await get_connection()
    try:
        user=await conn.fetchrow("""
        select * from users
        where telegram_id =$1
        """,tg_id)
        if user:
            return user
        user=await user.execute("""
        insert into users(telegram_id,name,role)
        values($1,$2,'student')
        """,tg_id,name)

        await conn.execute("""
        insert into students(user_id)
        values($1)
        """,user["id"])
        return user
    except Exception as er:
        print("Registration error:",er)

    finally:
        await conn.close()

async def get_user_tg_id(tg_id):
    conn=await get_connection()
    try:
        user= await conn.fetchrow("""
        select * from users
        where telegram_id=$1
        """,tg_id)
        return user
    except Exception as er:
        print("Get user by tg_id error:",er)

    finally:
        await conn.close()

async def get_user_id(id):
    conn=await get_connection()
    try:
        user= await conn.fetchrow("""
        select * from users
        where id=$1
        """,id)
        return user
    except Exception as er:
        print("Get user by id error:",er)

    finally:
        await conn.close()


async def get_users():
    conn=await get_connection()
    try:
        user= await conn.fetchrow("""
        select * from users
        order by id
        """,)
        return user
    except Exception as er:
        print("Get users error:",er)

    finally:
        await conn.close()

async def change_role(user_id,role):
    conn=await get_connection()
    try:
        user= await conn.fetchrow("""
        update users set role=$1
        where id=$2
        """,role,user_id)
        return user
    except Exception as er:
        print("changer role error:",er)

    finally:
        await conn.close()