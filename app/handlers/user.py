import re

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import default_state, State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from services import payment
from database import requests
from keyboards import user_kbs
from services.xui import XUIApi
from lexicon.lexicon import (LEXICON,
                             LEXICON_PERIODS_KB,
                             LEXICON_PAYMENT_METHODS_KB)

router = Router()

class FSMClient(StatesGroup):
    enter_contract = State()
    correct_contract = State()
    extend_subscription = State()
    payment = State()


# Обработчик первой команды /start
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext, session: AsyncSession):
    client = await requests.orm_get_client(session, message.from_user.id)
    if client:
        await message.answer(
            text=LEXICON['//start'],
            reply_markup=user_kbs.create_main_kb()
        )
        await state.set_state(FSMClient.correct_contract)
    else:
        await message.answer(
            text=LEXICON['/start'],
            reply_markup=user_kbs.create_main_kb()
        )
        await state.set_state(FSMClient.enter_contract)

    
# Обработчик последующих команд /start
@router.message(CommandStart(), ~StateFilter(default_state))
async def process_another_start_command(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON['//start'],
        reply_markup=user_kbs.create_main_kb()
    )
    await state.set_state(FSMClient.correct_contract)
    
    
# Обработчик команды /cancel, работающий при указанных состояниях
@router.message(Command('cancel'), StateFilter(
    default_state,
    FSMClient.enter_contract,
    FSMClient.correct_contract
))
async def process_fail_cancel_command(message: Message):
    await message.answer(
        text=LEXICON['nothing_canceled'],
        reply_markup=user_kbs.create_main_kb()
    )


# Обработчик команды /cancel при любых других состояниях
@router.message(Command('cancel'), ~StateFilter(
    default_state,
    FSMClient.enter_contract,
    FSMClient.correct_contract
))
async def process_cancel_command(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON['/cancel'],
        reply_markup=user_kbs.create_main_kb()
    )
    await state.clear()
    await state.set_state(FSMClient.correct_contract)


# Обработчик успешной передачи номера договора
@router.message(FSMClient.enter_contract, F.text)
async def process_contract_sent(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    xui: XUIApi
):
    client = await requests.orm_get_client_by_contract(session, message.text)
    if client and client.subscription == 0:
        await xui.update_client(session, message.text, message.from_user.id)
        await message.answer(
            text=LEXICON['correct_contract_id'],
            reply_markup=user_kbs.create_main_kb()
        )
        await state.set_state(FSMClient.correct_contract)
    else:
        await message.answer(text=LEXICON['contract_not_found'])


# --------------------------------------------------------------------------

    
# Обработчик кнопки оплаты подписки
@router.message(FSMClient.correct_contract, F.text == "🔑 Продлить подписку")
async def process_extend_sub_button(message: Message, session: AsyncSession):
    client = await requests.orm_get_client(session, message.from_user.id)
    await message.answer(
        text=LEXICON['extend_subscription'].format(
            exp_date=client.exp_date.strftime('%d.%m.%Y')
        ),
        reply_markup=user_kbs.create_1row_kb(LEXICON_PERIODS_KB)
    )


# Обработчик кнопки периода
@router.callback_query(FSMClient.correct_contract, F.data.func(lambda d: d in LEXICON_PERIODS_KB))
async def process_period_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON['choose_payment_method'],
        reply_markup=user_kbs.create_1row_kb(LEXICON_PAYMENT_METHODS_KB)
    )
    await state.update_data(
        period=callback.data,
        amount=re.search(r'\d+₽', LEXICON_PERIODS_KB[callback.data]).group()[:-1]
    )
    await state.set_state(FSMClient.extend_subscription)


# Обработчик кнопки метода оплаты
@router.callback_query(FSMClient.extend_subscription, F.data.func(lambda d: d in LEXICON_PAYMENT_METHODS_KB))
async def process_payment_method_button(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    payment_url, payment_id = payment.create_yookassa_payment(data['amount'], callback.message.chat.id)
    await callback.message.edit_text(
        text=LEXICON['pay'],
        reply_markup=user_kbs.create_payment_kb(payment_url, payment_id)
    )
    await state.update_data(payment_id=payment_id)
    await state.set_state(FSMClient.payment)


# Обработчик оплаты
@router.callback_query(FSMClient.payment, F.data)
async def process_payment(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    xui: XUIApi
):
    data = await state.get_data()
    result = payment.check_yookassa_payment(callback.data)
    if result:
        await callback.message.edit_text(text=LEXICON['success'])
        await xui.extend_subscription(session, callback.from_user.id, data['period'])
        await state.clear()
        await state.set_state(FSMClient.correct_contract)
    else:
        await callback.answer(
            text=LEXICON['fail'],
            show_alert=True
        )
#TODO webhook вместо кнопки проверки оплаты
# Сейчас такая проблема, что пользователь может совершить оплату после очистки состояния. Мб решится с помощью Redis, но пока его не хочу юзать

# --------------------------------------------------------------------------


# Обработчик кнопки профиля
@router.message(FSMClient.correct_contract, F.text == "👤 Профиль")
async def process_profile_button(message: Message, session: AsyncSession):
    client = await requests.orm_get_client(session, message.from_user.id)
    await message.answer(text=LEXICON['profile'].format(
        contract_id=client.contract_id,
        sub_status=(LEXICON['inactive'], LEXICON['active'])[client.subscription],
        exp_date=client.exp_date.strftime('%d.%m.%Y')
    ))
  
    
# Обработчик кнопки помощи
@router.message(FSMClient.correct_contract, F.text == "❓ Помощь")
async def process_reply_help_button(message: Message):
    await message.answer(text=LEXICON['help'])
    
    
# Обработчик кнопки about
@router.message(FSMClient.correct_contract, F.text == "🧠 Об HFK")
async def process_about_button(message: Message):
    await message.answer(text=LEXICON['about'])