from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.middlewares import ApiProvider
from bot.utils import (
    get_marketplaces_keyboard,
    get_run_intervals_keyboard,
    get_timedelta_from_callback_data,
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
    if marketplaces_keyboard is None:
        await message.answer("No marketplaces available. Please try again later.")
    else:
        await message.answer("Choose the marketplace for monitoring:", reply_markup=marketplaces_keyboard)
        await state.set_state(NewMonitoringState.choose_marketplace)


@router.callback_query(NewMonitoringState.choose_marketplace)
async def enter_url(query: CallbackQuery, state: FSMContext) -> None:
    """Saves the marketplace ID and asks user to enter monitoring URL.

    Args:
        query (CallbackQuery): CallbackQuery object.
        state (FSMContext): State context.

    """
    if query.data is None or query.message is None:
        await query.answer("Something went wrong. Please try again later.")
        return

    await state.update_data(marketplace_id=int(query.data))
    await query.message.answer("Enter search URL on the marketplace to monitor")
    await state.set_state(NewMonitoringState.enter_url)


@router.message(NewMonitoringState.enter_url)
async def choose_run_interval(message: Message, state: FSMContext) -> None:
    """Saves the monitoring URL and asks user to choose monitoring run interval.

    Args:
        message (Message): Message object.
        state (FSMContext): State context.

    """
    url = message.text
    if error_message := validate_monitoring_url(url):
        await message.answer(error_message)
        return

    await state.update_data(url=url)
    await message.answer("Choose monitoring run interval:", reply_markup=get_run_intervals_keyboard())
    await state.set_state(NewMonitoringState.choose_run_interval)


@router.callback_query(NewMonitoringState.choose_run_interval)
async def enter_name(query: CallbackQuery, state: FSMContext) -> None:
    """Saves the monitoring run interval and asks user to enter monitoring name.

    Args:
        query (CallbackQuery): CallbackQuery object.
        state (FSMContext): State context.

    """
    if query.data is None or query.message is None:
        await query.answer("Something went wrong. Please try again later.")
        return

    await state.update_data(run_interval=get_timedelta_from_callback_data(query.data))
    await query.message.answer("Enter monitoring name")
    await state.set_state(NewMonitoringState.enter_name)


@router.message(NewMonitoringState.enter_name)
async def create_monitoring(message: Message, api: ApiProvider, state: FSMContext) -> None:
    """Creates a new monitoring and sends a response to the user.

    Args:
        message (Message): Message object.
        api (ApiProvider): Provider for the API.
        state (FSMContext): State context.

    """
    name = message.text
    if error_message := validate_monitoring_name(name):
        await message.answer(error_message)
        return

    data = await state.get_data()
    monitoring = MonitoringCreate(
        user_id=message.chat.id,
        marketplace_id=data["marketplace_id"],
        name=name,
        url=data["url"],
        run_interval=data["run_interval"],
    )
    status = await api.request("POST", "/monitorings/", json_data=monitoring)

    if status == 200:
        answer_message = (
            "Monitoring has been created successfully. Monitoring will start soon.\n"
            "Please note that during the first run of monitoring, "
            "you will not receive messages about existing adverts. You will only receive messages about new adverts."
        )
    elif status == 409:
        answer_message = "Monitoring with this url already exists."
    else:
        answer_message = "Something went wrong. Please try again later."

    await message.answer(answer_message)
    await state.clear()
