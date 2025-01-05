from typing import Literal

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as get_i18n_text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold, hlink
from aiogram.utils.markdown import text as join_text

from bot.middlewares import ApiProvider
from bot.utils.keyboards import get_run_intervals_keyboard
from bot.utils.time import (
    get_readable_time_ago,
    get_readable_timedelta,
    get_timedelta_from_callback_data,
)
from bot.utils.validators import (
    validate_callback_data,
    validate_callback_message,
    validate_message_and_answer_method,
    validate_monitoring_name,
    validate_monitoring_url,
    validate_state_context_value,
)
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
    message, answer_method = validate_message_and_answer_method(event)

    monitorings = await api.request(
        "GET",
        "/monitorings/",
        query_params={"user_id": message.chat.id},
        response_model=MonitoringRead,
        response_as_list=True,
    )
    if not monitorings:
        await message.answer(get_i18n_text("You don't have any monitorings yet. Use /new_monitoring to add one."))
        return

    keyboard_builder = InlineKeyboardBuilder()
    for monitoring in monitorings:
        icon = "🟢" if monitoring.enabled else "🔴"
        keyboard_builder.button(
            text=f"{icon} {monitoring.name}", callback_data=MyMonitoringsDetailsCD(monitoring_id=monitoring.id)
        )
    keyboard_builder.adjust(1)

    await answer_method(get_i18n_text("Here are your monitorings:"), reply_markup=keyboard_builder.as_markup())


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
    _message, answer_method = validate_message_and_answer_method(event)
    monitoring_details = await api.request(
        "GET", f"/monitorings/{callback_data.monitoring_id}/details", response_model=MonitoringDetailsRead
    )

    if monitoring_details.enabled:
        status = get_i18n_text("🟢 Enabled")
        change_status_button_text = get_i18n_text("🔴 Disable")
        change_status_button_enabled_value = False
    else:
        status = get_i18n_text("🔴 Disabled")
        change_status_button_text = get_i18n_text("🟢 Enable")
        change_status_button_enabled_value = True

    last_run = (
        get_readable_time_ago(monitoring_details.last_successful_run)
        if monitoring_details.last_successful_run
        else get_i18n_text("Never")
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
        text=get_i18n_text("📝 Edit"), callback_data=MyMonitoringsUpdateCD(monitoring_id=callback_data.monitoring_id)
    )
    keyboard_builder.button(
        text=get_i18n_text("🗑 Delete"), callback_data=MyMonitoringsDeleteCD(monitoring_id=callback_data.monitoring_id)
    )
    keyboard_builder.button(text=get_i18n_text("<-- Back to monitorings list"), callback_data=MyMonitoringsListCD())
    keyboard_builder.adjust(1)

    await answer_method(
        text=join_text(
            f"{get_i18n_text("Monitoring")}: {hbold(monitoring_details.name)}",
            f"{get_i18n_text("Status")}: {hbold(status)}",
            f"{get_i18n_text("URL")}: {hlink(monitoring_details.marketplace_name, monitoring_details.url)}",
            f"{get_i18n_text("Run interval")}: {hbold(get_readable_timedelta(monitoring_details.run_interval))}",
            f"{get_i18n_text("Last run")}: {hbold(last_run)}",
            sep="\n",
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=keyboard_builder.as_markup(),
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
    await api.request(
        "PATCH",
        f"/monitorings/{callback_data.monitoring_id}",
        json_data=MonitoringUpdate(enabled=callback_data.enabled),
    )
    await show_monitoring_details(callback, api, MyMonitoringsDetailsCD(monitoring_id=callback_data.monitoring_id))


@router.callback_query(MyMonitoringsDeleteCD.filter(F.confirmed == False))  # noqa: E712  # pylint: disable=C0121
async def confirm_monitoring_deletion(callback: CallbackQuery, callback_data: MyMonitoringsDeleteCD) -> None:
    """Confirms monitoring deletion.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        callback_data (MyMonitoringsDeleteCD): Callback data.

    """
    message = validate_callback_message(callback)
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=get_i18n_text("Yes"),
        callback_data=MyMonitoringsDeleteCD(monitoring_id=callback_data.monitoring_id, confirmed=True),
    )
    keyboard_builder.button(
        text=get_i18n_text("No"), callback_data=MyMonitoringsDetailsCD(monitoring_id=callback_data.monitoring_id)
    )
    keyboard_builder.adjust(1)
    await message.edit_text(
        get_i18n_text("Are you sure you want to delete this monitoring?"), reply_markup=keyboard_builder.as_markup()
    )


@router.callback_query(MyMonitoringsDeleteCD.filter(F.confirmed == True))  # noqa: E712  # pylint: disable=C0121
async def delete_monitoring(callback: CallbackQuery, api: ApiProvider, callback_data: MyMonitoringsDeleteCD) -> None:
    """Deletes monitoring.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        api (ApiProvider): Provider for the API.
        callback_data (MyMonitoringsDeleteCD): Callback data.

    """
    await api.request("DELETE", f"/monitorings/{callback_data.monitoring_id}")
    await show_monitorings_list(callback, api)


@router.callback_query(MyMonitoringsUpdateCD.filter(F.field == None))  # noqa: E711  # pylint: disable=C0121
async def show_update_fields(callback: CallbackQuery, callback_data: MyMonitoringsUpdateCD) -> None:
    """Shows fields that can be updated.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        callback_data (MyMonitoringsUpdateCD): Callback data.

    """
    message = validate_callback_message(callback)
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=get_i18n_text("Name"),
        callback_data=MyMonitoringsUpdateCD(monitoring_id=callback_data.monitoring_id, field="name"),
    )
    keyboard_builder.button(
        text=get_i18n_text("URL"),
        callback_data=MyMonitoringsUpdateCD(monitoring_id=callback_data.monitoring_id, field="url"),
    )
    keyboard_builder.button(
        text=get_i18n_text("Run interval"),
        callback_data=MyMonitoringsUpdateCD(monitoring_id=callback_data.monitoring_id, field="run_interval"),
    )
    keyboard_builder.button(
        text=get_i18n_text("<-- Back to monitoring"),
        callback_data=MyMonitoringsDetailsCD(monitoring_id=callback_data.monitoring_id),
    )
    keyboard_builder.adjust(1)
    await message.edit_text(
        get_i18n_text("What property do you want to change?"), reply_markup=keyboard_builder.as_markup()
    )


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
    message = validate_callback_message(callback)

    if callback_data.field == "name":
        text = get_i18n_text("Enter new name for the monitoring")
        reply_markup = None
        new_state = MyMonitoringUpdateState.enter_name
    elif callback_data.field == "url":
        text = get_i18n_text("Enter new URL for the monitoring")
        reply_markup = None
        new_state = MyMonitoringUpdateState.enter_url
    else:
        text = get_i18n_text("Choose new run interval for the monitoring:")
        reply_markup = get_run_intervals_keyboard()
        new_state = MyMonitoringUpdateState.choose_run_interval

    await state.update_data(monitoring_id=callback_data.monitoring_id)
    await state.set_state(new_state)
    await message.answer(text, reply_markup=reply_markup)


