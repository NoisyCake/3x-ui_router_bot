from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_ADMIN_KB, LEXICON_ADMIN_CONFIRM_KB


def create_admin_kb() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()
    buttons = [
        KeyboardButton(text=LEXICON_ADMIN_KB[i]) 
        for i in range(len(LEXICON_ADMIN_KB))
    ]
    kb_builder.add(*buttons[:2])
    kb_builder.row(buttons[2])
    
    return kb_builder.as_markup(resize_keyboard=True)


def create_confirm_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text=LEXICON_ADMIN_CONFIRM_KB[button], callback_data=button)
        for button in LEXICON_ADMIN_CONFIRM_KB
    ]
    kb_builder.row(*buttons)
    
    return kb_builder.as_markup()