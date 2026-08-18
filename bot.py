import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Токен НЕ записываем в код.
TOKEN = os.environ["BOT_TOKEN"]

app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()


# Главное меню
def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("📚 Каталог", callback_data="catalog"),
            InlineKeyboardButton("🔥 Новинки", callback_data="new"),
        ],
        [
            InlineKeyboardButton("🔎 Поиск", callback_data="search"),
            InlineKeyboardButton("⭐ Избранное", callback_data="favorites"),
        ],
        [
            InlineKeyboardButton("ℹ️ О боте", callback_data="about"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎌 <b>КАНЬОН АНИМЕ</b>\n\n"
        "Добро пожаловать! 🍿\n\n"
        "Здесь будет каталог аниме, серии, "
        "озвучки и выбор качества.\n\n"
        "Выбери нужный раздел:"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# Обработка кнопок
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "catalog":
        keyboard = [
            [InlineKeyboardButton("🎬 Царство", callback_data="kingdom")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="home")],
        ]

        await query.edit_message_text(
            "📚 <b>Каталог</b>\n\n"
            "Выбери аниме:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "new":
        await query.edit_message_text(
            "🔥 <b>Новинки</b>\n\n"
            "Здесь будут последние добавленные аниме.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="home")]
            ])
        )

    elif query.data == "search":
        await query.edit_message_text(
            "🔎 <b>Поиск</b>\n\n"
            "Функцию поиска добавим следующим этапом.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="home")]
            ])
        )

    elif query.data == "favorites":
        await query.edit_message_text(
            "⭐ <b>Избранное</b>\n\n"
            "Здесь будут сохранённые аниме.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="home")]
            ])
        )

    elif query.data == "about":
        await query.edit_message_text(
            "ℹ️ <b>Каньон Аниме</b>\n\n"
            "🎌 Аниме-каталог\n"
            "🎙 Несколько озвучек\n"
            "🎞 Разное качество\n"
            "📺 Удобный просмотр серий",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="home")]
            ])
        )

    elif query.data == "kingdom":
        keyboard = [
            [InlineKeyboardButton("📺 1 сезон", callback_data="season1")],
            [InlineKeyboardButton("⬅️ Каталог", callback_data="catalog")],
        ]

        await query.edit_message_text(
            "🎬 <b>Царство</b>\n\n"
            "⭐ 7.87\n"
            "📅 2012\n"
            "🔞 18+\n"
            "⏱ 25 мин/эп.\n"
            "📌 Статус: Завершено\n\n"
            "Выбери сезон:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "season1":
        keyboard = [
            [InlineKeyboardButton("🎞 Серия 1", callback_data="episode1")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="kingdom")],
        ]

        await query.edit_message_text(
            "📺 <b>Царство — 1 сезон</b>\n\n"
            "Выбери серию:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "episode1":
        keyboard = [
            [
                InlineKeyboardButton("360p", callback_data="360"),
                InlineKeyboardButton("480p", callback_data="480"),
                InlineKeyboardButton("720p", callback_data="720"),
            ],
            [InlineKeyboardButton("⬅️ Назад", callback_data="season1")],
        ]

        await query.edit_message_text(
            "🎞 <b>Царство — серия 1</b>\n\n"
            "🎙 Озвучка: AniDUB\n\n"
            "Выбери качество:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data in ["360", "480", "720"]:
        quality = query.data + "p"

        await query.edit_message_text(
            f"🎬 <b>Царство — серия 1</b>\n\n"
            f"⚙️ Качество: {quality}\n\n"
            "▶️ Видео добавим следующим этапом.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="episode1")]
            ])
        )

    elif query.data == "home":
        await query.edit_message_text(
            "🎌 <b>КАНЬОН АНИМЕ</b>\n\n"
            "Выбери нужный раздел:",
            parse_mode="HTML",
            reply_markup=main_menu()
        )


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(buttons))


@app.route("/", methods=["GET"])
def home():
    return "Kanyon Anime Bot is running!"


@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"


if __name__ == "__main__":
    import asyncio

    async def run():
        await telegram_app.initialize()
        await telegram_app.start()

        port = int(os.environ.get("PORT", 10000))

        from werkzeug.serving import run_simple
        run_simple("0.0.0.0", port, app)

        await telegram_app.stop()
        await telegram_app.shutdown()

    asyncio.run(run())
