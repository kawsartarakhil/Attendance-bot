from database.connection import get_connection

async def create_notification(user_id,message,notification_type):
    conn=await get_connection()
    try:
        await conn.execute("""
        insert into notifications(user_id,message,notification_type)
        values($1,$2,$3)
        """,user_id,message,notification_type)
    except Exception as er:
        print("create notification error:",er)
    finally:
        await conn.close()


async def get_user_notifications(user_id):
    conn=await get_connection()
    try:
        notifications=await conn.fetch("""
        select * from notifications
        where user_id=$1
        order by created_at desc
        """,user_id)
        return notifications
    except Exception as er:
        print("get user notifications error:",er)
    finally:
        await conn.close()

async def get_unread_notifications(user_id):
    conn=await get_connection()
    try:
        notifications=await conn.fetch("""
        select * from notifications
        where user_id=$1 and is_read=false
        order by created_at desc
        """,user_id)
        return notifications
    except Exception as er:
        print("get unread notifications error:",er)
    finally:
        await conn.close()


async def mark_notification_read(notification_id):
    conn=await get_connection()
    try:
        await conn.execute("""
        update notifications set is_read=true
        where id=$1
        """,notification_id)
    except Exception as er:
        print("mark notification read error:",er)
    finally:
        await conn.close()