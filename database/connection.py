from dotenv import load_dotenv
import asyncpg
import os

load_dotenv()

async def get_connection():
    try:
        user=await asyncpg.connect(
            host="localhost",
            user="postgres",
            database="attendance_bot",
            password=os.getenv("SQL_PASSWORD"),

            port=5432
        )
        return user
    except Exception as er:
        print("Connection error:",er)


async def init_tables():
    conn=await get_connection()
    try:
        await conn.execute("""
    create table if not exists users (
        id serial primary key,
        telegram_id bigint unique not null,
        name varchar(100) not null,
        role varchar(20) not null
            check (role in ('student', 'teacher', 'admin')),
        created_at timestamp default current_timestamp
    );

    create table if not exists students (
        id serial primary key,
        user_id integer unique not null
            references users(id) on delete cascade,
        group_name varchar(100),
        average_grade decimal(5,2) default 0
    );

    create table if not exists teachers (
    id serial primary key,
    user_id integer unique not null
        references users(id) on delete cascade
);

    create table if not exists lessons (
        id serial primary key,
        teacher_id integer not null
            references teachers(id) on delete cascade,
        subject varchar(100) not null,
        lesson_date date not null
    );

    create table if not exists attendance (
        id serial primary key,
        lesson_id integer not null
            references lessons(id) on delete cascade,
        student_id integer not null
            references students(id) on delete cascade,
        status varchar(20) not null
            check (status in ('present', 'absent', 'late')),
        unique (lesson_id, student_id)
    );

    create table if not exists grades (
        id serial primary key,
        student_id integer not null
            references students(id) on delete cascade,
        subject varchar(100) not null,
        grade decimal(5,2) not null
            check (grade >= 0 and grade <= 100),
        created_at timestamp default current_timestamp
    );
    """)

    except Exception as er:
        print("Initailazation error:",er)

    finally:
        await conn.close()