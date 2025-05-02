import os
import dotenv

from aiogram import Bot, Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import default_state, StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from services import utils
from database import requests
from services.xui import XUIApi
from keyboards import admin_kbs
from filters.basic import IsAdmin
from lexicon.lexicon import LEXICON, LEXICON_ADMIN


dotenv.load_dotenv()

router = Router()
router.message.filter(IsAdmin(os.getenv('ADMIN_IDS')))

class FSMWorkWithContracts(StatesGroup):
    add_contract = State()
    delete_contract = State()


#TODO сделать поиск по номеру контракта
#TODO фильтрация договоров по истечению подписки и неактивным

@router.message(CommandStart())
async def greet_admin(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON_ADMIN['/start'],
        reply_markup=admin_kbs.create_admin_kb()
    )
    await state.clear()
    
    
@router.message(Command('cancel'), StateFilter(default_state))
async def process_fail_cancel_command(message: Message):
    await message.edit_text(text=LEXICON['nothing_canceled'])
        
        
@router.message(Command('cancel'), ~StateFilter(default_state))
async def process_cancel_command(message: Message, state: FSMContext):
    await message.delete()
    await message.edit_text(text=LEXICON['/cancel'])
    await state.clear()
    
    
# --------------------------------------------------------------------------
    
    
@router.message(F.text == "📜 Добавить договор")
async def process_add_contract_button(message: Message, state: FSMContext):
    contract_id = utils.generate_contract_id()
    await state.update_data(contract_id=contract_id)
    await message.answer(
        text=LEXICON_ADMIN['confirmation'].format(contract_id=contract_id),
        reply_markup=admin_kbs.create_confirm_kb()
    )
    await state.set_state(FSMWorkWithContracts.add_contract)


@router.callback_query(FSMWorkWithContracts.add_contract, F.data == 'confirm')
async def process_confirm_adding(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    xui: XUIApi
):
    await callback.message.delete()
    try:
        data = await state.get_data()
        await xui.add_client(session, data['contract_id'])
        await callback.message.answer(
            text=LEXICON_ADMIN['contract_added'].format(contract_id=data['contract_id']),
            reply_markup=admin_kbs.create_admin_kb()
        )
    except Exception as e:
        await callback.message.answer(
            text=f"{LEXICON_ADMIN['error']}\n\n"
            f"Текст ошибки: \"{e}\"",
            reply_markup=admin_kbs.create_admin_kb()
        )
    await state.clear()
    
    
@router.callback_query(
    StateFilter(
        FSMWorkWithContracts.add_contract,
        FSMWorkWithContracts.delete_contract),
    F.data == 'cancel'
)
async def cancel_deleting(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON['/cancel']
    )
    await state.clear()


# --------------------------------------------------------------------------


@router.message(F.text == "🗂️ Просмотреть контракты", StateFilter(default_state))
async def process_show_all_button(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()

    all_contracts = await requests.orm_get_contracts(session)
    if not all_contracts:
        await message.answer(text=LEXICON_ADMIN['no_contracts_found'])
    else:
        page = 1
        contracts, total_pages = utils.get_paginated_contracts(all_contracts, page)
        
        await state.update_data(all_contracts=all_contracts)
        await message.answer(
            text=LEXICON_ADMIN['view_contracts'],
            reply_markup=admin_kbs.create_view_pag_kb(contracts, page, total_pages)
        )
    
    
@router.callback_query(F.data.startswith("contracts_page:"))
async def paginate_contracts(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split(':')[1])
    await state.update_data(page=page)
    
    all_contracts = (await state.get_data())['all_contracts']
    contracts, total_pages = utils.get_paginated_contracts(all_contracts, page)
    
    await callback.message.edit_text(
        text=LEXICON_ADMIN['view_contracts'],
        reply_markup=admin_kbs.create_view_pag_kb(contracts, page, total_pages)
    )
    
    
@router.callback_query(F.data == '_')
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()
    
    
@router.callback_query(F.data.startswith("view_contract:"))
async def view_contract(callback: CallbackQuery, session: AsyncSession):
    bot = callback.bot
    contract_id = callback.data.split(':')[1]
    client = await requests.orm_get_client_by_contract(session, contract_id)
    try:
        username = (await bot.get_chat(client.tg_id)).username
    except:
        username = '—'
    
    await callback.message.edit_text(
        text=LEXICON_ADMIN['contract_info'].format(
            contract_id=contract_id,
            username=username,
            sub_status=(LEXICON['inactive'], LEXICON['active'])[client.subscription],
            exp_date=client.exp_date.strftime('%d.%m.%Y') if client.exp_date else '—'
        ),
        reply_markup=admin_kbs.create_view_contract_kb(contract_id)
    )
    
    
@router.callback_query(F.data == 'back')
async def go_back(callback: CallbackQuery, state: FSMContext):
    page = int((await state.get_data()).get('page', 1))
    all_contracts = (await state.get_data())['all_contracts']
    contracts, total_pages = utils.get_paginated_contracts(all_contracts, page)
    
    await callback.message.edit_text(
        text=LEXICON_ADMIN['view_contracts'],
        reply_markup=admin_kbs.create_view_pag_kb(contracts, page, total_pages)
    )
    
    
@router.callback_query(F.data.startswith("delete_contract:"))
async def process_delete_button(callback: CallbackQuery, state: FSMContext):
    contract_id = callback.data.split(':')[1]
    await callback.message.edit_text(
        text=LEXICON_ADMIN['delete'].format(contract_id=contract_id),
        reply_markup=admin_kbs.create_confirm_kb()
    )
    await state.set_state(FSMWorkWithContracts.delete_contract)
    await state.update_data(contract_id=contract_id)
    
    
@router.callback_query(FSMWorkWithContracts.delete_contract, F.data == 'confirm')
async def delete_contract(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    xui: XUIApi
):
    contract_id = (await state.get_data())['contract_id']
    client = await requests.orm_get_client_by_contract(session, contract_id)
    if client:
        await xui.delete_client(session, client)
        await callback.message.edit_text(
            text=LEXICON_ADMIN['deleted'].format(contract_id=contract_id)
        )
    else:
        await callback.message.edit_text(
            text=LEXICON_ADMIN['contract_not_found']
        )
    await state.clear()