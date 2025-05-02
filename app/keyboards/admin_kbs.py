from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from lexicon.lexicon import (LEXICON_ADMIN_KB,
                             LEXICON_CONTRACT_KB,
                             LEXICON_ADMIN_CONFIRM_KB)


def create_admin_kb() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()
    buttons = [
        KeyboardButton(text=LEXICON_ADMIN_KB[i]) 
        for i in range(len(LEXICON_ADMIN_KB))
    ]
    kb_builder.row(*buttons, width=1)
    
    return kb_builder.as_markup(resize_keyboard=True)


def create_confirm_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text=LEXICON_ADMIN_CONFIRM_KB[button], callback_data=button)
        for button in LEXICON_ADMIN_CONFIRM_KB
    ]
    kb_builder.row(*buttons)
    
    return kb_builder.as_markup()


def create_view_pag_kb(
    contracts: list[tuple[str]],
    cur_page: int,
    total_pages: int
) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for contract in contracts:
        contract_id, _ = contract
        kb_builder.row(InlineKeyboardButton(
            text=contract_id,
            callback_data=f'view_contract:{contract_id}'
        ))
    
    nav_buttons = []
    if cur_page > 1:
        nav_buttons.append(InlineKeyboardButton(
            text="◀️",
            callback_data=f'contracts_page:{cur_page-1}'
        ))
    nav_buttons.append(InlineKeyboardButton(
        text=f'{cur_page}/{total_pages}',
        callback_data='_'
    ))
    if cur_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(
            text="▶️",
            callback_data=f'contracts_page:{cur_page+1}'
        ))
        
    if nav_buttons:
        kb_builder.row(*nav_buttons)
        
    return kb_builder.as_markup()


def create_view_contract_kb(contract_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=LEXICON_CONTRACT_KB['delete'],
            callback_data=f'delete_contract:{contract_id}'
        )],
        [InlineKeyboardButton(
            text=LEXICON_CONTRACT_KB['back'],
            callback_data='back'
        )]
    ])
    return kb