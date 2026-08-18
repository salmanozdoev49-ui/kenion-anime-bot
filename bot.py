import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.environ["BOT_TOKEN"]

app = Flask(__name__)

# ---------- Главное меню ----------

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


# ---------- /start ----------

async def start(update: Update, context):
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


# ---------- Кнопки ----------

async def buttons(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "catalog":
        keyboard = [
            [InlineKeyboardButton("🎬 Царство", callback_data="kingdom")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="home")],
        ]

        await query.edit_message_text(
            "📚 <b>Каталог</b>\n\nВыбери аниме:",
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
            "Поиск добавим следующим этапом.",
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
            "📺 <b>Царство — 1 сезон</b>\n\nВыбери серию:",
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


# ---------- Flask ----------

@app.route("/")
def home():
    return "Kanyon Anime Bot is running!"


# ---------- Запуск ----------

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


def main():
    bot = Application.builder().token(TOKEN).build()

    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CallbackQueryHandler(buttons))

    # Веб-сервер запускаем отдельно
    threading.Thread(target=run_server, daemon=True).start()

    # Бот получает сообщения через polling
    bot.run_polling()


if __name__ == "__main__":
    main()
