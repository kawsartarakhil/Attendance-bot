from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from keyboards.reply import student_menu, teacher_menu, admin_menu
from servicce.user_services import get_user_tg_id, register
from states import RegistrationStates

router=Router()

@router.message(CommandStart())
async def start_handler(message: types.Message,state: FSMContext):
    await state.clear()
    user=await get_user_tg_id(message.from_user.id)
    if user is None:
        await state.set_state(RegistrationStates.full_name)
        await message.answer("Welcome To our AI student attendance analytics bot\n\nPlease enter your full name:")
        return
    if user["role"]=="student":
        await message.answer(f"Welcome {user['full_name']}",reply_markup=student_menu())
    elif user["role"]=="teacher":
        await message.answer(f"Welcome Teacher {user['full_name']}",reply_markup=teacher_menu())
    elif user["role"]=="admin":
        await message.answer(f"Welcome Admin {user['full_name']}",reply_markup=admin_menu())

@router.message(RegistrationStates.full_name)
async def register_full_name(message: types.Message,state: FSMContext):
    full_name=message.text
    await register(message.from_user.id,full_name)
    await state.clear()
    await message.answer(f"Registration successful\n\nWelcome {full_name}\n\nTo know about all of our commands and buttons click on /help",reply_markup=student_menu() )

@router.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer("""
/start - Register the user if not already registered and start the program.

/help - Show all available commands and buttons.

/cancel - Cancel whatever multi-step action you're in the middle of.
""")


@router.message(Command("cancel"))
async def cancel_handler(message: types.Message,state: FSMContext):
    current_state=await state.get_state()
    if current_state is None:
        await message.answer("There is nothing to cancel.")
        return
    await state.clear()
    await message.answer("Cancelled. Use /start to see your menu again.")