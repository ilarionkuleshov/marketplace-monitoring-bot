from datetime import timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import ValidationError
from pydantic.networks import AnyHttpUrl

from bot.middlewares import ApiProvider
from bot.utils import get_marketplaces_keyboard
from database.schemas import MonitoringCreate

router = Router(name="new_monitoring")


class NewMonitoringState(StatesGroup):
    """New monitoring state group."""

    choose_marketplace = State()
    enter_url = State()
    choose_run_interval = State()
    enter_name = State()


RUN_INTERVALS = {
    "5min": timedelta(minutes=5),
    "10min": timedelta(minutes=10),
    "15min": timedelta(minutes=15),
    "30min": timedelta(minutes=30),
    "1h": timedelta(hours=1),
    "2h": timedelta(hours=2),
    "3h": timedelta(hours=3),
    "6h": timedelta(hours=6),
    "12h": timedelta(hours=12),
    "24h": timedelta(days=1),
}


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
    if not url:
        await message.answer("URL is required. Please enter a URL.")
        return

    try:
        AnyHttpUrl(url)
    except ValidationError:
        await message.answer("Invalid URL. Please enter a valid URL.")
        return
    if len(url) > 2000:
        await message.answer("URL is too long. Please enter a shorter URL (max 2000 characters).")
        return

    await state.update_data(url=url)

    keyboard_builder = InlineKeyboardBuilder()
    for interval in RUN_INTERVALS:
        keyboard_builder.button(text=interval, callback_data=interval)
    keyboard_builder.adjust(3)

    await message.answer("Choose monitoring interval:", reply_markup=keyboard_builder.as_markup())
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

    await state.update_data(run_interval=RUN_INTERVALS[query.data])
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
    if not name:
        await message.answer("Name is required. Please enter a name.")
        return

    if len(name) > 100:
        await message.answer("Name is too long. Please enter a shorter name (max 100 characters).")
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
