from typing import Literal

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.middlewares import ApiProvider
from bot.utils.api import update_monitoring
from bot.utils.events import get_message_and_answer_method_from_event
from bot.utils.keyboards import get_run_intervals_keyboard
from bot.utils.time import (
    get_readable_time_ago,
    get_readable_timedelta,
    get_timedelta_from_callback_data,
)
from bot.utils.validators import validate_monitoring_name, validate_monitoring_url
from database.schemas import MonitoringDetailsRead, MonitoringRead, MonitoringUpdate

router = Router(name="my_monitorings")


class MyMonitoringsListCD(CallbackData, prefix="my_monitorings_list"):
    """Callback data for showing monitorings list."""


class MyMonitoringsDetailsCD(CallbackData, prefix="my_monitorings_details"):
    """Callback data for showing monitoring details."""

    monitoring_id: int


class MyMonitoringsUpdateEnabledCD(CallbackData, prefix="my_monitorings_update_enabled"):
    """Callback data for updating monitoring enabled."""

    monitoring_id: int
    enabled: bool


class MyMonitoringsDeleteCD(CallbackData, prefix="my_monitorings_delete"):
    """Callback data for deleting monitoring."""

    monitoring_id: int
    confirmed: bool = False


class MyMonitoringsUpdateCD(CallbackData, prefix="my_monitorings_update"):
    """Callback data for updating monitoring."""

    monitoring_id: int
    field: Literal["name", "url", "run_interval"] | None = None


class MyMonitoringUpdateState(StatesGroup):
    """State group for updating monitoring."""

    enter_url = State()
    choose_run_interval = State()
    enter_name = State()


@router.message(Command("my_monitorings"))
@router.callback_query(MyMonitoringsListCD.filter())
async def show_monitorings_list(event: Message | CallbackQuery, api: ApiProvider) -> None:
    """Shows user's monitorings list.

    Args:
        event (Message | CallbackQuery): Event object.
        api (ApiProvider): Provider for the API.

    """
    message_and_answer_method = get_message_and_answer_method_from_event(event)
    if message_and_answer_method is None:
        await event.answer("Something went wrong. Please try again later.")
        return
    message, answer_method = message_and_answer_method

    response_status, monitorings = await api.request(
        "GET",
        "/monitorings/",
        query_params={"user_id": message.chat.id},
        response_model=MonitoringRead,
        response_as_list=True,
    )
    if response_status != 200 or monitorings is None:
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
    event: Message | CallbackQuery, api: ApiProvider, callback_data: MyMonitoringsDetailsCD
) -> None:
    """Shows monitoring details.

    Args:
        event (Message | CallbackQuery): Event object.
        api (ApiProvider): Provider for the API.
        callback_data (MyMonitoringsDetailsCD): Callback data.

    """
    message_and_answer_method = get_message_and_answer_method_from_event(event)
    if message_and_answer_method is None:
        await event.answer("Something went wrong. Please try again later.")
        return
    message, answer_method = message_and_answer_method

    response_status, monitoring_details = await api.request(
        "GET", f"/monitorings/{callback_data.monitoring_id}/details", response_model=MonitoringDetailsRead
    )
    if response_status != 200 or monitoring_details is None:
        await message.answer("Something went wrong. Please try again later.")
        return

    if monitoring_details.enabled:
        status = "🟢 *Enabled*"
        change_status_button_text = "🔴 Disable"
        change_status_button_enabled_value = False
    else:
        status = "🔴 *Disabled*"
        change_status_button_text = "🟢 Enable"
        change_status_button_enabled_value = True

    last_run = (
        get_readable_time_ago(monitoring_details.last_successful_run)
        if monitoring_details.last_successful_run
        else "never"
    )
    text = (
        f"Name: *{monitoring_details.name}*\n"
        f"Status: {status}\n"
        f"URL: [*{monitoring_details.marketplace_name}*]({monitoring_details.url})\n"
        f"Run interval: *every {get_readable_timedelta(monitoring_details.run_interval)}*\n"
        f"Last run: *{last_run}*"
    )

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=change_status_button_text,
        callback_data=MyMonitoringsUpdateEnabledCD(
            monitoring_id=callback_data.monitoring_id,
            enabled=change_status_button_enabled_value,
        ),
    )
    keyboard_builder.button(
        text="📝 Edit", callback_data=MyMonitoringsUpdateCD(monitoring_id=callback_data.monitoring_id)
    )
    keyboard_builder.button(
        text="🗑 Delete", callback_data=MyMonitoringsDeleteCD(monitoring_id=callback_data.monitoring_id)
    )
    keyboard_builder.button(text="<-- Back to monitorings list", callback_data=MyMonitoringsListCD())
    keyboard_builder.adjust(1)

    await answer_method(
        text, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=keyboard_builder.as_markup()
    )


