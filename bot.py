import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.environ["BOT_TOKEN"]

app = Flask(__name__)


# =========================================================
# ДАННЫЕ АНИМЕ
# =========================================================

ANIME_TITLE = "🧙‍♀️ Ведьма и чудовище"

EPISODES = {
    1: "Ведьма и город пылающего красного",
    2: "Ведьмино развлечение: Начальная часть",
    3: "Ведьмино развлечение: Финальная часть",
    4: "Красота и смерть: Начальная часть",
    5: "Красота и смерть: Финальная часть",
    6: "Ведьма и демонический меч: Начальная часть",
    7: "Ведьма и демонический меч: Часть II",
    8: "Ведьма и демонический меч: Часть III",
    9: "Ведьма и демонический меч: Финальная часть",
    10: "Первородная ведьма",
    11: "Красноречие и тишина: Начальная часть",
    12: "Красноречие и тишина: Финальная часть",
}


# =========================================================
# ВИДЕО
# =========================================================
#
# Сюда позже можно добавить file_id видео,
# которое ты сам загрузил в Telegram и имеешь право
# распространять.
#
# Пример:
#
# VIDEO_FILES = {
#     1: {
#         "360": "FILE_ID_360",
#         "480": "FILE_ID_480",
#         "720": "FILE_ID_720",
#     }
# }
#
# Пока оставляем пустым.

VIDEO_FILES = {}


# =========================================================
# ГЛАВНОЕ МЕНЮ
# =========================================================

