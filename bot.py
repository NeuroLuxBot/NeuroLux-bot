import os
import logging
import json

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from counter import increment_counter  # счётчик всех заявок

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
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_orders(data: dict):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        logger.error(f"Ошибка сохранения данных: {e}")


# === Главное меню (клавиатура снизу) ===
def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("Заказать монтаж")],
            [KeyboardButton("Заказать ИИ контент")],
            [KeyboardButton("Связаться с менеджером")],
            [KeyboardButton("Портфолио работ")],
            [KeyboardButton("Сайт(больше о нас)")],
        ],
        resize_keyboard=True
    )


# === Inline-меню: Монтаж (кнопки под сообщением) ===
def get_montage_inline_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Видео для TikTok / Instagram", callback_data="M_TT")],
            [InlineKeyboardButton("Видео для YouTube", callback_data="M_YT")],
            [InlineKeyboardButton("Рекламный ролик", callback_data="M_AD")],
            [InlineKeyboardButton("Другое (монтаж)", callback_data="M_OTHER")],
            [InlineKeyboardButton("⬅️ Назад в меню", callback_data="BACK_MAIN")],
        ]
    )


# === Inline-меню: ИИ (кнопки под сообщением) ===
def get_ai_inline_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Обработка фото/ретушь", callback_data="A_PHOTO")],
            [InlineKeyboardButton("Добавление субтитров", callback_data="A_SUBS")],
            [InlineKeyboardButton("Создание ИИ ассистента GPTs", callback_data="A_GPTS")],
            [InlineKeyboardButton("Создание сайта", callback_data="A_SITE")],
            [InlineKeyboardButton("Клонирование голоса / озвучка", callback_data="A_VOICE")],
            [InlineKeyboardButton("Создание ИИ аватара", callback_data="A_AVATAR")],
            [InlineKeyboardButton("Создание ИИ бота", callback_data="A_AI_BOT")],
            [InlineKeyboardButton("Создание Telegram бота", callback_data="A_TG_BOT")],
            [InlineKeyboardButton("Другое (ИИ)", callback_data="A_OTHER")],
            [InlineKeyboardButton("⬅️ Назад в меню", callback_data="BACK_MAIN")],
        ]
    )


# === Запись заявки + уведомление админу ===
async def register_order_and_notify(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    service_title: str,
):
    user = None
    user_id = None
    username = None

    if update.callback_query:
        user = update.callback_query.from_user
    elif update.message:
        user = update.message.from_user

    if not user:
        return

    user_id = user.id
    username = user.username or user.full_name

    orders = load_orders()
    user_orders = orders.get(str(user_id), 0) + 1
    orders[str(user_id)] = user_orders
    save_orders(orders)

    total_requests = increment_counter()
    logger.info(f"New order: {service_title} | user={user_id} total_requests={total_requests}")

    # Сообщение пользователю
    if update.callback_query:
        await update.callback_query.message.reply_text(
            "✅ Спасибо! В течение 20 минут с вами свяжется наш менеджер."
        )
    else:
        await update.message.reply_text(
            "✅ Спасибо! В течение 20 минут с вами свяжется наш менеджер."
        )

    # Сообщение админу
    admin_id = context.bot_data.get("ADMIN_ID")
    if admin_id:
        await context.bot.send_message(
            chat_id=admin_id,
            text=(
                f"🚨 Новая заявка: {service_title}\n"
                f"👤 Пользователь: {username}\n"
                f"🆔 ID: {user_id}\n"
                f"📦 Всего заказов (у пользователя): {user_orders}\n"
                f"📊 Всего заявок (счётчик): {total_requests}"
            )
        )


# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Ты попал в NeuroLux — сервис, где ты получишь:\n"
        "🔥 Бесплатный монтаж или нейро-контент.\n"
        "⏱️ Заявка займёт не больше 30 секунд.\n"
        "👉 Выбери, что тебе нужно:",
        reply_markup=get_main_menu_keyboard()
    )


# === Текстовые сообщения (клавиатура) ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    if text == "Заказать монтаж":
        await update.message.reply_text(
            "🎬 Отлично, выбери тип монтажа:",
            reply_markup=get_montage_inline_menu()
        )
        return

    if text == "Заказать ИИ контент":
        await update.message.reply_text(
            "🤖 Отлично, выбери тип ИИ услуг:",
            reply_markup=get_ai_inline_menu()
        )
        return

    if text == "Портфолио работ":
        await update.message.reply_text(
            "🎨 Наши работы можно посмотреть здесь:\nhttps://t.me/neurolux2025",
            reply_markup=get_main_menu_keyboard()
        )
        return

    if text == "Связаться с менеджером":
        await update.message.reply_text(
            "🕒 Ожидайте — с вами свяжется менеджер в ближайшее время, "
            "либо можете сами ему написать: @iksan0v",
            reply_markup=get_main_menu_keyboard()
        )
        admin_id = context.bot_data.get("ADMIN_ID")
        user = update.message.from_user
        username = user.username or user.full_name
        if admin_id:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📞 Запрос на связь от: {username} (ID: {user.id})"
            )
        return

    if text == "Сайт(больше о нас)":
        await update.message.reply_text(
            "📝 Сайт (больше о нас):\nhttps://montazh-i-oformlenie-i-jcylmrg.gamma.site/",
            reply_markup=get_main_menu_keyboard()
        )
        return

    await update.message.reply_text(
        "ℹ️ Выбери действие из меню ниже.",
        reply_markup=get_main_menu_keyboard()
    )


# === Inline callbacks ===
SERVICE_MAP = {
    # Монтаж
    "M_TT": "Видео для TikTok / Instagram",
    "M_YT": "Видео для YouTube",
    "M_AD": "Рекламный ролик",
    "M_OTHER": "Другое (монтаж)",
    # ИИ
    "A_PHOTO": "Обработка фото/ретушь",
    "A_SUBS": "Добавление субтитров",
    "A_GPTS": "Создание ИИ ассистента GPTs",
    "A_SITE": "Создание сайта",
    "A_VOICE": "Клонирование голоса / озвучка",
    "A_AVATAR": "Создание ИИ аватара",
    "A_AI_BOT": "Создание ИИ бота",
    "A_TG_BOT": "Создание Telegram бота",
    "A_OTHER": "Другое (ИИ)",
}


async def handle_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    await query.answer()

    if data == "BACK_MAIN":
        # Можно “снять” inline-меню, чтобы не висело
        try:
            await query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

        await query.message.reply_text(
            "🏠 Главное меню:",
            reply_markup=get_main_menu_keyboard()
        )
        return

    service_title = SERVICE_MAP.get(data)
    if not service_title:
        await query.message.reply_text(
            "⚠️ Неизвестная кнопка. Открой меню заново.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    await register_order_and_notify(update, context, service_title)


# === Запуск приложения ===
def main():
    token = os.getenv("BOT_TOKEN")
    admin_id = os.getenv("ADMIN_ID")

    if not token or not admin_id:
        logger.error("Не заданы переменные окружения BOT_TOKEN или ADMIN_ID")
        raise SystemExit(1)

    try:
        admin_id = int(admin_id)
    except ValueError:
        logger.error("ADMIN_ID должен быть числом")
        raise SystemExit(1)

    application = Application.builder().token(token).build()
    application.bot_data["ADMIN_ID"] = admin_id

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_inline))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен")
    application.run_polling()


if __name__ == "__main__":
    main()