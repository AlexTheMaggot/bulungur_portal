from aiogram import types


def get_lang_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("🇷🇺 Русский", "🇺🇿 O'zbekcha")
    return kb


def get_contact_kb(lang: str):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if lang == 'ru':
        kb.add(types.KeyboardButton(text='Поделиться контактом', request_contact=True))
    else:
        kb.add(types.KeyboardButton(text="Kontaktni baham ko'ring", request_contact=True))
    return kb


def get_menu_1_kb(lang: str):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if lang == 'ru':
        kb.add('Новая заявка', 'Сменить язык')
    else:
        kb.add('Yangi ilova', "Tilni o'zgartirish")
    return kb
