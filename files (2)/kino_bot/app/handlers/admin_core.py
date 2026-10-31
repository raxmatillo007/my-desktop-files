from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .. import keyboards as kb
from ..utils import IsAdmin, safe_edit

core = Router()
core.message.filter(IsAdmin())
core.callback_query.filter(IsAdmin())

PANEL = "🛠 <b>Admin panel</b>"


@core.message(Command("cancel"))
async def cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("❌ Bekor qilindi.", reply_markup=kb.admin_menu())


@core.message(Command("admin"))
@core.message(F.text == kb.BTN_ADMIN)
async def panel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer(PANEL, reply_markup=kb.admin_menu())


@core.callback_query(F.data == "a:back")
async def back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    await safe_edit(call.message, PANEL, kb.admin_menu())
