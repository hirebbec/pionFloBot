from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from core.config import settings
from core.decorators import with_services
from service.month import MonthService
from service.shift import ShiftService
from service.user import UserService


@with_services("user", "month", "shift")
async def begin_shift(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
    shift_service: ShiftService,
) -> str | None:
    if not await month_service.get_active_month(telegram_id=update.message.chat.id):
        return 'Сначала нажмите "Начать месяц"!'

    if await shift_service.get_active_shift(telegram_id=update.message.chat.id):
        return "Чтобы начать новую смену, необходимо завершить текущую смену."

    reply_markup = ReplyKeyboardMarkup(settings().keyboard_ratio, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите ставку для расчета:", reply_markup=reply_markup
    )


async def _set_ratio(
    update, context, user_service, month_service, shift_service, rate: int
):
    month = await month_service.get_active_month(telegram_id=update.message.chat.id)

    if not month:
        await update.message.reply_text('Сначала нажмите "Начать месяц"!')

    if await shift_service.get_active_shift(telegram_id=update.message.chat.id):
        await update.message.reply_text(
            "Чтобы начать новую смену, необходимо завершить текущую смену."
        )

    await shift_service.begin_shift(
        telegram_id=update.message.chat.id, month_id=month.id, rate=rate
    )

    reply_markup = ReplyKeyboardMarkup(settings().keyboard_main, resize_keyboard=True)

    await update.message.reply_text("Смена открыта!", reply_markup=reply_markup)


@with_services("user", "month", "shift")
async def set_ratio_5(update, context, user_service, month_service, shift_service):
    return await _set_ratio(
        update, context, user_service, month_service, shift_service, rate=5
    )


@with_services("user", "month", "shift")
async def set_ratio_10(update, context, user_service, month_service, shift_service):
    return await _set_ratio(
        update, context, user_service, month_service, shift_service, rate=10
    )
