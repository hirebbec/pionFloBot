import logging
import matplotlib.pyplot as plt
import io
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

TOKEN: str = "1684742732:AAGZK2_5gx7HcuvgCOgJYFQTeytZu_MalXk"
# TOKEN = str = "8362502167:AAFzOIH8k-nionNZFXw8QIJv07pIEyJSLzo" # Diana

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальные переменные
user_sessions = {}
user_monthly_data = {}
user_daily_stats = {}  # <-- тут будем хранить статистику по дням

keyboard_main = [
    ["Начать смену", "Начать месяц", "Закрыть смену"],
    ["Текущий итог", "Текущий месяц", "Посчитать з/п"],
    ["📉 График заказов", "📊 Средняя цена по дням недели"],
]

keyboard_ratio = [["Ставка 5%", "Ставка 10%"]]


# Команда /start - приветствие и показ кнопок
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_markup = ReplyKeyboardMarkup(keyboard_main, resize_keyboard=True)
    await update.message.reply_text(
        'Привет! Я бот для учета букетов и расчета з/п. Нажми "Начать месяц", а затем "Начать смену".',
        reply_markup=reply_markup,
    )


# Обработка нажатия кнопки "Начать месяц"
async def begin_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    # Обнуляем данные за месяц
    user_monthly_data[user_id] = {
        "shifts_count": 0,
        "shifts_total": 0,
        "bouquets_count": 0,
    }

    await update.message.reply_text(
        "✅ Новый месяц начат! Все предыдущие данные обнулены. Теперь можно начинать смены."
    )


