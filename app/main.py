from telegram.ext import Application, CommandHandler, filters, MessageHandler

from core.config import settings
from factories import build_services
from handlers.common import start
from handlers.mouth import begin_mouth
from utils.logging import setup_logging

# async def begin_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     async with SessionLocal() as session:
#         tg_id = update.effective_user.id
#         user = await session.scalar(select(User).where(User.telegram_id == tg_id))
#         if not user:
#             user = User(telegram_id=tg_id)
#             session.add(user)
#             await session.commit()
#         # закрываем предыдущие смены, если остались активные
#         await session.execute(
#             f"UPDATE shifts SET is_active=false WHERE user_id={user.id} AND is_active=true"
#         )
#         # создаем новую смену
#         new_shift = Shift(user_id=user.id)
#         session.add(new_shift)
#         await session.commit()
#     reply_markup = ReplyKeyboardMarkup(keyboard_ratio, resize_keyboard=True)
#     await update.message.reply_text(
#         "Смена начата! Выберите ставку:", reply_markup=reply_markup
#     )
#
#
# async def set_rate(update: Update, context: ContextTypes.DEFAULT_TYPE, rate: float):
#     async with SessionLocal() as session:
#         tg_id = update.effective_user.id
#         user = await session.scalar(select(User).where(User.telegram_id == tg_id))
#         shift = await session.scalar(
#             select(Shift).where(Shift.user_id == user.id, Shift.is_active == True)
#         )
#         if shift:
#             shift.rate = rate
#             await session.commit()
#     reply_markup = ReplyKeyboardMarkup(keyboard_main, resize_keyboard=True)
#     await update.message.reply_text(
#         f"✅ Установлена ставка {int(rate * 100)}%", reply_markup=reply_markup
#     )
#
#
# async def set_rate_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await set_rate(update, context, 0.05)
#
#
# async def set_rate_10(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await set_rate(update, context, 0.10)
#
#
# async def handle_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         price = float(update.message.text)
#     except ValueError:
#         return
#     async with SessionLocal() as session:
#         tg_id = update.effective_user.id
#         user = await session.scalar(select(User).where(User.telegram_id == tg_id))
#         shift = await session.scalar(
#             select(Shift).where(Shift.user_id == user.id, Shift.is_active == True)
#         )
#         if not shift or not shift.rate:
#             return
#         order = Order(shift_id=shift.id, amount=price)
#         shift.count += 1
#         shift.total += price
#         session.add(order)
#         await session.commit()
#
#
# async def end_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     async with SessionLocal() as session:
#         tg_id = update.effective_user.id
#         user = await session.scalar(select(User).where(User.telegram_id == tg_id))
#         shift = await session.scalar(
#             select(Shift).where(Shift.user_id == user.id, Shift.is_active == True)
#         )
#         if not shift:
#             await update.message.reply_text("Смена не найдена.")
#             return
#         salary = (shift.total * shift.rate) + 1000
#         shift.is_active = False
#         shift.end_time = datetime.datetime.now()
#         await session.commit()
#     await update.message.reply_text(
#         f"✅ Смена закрыта.\n"
#         f"Букетов: {shift.count}\n"
#         f"Продажи: {shift.total:.0f} руб.\n"
#         f"Зарплата: {salary:.0f} руб."
#     )
#
#
# async def plot_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     async with SessionLocal() as session:
#         tg_id = update.effective_user.id
#         user = await session.scalar(select(User).where(User.telegram_id == tg_id))
#         result = await session.execute(
#             select(func.date(Order.created_at), func.sum(Order.amount))
#             .join(Shift)
#             .where(Shift.user_id == user.id)
#             .group_by(func.date(Order.created_at))
#         )
#         data = result.all()
#     if not data:
#         await update.message.reply_text("Нет данных для графика.")
#         return
#     days, totals = zip(*data)
#     plt.figure(figsize=(6, 4))
#     plt.plot(days, totals, marker="o")
#     plt.title("Продажи по дням")
#     buf = io.BytesIO()
#     plt.savefig(buf, format="png")
#     buf.seek(0)
#     plt.close()
#     await update.message.reply_photo(photo=buf)
#
#
# async def begin_mouth(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     mouth_service_factory = context.application.bot_data["mouth_service_factory"]
#     mouth_service = await mouth_service_factory()  # создаём сервис с новой сессией
#
#     # вызываем нужный метод
#     await mouth_service.begin_mouth()
#
#     await update.message.reply_text(
#         "✅ Новый месяц начат! Все предыдущие данные обнулены. Теперь можно начинать смены."
#     )

logger = setup_logging()


def main():
    app = Application.builder().token(settings().TOKEN).build()
    app.bot_data.update(build_services())

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text("Начать месяц"), begin_mouth))

    app.run_polling()


if __name__ == "__main__":
    main()
