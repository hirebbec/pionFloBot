from telegram import Update
from telegram.ext import ContextTypes


async def begin_mouth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mouth_service_factory = context.application.bot_data["mouth_service_factory"]
    mouth_service = await mouth_service_factory()

    await mouth_service.begin_mouth()

    await update.message.reply_text("✅ Новый месяц начат!")
