from typing import Callable

from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InaccessibleMessage, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.middlewares import ApiProvider
from bot.utils import get_time_ago, get_timedelta_frequency
from database.schemas import MonitoringDetailsRead, MonitoringRead

router = Router(name="my_monitorings")


class MyMonitoringsListCD(CallbackData, prefix="my_monitorings_list"):
    """Callback data for showing monitorings list."""


class MyMonitoringsDetailsCD(CallbackData, prefix="my_monitorings_details"):
    """Callback data for showing monitoring details."""

    monitoring_id: int


@router.message(Command("my_monitorings"))
@router.callback_query(MyMonitoringsListCD.filter())
async def show_monitorings_list(event: Message | CallbackQuery, api: ApiProvider) -> None:
    """Shows user's monitorings list.

    Args:
        event (Message | CallbackQuery): Event object.
        api (ApiProvider): Provider for the API.

    """
    answer_method: Callable

    if isinstance(event, Message):
        message = event
        answer_method = message.answer
    else:
        if event.message is None or isinstance(event.message, InaccessibleMessage):
            await event.answer("Something went wrong. Please try again later.")
            return
        message = event.message
        answer_method = message.edit_text

    status, monitorings = await api.request(
        "GET",
        "/monitorings/",
        query_params={"user_id": message.chat.id},
        response_model=MonitoringRead,
        response_as_list=True,
    )
    if status != 200 or monitorings is None:
        await message.answer("Something went wrong. Please try again later.")
        return

    if not monitorings:
        await message.answer("You don't have any monitorings yet. Use /new_monitoring to add one.")
        return

    keyboard_builder = InlineKeyboardBuilder()
    for monitoring in monitorings:
        icon = "🟢" if monitoring.enabled else "🔴"
        keyboard_builder.button(
            text=f"{icon} {monitoring.name}", callback_data=MyMonitoringsDetailsCD(monitoring_id=monitoring.id)
        )
    keyboard_builder.adjust(1)

    await answer_method("Here are your monitorings:", reply_markup=keyboard_builder.as_markup())


@router.callback_query(MyMonitoringsDetailsCD.filter())
async def show_monitoring_details(
    query: CallbackQuery, api: ApiProvider, callback_data: MyMonitoringsDetailsCD
) -> None:
    """Shows monitoring details.

    Args:
        query (CallbackQuery): CallbackQuery object.
        api (ApiProvider): Provider for the API.
        callback_data (MyMonitoringsDetailsCD): Callback data.

    """
    if query.message is None or isinstance(query.message, InaccessibleMessage):
        await query.answer("Something went wrong. Please try again later.")
        return

    response_status, monitoring_details = await api.request(
        "GET", f"/monitorings/{callback_data.monitoring_id}/details", response_model=MonitoringDetailsRead
    )
    if response_status != 200 or monitoring_details is None:
        await query.answer("Something went wrong. Please try again later.")
        return

    status = "🟢 *Enabled*" if monitoring_details.enabled else "🔴 *Disabled*"
    last_run = (
        get_time_ago(monitoring_details.last_successful_run) if monitoring_details.last_successful_run else "never"
    )
    text = (
        f"Name: *{monitoring_details.name}*\n"
        f"Status: {status}\n"
        f"URL: [*{monitoring_details.marketplace_name}*]({monitoring_details.url})\n"
        f"Run interval: *{get_timedelta_frequency(monitoring_details.run_interval)}*\n"
        f"Last run: *{last_run}*"
    )

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="<-- Back to monitorings list", callback_data=MyMonitoringsListCD())
    keyboard_builder.adjust(1)

    await query.message.edit_text(
        text, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=keyboard_builder.as_markup()
    )
