from telegram import Update
from telegram.ext import ContextTypes
import io
import matplotlib.pyplot as plt
from core.decorators import with_services
from service.month import MonthService
from service.order import OrderService
from service.shift import ShiftService
from service.user import UserService
from telegram import InputFile


@with_services("user", "month")
async def begin_month(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
) -> None:
    text = await month_service.begin_month(telegram_id=update.message.chat.id)

    await update.message.reply_text(text=text)


@with_services("user", "month", "shift")
async def end_month(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
    shift_service: ShiftService,
) -> None:
    if not await month_service.get_active_month(telegram_id=update.message.chat.id):
        await update.message.reply_text(text="Месяц еще не начат.")
        return

    if await shift_service.get_active_shift(telegram_id=update.message.chat.id):
        await update.message.reply_text(
            text="Чтобы завершить месяц, необходимо закончить активную смену."
        )
        return

    await month_service.end_month(telegram_id=update.message.chat.id)

    await update.message.reply_text(text="Месяц завершен.")


@with_services("user", "month", "shift", "order")
async def get_month_stat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
    shift_service: ShiftService,
    order_service: OrderService,
) -> None:
    month = await month_service.get_active_month(telegram_id=update.message.chat.id)

    if not month:
        await update.message.reply_text(text="Месяц еще не начат.")
        return

    shifts = await shift_service.get_shift_by_month_id(month_id=month.id)

    orders_stats = [
        (await order_service.get_orders_stat_by_shift_id(shift.id)) for shift in shifts
    ]

    total_orders_sum = sum(order_stat.total for order_stat in orders_stats)
    total_orders_count = sum(order_stat.count for order_stat in orders_stats)

    salary = (
        f"{total_orders_sum:,} + 1000 × {len(shifts)} = {total_orders_sum + (1000 * len(shifts))} руб."
    ).replace(",", " ")

    start_date_str = (
        month.start_time.strftime("%d.%m.%Y")
        if hasattr(month, "start_time")
        else "неизвестно"
    )

    await update.message.reply_text(
        f"📅 Месяц начат: {start_date_str}\n"
        f"📊 Прогресс за месяц:\n"
        f"Отработано смен: {len(shifts)}\n"
        f"Общее количество букетов: {total_orders_count}\n"
        f"Общая сумма: {salary}"
    )


@with_services("user", "month", "shift", "order")
async def plot_month(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService,
    month_service: MonthService,
    shift_service: ShiftService,
    order_service: OrderService,
) -> None:
    month = await month_service.get_active_month(telegram_id=update.message.chat.id)

    if not month:
        await update.message.reply_text("Месяц ещё не начат.")
        return

    shifts = await shift_service.get_shift_by_month_id(month_id=month.id)

    if not shifts:
        await update.message.reply_text("Пока нет смен за этот месяц.")
        return

    shifts.sort(key=lambda s: s.start_time)

    orders_stats = [
        await order_service.get_orders_stat_by_shift_id(shift.id) for shift in shifts
    ]

    shift_labels = [s.start_time.strftime("%d.%m") for s in shifts]
    shift_totals = [stat.total for stat in orders_stats]
    cumulative_sum = [sum(shift_totals[:i]) for i in range(1, len(shift_totals) + 1)]

    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(shift_labels, cumulative_sum, marker="o", color="blue", linewidth=2)
    ax1.set_xlabel("Дата смены")
    ax1.set_ylabel("Накопленная сумма (₽)")
    ax1.set_title("📈 Динамика изменения суммы по сменам")
    ax1.grid(True, linestyle="--", alpha=0.6)

    buf1 = io.BytesIO()
    plt.tight_layout()
    fig1.savefig(buf1, format="png")
    buf1.seek(0)
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    bars = ax2.bar(shift_labels, shift_totals, color="orange")

    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            height + max(shift_totals) * 0.02,
            f"{int(height):,} ₽".replace(",", " "),
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    ax2.set_xlabel("Дата смены")
    ax2.set_ylabel("Сумма заказов (₽)")
    ax2.set_title("💰 Сумма заказов по сменам за месяц")
    ax2.grid(True, axis="y", linestyle="--", alpha=0.6)

    buf2 = io.BytesIO()
    plt.tight_layout()
    fig2.savefig(buf2, format="png")
    buf2.seek(0)
    plt.close(fig2)

    await update.message.reply_photo(
        photo=InputFile(buf1, filename="month_dynamics.png")
    )
    await update.message.reply_photo(photo=InputFile(buf2, filename="month_shifts.png"))
