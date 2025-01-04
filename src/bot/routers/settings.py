from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.middlewares import ApiProvider
from bot.utils.validators import (
    validate_callback_message,
    validate_message_and_answer_method,
)
from database.enums import UserLanguage
from database.schemas import UserRead, UserUpdate

router = Router(name="settings")


class SettingsListCD(CallbackData, prefix="settings_list"):
    """Callback data for the settings list."""


class SettingsChooseLanguageCD(CallbackData, prefix="settings_choose_language"):
    """Callback data for choosing the language."""


class SettingsUpdateLanguageCD(CallbackData, prefix="settings_update_language"):
    """Callback data for updating the language."""

    language: UserLanguage


@router.message(Command("settings"))
@router.callback_query(SettingsListCD.filter())
async def show_settings(event: Message | CallbackQuery, user: UserRead) -> None:
    """Shows the settings.

    Args:
        event (Message | CallbackQuery): Event object.
        user (UserRead): Current user.

    """
    _message, answer_method = validate_message_and_answer_method(event)

    if user.language == UserLanguage.EN:
        current_language = _("English", locale=user.language)
    elif user.language == UserLanguage.RU:
        current_language = _("Russian", locale=user.language)
    else:
        current_language = _("Ukrainian", locale=user.language)

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=_("Language (current: {current_language})", locale=user.language).format(
            current_language=current_language
        ),
        callback_data=SettingsChooseLanguageCD(),
    )
    keyboard_builder.adjust(1)
    await answer_method(_("Here are the settings:", locale=user.language), reply_markup=keyboard_builder.as_markup())


@router.callback_query(SettingsChooseLanguageCD.filter())
async def choose_language(callback: CallbackQuery) -> None:
    """Asks user to choose the language.

    Args:
        callback (CallbackQuery): CallbackQuery object.

    """
    message = validate_callback_message(callback)
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text=f"{_("English", locale=UserLanguage.EN)} ({_("English")})",
        callback_data=SettingsUpdateLanguageCD(language=UserLanguage.EN),
    )
    keyboard_builder.button(
        text=f"{_("Russian", locale=UserLanguage.RU)} ({_("Russian")})",
        callback_data=SettingsUpdateLanguageCD(language=UserLanguage.RU),
    )
    keyboard_builder.button(
        text=f"{_("Ukrainian", locale=UserLanguage.UK)} ({_("Ukrainian")})",
        callback_data=SettingsUpdateLanguageCD(language=UserLanguage.UK),
    )
    keyboard_builder.button(text=_("<-- Back to settings"), callback_data=SettingsListCD())
    keyboard_builder.adjust(1)
    await message.edit_text(_("Choose new language:"), reply_markup=keyboard_builder.as_markup())


@router.callback_query(SettingsUpdateLanguageCD.filter())
async def update_language(
    callback: CallbackQuery, callback_data: SettingsUpdateLanguageCD, api: ApiProvider, user: UserRead
) -> None:
    """Updates the language.

    Args:
        callback (CallbackQuery): CallbackQuery object.
        callback_data (SettingsUpdateLanguageCD): Callback data.
        api (ApiProvider): Provider for the API.
        user (UserRead): Current user.

    """
    user = await api.request(
        "PATCH", f"/users/{user.id}", json_data=UserUpdate(language=callback_data.language), response_model=UserRead
    )
    await show_settings(callback, user)