# Обработка нажатия кнопки "Начать смену"
async def begin_shift(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id not in user_monthly_data:
        await update.message.reply_text('Сначала нажмите "Начать месяц"!')
        return

    # Пока не задаем ставку, только инициализируем смену
    user_sessions[user_id] = {"count": 0, "total": 0, "is_active": True, "rate": None}

    # Клавиатура с выбором ставки

    reply_markup = ReplyKeyboardMarkup(keyboard_ratio, resize_keyboard=True)

    await update.message.reply_text(
        "Смена открыта! Теперь выберите ставку для расчета:", reply_markup=reply_markup
    )


async def set_rate_5(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in user_sessions or not user_sessions[user_id]["is_active"]:
        await update.message.reply_text("Сначала начните смену.")
        return
    user_sessions[user_id]["rate"] = 0.05
    reply_markup = ReplyKeyboardMarkup(keyboard_main, resize_keyboard=True)
    await update.message.reply_text(
        "✅ Установлена ставка 5%. Теперь отправляйте суммы букетов.",
        reply_markup=reply_markup,
    )


async def set_rate_10(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in user_sessions or not user_sessions[user_id]["is_active"]:
        await update.message.reply_text("Сначала начните смену.")
        return
    user_sessions[user_id]["rate"] = 0.10
    reply_markup = ReplyKeyboardMarkup(keyboard_main, resize_keyboard=True)
    await update.message.reply_text(
        "✅ Установлена ставка 10%. Теперь отправляйте суммы букетов.",
        reply_markup=reply_markup,
    )


# Обработка нажатия кнопки "Текущий итог" (за смену)
async def current_total(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    session_data = user_sessions.get(user_id)

    if not session_data or not session_data["is_active"]:
        await update.message.reply_text('Смена не активна. Нажмите "Начать смену".')
        return

    count = session_data["count"]
    total = session_data["total"]
    await update.message.reply_text(
        f"На данный момент: {count} букет(а/ов) на сумму {total:,} руб.".replace(
            ",", " "
        )
    )


# Обработка нажатия кнопки "Текущий месяц"
async def current_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    monthly_data = user_monthly_data.get(user_id)

    if not monthly_data:
        await update.message.reply_text('Месяц еще не начат. Нажмите "Начать месяц".')
        return

    shifts_count = monthly_data["shifts_count"]
    shifts_total = monthly_data["shifts_total"]
    bouquets_count = monthly_data["bouquets_count"]

    await update.message.reply_text(
        f"📊 Прогресс за месяц:\n"
        f"Отработано смен: {shifts_count}\n"
        f"Общее количество букетов: {bouquets_count}\n"
        f"Общая сумма: {shifts_total:,} руб.".replace(",", " ")
    )


# Обработка нажатия кнопки "Закрыть смену"
async def end_shift(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    session_data = user_sessions.get(user_id)
    monthly_data = user_monthly_data.get(user_id)

    if not monthly_data:
        await update.message.reply_text('Сначала нажмите "Начать месяц"!')
        return
    if not session_data or not session_data["is_active"]:
        await update.message.reply_text("Смена не активна.")
        return
    if not session_data["rate"]:
        await update.message.reply_text("Сначала выберите ставку (5% или 10%).")
        return

    count = session_data["count"]
    total = session_data["total"]
    rate = session_data["rate"]

    # Сохраняем данные в месячные итоги
    monthly_data["shifts_count"] += 1
    monthly_data["shifts_total"] += total
    monthly_data["bouquets_count"] += count

    # Добавим еще хранение зарплаты за смены
    if "salary_total" not in monthly_data:
        monthly_data["salary_total"] = 0
    salary_for_shift = (total * rate) + 1000
    monthly_data["salary_total"] += salary_for_shift

    session_data["is_active"] = False

    await update.message.reply_text(
        f"✅ Смена закрыта!\n"
        f"За сегодня: {count} букет(а/ов) на сумму {total:,} руб.\n"
        f"Ставка: {int(rate * 100)}%\n"
        f"Зарплата за смену: {salary_for_shift:,.0f} руб.\n"
        f"📌 Расчет: {total:,} × {int(rate * 100)}% + 1000 = {salary_for_shift:,.0f} руб.".replace(
            ",", " "
        )
    )


# Обработка нажатия кнопки "Посчитать з/п"
async def calculate_salary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    monthly_data = user_monthly_data.get(user_id)

    if not monthly_data or monthly_data["shifts_count"] == 0:
        await update.message.reply_text("Нет данных за месяц.")
        return

    shifts_count = monthly_data["shifts_count"]
    bouquets_count = monthly_data["bouquets_count"]
    shifts_total = monthly_data["shifts_total"]
    salary_total = monthly_data.get("salary_total", 0)

    await update.message.reply_text(
        f"💰 Итоги за месяц:\n"
        f"Отработано смен: {shifts_count}\n"
        f"Букетов собрано: {bouquets_count}\n"
        f"Продажи: {shifts_total:,} руб.\n"
        f"-------------------------\n"
        f"Зарплата: {salary_total:,.0f} руб.".replace(",", " ")
    )


# Новый хендлер: показать график заказов по дням
async def plot_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    stats = user_daily_stats.get(user_id)

    if not stats:
        await update.message.reply_text("Пока нет данных для построения графика 📉")
        return

    days = list(stats.keys())
    orders = [stats[day]["count"] for day in days]
    totals = [stats[day]["total"] for day in days]

    # Строим график
    plt.figure(figsize=(6, 4))
    plt.plot(days, orders, marker="o", label="Количество заказов")
    plt.plot(days, totals, marker="s", label="Сумма заказов (руб.)")
    plt.title("Динамика заказов по дням")
    plt.xlabel("День")
    plt.ylabel("Значение")
    plt.legend()
    plt.grid(True)

    # Сохраняем в память
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    await update.message.reply_photo(photo=buf)


# Новый хендлер: показать среднюю цену по дням недели
async def plot_avg_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    import datetime

    user_id = update.effective_user.id
    stats = user_daily_stats.get(user_id)

    if not stats:
        await update.message.reply_text("Нет данных для статистики 📊")
        return

    week_stats = {}
    for day, data in stats.items():
        weekday = datetime.datetime.strptime(day, "%Y-%m-%d").strftime(
            "%A"
        )  # Понедельник, Вторник и т.д.
        if weekday not in week_stats:
            week_stats[weekday] = {"count": 0, "total": 0}
        week_stats[weekday]["count"] += data["count"]
        week_stats[weekday]["total"] += data["total"]

    days = list(week_stats.keys())
    avg_prices = [
        week_stats[d]["total"] / week_stats[d]["count"]
        if week_stats[d]["count"] > 0
        else 0
        for d in days
    ]

    plt.figure(figsize=(6, 4))
    plt.bar(days, avg_prices, color="skyblue")
    plt.title("Средняя цена заказа по дням недели")
    plt.ylabel("Средняя цена (руб.)")
    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    await update.message.reply_photo(photo=buf)


# Обновим обработку букетов, чтобы сохранять статистику по дням
async def handle_bouquet_price(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    import datetime

    user_id = update.effective_user.id
    session_data = user_sessions.get(user_id)

    if not session_data or not session_data["is_active"]:
        return

    try:
        price = int(update.message.text)
        if price <= 0:
            return
    except ValueError:
        return

    session_data["count"] += 1
    session_data["total"] += price

    # Обновляем статистику по дням
    today = datetime.date.today().strftime("%Y-%m-%d")
    if user_id not in user_daily_stats:
        user_daily_stats[user_id] = {}
    if today not in user_daily_stats[user_id]:
        user_daily_stats[user_id][today] = {"count": 0, "total": 0}
    user_daily_stats[user_id][today]["count"] += 1
    user_daily_stats[user_id][today]["total"] += price


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text("Начать месяц"), begin_month))
    application.add_handler(MessageHandler(filters.Text("Начать смену"), begin_shift))
    application.add_handler(MessageHandler(filters.Text("Текущий итог"), current_total))
    application.add_handler(
        MessageHandler(filters.Text("Текущий месяц"), current_month)
    )
    application.add_handler(MessageHandler(filters.Text("Закрыть смену"), end_shift))
    application.add_handler(
        MessageHandler(filters.Text("Посчитать з/п"), calculate_salary)
    )
    application.add_handler(
        MessageHandler(filters.Text("📉 График заказов"), plot_orders)
    )
    application.add_handler(
        MessageHandler(filters.Text("📊 Средняя цена по дням недели"), plot_avg_price)
    )
    application.add_handler(MessageHandler(filters.Text("Ставка 5%"), set_rate_5))
    application.add_handler(MessageHandler(filters.Text("Ставка 10%"), set_rate_10))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bouquet_price)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
