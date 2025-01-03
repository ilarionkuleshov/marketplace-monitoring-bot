from typing import Callable

from aiogram.types import CallbackQuery, Message


def get_message_and_answer_method_from_event(event: Message | CallbackQuery) -> tuple[Message, Callable] | None:
    """Returns the message and the answer method from the event.

    Args:
        event (Message | CallbackQuery): Target event.

    Returns:
        tuple[Message, Callable]: The message and the answer method.
        None: If the event is invalid.

    """
    if isinstance(event, Message):
        return event, event.answer

    if not isinstance(event.message, Message):
        return None
    return event.message, event.message.edit_text
