from telegram import Update
from telegram.ext import ContextTypes


async def begin_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_service_factory = context.application.bot_data["user_service_factory"]
    user_service = await user_service_factory()

    month_service_factory = context.application.bot_data["month_service_factory"]
    month_service = await month_service_factory()

    if not await user_service.get_by_telegram_id(telegram_id=update.message.chat.id):
        await user_service.create_user(telegram_id=update.message.chat.id)

    message = await month_service.begin_month(telegram_id=update.message.chat.id)

    await update.message.reply_text(message)


async def end_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_service_factory = context.application.bot_data["user_service_factory"]
    user_service = await user_service_factory()

    month_service_factory = context.application.bot_data["month_service_factory"]
    month_service = await month_service_factory()

    if not await user_service.get_by_telegram_id(telegram_id=update.message.chat.id):
        await user_service.create_user(telegram_id=update.message.chat.id)

    message = await month_service.end_month(telegram_id=update.message.chat.id)

    await update.message.reply_text(message)
