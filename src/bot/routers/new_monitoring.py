from aiogram import Router
from aiogram.exceptions import DetailedAiogramError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.middlewares import ApiProvider
from bot.utils.keyboards import get_marketplaces_keyboard, get_run_intervals_keyboard
from bot.utils.time import get_timedelta_from_callback_data
from bot.utils.validators import (
    validate_callback_data,
    validate_callback_message,
    validate_monitoring_name,
    validate_monitoring_url,
)
from database.schemas import MonitoringCreate

router = Router(name="new_monitoring")


class NewMonitoringState(StatesGroup):
    """New monitoring state group."""

    choose_marketplace = State()
    enter_url = State()
    choose_run_interval = State()
    enter_name = State()


@router.message(Command("new_monitoring"))
async def choose_marketplace(message: Message, api: ApiProvider, state: FSMContext) -> None:
    """Asks user to choose a marketplace for monitoring.

    Args:
        message (Message): Message object.
        api (ApiProvider): Provider for the API.
        state (FSMContext): State context.

    """
    marketplaces_keyboard = await get_marketplaces_keyboard(api, provide_id=True, provide_url=False)
    await message.answer("Choose the marketplace for monitoring:", reply_markup=marketplaces_keyboard)
    await state.set_state(NewMonitoringState.choose_marketplace)


@router.callback_query(NewMonitoringState.choose_marketplace)
async def enter_url(callback: CallbackQuery, state: FSMContext) -> None:
    """Saves the marketplace ID and asks user to enter monitoring URL.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        state (FSMContext): State context.

    """
    message = validate_callback_message(callback)
    marketplace_id = int(validate_callback_data(callback))
    await state.update_data(marketplace_id=marketplace_id)
    await state.set_state(NewMonitoringState.enter_url)
    await message.answer("Enter search URL on the marketplace to monitor")


@router.message(NewMonitoringState.enter_url)
async def choose_run_interval(message: Message, state: FSMContext) -> None:
    """Saves the monitoring URL and asks user to choose monitoring run interval.

    Args:
        message (Message): Message object.
        state (FSMContext): State context.

    """
    url = validate_monitoring_url(message.text)
    await state.update_data(url=url)
    await state.set_state(NewMonitoringState.choose_run_interval)
    await message.answer("Choose monitoring run interval:", reply_markup=get_run_intervals_keyboard())


@router.callback_query(NewMonitoringState.choose_run_interval)
async def enter_name(callback: CallbackQuery, state: FSMContext) -> None:
    """Saves the monitoring run interval and asks user to enter monitoring name.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        state (FSMContext): State context.

    """
    message = validate_callback_message(callback)
    run_interval = get_timedelta_from_callback_data(validate_callback_data(callback))
    await state.update_data(run_interval=run_interval)
    await state.set_state(NewMonitoringState.enter_name)
    await message.answer("Enter monitoring name")


@router.message(NewMonitoringState.enter_name)
async def create_monitoring(message: Message, api: ApiProvider, state: FSMContext) -> None:
    """Creates a new monitoring and sends a response to the user.

    Args:
        message (Message): Message object.
        api (ApiProvider): Provider for the API.
        state (FSMContext): State context.

    """
    data = await state.get_data()
    await state.clear()

    monitoring = MonitoringCreate(
        user_id=message.chat.id,
        marketplace_id=data["marketplace_id"],
        name=validate_monitoring_name(message.text),
        url=data["url"],
        run_interval=data["run_interval"],
    )
    response_status = await api.request("POST", "/monitorings/", json_data=monitoring)

    if response_status == 409:
        raise DetailedAiogramError("Monitoring with this url already exists.")
    if response_status != 200:
        raise DetailedAiogramError("Something went wrong. Please try again later.")

    await message.answer(
        "Monitoring has been created successfully. Monitoring will start soon.\n"
        "Please note that during the first run of monitoring, "
        "you will not receive messages about existing adverts. You will only receive messages about new adverts."
    )
