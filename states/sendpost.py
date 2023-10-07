from aiogram.dispatcher.filters.state import StatesGroup, State

class sendPost(StatesGroup):
    text = State()
    state = State()
    photo = State()
    video = State()
    document = State()
