from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    full_name=State()

class CreateGroupStates(StatesGroup):
    group_name=State()
    course=State()
    teacher=State()
    room=State()
    confirm=State()


class CreateScheduleStates(StatesGroup):
    group=State()
    weekday=State()
    start_time=State()
    end_time=State()
    room=State()
    confirm=State()


class EditScheduleStates(StatesGroup):
    group=State()
    weekday=State()
    start_time=State()
    end_time=State()
    room=State()
    confirm=State()


class ManualAttendanceStates(StatesGroup):
    student=State()
    status=State()
    reason=State()
    confirm=State()


class CreateCourseStates(StatesGroup):
    name=State()
    description=State()
    confirm=State()

class EditCourseStates(StatesGroup):
    name=State()
    description=State()
    confirm=State()

class DeleteCourseStates(StatesGroup):
    confirm=State()


class EditGroupStates(StatesGroup):
    name=State()
    course=State()
    teacher=State()
    confirm=State()

class DeleteGroupStates(StatesGroup):
    confirm=State()


class CreateRoomStates(StatesGroup):
    name=State()
    capacity=State()
    confirm=State()


class EditRoomStates(StatesGroup):
    name=State()
    capacity=State()
    confirm=State()


class DeleteRoomStates(StatesGroup):
    confirm=State()


class CreateLessonStates(StatesGroup):
    group=State()
    teacher=State()
    room=State()
    subject=State()
    lesson_date=State()
    start_time=State()
    end_time=State()
    confirm=State()