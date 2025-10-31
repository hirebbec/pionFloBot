from telegram import Update
from telegram.ext import ContextTypes

from core.decorators import with_services
from service.month import MonthService
from service.user import UserService


@with_services("user", "month")
async def begin_month(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
) -> None:
    text = await month_service.begin_month(telegram_id=update.message.chat.id)

    await update.message.reply_text(text=text)


@with_services("user", "month")
async def end_month(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
) -> None:
    text = await month_service.end_month(telegram_id=update.message.chat.id)

    await update.message.reply_text(text=text)
