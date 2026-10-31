"""Administrator commands and callbacks for aiogram 3.x."""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse

from aiogram import Bot, F, Router
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from database import Database
from keyboards import admin_keyboard
from states import AddMovieStates, BroadcastStates, DeleteMovieStates


router = Router(name="admin")


def _is_valid_http_url(value: str) -> bool:
    """Check that a value is an HTTP(S) URL with a host name."""
    parsed = urlparse(value.strip())
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


@router.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def open_admin_menu(message: Message) -> None:
    """Show the administrator menu to the configured administrator only."""
    await message.answer(
        "Admin panel:",
        reply_markup=admin_keyboard(),
    )


@router.message(Command("cancel"), F.from_user.id == ADMIN_ID)
async def cancel_admin_action(message: Message, state: FSMContext) -> None:
    """Cancel the current administrator flow and clear its FSM state."""
    await state.clear()
    await message.answer("Amal bekor qilindi.")


@router.callback_query(
    F.data == "admin:stats",
    F.from_user.id == ADMIN_ID,
)
async def show_statistics(
    callback: CallbackQuery,
    db: Database,
) -> None:
    """Display current user and movie totals from SQLite."""
    await callback.answer()
    user_count = await db.get_user_count()
    movie_count = await db.get_movie_count()

    if isinstance(callback.message, Message):
        await callback.message.answer(
            "📊 Statistika\n"
            f"👥 Jami foydalanuvchilar: {user_count}\n"
            f"🎬 Jami kinolar: {movie_count}"
        )


