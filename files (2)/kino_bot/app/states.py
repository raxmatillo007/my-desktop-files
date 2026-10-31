from aiogram.fsm.state import State, StatesGroup


class AddMovie(StatesGroup):
    file = State()
    title = State()
    desc = State()
    category = State()


class AddEpisode(StatesGroup):
    files = State()


class Manage(StatesGroup):
    code = State()


class EditField(StatesGroup):
    value = State()


class DelEpisode(StatesGroup):
    number = State()


class AddCategory(StatesGroup):
    name = State()


class AddChannel(StatesGroup):
    chat = State()


class Broadcast(StatesGroup):
    msg = State()
    confirm = State()


class UserAction(StatesGroup):
    target = State()


class SetWelcome(StatesGroup):
    text = State()


class AddAdmin(StatesGroup):
    uid = State()
