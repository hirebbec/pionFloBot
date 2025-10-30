from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from core.config import settings


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(settings().keyboard_main, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я бот учёта смен и заказов 💐", reply_markup=reply_markup
    )