@router.message(MyMonitoringUpdateState.enter_name)
async def update_monitoring_name(message: Message, api: ApiProvider, state: FSMContext) -> None:
    """Updates monitoring name.

    Args:
        message (Message): Message object.
        api (ApiProvider): Provider for the API.
        state (FSMContext): State context.

    """
    name = validate_monitoring_name(message.text)
    monitoring_id = await validate_state_context_value(state, "monitoring_id", int)
    await state.clear()
    await api.request("PATCH", f"/monitorings/{monitoring_id}", json_data=MonitoringUpdate(name=name))
    await show_monitoring_details(message, api, MyMonitoringsDetailsCD(monitoring_id=monitoring_id))


@router.message(MyMonitoringUpdateState.enter_url)
async def update_monitoring_url(message: Message, api: ApiProvider, state: FSMContext) -> None:
    """Updates monitoring URL.

    Args:
        message (Message): Message object.
        api (ApiProvider): Provider for the API.
        state (FSMContext): State context.

    """
    url = validate_monitoring_url(message.text)
    monitoring_id = await validate_state_context_value(state, "monitoring_id", int)
    await state.clear()
    await api.request("PATCH", f"/monitorings/{monitoring_id}", json_data=MonitoringUpdate(url=url))
    await show_monitoring_details(message, api, MyMonitoringsDetailsCD(monitoring_id=monitoring_id))


@router.callback_query(MyMonitoringUpdateState.choose_run_interval)
async def update_monitoring_run_interval(callback: CallbackQuery, api: ApiProvider, state: FSMContext) -> None:
    """Updates monitoring run interval.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        api (ApiProvider): Provider for the API.
        state (FSMContext): State context.

    """
    run_interval = get_timedelta_from_callback_data(validate_callback_data(callback))
    monitoring_id = await validate_state_context_value(state, "monitoring_id", int)
    await state.clear()
    await api.request("PATCH", f"/monitorings/{monitoring_id}", json_data=MonitoringUpdate(run_interval=run_interval))
    await show_monitoring_details(callback, api, MyMonitoringsDetailsCD(monitoring_id=monitoring_id))