def main_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                "📚 Каталог",
                callback_data="catalog"
            ),
            InlineKeyboardButton(
                "🔥 Новинки",
                callback_data="new"
            )
        ],
        [
            InlineKeyboardButton(
                "🔎 Поиск",
                callback_data="search"
            ),
            InlineKeyboardButton(
                "⭐ Избранное",
                callback_data="favorites"
            )
        ],
        [
            InlineKeyboardButton(
                "ℹ️ О боте",
                callback_data="about"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# КАРТОЧКА АНИМЕ
# =========================================================

def anime_card():

    keyboard = [
        [
            InlineKeyboardButton(
                "📺 1 сезон • 12 серий",
                callback_data="season1"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="home"
            )
        ]
    ]

    text = (
        f"<b>{ANIME_TITLE}</b>\n\n"
        "⭐ Рейтинг: 7.77\n"
        "📅 Год: 2024\n"
        "📺 Серий: 12\n"
        "⏱ Продолжительность: ~24 мин.\n"
        "📌 Статус: Завершено\n"
        "🎭 Жанры: фэнтези, экшен, мистика\n\n"
        "📝 <b>Описание:</b>\n"
        "Гидо и загадочный маг Ашраф путешествуют "
        "по миру в поисках ведьмы, наложившей проклятие.\n\n"
        "Выбери сезон:"
    )

    return text, InlineKeyboardMarkup(keyboard)


# =========================================================
# СПИСОК СЕРИЙ
# =========================================================

def episodes_menu():

    keyboard = []

    # Делаем по две серии в ряд
    row = []

    for episode in range(1, 13):

        button = InlineKeyboardButton(
            f"🎞 {episode}",
            callback_data=f"episode_{episode}"
        )

        row.append(button)

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="anime"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# КАЧЕСТВО
# =========================================================

def quality_menu(episode):

    keyboard = [
        [
            InlineKeyboardButton(
                "360p",
                callback_data=f"quality_{episode}_360"
            ),
            InlineKeyboardButton(
                "480p",
                callback_data=f"quality_{episode}_480"
            ),
            InlineKeyboardButton(
                "720p",
                callback_data=f"quality_{episode}_720"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ К сериям",
                callback_data="season1"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# /START
# =========================================================

async def start(update: Update, context):

    text = (
        "🎌 <b>КАНЬОН АНИМЕ</b>\n\n"
        "Добро пожаловать! 🍿\n\n"
        "Здесь ты сможешь находить аниме, "
        "смотреть серии и выбирать качество.\n\n"
        "📚 Каталог постепенно пополняется.\n\n"
        "Выбери нужный раздел:"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# =========================================================
# КНОПКИ
# =========================================================

async def buttons(update: Update, context):

    query = update.callback_query

    await query.answer()

    data = query.data


    # -----------------------------------------------------
    # ГЛАВНАЯ
    # -----------------------------------------------------

    if data == "home":

        await query.edit_message_text(
            "🎌 <b>КАНЬОН АНИМЕ</b>\n\n"
            "Выбери нужный раздел:",
            parse_mode="HTML",
            reply_markup=main_menu()
        )


    # -----------------------------------------------------
    # КАТАЛОГ
    # -----------------------------------------------------

    elif data == "catalog":

        keyboard = [
            [
                InlineKeyboardButton(
                    "🧙‍♀️ Ведьма и чудовище",
                    callback_data="anime"
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Назад",
                    callback_data="home"
                )
            ]
        ]

        await query.edit_message_text(
            "📚 <b>Каталог</b>\n\n"
            "Выбери аниме:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    # -----------------------------------------------------
    # КАРТОЧКА АНИМЕ
    # -----------------------------------------------------

    elif data == "anime":

        text, keyboard = anime_card()

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


    # -----------------------------------------------------
    # СЕЗОН
    # -----------------------------------------------------

    elif data == "season1":

        await query.edit_message_text(
            "📺 <b>Ведьма и чудовище</b>\n\n"
            "1 сезон • 12 серий\n\n"
            "Выбери серию:",
            parse_mode="HTML",
            reply_markup=episodes_menu()
        )


    # -----------------------------------------------------
    # СЕРИЯ
    # -----------------------------------------------------

    elif data.startswith("episode_"):

        episode = int(data.split("_")[1])

        title = EPISODES[episode]

        text = (
            f"🎞 <b>Серия {episode} из 12</b>\n\n"
            f"<b>{title}</b>\n\n"
            "🎙 Озвучка: будет указана после добавления\n"
            "🎬 Выбери качество:"
        )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=quality_menu(episode)
        )


    # -----------------------------------------------------
    # КАЧЕСТВО
    # -----------------------------------------------------

    elif data.startswith("quality_"):

        parts = data.split("_")

        episode = int(parts[1])
        quality = parts[2]

        # Проверяем, есть ли видео
        video = VIDEO_FILES.get(episode, {}).get(quality)

        if video:

            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=video,
                caption=(
                    f"🎬 <b>Ведьма и чудовище</b>\n"
                    f"🎞 Серия {episode}\n"
                    f"⚙️ Качество: {quality}p"
                ),
                parse_mode="HTML"
            )

        else:

            await query.answer(
                f"Видео {quality}p пока не добавлено",
                show_alert=True
            )


    # -----------------------------------------------------
    # НОВИНКИ
    # -----------------------------------------------------

    elif data == "new":

        await query.edit_message_text(
            "🔥 <b>Новинки</b>\n\n"
            "🧙‍♀️ Ведьма и чудовище\n"
            "📺 1 сезон • 12/12 серий",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🎬 Открыть",
                        callback_data="anime"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Назад",
                        callback_data="home"
                    )
                ]
            ])
        )


    # -----------------------------------------------------
    # ПОИСК
    # -----------------------------------------------------

    elif data == "search":

        await query.edit_message_text(
            "🔎 <b>Поиск</b>\n\n"
            "Полноценный поиск добавим следующим этапом.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Назад",
                        callback_data="home"
                    )
                ]
            ])
        )


    # -----------------------------------------------------
    # ИЗБРАННОЕ
    # -----------------------------------------------------

    elif data == "favorites":

        await query.edit_message_text(
            "⭐ <b>Избранное</b>\n\n"
            "Система избранного будет добавлена следующим этапом.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Назад",
                        callback_data="home"
                    )
                ]
            ])
        )


    # -----------------------------------------------------
    # О БОТЕ
    # -----------------------------------------------------

    elif data == "about":

        await query.edit_message_text(
            "ℹ️ <b>Каньон Аниме</b>\n\n"
            "🎌 Каталог аниме\n"
            "📺 Серии\n"
            "🎙 Озвучки\n"
            "⚙️ Выбор качества\n\n"
            "Новые возможности будут добавляться постепенно.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Назад",
                        callback_data="home"
                    )
                ]
            ])
        )


# =========================================================
# WEB SERVER ДЛЯ RENDER
# =========================================================

@app.route("/")
def web():

    return "Kanyon Anime Bot is running!"


def run_server():

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )


# =========================================================
# ЗАПУСК БОТА
# =========================================================

def main():

    bot = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    bot.add_handler(
        CommandHandler("start", start)
    )

    bot.add_handler(
        CallbackQueryHandler(buttons)
    )

    threading.Thread(
        target=run_server,
        daemon=True
    ).start()

    bot.run_polling()


if __name__ == "__main__":

    main()
