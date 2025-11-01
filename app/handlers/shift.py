from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from core.config import settings
from core.decorators import with_services
from service.month import MonthService
from service.order import OrderService
from service.shift import ShiftService
from service.user import UserService


@with_services("user", "month", "shift")
async def begin_shift(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
    shift_service: ShiftService,
) -> None:
    if not await month_service.get_active_month(telegram_id=update.message.chat.id):
        await update.message.reply_text(text='Сначала нажмите "Начать месяц"!')
        return

    if await shift_service.get_active_shift(telegram_id=update.message.chat.id):
        await update.message.reply_text(
            text="Чтобы начать новую смену, необходимо завершить текущую смену."
        )
        return

    reply_markup = ReplyKeyboardMarkup(settings().keyboard_ratio, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите ставку для расчета:", reply_markup=reply_markup
    )


@with_services("user", "month", "shift")
async def end_shift(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
    shift_service: ShiftService,
) -> None:
    text = await shift_service.end_shift(telegram_id=update.message.chat.id)

    await update.message.reply_text(text=text)


async def _set_ratio(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
    shift_service: ShiftService,
    rate: int,
):
    month = await month_service.get_active_month(telegram_id=update.message.chat.id)

    if not month:
        await update.message.reply_text('Сначала нажмите "Начать месяц"!')
        return

    if await shift_service.get_active_shift(telegram_id=update.message.chat.id):
        await update.message.reply_text(
            "Чтобы начать новую смену, необходимо завершить текущую смену."
        )
        return

    await shift_service.begin_shift(
        telegram_id=update.message.chat.id, month_id=month.id, rate=rate
    )

    reply_markup = ReplyKeyboardMarkup(settings().keyboard_main, resize_keyboard=True)

    await update.message.reply_text("Смена открыта!", reply_markup=reply_markup)


@with_services("user", "month", "shift")
async def set_ratio_5(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
    shift_service: ShiftService,
):
    return await _set_ratio(
        update, context, user_service, month_service, shift_service, rate=5
    )


@with_services("user", "month", "shift")
async def set_ratio_10(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
    shift_service: ShiftService,
):
    return await _set_ratio(
        update, context, user_service, month_service, shift_service, rate=10
    )


@with_services("user", "month", "shift", "order")
async def get_shift_stat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
    shift_service: ShiftService,
    order_service: OrderService,
) -> None:
    shift = await shift_service.get_active_shift(telegram_id=update.message.chat.id)

    if not shift:
        await update.message.reply_text("Смена не начата!")
        return

    orders_stats = await order_service.get_orders_stat_by_shift_id(shift_id=shift.id)
    await update.message.reply_text(
        f"На данный момент: {orders_stats.count} букет(а/ов) на сумму {orders_stats.total:,} руб."
    )