@router.callback_query(
    F.data == "admin:add_movie",
    F.from_user.id == ADMIN_ID,
)
async def begin_add_movie(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Start the add-movie FSM."""
    await state.clear()
    await state.set_state(AddMovieStates.waiting_for_code)
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer("Kino kodini yuboring:")


@router.message(
    AddMovieStates.waiting_for_code,
    F.from_user.id == ADMIN_ID,
    F.text,
)
async def receive_movie_code(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    """Validate a new movie code before asking for its title."""
    code = (message.text or "").strip()
    if not code:
        await message.answer("Kino kodi bo'sh bo'lmasin. Qayta yuboring:")
        return

    if await db.movie_exists(code):
        await message.answer(
            "Bu kod allaqachon mavjud. Boshqa kino kodini yuboring:"
        )
        return

    await state.update_data(movie_code=code)
    await state.set_state(AddMovieStates.waiting_for_title)
    await message.answer("Kino nomini yuboring:")


@router.message(
    AddMovieStates.waiting_for_code,
    F.from_user.id == ADMIN_ID,
)
async def require_movie_code_text(message: Message) -> None:
    """Ask for a text code when a non-text message is sent in the code step."""
    await message.answer("Kino kodini matn ko'rinishida yuboring:")


@router.message(
    AddMovieStates.waiting_for_title,
    F.from_user.id == ADMIN_ID,
    F.text,
)
async def receive_movie_title(
    message: Message,
    state: FSMContext,
) -> None:
    """Save the title in FSM data and ask for a video or URL."""
    title = (message.text or "").strip()
    if not title:
        await message.answer("Kino nomi bo'sh bo'lmasin. Qayta yuboring:")
        return

    await state.update_data(movie_title=title)
    await state.set_state(AddMovieStates.waiting_for_media)
    await message.answer(
        "Kino videosini yuboring yoki http:// / https:// bilan boshlanadigan "
        "havolani yuboring:"
    )


@router.message(
    AddMovieStates.waiting_for_title,
    F.from_user.id == ADMIN_ID,
)
async def require_movie_title_text(message: Message) -> None:
    """Ask for a text title when a non-text message is sent in the title step."""
    await message.answer("Kino nomini matn ko'rinishida yuboring:")


async def _save_movie(
    message: Message,
    state: FSMContext,
    db: Database,
    media_value: str,
) -> None:
    """Persist the collected movie information and finish the add flow."""
    data = await state.get_data()
    code = str(data.get("movie_code", "")).strip()
    title = str(data.get("movie_title", "")).strip()

    if not code or not title:
        await state.clear()
        await message.answer(
            "Kino ma'lumotlari topilmadi. Iltimos, kino qo'shishni boshidan boshlang."
        )
        return

    await db.add_movie(
        code=code,
        title=title,
        file_id_or_link=media_value,
    )
    await state.clear()
    await message.answer(
        f"✅ Kino saqlandi.\nKod: {code}\nNomi: {title}"
    )


@router.message(
    AddMovieStates.waiting_for_media,
    F.from_user.id == ADMIN_ID,
    F.video,
)
async def receive_movie_video(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    """Save a Telegram video using its file_id."""
    if message.video is None:
        await message.answer("Video topilmadi. Qayta yuboring:")
        return

    await _save_movie(
        message=message,
        state=state,
        db=db,
        media_value=message.video.file_id,
    )


@router.message(
    AddMovieStates.waiting_for_media,
    F.from_user.id == ADMIN_ID,
    F.text,
)
async def receive_movie_url(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    """Validate and save an HTTP(S) movie URL."""
    media_value = (message.text or "").strip()
    if not _is_valid_http_url(media_value):
        await message.answer(
            "Havola http:// yoki https:// bilan boshlanishi va manzilga ega "
            "bo'lishi kerak. Yoki video yuboring:"
        )
        return

    await _save_movie(
        message=message,
        state=state,
        db=db,
        media_value=media_value,
    )


@router.message(
    AddMovieStates.waiting_for_media,
    F.from_user.id == ADMIN_ID,
)
async def require_movie_media(message: Message) -> None:
    """Ask for a video or HTTP(S) link when another message type is sent."""
    await message.answer(
        "Video yuboring yoki http:// / https:// bilan boshlanadigan "
        "havolani yuboring:"
    )


@router.callback_query(
    F.data == "admin:delete_movie",
    F.from_user.id == ADMIN_ID,
)
async def begin_delete_movie(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Start the delete-movie FSM."""
    await state.clear()
    await state.set_state(DeleteMovieStates.waiting_for_code)
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer("O'chiriladigan kino kodini yuboring:")


@router.message(
    DeleteMovieStates.waiting_for_code,
    F.from_user.id == ADMIN_ID,
    F.text,
)
async def delete_movie_by_code(
    message: Message,
    state: FSMContext,
    db: Database,
) -> None:
    """Delete a movie by its code and report whether it existed."""
    code = (message.text or "").strip()
    if not code:
        await message.answer("Kino kodini yuboring:")
        return

    deleted = await db.delete_movie(code)
    await state.clear()
    if deleted:
        await message.answer(f"🗑 Kino o'chirildi. Kod: {code}")
    else:
        await message.answer("❌ Bunday kodli kino topilmadi.")


@router.message(
    DeleteMovieStates.waiting_for_code,
    F.from_user.id == ADMIN_ID,
)
async def require_delete_code_text(message: Message) -> None:
    """Ask for a text code when a non-text message is sent in the delete step."""
    await message.answer("Kino kodini matn ko'rinishida yuboring:")


@router.callback_query(
    F.data == "admin:broadcast",
    F.from_user.id == ADMIN_ID,
)
async def begin_broadcast(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Start the broadcast message FSM."""
    await state.clear()
    await state.set_state(BroadcastStates.waiting_for_message)
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer(
            "Foydalanuvchilarga yuboriladigan xabarni yuboring:"
        )


@router.message(
    BroadcastStates.waiting_for_message,
    F.from_user.id == ADMIN_ID,
)
async def broadcast_message(
    message: Message,
    state: FSMContext,
    bot: Bot,
    db: Database,
) -> None:
    """Copy an administrator's Telegram message to every registered user."""
    await state.clear()
    user_ids = await db.get_all_users()
    total_count = len(user_ids)
    sent_count = 0
    failed_count = 0

    for user_id in user_ids:
        try:
            while True:
                try:
                    await bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id,
                    )
                    sent_count += 1
                    break
                except TelegramRetryAfter as exc:
                    await asyncio.sleep(exc.retry_after)
        except (TelegramForbiddenError, TelegramBadRequest):
            failed_count += 1
        finally:
            await asyncio.sleep(0.05)

    await message.answer(
        "📢 Xabar yuborish yakunlandi.\n"
        f"👥 Jami: {total_count}\n"
        f"✅ Yuborildi: {sent_count}\n"
        f"❌ Yuborilmadi: {failed_count}"
    )


@router.callback_query(
    F.data == "admin:close",
    F.from_user.id == ADMIN_ID,
)
async def close_admin_menu(callback: CallbackQuery) -> None:
    """Close the admin menu by removing its inline keyboard."""
    await callback.answer("Admin panel yopildi.")
    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data.startswith("admin:"))
async def reject_unauthorized_admin_callback(callback: CallbackQuery) -> None:
    """Answer admin callbacks from non-admin users without performing actions."""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "Bu tugma faqat administrator uchun.",
            show_alert=True,
        )
        return

    await callback.answer(
        "Noma'lum admin tugmasi.",
        show_alert=True,
    )