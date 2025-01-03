from aiogram.exceptions import DetailedAiogramError
from aiogram.types import CallbackQuery, ErrorEvent, Message


async def handle_detailed_error(
    event: ErrorEvent, message: Message | None = None, callback: CallbackQuery | None = None
) -> None:
    """Handles DetailedAiogramError exceptions by sending the error message to the user.

    Args:
        event (ErrorEvent): The error event.
        message (Message | None): The message to reply to. Default is None.
        callback (CallbackQuery | None): The callback query to answer. Default is None.

    """
    if not isinstance(event.exception, DetailedAiogramError):
        return

    if callback is not None:
        await callback.answer(event.exception.message)
    elif message is not None:
        await message.answer(event.exception.message)
