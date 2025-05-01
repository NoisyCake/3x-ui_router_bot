import os
import dotenv

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import default_state, StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from database import requests
from services.xui import XUIApi
from filters.basic import IsAdmin
from lexicon.lexicon import LEXICON_ADMIN
from keyboards.admin_kbs import create_admin_kb, create_confirm_kb

dotenv.load_dotenv()

router = Router()
router.message.filter(IsAdmin(os.getenv('ADMIN_IDS')))

class FSMWorkWithContracts(StatesGroup):
    add_contract = State()
    delete_contract = State()


@router.message(CommandStart())
async def greet_admin(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON_ADMIN['/start'],
        reply_markup=create_admin_kb()
    )
    await state.clear()
    
    
@router.message(Command('cancel'), StateFilter(default_state))
async def process_fail_cancel_command(message: Message):
    await message.answer(
        text=LEXICON_ADMIN['nothing_canceled'],
        reply_markup=create_admin_kb()
    )
        
        
@router.message(Command('cancel'), ~StateFilter(default_state))
async def process_cancel_command(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON_ADMIN['/cancel'],
        reply_markup=create_admin_kb()
    )
    await state.clear()
    
    
# --------------------------------------------------------------------------
    
    
@router.message(F.text == "📜 Добавить договор")
async def process_add_contract_button(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ADMIN['contract_num'])
    await state.set_state(FSMWorkWithContracts.add_contract)


@router.message(StateFilter(FSMWorkWithContracts.add_contract, FSMWorkWithContracts.delete_contract), F.text)
async def add_contract(message: Message, state: FSMContext):
    await state.update_data(contract_num=message.text)
    await message.answer(
        text=LEXICON_ADMIN['confirmation'].format(num=message.text),
        reply_markup=create_confirm_kb()
    )


@router.callback_query(FSMWorkWithContracts.add_contract, F.data == 'confirm')
async def process_confirm_adding(callback: CallbackQuery, state: FSMContext, session: AsyncSession, xui: XUIApi):
    await callback.message.delete()
    try:
        data = await state.get_data()
        await xui.add_client(session, data['contract_num'])
        await callback.message.answer(
            text=LEXICON_ADMIN['contract_added'].format(num=data['contract_num']),
            reply_markup=create_admin_kb()
        )
    except Exception as e:
        await callback.message.answer(
            text=f"{LEXICON_ADMIN['error']}\n\n"
            "Текст ошибки: \"{e}\"",
            reply_markup=create_admin_kb()
        )
    await state.clear()
    
    
@router.callback_query(StateFilter(FSMWorkWithContracts.add_contract, FSMWorkWithContracts.delete_contract), F.data == 'cancel')
async def process_cancel_adding(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text=LEXICON_ADMIN['/cancel'], reply_markup=create_admin_kb())
    await state.clear()
    
    
# --------------------------------------------------------------------------


@router.message(F.text == "❌ Удалить договор", StateFilter(default_state))
async def process_delete_button(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ADMIN['contract_num'])
    await state.set_state(FSMWorkWithContracts.delete_contract)
    
    
@router.callback_query(FSMWorkWithContracts.delete_contract, F.data == 'confirm')
async def delete_client(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    xui: XUIApi
):
    data = await state.get_data()
    client = await requests.orm_get_client_by_contract(session, data['contract_num'])
    if client:
        await xui.delete_client(session, client)
        await callback.message.answer(
            text=LEXICON_ADMIN['deleted'].format(num=data['contract_num']),
            reply_markup=create_admin_kb()
        )
    else:
        await callback.message.answer(
            text=LEXICON_ADMIN['contract_not_found'],
            reply_markup=create_admin_kb()
        )
    await state.clear()
    
#TODO удаление через инлайн-кнопки
# --------------------------------------------------------------------------


@router.message(F.text == "Показать все контракты", StateFilter(default_state))
async def process_show_all_button(message: Message, session: AsyncSession):
    contracts = await requests.orm_get_contracts(session)
    if not contracts:
        await message.answer(text=LEXICON_ADMIN['no_contracts_found'])
    else:
        contracts = '\n'.join(map(lambda contract: f'{str(contract[1] or '—')}: <b>{contract[0]}</b>', contracts))
        await message.answer(text=contracts)