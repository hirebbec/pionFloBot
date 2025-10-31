from telegram import Update
from telegram.ext import ContextTypes


async def begin_mouth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_service_factory = context.application.bot_data["user_service_factory"]
    user_service = await user_service_factory()

    mouth_service_factory = context.application.bot_data["mouth_service_factory"]
    mouth_service = await mouth_service_factory()

    if not await user_service.get_by_telegram_id(telegram_id=update.message.chat.id):
        await user_service.create_user(telegram_id=update.message.chat.id)

    message = await mouth_service.begin_mouth(telegram_id=update.message.chat.id)

    await update.message.reply_text(message)
