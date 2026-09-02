from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def student_menu():
    keyboard=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Check In"),
                KeyboardButton(text="Check Out")
            ],
            [
                KeyboardButton(text="Today's Lesson"),
                KeyboardButton(text="Upcoming Lessons")
            ],
            [
                KeyboardButton(text="My Group"),
                KeyboardButton(text="My Attendance")
            ],
            [
                KeyboardButton(text="Attendance History")
            ],
            [
                KeyboardButton(text="AI Attendance Analysis"),
                KeyboardButton(text="Notifications")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def teacher_menu():
    keyboard=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="My Groups"),
                KeyboardButton(text="Today's Lessons")
            ],
            [
                KeyboardButton(text="Today's Attendance")
            ],
            [
                KeyboardButton(text="Present Students"),
                KeyboardButton(text="Late Students")
            ],
            [
                KeyboardButton(text="Absent Students")
            ],
            [
                KeyboardButton(text="Edit Attendance"),
                KeyboardButton(text="Manual Attendance")
            ],
            [
                KeyboardButton(text="Weekly Report"),
                KeyboardButton(text="Group Statistics")
            ],
            [
                KeyboardButton(text="Students at Risk")
            ],
            [
                KeyboardButton(text="AI Group Analysis"),
                KeyboardButton(text="Notifications")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def admin_menu():
    keyboard=ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Students"),
                KeyboardButton(text="Teachers")
            ],
            [
                KeyboardButton(text="Courses"),
                KeyboardButton(text="Groups")
            ],
            [
                KeyboardButton(text="Rooms")
            ],
            [
                KeyboardButton(text="Schedules"),
                KeyboardButton(text="Lessons")
            ],
            [
                KeyboardButton(text="Attendance")
            ],
            [
                KeyboardButton(text="Attendance Corrections")
            ],
            [
                KeyboardButton(text="Attendance Rules")
            ],
            [
                KeyboardButton(text="Late Rules"),
                KeyboardButton(text="Absence Rules")
            ],
            [
                KeyboardButton(text="Early Leave Rules")
            ],
            [
                KeyboardButton(text="Reports")
            ],
            [
                KeyboardButton(text="Weekly Reports"),
                KeyboardButton(text="Monthly Reports")
            ],
            [
                KeyboardButton(text="Teacher Statistics"),
                KeyboardButton(text="Group Statistics")
            ],
            [
                KeyboardButton(text="Students at Risk"),
                KeyboardButton(text="AI Analytics")
            ],
            [
                KeyboardButton(text="Notifications")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard