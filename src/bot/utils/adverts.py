from aiogram import Bot
from aiogram.utils.i18n.core import I18n
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold

from database.schemas import AdvertRead, UserRead
from settings import BotSettings


def format_advert_price(price: float) -> str:
    """Returns formatted price.

    Args:
        price (float): Price to format.

    """
    simplified_price = int(price) if price.is_integer() else price
    return str(simplified_price)


def get_advert_message(advert: AdvertRead) -> str:
    """Returns advert message.

    Args:
        advert (AdvertRead): Advert to create message for.

    """
    paragraphs = [hbold(advert.title)]

    if advert.description:
        paragraphs.append("")
        paragraphs.append(advert.description)

    if advert.price is not None and advert.max_price is not None:
        price_paragraph = f"{format_advert_price(advert.price)} - {format_advert_price(advert.max_price)}"
    elif advert.price is not None:
        price_paragraph = format_advert_price(advert.price)
    elif advert.max_price is not None:
        price_paragraph = format_advert_price(advert.max_price)
    else:
        price_paragraph = None

    if price_paragraph:
        paragraphs.append("")
        if advert.currency:
            price_paragraph += f" {advert.currency}"
        paragraphs.append(hbold(price_paragraph))

    return "\n".join(paragraphs)


async def send_advert_message(advert: AdvertRead, user: UserRead) -> None:
    """Sends advert message to user.

    Args:
        advert (AdvertRead): Advert to send.
        user (UserRead): User to send advert to.

    """
    bot = Bot(BotSettings().token)
    message = get_advert_message(advert)

    i18n = I18n(path="bot/locales")
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text=i18n.gettext("View advert", locale=user.language), url=advert.url)

    if advert.image:
        await bot.send_photo(
            chat_id=user.id,
            photo=advert.image,
            caption=message,
            parse_mode="HTML",
            reply_markup=keyboard_builder.as_markup(),
        )
    else:
        await bot.send_message(
            chat_id=user.id, text=message, parse_mode="HTML", reply_markup=keyboard_builder.as_markup()
        )
