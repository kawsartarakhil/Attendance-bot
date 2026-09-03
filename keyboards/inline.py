from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def groups_keyboard(groups):
    keyboard=[]
    for group in groups:
        keyboard.append([
            InlineKeyboardButton(text=group["name"],callback_data=f"group_{group['id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def students_keyboard(students):
    keyboard=[]
    for student in students:
        keyboard.append([
            InlineKeyboardButton( text=student["full_name"], callback_data=f"student_{student['id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def teachers_keyboard(teachers):
    keyboard=[]
    for teacher in teachers:
        keyboard.append([  InlineKeyboardButton(  text=teacher["full_name"],  callback_data=f"teacher_{teacher['id']}" )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def courses_keyboard(courses):
    keyboard=[]
    for course in courses:
        keyboard.append([
            InlineKeyboardButton( text=course["name"], callback_data=f"course_{course['id']}" )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def rooms_keyboard(rooms):
    keyboard=[]
    for room in rooms:
        keyboard.append([
            InlineKeyboardButton( text=room["name"], callback_data=f"room_{room['id']}" )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def schedules_keyboard(schedules):
    keyboard=[]
    for schedule in schedules:
        keyboard.append([
            InlineKeyboardButton( text=f"{schedule['weekday']} | {schedule['start_time']} - {schedule['end_time']}", callback_data=f"schedule_{schedule['id']}" )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def lessons_keyboard(lessons):
    keyboard=[]
    for lesson in lessons:
        keyboard.append([
            InlineKeyboardButton( text=f"{lesson['subject']} | {lesson['lesson_date']}", callback_data=f"lesson_{lesson['id']}" )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def attendance_report_keyboard():
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton( text="Student Attendance", callback_data="attendance_students" )
            ],
            [
                InlineKeyboardButton( text="Group Attendance", callback_data="attendance_groups" )
            ],
            [
                InlineKeyboardButton( text="Teacher Statistics", callback_data="attendance_teachers"  )
            ]
        ]
    )

    return keyboard


def attendance_status_keyboard(attendance_id):
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton( text="Present", callback_data=f"status_present_{attendance_id}"),
                InlineKeyboardButton(text="Late",callback_data=f"status_late_{attendance_id}")
            ],
            [
                InlineKeyboardButton(text="Absent",callback_data=f"status_absent_{attendance_id}"),
                InlineKeyboardButton(text="Excused",callback_data=f"status_excused_{attendance_id}")
            ],
            [
                InlineKeyboardButton(text="Left Early",callback_data=f"status_left_early_{attendance_id}")
            ]
        ]
    )

    return keyboard


def report_filter_keyboard():
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton( text="This Week", callback_data="report_week" ),
                InlineKeyboardButton( text="This Month",callback_data="report_month" )
            ],
            [
                InlineKeyboardButton(text="All",callback_data="report_all" )
            ]
        ]
    )

    return keyboard


def confirmation_keyboard(action):
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton( text="Confirm", callback_data=f"confirm_{action}" ),
                InlineKeyboardButton(text="Cancel",callback_data=f"cancel_{action}" )
            ]
        ]
    )
    return keyboard


def pagination_keyboard(page,total_pages,prefix):
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Previous",callback_data=f"{prefix}_prev_{page}"),
                InlineKeyboardButton(text=f"{page} / {total_pages}",callback_data="current_page"),
                InlineKeyboardButton( text="Next", callback_data=f"{prefix}_next_{page}")
            ]
        ]
    )

    return keyboard


def present_lessons_keyboard(lessons):
    keyboard=[]
    for lesson in lessons:
        keyboard.append([
            InlineKeyboardButton(text=f"{lesson['subject']} | {lesson['lesson_date']}",callback_data=f"present_lesson_{lesson['id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def late_lessons_keyboard(lessons):
    keyboard=[]
    for lesson in lessons:
        keyboard.append([
            InlineKeyboardButton(text=f"{lesson['subject']} | {lesson['lesson_date']}",callback_data=f"late_lesson_{lesson['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def absent_lessons_keyboard(lessons):
    keyboard=[]
    for lesson in lessons:
        keyboard.append([
            InlineKeyboardButton(text=f"{lesson['subject']} | {lesson['lesson_date']}",callback_data=f"absent_lesson_{lesson['id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def attendance_lessons_keyboard(lessons):
    keyboard=[]
    for lesson in lessons:
        keyboard.append([
            InlineKeyboardButton(text=f"{lesson['subject']} | {lesson['lesson_date']}",callback_data=f"manual_lesson_{lesson['id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)