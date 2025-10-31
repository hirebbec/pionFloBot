from core.decorators import with_services
from telegram import Update
from telegram.ext import ContextTypes

from service.month import MonthService
from service.order import OrderService
from service.shift import ShiftService
from service.user import UserService


@with_services("user", "month", "shift", "order")
async def save_order(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
    shift_service: ShiftService,
    order_service: OrderService,
) -> None:
    price = int(update.message.text)
    if price <= 0:
        return

    if not await month_service.get_active_month(telegram_id=update.message.chat.id):
        await update.message.reply_text(text='Сначала нажмите "Начать месяц"!')

    elif not await shift_service.get_active_shift(telegram_id=update.message.chat.id):
        await update.message.reply_text(text='Сначала нажмите "Начать смену"!')

    else:
        shift = await shift_service.get_active_shift(telegram_id=update.message.chat.id)
        await order_service.create_order(
            shift_id=shift.id, amount=int(update.message.text)
        )
