from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from lexicon.lexicon import (LEXICON_PAY_KB,
                             LEXICON_CLIENT_KB)


def create_main_kb() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()
    buttons = [
        KeyboardButton(text=LEXICON_CLIENT_KB[i]) 
        for i in range(len(LEXICON_CLIENT_KB))
    ]
    kb_builder.add(buttons[0])
    kb_builder.row(*buttons[1:])
    
    return kb_builder.as_markup(resize_keyboard=True)


def create_1row_kb(LEXICON: dict[str, str]) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text=LEXICON[button], callback_data=button)
        for button in LEXICON
    ]
    kb_builder.row(*buttons, width=1)
    
    return kb_builder.as_markup()


def create_payment_kb(payment_url: str, payment_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=LEXICON_PAY_KB['pay'],
            url=payment_url
        ),
        InlineKeyboardButton(
            text=LEXICON_PAY_KB['check'],
            callback_data=payment_id
        )
    ]])
    return kb