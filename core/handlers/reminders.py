from core.my_bot import bot
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from core.keyboards import position


class CreateReminder(StatesGroup):
    photo = State()
    title = State()
    description = State()
    user = State()
    worker = State()


async def create_reminder(message: types.Message):
    await message.reply('Вы начали создание задачи.\nЗагрузите фото.', reply_markup=position.cancel_kb)
    await CreateReminder.photo.set()


async def cancel_reminder(message: types.Message, state: FSMContext):
    if state is None:
        return
    await message.reply('Вы закончили создание задачи.', reply_markup=position.delete_kb)
    await state.finish()


# Проверка на загрузку фотографии
async def check_photo(message: types.Message):
    await message.reply('Это не фотография!')


async def load_photo(message: types.Message, state: FSMContext):
    await message.answer('Введите название задачи', reply_markup=position.cancel_kb)
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await CreateReminder.next()


async def load_title(message: types.Message, state: FSMContext):
    if message.text == '❌Назад':
        await message.answer('Загрузите новое фото')
        await CreateReminder.photo.set()
    else:
        await message.answer('Введите краткое описание задачи')
        async with state.proxy() as data:
            data['title'] = message.text
        await CreateReminder.next()


async def load_description(message: types.Message, state: FSMContext):
    if message.text == '❌Назад':
        await message.answer('Введите новое название задачи')
        await CreateReminder.title.set()
    else:
        await message.answer('Введите как вас зовут')
        async with state.proxy() as data:
            data['description'] = message.text
        await CreateReminder.next()


async def load_user(message: types.Message, state: FSMContext):
    if message.text == '❌Назад':
        await message.answer('Введите новое краткое описание задачи')
        await CreateReminder.description.set()
    else:
        await message.answer('Выберете кому назначается задача', reply_markup=position.position_kb)
        async with state.proxy() as data:
            data['user'] = message.text
        await CreateReminder.next()


async def load_worker(message: types.Message, state: FSMContext):
    if message.text == '❌Назад':
        await message.answer('Введите заново как вас зовут', reply_markup=position.cancel_kb)
        await CreateReminder.user.set()
    else:
        async with state.proxy() as data:
            data['worker'] = message.text
        await message.answer('Задача успешно создана!', reply_markup=position.delete_kb)
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=data['photo'],
                             caption=f"{data['title']}\n"
                                     f"{data['description']}\n\n"
                                     f"От: {data['user']}\n"
                                     f"Кому: {data['worker']}")
        await state.finish()


def register_handler_reminders(dp: Dispatcher):
    dp.register_message_handler(create_reminder, commands=['create'], state=None)
    dp.register_message_handler(cancel_reminder, commands=['cancel'], state='*')  # state='*' учитывать все состояния
    dp.register_message_handler(check_photo, lambda message: not message.photo, state=CreateReminder.photo)
    dp.register_message_handler(load_photo, content_types=['photo'], state=CreateReminder.photo)
    dp.register_message_handler(load_title, state=CreateReminder.title)
    dp.register_message_handler(load_description, state=CreateReminder.description)
    dp.register_message_handler(load_user, state=CreateReminder.user)
    dp.register_message_handler(load_worker, state=CreateReminder.worker)
