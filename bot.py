import os
import logging
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from counter import increment_counter  # <-- счётчик всех заявок

# === Настройка логирования ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Хранение данных ===
DATA_FILE = "orders.json"

def load_orders() -> dict:
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_orders(data: dict):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        logger.error(f"Ошибка сохранения данных: {e}")

# === Меню ===
def get_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Заказать дизайн / монтаж/ ии-услуги")],
        [KeyboardButton("Портфолио работ")],
        [KeyboardButton("Связаться с менеджером")],
        [KeyboardButton("Сайт(больше о нас)")]
    ], resize_keyboard=True)

def get_services_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Монтаж коротких видео-до/более 1 мин")],
        [KeyboardButton("Монтаж коротких видео-эдит")],
        [KeyboardButton("Монтаж длинных видео-до/более 10 мин")],
        [KeyboardButton("Дизайн-логотипа/аватарки")],
        [KeyboardButton("Полное оформление профиля под ключ")],
        [KeyboardButton("Дизайн-превью")],
        [KeyboardButton("Обработка фото/ретушь")],
        [KeyboardButton("Добавление субтитров")],
        [KeyboardButton("Создание-ИИ асистента gpts")],
        [KeyboardButton("Создание-сайта")],
        [KeyboardButton("Клонирование голоса-озвучка")],
        [KeyboardButton("Создание-ИИ аватара")],
        [KeyboardButton("Создание-ИИ бота")],
        [KeyboardButton("Создание-Telegram бота")],
        [KeyboardButton("Другое")]
    ], resize_keyboard=True)

def get_extra_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Оставить отзыв")],
        [KeyboardButton("Назад в меню")]
    ], resize_keyboard=True)

# === Обработчики команд ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Здравствуйте! Я — бот NeuroLux. Готов помочь с заказом наших бесплатных услуг монтажа, дизайна, или нейросетей.",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        user = update.message.from_user
        user_id = user.id
        username = user.username or user.full_name

        if text == "Заказать дизайн / монтаж/ ии-услуги":
            await update.message.reply_text("Выберите нужную услугу:", reply_markup=get_services_menu())

        elif text in [
            "Монтаж коротких видео-до/более 1 мин", "Монтаж коротких видео-эдит",
            "Монтаж длинных видео-до/более 10 мин", "Дизайн-логотипа/аватарки",
            "Полное оформление профиля под ключ", "Дизайн-превью",
            "Обработка фото/ретушь", "Создание-ИИ асистента gpts",
            "Создание-сайта", "Клонирование голоса-озвучка",
            "Создание-ИИ аватара", "Создание-ИИ бота",
            "Добавление субтитров", "Создание-Telegram бота",
            "Другое",
        ]:
            orders = load_orders()
            user_orders = orders.get(str(user_id), 0)
            user_orders += 1
            orders[str(user_id)] = user_orders
            save_orders(orders)

            total_requests = increment_counter()
            print(f"[DEBUG] total_requests: {total_requests}")

            await update.message.reply_text("✅ Спасибо! В течение 20 минут с вами свяжется наш менеджер по поводу вашего заказа.")
            await context.bot.send_message(
                chat_id=context.bot_data["ADMIN_ID"],
                text=f"🚨 Новая заявка: {text}\n"
                     f"👤 Пользователь: {username}\n"
                     f"🆔 ID: {user_id}\n"
                     f"📦 Всего заказов: {user_orders}\n"
                     f"📊 Всего заявок за сессию: {total_requests}"
            )

        elif text == "Портфолио работ":
            await update.message.reply_text(
                "🎨 Наши работы можно посмотреть здесь:\n"
                "https://t.me/neurolux2025"
            )

        elif text == "Связаться с менеджером":
            await update.message.reply_text("🕒 Ожидайте — с вами свяжется менеджер в ближайшее время, либо можете сами ему написать @iksan0v")
            await context.bot.send_message(
                chat_id=context.bot_data["ADMIN_ID"],
                text=f"📞 Запрос на связь от: {username} (ID: {user_id})"
            )

        elif text == "Сайт(больше о нас)":
            await update.message.reply_text(
                "📝 Мы будем рады вашему отзыву!\n"
                "https://montazh-i-oformlenie-i-jcylmrg.gamma.site/"
            )

        elif text == "Назад в меню":
            await update.message.reply_text("🏠 Вы вернулись в главное меню.", reply_markup=get_main_menu())

        else:
            await update.message.reply_text("ℹ️ Пожалуйста, выберите действие из меню ниже.", reply_markup=get_main_menu())

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.")

# === Запуск приложения ===
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = os.getenv("ADMIN_ID")

    if not TOKEN or not ADMIN_ID:
        logger.error("Не заданы переменные окружения BOT_TOKEN или ADMIN_ID")
        exit(1)

    try:
        ADMIN_ID = int(ADMIN_ID)
    except ValueError:
        logger.error("ADMIN_ID должен быть числом")
        exit(1)

    application = Application.builder().token(TOKEN).build()
    application.bot_data["ADMIN_ID"] = ADMIN_ID
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Бот запущен")
    application.run_polling()

if __name__ == "__main__":
    main()
