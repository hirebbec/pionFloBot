from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from core.config import settings


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_service_factory = context.application.bot_data["user_service_factory"]
    user_service = await user_service_factory()

    if not await user_service.get_by_telegram_id(telegram_id=update.message.chat.id):
        await user_service.create_user(telegram_id=update.message.chat.id)

    reply_markup = ReplyKeyboardMarkup(settings().keyboard_main, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я бот учёта смен и заказов 💐", reply_markup=reply_markup
    )
