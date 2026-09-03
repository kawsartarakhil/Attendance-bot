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


class ManualAttendanceStates(StatesGroup):
    student=State()
    status=State()
    reason=State()
    confirm=State()