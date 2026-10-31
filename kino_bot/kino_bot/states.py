"""Finite-state machine definitions for aiogram 3.x handlers."""

from aiogram.fsm.state import State, StatesGroup


class AddMovieStates(StatesGroup):
    """States used while an administrator adds or updates a movie."""

    waiting_for_code = State()
    waiting_for_title = State()
    waiting_for_media = State()


class DeleteMovieStates(StatesGroup):
    """State used while an administrator selects a movie to delete."""

    waiting_for_code = State()


class BroadcastStates(StatesGroup):
    """State used while an administrator prepares a user broadcast."""

    waiting_for_message = State()