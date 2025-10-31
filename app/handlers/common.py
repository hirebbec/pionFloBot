from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from core.config import settings
from core.decorators import with_services
from service.user import UserService


@with_services("user")
async def start(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_service: UserService
) -> None:
    reply_markup = ReplyKeyboardMarkup(settings().keyboard_main, resize_keyboard=True)

    await update.message.reply_text(
        text="Привет! Я бот учёта смен и заказов 💐", reply_markup=reply_markup
    )
