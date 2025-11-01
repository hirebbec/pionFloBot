from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from core.config import settings
from core.decorators import with_services
from service.month import MonthService
from service.order import OrderService
from service.shift import ShiftService
from service.user import UserService
import matplotlib.pyplot as plt
import io
from telegram import InputFile


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

    start_time_str = shift.start_time.strftime("%d.%m.%Y %H:%M")

    salary = f"{orders_stats.total:,} × {shift.rate}% + 1000 = {orders_stats.total * (shift.rate / 100) + 1000:,.2f} руб."

    await update.message.reply_text(
        f"📅 Смена начата: {start_time_str}\n"
        f"💸 Ставка: {shift.rate}%\n"
        f"🧾 Заказы: {orders_stats.count} шт. на сумму {orders_stats.total:,} руб.\n\n"
        f"💰 Зарплата: {salary}\n"
    )


@with_services("user", "month", "shift", "order")
async def plot_shift(
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

    orders = await order_service.get_orders_by_shift_id(shift_id=shift.id)

    if not orders:
        await update.message.reply_text("Заказов пока нет.")
        return

    orders.sort(key=lambda o: o.created_at)

    times = [o.created_at.strftime("%H:%M") for o in orders]  # только часы и минуты
    totals = [o.amount for o in orders]
    cumulative_sum = [sum(totals[:i]) for i in range(1, len(totals) + 1)]

    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(times, cumulative_sum, label="Сумма заказов (₽)", marker="o", color="blue")
    ax1.set_xlabel("Время (ч:м)")
    ax1.set_ylabel("Накопленная сумма (₽)")
    ax1.set_title("📈 Динамика роста суммы заказов")
    ax1.legend()
    ax1.grid(True)

    buf1 = io.BytesIO()
    plt.tight_layout()
    fig1.savefig(buf1, format="png")
    buf1.seek(0)
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    bars = ax2.bar(range(1, len(totals) + 1), totals, color="orange")

    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            height + max(totals) * 0.02,
            f"{int(height):,}".replace(",", " "),
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    ax2.set_xlabel("№ заказа")
    ax2.set_ylabel("Сумма заказа (₽)")
    ax2.set_title("💰 Стоимость заказов по порядку")
    ax2.grid(True, axis="y", linestyle="--", alpha=0.6)

    buf2 = io.BytesIO()
    plt.tight_layout()
    fig2.savefig(buf2, format="png")
    buf2.seek(0)
    plt.close(fig2)

    await update.message.reply_photo(photo=InputFile(buf1, filename="shift_growth.png"))
    await update.message.reply_photo(photo=InputFile(buf2, filename="shift_orders.png"))
