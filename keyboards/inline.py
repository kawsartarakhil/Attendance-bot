from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def groups_keyboard(groups, is_admin=False):
    buttons = []

    for group in groups:

        if is_admin:
            callback = f"group_{group['id']}"
        else:
            callback = f"teacher_group_{group['id']}"

        buttons.append([
            InlineKeyboardButton(
                text=group["name"],
                callback_data=callback
            )
        ])

    if is_admin:
        buttons.append([
            InlineKeyboardButton(
                text="➕ Create Group",
                callback_data="create_group"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def students_keyboard(students):
    keyboard = []

    for student in students:
        keyboard.append([
            InlineKeyboardButton(
                text=student["full_name"],
                callback_data=f"student_{student['id']}"
            )
        ])

        keyboard.append([
            InlineKeyboardButton(
                text="✏️ Edit",
                callback_data=f"edit_student_{student['id']}"
            ),
            InlineKeyboardButton(
                text="🗑 Delete",
                callback_data=f"delete_student_{student['id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="➕ Create Student",
            callback_data="create_student"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )

def teachers_keyboard(teachers):
    keyboard = []

    for teacher in teachers:
        keyboard.append([
            InlineKeyboardButton(
                text=teacher["full_name"],
                callback_data=f"teacher_{teacher['id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="➕ Create Teacher",
            callback_data="create_teacher"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def courses_keyboard(courses):
    keyboard=[]
    for course in courses:
        keyboard.append([
            InlineKeyboardButton(text=course["name"],callback_data=f"course_{course['id']}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="➕ Create Course",callback_data="create_course")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def course_actions_keyboard(course_id):
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Edit Course",callback_data=f"edit_course_{course_id}"
    )
            ],
            [
                InlineKeyboardButton(text="Delete Course",callback_data=f"delete_course_{course_id}")
            ]
        ]
    )
    return keyboard

def rooms_keyboard(rooms):
    keyboard=[]
    for room in rooms:
        keyboard.append([
            InlineKeyboardButton(
                text=room["name"],
                callback_data=f"room_{room['id']}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(
            text="➕ Create Room",
            callback_data="create_room"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def room_actions_keyboard(room_id):
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Edit Room",
                    callback_data=f"edit_room_{room_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Delete Room",
                    callback_data=f"delete_room_{room_id}"
                )
            ]
        ]
    )
    return keyboard

def schedules_keyboard(schedules):
    keyboard=[]
    for schedule in schedules:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{schedule['weekday']} | {schedule['start_time']} - {schedule['end_time']}",
                callback_data=f"schedule_{schedule['id']}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(
            text="➕ Create Schedule",
            callback_data="create_schedule"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def schedule_actions_keyboard(schedule_id):
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Edit Schedule",
                    callback_data=f"edit_schedule_{schedule_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Delete Schedule",
                    callback_data=f"delete_schedule_{schedule_id}"
                )
            ]
        ]
    )
    return keyboard


def schedule_groups_keyboard(groups):
    keyboard=[]
    for group in groups:
        keyboard.append([
            InlineKeyboardButton(
                text=group["name"],
                callback_data=f"schedule_group_{group['id']}"
            )
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


def check_in_lessons_keyboard(lessons):
    keyboard=[]
    for lesson in lessons:
        keyboard.append([
            InlineKeyboardButton(
                text=f"✅ {lesson['subject']} | {lesson['start_time']}-{lesson['end_time']}",
                callback_data=f"checkin_lesson_{lesson['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def check_out_lessons_keyboard(lessons):
    keyboard=[]
    for lesson in lessons:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🚪 {lesson['subject']} | {lesson['start_time']}-{lesson['end_time']}",
                callback_data=f"checkout_lesson_{lesson['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
def group_courses_keyboard(courses):
    keyboard=[]
    for course in courses:
        keyboard.append([
            InlineKeyboardButton(text=course["name"],callback_data=f"group_course_{course['id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def group_teachers_keyboard(teachers):
    keyboard=[]
    for teacher in teachers:
        keyboard.append([
            InlineKeyboardButton(text=teacher["full_name"],callback_data=f"group_teacher_{teacher['id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)




def edit_group_courses_keyboard(courses):
    keyboard=[]
    for course in courses:
        keyboard.append([
            InlineKeyboardButton(text=course["name"],callback_data=f"edit_group_course_{course['id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def edit_group_teachers_keyboard(teachers):
    keyboard=[]
    for teacher in teachers:
        keyboard.append([
            InlineKeyboardButton(text=teacher["full_name"],callback_data=f"edit_group_teacher_{teacher['id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def group_actions_keyboard(group_id):
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Edit Group",callback_data=f"edit_group_{group_id}"
                )
            ],
            [
                InlineKeyboardButton(text="Delete Group",callback_data=f"delete_group_{group_id}"
                )
            ]
        ]
    )
    return keyboard



def lesson_actions_keyboard(lesson_id):
    keyboard=[
        [
            InlineKeyboardButton(text="Edit",callback_data=f"edit_lesson_{lesson_id}"),
            InlineKeyboardButton(text="Delete",callback_data=f"delete_lesson_{lesson_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def schedule_rooms_keyboard(rooms):
    keyboard=[]
    for room in rooms:
        keyboard.append([
            InlineKeyboardButton(
                text=room["name"],
                callback_data=f"schedule_room_{room['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



def teacher_groups_keyboard(groups,prefix):
    keyboard=[]
    for group in groups:
        keyboard.append([
            InlineKeyboardButton(
                text=group["name"],
                callback_data=f"{prefix}_{group['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def attendance_lessons_keyboard(lessons):
    keyboard=[]
    for lesson in lessons:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{lesson['subject']} | {lesson['lesson_date']}",
                callback_data=f"manual_lesson_{lesson['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



def lesson_groups_keyboard(groups):
    keyboard = []

    for group in groups:
        keyboard.append([
            InlineKeyboardButton(
                text=group["name"],
                callback_data=f"create_lesson_group_{group['id']}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)