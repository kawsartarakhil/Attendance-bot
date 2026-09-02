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
    conn = await get_connection()

    try:
        await conn.execute("""
        
    create table if not exists users (
        id serial primary key,
        telegram_id bigint unique not null,
        full_name varchar(100) not null,
        username varchar(100),
        phone varchar(30),
        role varchar(20) not null check (role in ('student', 'teacher', 'admin')),
        created_at timestamp default current_timestamp
    );

    create table if not exists students (
        id serial primary key,
        user_id integer unique not null references users(id) on delete cascade
    );

    create table if not exists teachers (
        id serial primary key,
        user_id integer unique not null references users(id) on delete cascade
    );

    create table if not exists courses (
        id serial primary key,
        name varchar(100) unique not null,
        description text,
        created_at timestamp default current_timestamp
    );

    create table if not exists groups (
        id serial primary key,
        name varchar(100) unique not null,
        course_id integer not null references courses(id) on delete cascade,
        teacher_id integer references teachers(id) on delete set null,
        created_at timestamp default current_timestamp
    );

    create table if not exists group_students (
        id serial primary key,
        group_id integer not null references groups(id) on delete cascade,
        student_id integer not null references students(id) on delete cascade,
        joined_at timestamp default current_timestamp,
        unique (group_id, student_id)
    );

    create table if not exists rooms (
        id serial primary key,
        name varchar(100) unique not null,
        capacity integer not null check (capacity > 0),
        created_at timestamp default current_timestamp
    );


    create table if not exists schedules (
        id serial primary key,
        group_id integer not null references groups(id) on delete cascade,
        weekday integer not null check (weekday between 1 and 7),
        start_time time not null,
        end_time time not null,
        room_id integer references rooms(id) on delete set null,
        is_active boolean default true,
        check (end_time > start_time)
    );

    create table if not exists lessons (
        id serial primary key,
        group_id integer not null references groups(id) on delete cascade,
        teacher_id integer not null references teachers(id) on delete cascade,
        room_id integer references rooms(id) on delete set null,
        subject varchar(100) not null,
        lesson_date date not null,
        start_time time not null,
        end_time time not null,
        status varchar(20) not null default 'planned' check (status in ( 'planned', 'started','completed','cancelled' ) ),
        created_at timestamp default current_timestamp,
        check (end_time > start_time)
    );


    create table if not exists attendance_records (
        id serial primary key,
        lesson_id integer not null references lessons(id) on delete cascade,
        student_id integer not null references students(id) on delete cascade,
        check_in_time timestamp,
        check_out_time timestamp,
        late_minutes integer default 0 check (late_minutes >= 0),
        early_leave_minutes integer default 0 check (early_leave_minutes >= 0),
        time_in_class integer default 0 check (time_in_class >= 0),
        status varchar(20) not null default 'absent' check (status in ( 'present','late','absent','excused','left_early')),
        created_at timestamp default current_timestamp,
        unique (lesson_id, student_id)
    );

    create table if not exists attendance_edits (
        id serial primary key,
        attendance_id integer not null references attendance_records(id) on delete cascade,
        edited_by integer not null references users(id) on delete cascade,
        old_status varchar(20) not null,
        new_status varchar(20) not null,
        edit_reason text not null,
        edited_at timestamp default current_timestamp
    );


    create table if not exists notifications (
        id serial primary key,
        user_id integer not null references users(id) on delete cascade,
        message text not null,
        notification_type varchar(30) not null check (notification_type in ('lesson_reminder', 'check_in_reminder', 'attendance_warning', 'weekly_report',  'monthly_report','general'  ) ),
        is_read boolean default false,
        created_at timestamp default current_timestamp
    );

    """)

    except Exception as er:
        print("Initailazation error:", er)

    finally:
        await conn.close()