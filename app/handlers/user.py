from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.state import default_state, State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from database import requests
from services.xui import XUIApi
from lexicon.lexicon import LEXICON
from keyboards.user_kbs import create_main_kb, create_period_kb

router = Router()

class FSMEnterContract(StatesGroup):
    enter_contract = State()
    correct_contract = State()
    renew_subscription = State()


# Обработчик первой команды /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext, session: AsyncSession):
    client = await requests.orm_get_client(session, message.from_user.id)
    if client:
        await message.answer(
            text=LEXICON['//start'],
            reply_markup=create_main_kb()
        )
        await state.set_state(FSMEnterContract.correct_contract)
    else:
        await message.answer(
            text=LEXICON['/start'],
            reply_markup=create_main_kb()
        )
        await state.set_state(FSMEnterContract.enter_contract)

    
# Обработчик последующих команд /start
@router.message(CommandStart(), ~StateFilter(default_state))
async def process_another_start_command(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON['//start'],
        reply_markup=create_main_kb()
    )
    await state.set_state(FSMEnterContract.correct_contract)


# Обработчик успешной передачи номера договора
@router.message(FSMEnterContract.enter_contract, F.text)
async def process_contract_sent(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    xui: XUIApi
):
    if await requests.orm_contract_in_db(session, message.text):
        await xui.update_client(session, message.text, message.from_user.id)
        await message.answer(
            text=LEXICON['correct_contract_num'],
            reply_markup=create_main_kb()
        )
        await state.set_state(FSMEnterContract.correct_contract)
    else:
        await message.answer(text=LEXICON['contract_not_found'])


# --------------------------------------------------------------------------

    
# Обработчик кнопки оплаты подписки
@router.message(FSMEnterContract.correct_contract, F.text == "🔑 Продлить подписку")
async def process_renew_sub_button(message: Message):
    await message.answer(
        text=LEXICON['renew_subscription'],
        reply_markup=create_period_kb()
    )
    
    
#TODO Тут обработчики для оплаты наверн


# --------------------------------------------------------------------------


# Обработчик кнопки профиля
@router.message(FSMEnterContract.correct_contract, F.text == "👤 Профиль")
async def process_profile_button(message: Message, session: AsyncSession):
    client = await requests.orm_get_client(session, message.from_user.id)
    await message.answer(text=LEXICON['profile'].format(
        contract_num=client.contract_num,
        sub_status=(LEXICON['inactive'], LEXICON['active'])[client.subscription],
        exp_date=client.exp_date
    ))
  
    
# Обработчик кнопки помощи
@router.message(FSMEnterContract.correct_contract, F.text == "❓ Помощь")
async def process_reply_help_button(message: Message):
    await message.answer(text=LEXICON['help'])
    
    
# Обработчик кнопки about
@router.message(FSMEnterContract.correct_contract, F.text == "🧠 Об HFK")
async def process_about_button(message: Message):
    await message.answer(text=LEXICON['about'])