@router.callback_query(MyMonitoringsUpdateEnabledCD.filter())
async def update_monitoring_enabled(
    callback: CallbackQuery, api: ApiProvider, callback_data: MyMonitoringsUpdateEnabledCD
) -> None:
    """Updates monitoring enabled.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        api (ApiProvider): Provider for the API.
        callback_data (MyMonitoringsUpdateEnabledCD): Callback data.

    """
    status = await update_monitoring(api, callback_data.monitoring_id, MonitoringUpdate(enabled=callback_data.enabled))
    if status is False:
        await callback.answer("Something went wrong. Please try again later.")
        return
    await show_monitoring_details(callback, api, MyMonitoringsDetailsCD(monitoring_id=callback_data.monitoring_id))


@router.callback_query(MyMonitoringsDeleteCD.filter(F.confirmed == False))  # noqa: E712  # pylint: disable=C0121
async def confirm_monitoring_deletion(callback: CallbackQuery, callback_data: MyMonitoringsDeleteCD) -> None:
    """Confirms monitoring deletion.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        callback_data (MyMonitoringsDeleteCD): Callback data.

    """
    if not isinstance(callback.message, Message):
        await callback.answer("Something went wrong. Please try again later.")
        return

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="Yes", callback_data=MyMonitoringsDeleteCD(monitoring_id=callback_data.monitoring_id, confirmed=True)
    )
    keyboard_builder.button(text="No", callback_data=MyMonitoringsDetailsCD(monitoring_id=callback_data.monitoring_id))
    keyboard_builder.adjust(1)
    await callback.message.edit_text(
        "Are you sure you want to delete this monitoring?", reply_markup=keyboard_builder.as_markup()
    )


@router.callback_query(MyMonitoringsDeleteCD.filter(F.confirmed == True))  # noqa: E712  # pylint: disable=C0121
async def delete_monitoring(callback: CallbackQuery, api: ApiProvider, callback_data: MyMonitoringsDeleteCD) -> None:
    """Deletes monitoring.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        api (ApiProvider): Provider for the API.
        callback_data (MyMonitoringsDeleteCD): Callback data.

    """
    response_status = await api.request("DELETE", f"/monitorings/{callback_data.monitoring_id}")
    if response_status != 200:
        await callback.answer("Something went wrong. Please try again later.")
        return
    await show_monitorings_list(callback, api)


@router.callback_query(MyMonitoringsUpdateCD.filter(F.field == None))  # noqa: E711  # pylint: disable=C0121
async def show_update_fields(callback: CallbackQuery, callback_data: MyMonitoringsUpdateCD) -> None:
    """Shows fields that can be updated.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        callback_data (MyMonitoringsUpdateCD): Callback data.

    """
    if not isinstance(callback.message, Message):
        await callback.answer("Something went wrong. Please try again later.")
        return

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="Name", callback_data=MyMonitoringsUpdateCD(monitoring_id=callback_data.monitoring_id, field="name")
    )
    keyboard_builder.button(
        text="URL", callback_data=MyMonitoringsUpdateCD(monitoring_id=callback_data.monitoring_id, field="url")
    )
    keyboard_builder.button(
        text="Run interval",
        callback_data=MyMonitoringsUpdateCD(monitoring_id=callback_data.monitoring_id, field="run_interval"),
    )
    keyboard_builder.button(
        text="<-- Back to monitoring", callback_data=MyMonitoringsDetailsCD(monitoring_id=callback_data.monitoring_id)
    )
    keyboard_builder.adjust(1)
    await callback.message.edit_text("What field do you want to update?", reply_markup=keyboard_builder.as_markup())


