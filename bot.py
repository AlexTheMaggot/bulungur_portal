import logging
import kb
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from config import *
import db_methods as dbm


logging.basicConfig(level=logging.INFO)
API_TOKEN = TELEGRAM_BOT_TOKEN
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
conn = sqlite3.connect('db.sqlite3')
curs = conn.cursor()


class Form(StatesGroup):
    language = State()
    name = State()
    contact = State()
    message = State()
    menu_1 = State()
    lang_choose = State()


@dp.message_handler()
async def cmd_start(message: types.Message):
    answer_text = 'Вас приветствует бот обработки жалоб и предложений! Выберите язык чтобы продолжить.\n\n'
    answer_text += 'Shikoyat va takliflarni qayta ishlash botiga xush kelibsiz! Davom etish uchun tilni tanlang.'
    await Form.language.set()
    await message.reply(answer_text, reply_markup=kb.get_lang_kb())


@dp.message_handler(state=Form.language)
async def chosing_language(message, state: FSMContext):
    async with state.proxy() as data:
        user = dbm.get_user_detail(['tg_id', str(message.chat.id)])
        if user:
            data['name'] = user[1]
            data['contact'] = {
                'phone_number': user[3],
                'user_id': user[2]
            }
            data['user_from_db'] = True
            if message.text == "🇷🇺 Русский":
                data['lang'] = 'ru'
                await Form.message.set()
                await message.reply('Расскажите подробно о вашей проблеме')
            elif message.text == "🇺🇿 O'zbekcha":
                data['lang'] = 'uz'
                await Form.message.set()
                await message.reply('Muammoingiz haqida bizga batafsil aytib bering')
            else:
                answer_text = "Пожалуйста укажите язык\n\nIltimos, tilni ko'rsating"
                await message.reply(answer_text, reply_markup=kb.get_lang_kb())
        else:
            data['user_from_db'] = False
            if message.text == "🇷🇺 Русский":
                data['lang'] = 'ru'
                answer_text = 'Как вас зовут?'
                await Form.next()
                await message.reply(answer_text)
            elif message.text == "🇺🇿 O'zbekcha":
                data['lang'] = 'uz'
                answer_text = 'Ismingiz nima?'
                await Form.next()
                await message.reply(answer_text)
            else:
                answer_text = "Пожалуйста укажите язык\n\nIltimos, tilni ko'rsating"
                await message.reply(answer_text, reply_markup=kb.get_lang_kb())


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        await Form.next()
        if data['lang'] == 'ru':
            text = "Пожалуйста поделитесь контактом, чтобы мы смогли связаться с вами."
        else:
            text = "Iltimos, siz bilan bog'lanishimiz uchun kontaktingizni baham ko'ring."
        await message.reply(text, reply_markup=kb.get_contact_kb(data['lang']))


@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.contact)
async def process_contact(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['contact'] = message.contact
        await Form.next()
        if data['lang'] == 'ru':
            await message.reply('Расскажите подробно о вашей проблеме')
        else:
            await message.reply('Muammoingiz haqida bizga batafsil aytib bering')


@dp.message_handler(state=Form.message)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not data['user_from_db']:
            dbm.create_user(data)
            data['user_from_db'] = True
        data['message'] = message.text
        message_text = 'Новая заявка!'
        message_text += '\n\nИмя: ' + data['name']
        message_text += '\nТелефон: ' + data['contact']['phone_number']
        message_text += '\n\nТекст Сообщения: ' + data['message']
        await bot.send_message(-1001978015372, message_text)
        await Form.next()
        if data['lang'] == 'ru':
            text = 'Ваша заявка принята в обработку. Через несколько дней с вами свяжутся. Ожидайте'
            await message.reply(text, reply_markup=kb.get_menu_1_kb('ru'))
        else:
            text = "Sizning arizangiz ko'rib chiqish uchun qabul qilindi. "
            text += "Bir necha kundan keyin siz bilan bog'lanadi. Kutish"
            await message.reply(text, reply_markup=kb.get_menu_1_kb('uz'))


@dp.message_handler(state=Form.menu_1)
async def process_menu_1(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data['lang'] == 'ru':
            if message.text == 'Новая заявка':
                await Form.message.set()
                await message.reply('Расскажите подробно о вашей проблеме')
            elif message.text == 'Сменить язык':
                await Form.lang_choose.set()
                await message.reply('Пожалуйста, укажите язык', reply_markup=kb.get_lang_kb())
            else:
                await message.reply('Пожалуйста, выберите пункт меню', reply_markup=kb.get_menu_1_kb('ru'))
        else:
            if message.text == 'Yangi ilova':
                await Form.message.set()
                await message.reply('Muammoingiz haqida bizga batafsil aytib bering')
            elif message.text == "Tilni o'zgartirish":
                await Form.lang_choose.set()
                await message.reply('Tilni tanlang', reply_markup=kb.get_lang_kb())
            else:
                await message.reply('Menyu bandini tanlang', reply_markup=kb.get_menu_1_kb('uz'))


@dp.message_handler(state=Form.lang_choose)
async def choosing_lang(message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "🇷🇺 Русский":
            data['lang'] = 'ru'
            answer_text = "Язык изменен"
            await Form.menu_1.set()
            await message.reply(answer_text, reply_markup=kb.get_menu_1_kb('ru'))
        elif message.text == "🇺🇿 O'zbekcha":
            data['lang'] = 'uz'
            answer_text = "Til o'zgartirildi"
            await Form.menu_1.set()
            await message.reply(answer_text, reply_markup=kb.get_menu_1_kb('uz'))
        else:
            answer_text = "Пожалуйста укажите язык\n\nIltimos, tilni ko'rsating"
            await message.reply(answer_text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
