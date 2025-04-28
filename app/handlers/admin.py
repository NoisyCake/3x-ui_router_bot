import os
import dotenv

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import default_state, StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from filters.basic import IsAdmin
from lexicon.lexicon import LEXICON_ADMIN
from database import requests
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
async def process_fail_cancel_command(message: Message, state: FSMContext):
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


@router.message(FSMWorkWithContracts.add_contract, F.text)
async def add_contract(message: Message, state: FSMContext):
    await state.update_data(contract_num=message.text)
    await message.answer(
        text=LEXICON_ADMIN['confirmation'].format(num=message.text),
        reply_markup=create_confirm_kb()
    )


@router.callback_query(FSMWorkWithContracts.add_contract, F.data == 'confirm')
async def process_confirm_adding(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.delete()
    try:
        data = await state.get_data()
        await requests.orm_add_contract(session, data['contract_num'])
        await callback.message.answer(
            text=LEXICON_ADMIN['contract_added'].format(num=data['contract_num']),
            reply_markup=create_admin_kb()
        )
    except:
        await callback.message.answer(
            text=LEXICON_ADMIN['error'],
            reply_markup=create_admin_kb()
        )
    await state.clear()
    
    
@router.callback_query(FSMWorkWithContracts.add_contract, F.data == 'cancel')
async def process_cancel_adding(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text=LEXICON_ADMIN['/cancel'], reply_markup=create_admin_kb())
    await state.clear()
    
    
# --------------------------------------------------------------------------


@router.message(F.text == "❌ Удалить договор", StateFilter(default_state))
async def process_delete_button(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_ADMIN['contract_num'])
    await state.set_state(FSMWorkWithContracts.delete_contract)
    
    
@router.message(FSMWorkWithContracts.delete_contract, F.text)
async def delete_contract(message: Message, state: FSMContext, session: AsyncSession):
    success = await requests.orm_delete_contract(session, contract_num=message.text)
    if success:
        await requests.orm_delete_contract(session, message.text)
        await message.answer(
            text=LEXICON_ADMIN['deleted'].format(num=message.text),
            reply_markup=create_admin_kb()
        )
    else:
        await message.answer(
            text=LEXICON_ADMIN['contract_not_found'],
            reply_markup=create_admin_kb()
        )
    await state.clear()
    
    
# --------------------------------------------------------------------------


@router.message(F.text == "Показать все контракты", StateFilter(default_state))
async def process_show_all_button(message: Message, state: FSMContext, session: AsyncSession):
    contracts = await requests.orm_get_contracts(session)
    if not contracts:
        await message.answer(text=LEXICON_ADMIN['no_contracts_found'])
    else:
        contracts = '\n'.join(map(lambda contract: f'{str(contract[1] or '—')}: <b>{contract[0]}</b>', contracts))
        await message.answer(text=contracts)