@router.callback_query(MyMonitoringsUpdateCD.filter(F.field != None))  # noqa: E711  # pylint: disable=C0121
async def enter_new_field_value(
    callback: CallbackQuery, callback_data: MyMonitoringsUpdateCD, state: FSMContext
) -> None:
    """Enters new field value.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        callback_data (MyMonitoringsUpdateCD): Callback data.
        state (FSMContext): State context.

    """
    if not isinstance(callback.message, Message):
        await callback.answer("Something went wrong. Please try again later.")
        return

    if callback_data.field == "name":
        text = "Enter new name for the monitoring"
        reply_markup = None
        new_state = MyMonitoringUpdateState.enter_name
    elif callback_data.field == "url":
        text = "Enter new URL for the monitoring"
        reply_markup = None
        new_state = MyMonitoringUpdateState.enter_url
    else:
        text = "Choose new run interval for the monitoring:"
        reply_markup = get_run_intervals_keyboard()
        new_state = MyMonitoringUpdateState.choose_run_interval

    await callback.message.answer(text, reply_markup=reply_markup)
    await state.update_data(monitoring_id=callback_data.monitoring_id)
    await state.set_state(new_state)


@router.message(MyMonitoringUpdateState.enter_name)
async def update_monitoring_name(message: Message, api: ApiProvider, state: FSMContext) -> None:
    """Updates monitoring name.

    Args:
        message (Message): Message object.
        api (ApiProvider): Provider for the API.
        state (FSMContext): State context.

    """
    name = message.text
    if error_message := validate_monitoring_name(name):
        await message.answer(error_message)
        return

    monitoring_id = await state.get_value("monitoring_id")
    if not isinstance(monitoring_id, int):
        await message.answer("Something went wrong. Please try again later.")
        return

    status = await update_monitoring(api, monitoring_id, MonitoringUpdate(name=name))
    if status is False:
        await message.answer("Something went wrong. Please try again later.")
        return
    await state.clear()

    await show_monitoring_details(message, api, MyMonitoringsDetailsCD(monitoring_id=monitoring_id))


@router.message(MyMonitoringUpdateState.enter_url)
async def update_monitoring_url(message: Message, api: ApiProvider, state: FSMContext) -> None:
    """Updates monitoring URL.

    Args:
        message (Message): Message object.
        api (ApiProvider): Provider for the API.
        state (FSMContext): State context.

    """
    url = message.text
    if error_message := validate_monitoring_url(url):
        await message.answer(error_message)
        return

    monitoring_id = await state.get_value("monitoring_id")
    if not isinstance(monitoring_id, int):
        await message.answer("Something went wrong. Please try again later.")
        return

    status = await update_monitoring(api, monitoring_id, MonitoringUpdate(url=url))
    if status is False:
        await message.answer("Something went wrong. Please try again later.")
        return
    await state.clear()

    await show_monitoring_details(message, api, MyMonitoringsDetailsCD(monitoring_id=monitoring_id))


@router.callback_query(MyMonitoringUpdateState.choose_run_interval)
async def update_monitoring_run_interval(callback: CallbackQuery, api: ApiProvider, state: FSMContext) -> None:
    """Updates monitoring run interval.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        api (ApiProvider): Provider for the API.
        state (FSMContext): State context.

    """
    monitoring_id = await state.get_value("monitoring_id")
    if not isinstance(monitoring_id, int) or callback.data is None:
        await callback.answer("Something went wrong. Please try again later.")
        return

    run_interval = get_timedelta_from_callback_data(callback.data)
    status = await update_monitoring(api, monitoring_id, MonitoringUpdate(run_interval=run_interval))
    if status is False:
        await callback.answer("Something went wrong. Please try again later.")
        return
    await state.clear()

    await show_monitoring_details(callback, api, MyMonitoringsDetailsCD(monitoring_id=monitoring_id))
