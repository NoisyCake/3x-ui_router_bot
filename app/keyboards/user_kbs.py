from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_CLIENT_KB, LEXICON_PERIODS_KB


def create_main_kb() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()
    buttons = [
        KeyboardButton(text=LEXICON_CLIENT_KB[i]) 
        for i in range(len(LEXICON_CLIENT_KB))
    ]
    kb_builder.add(buttons[0])
    kb_builder.row(*buttons[1:])
    
    return kb_builder.as_markup(resize_keyboard=True)

def create_period_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text=LEXICON_PERIODS_KB[button], callback_data=button)
        for button in LEXICON_PERIODS_KB
    ]
    kb_builder.row(buttons[:2])
    kb_builder.add(buttons[2])
    
    return kb_builder.as_markup()