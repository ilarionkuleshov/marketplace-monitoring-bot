from typing import Callable

from aiogram.exceptions import DetailedAiogramError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from pydantic import ValidationError
from pydantic.networks import AnyHttpUrl


def validate_callback_message(callback: CallbackQuery) -> Message:
    """Returns validated message from the callback.

    Args:
        callback (CallbackQuery): CallbackQuery object.

    """
    if isinstance(callback.message, Message):
        return callback.message
    raise DetailedAiogramError(_("Something went wrong. Please try again later."))


def validate_callback_data(callback: CallbackQuery) -> str:
    """Returns validated callback data from the callback.

    Args:
        callback (CallbackQuery): CallbackQuery object.

    """
    if callback.data is not None:
        return callback.data
    raise DetailedAiogramError(_("Something went wrong. Please try again later."))


def validate_message_and_answer_method(event: Message | CallbackQuery) -> tuple[Message, Callable]:
    """Returns the message and the answer method from the event.

    Args:
        event (Message | CallbackQuery): Target event.

    """
    if isinstance(event, Message):
        return event, event.answer

    message = validate_callback_message(event)
    return message, message.edit_text


def validate_monitoring_name(name: str | None) -> str:
    """Returns validated monitoring name.

    Args:
        name (str | None): Monitoring name.

    """
    if not name:
        raise DetailedAiogramError(_("Name is required. Please enter a name."))
    if len(name) > 100:
        raise DetailedAiogramError(_("Name is too long. Please enter a shorter name (max 100 characters)."))
    return name


def validate_monitoring_url(url: str | None) -> str:
    """Returns validated monitoring URL.

    Args:
        url (str | None): Monitoring URL.

    """
    if not url:
        raise DetailedAiogramError(_("URL is required. Please enter a URL."))
    try:
        AnyHttpUrl(url)
    except ValidationError:
        raise DetailedAiogramError(_("Invalid URL. Please enter a valid URL."))
    if len(url) > 2000:
        raise DetailedAiogramError(_("URL is too long. Please enter a shorter URL (max 2000 characters)."))
    return url


async def validate_state_context_value[T](state: FSMContext, key: str, expected_type: type[T]) -> T:
    """Returns validated state context value.

    Args:
        state (FSMContext): State context.
        key (str): Key of the value.
        expected_type (type[T]): Expected type of the value.

    """
    value = await state.get_value(key)
    if not isinstance(value, expected_type):
        raise DetailedAiogramError(_("Something went wrong. Please try again later."))
    return value
