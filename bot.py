import os
import threading

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]

# =========================================================
# АДМИНИСТРАТОР
# =========================================================

ADMIN_ID = 6502304303

app = Flask(__name__)


# =========================================================
# ДАННЫЕ АНИМЕ
# =========================================================

ANIME_TITLE = "🧙‍♀️ Ведьма и чудовище"

# Здесь будут все аниме каталога.
# Сейчас добавлено только одно.

ANIME_LIST = {
    "В": [
        {
            "title": "🧙‍♀️ Ведьма и чудовище",
            "callback": "anime"
        }
    ]
}


# =========================================================
# СЕРИИ «ВЕДЬМА И ЧУДОВИЩЕ»
# =========================================================

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

VIDEO_FILES = {}

# Последнее отправленное администратором видео
PENDING_VIDEOS = {}


# =========================================================
# ПРОВЕРКА АДМИНА
# =========================================================

def is_admin(update: Update):

    return (
        update.effective_user
        and update.effective_user.id == ADMIN_ID
    )


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
            ),
        ],
        [
            InlineKeyboardButton(
                "🔎 Поиск",
                callback_data="search"
            ),
            InlineKeyboardButton(
                "⭐ Избранное",
                callback_data="favorites"
            ),
        ],
        [
            InlineKeyboardButton(
                "ℹ️ О боте",
                callback_data="about"
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# АЛФАВИТ КАТАЛОГА
# =========================================================

def alphabet_menu():

    letters = [
        "А", "Б", "В", "Г", "Д", "Е", "Ё",
        "Ж", "З", "И", "Й", "К", "Л", "М",
        "Н", "О", "П", "Р", "С", "Т", "У",
        "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Ъ",
        "Ы", "Ь", "Э", "Ю", "Я"
    ]

    keyboard = []
    row = []

    for letter in letters:

        row.append(
            InlineKeyboardButton(
                letter,
                callback_data=f"letter_{letter}"
            )
        )

        if len(row) == 7:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="home"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# АНИМЕ НА ВЫБРАННУЮ БУКВУ
# =========================================================

def anime_by_letter(letter):

    keyboard = []

    anime_list = ANIME_LIST.get(letter, [])

    for anime in anime_list:

        keyboard.append([
            InlineKeyboardButton(
                anime["title"],
                callback_data=anime["callback"]
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ К буквам",
            callback_data="catalog"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def anime_letter_text(letter):

    if letter in ANIME_LIST and ANIME_LIST[letter]:

        return (
            f"🔤 <b>Аниме на букву «{letter}»</b>\n\n"
            "Выбери аниме:"
        )

    return (
        f"🔤 <b>Аниме на букву «{letter}»</b>\n\n"
        "😔 Пока ничего нет."
    )


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
                "⬅️ К каталогу",
                callback_data="catalog"
            )
        ],
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
    row = []

    for episode in range(1, 13):

        row.append(
            InlineKeyboardButton(
                f"🎞 {episode}",
                callback_data=f"episode_{episode}"
            )
        )

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
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ К сериям",
                callback_data="season1"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# /START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "🎌 <b>КАНЬОН АНИМЕ</b>\n\n"
        "Добро пожаловать! 🍿\n\n"
        "Здесь ты сможешь находить аниме, "
        "смотреть серии и выбирать качество.\n\n"
        "Выбери нужный раздел:"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# =========================================================
# /MYID
# =========================================================

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"🆔 Твой Telegram ID:\n"
        f"{update.effective_user.id}"
    )


# =========================================================
# ПОЛУЧЕНИЕ ВИДЕО
# =========================================================

async def receive_video(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ У тебя нет прав для добавления видео."
        )

        return

    video = update.message.video

    if not video:
        return

    user_id = update.effective_user.id

    PENDING_VIDEOS[user_id] = video.file_id

    await update.message.reply_text(
        "✅ Видео получено!\n\n"
        "Теперь напиши:\n\n"
        "/set НОМЕР_СЕРИИ КАЧЕСТВО\n\n"
        "Например:\n"
        "/set 1 720"
    )


# =========================================================
# /SET
# =========================================================

async def set_video(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ У тебя нет прав для этой команды."
        )

        return

    user_id = update.effective_user.id

    if user_id not in PENDING_VIDEOS:

        await update.message.reply_text(
            "❌ Сначала перешли мне видео."
        )

        return

    if len(context.args) != 2:

        await update.message.reply_text(
            "❌ Неверный формат.\n\n"
            "Используй:\n"
            "/set 1 720"
        )

        return

    try:

        episode = int(context.args[0])
        quality = context.args[1]

    except ValueError:

        await update.message.reply_text(
            "❌ Номер серии должен быть числом."
        )

        return

    if episode < 1 or episode > 12:

        await update.message.reply_text(
            "❌ Серия должна быть от 1 до 12."
        )

        return

    if quality not in ["360", "480", "720"]:

        await update.message.reply_text(
            "❌ Качество должно быть 360, 480 или 720."
        )

        return

    file_id = PENDING_VIDEOS[user_id]

    if episode not in VIDEO_FILES:

        VIDEO_FILES[episode] = {}

    VIDEO_FILES[episode][quality] = file_id

    await update.message.reply_text(
        f"✅ Видео сохранено!\n\n"
        f"🎞 Серия: {episode}\n"
        f"⚙️ Качество: {quality}p"
    )


# =========================================================
# /VIDEOS
# =========================================================

async def videos_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ У тебя нет прав для этой команды."
        )

        return

    if not VIDEO_FILES:

        await update.message.reply_text(
            "📂 Видео пока не добавлены."
        )

        return

    text = "📂 <b>Добавленные видео</b>\n\n"

    for episode in sorted(VIDEO_FILES):

        qualities = []

        for quality in ["360", "480", "720"]:

            if quality in VIDEO_FILES[episode]:

                qualities.append(f"{quality}p")

        text += (
            f"🎞 Серия {episode}: "
            f"{', '.join(qualities)}\n"
        )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
)
# =========================================================
# КНОПКИ
# =========================================================

async def buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    # =====================================================
    # ГЛАВНАЯ
    # =====================================================

    if data == "home":

        await query.edit_message_text(
            "🎌 <b>КАНЬОН АНИМЕ</b>\n\n"
            "Выбери нужный раздел:",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    # =====================================================
    # КАТАЛОГ
    # =====================================================

    elif data == "catalog":

        await query.edit_message_text(
            "📚 <b>Каталог аниме</b>\n\n"
            "Выбери первую букву названия:",
            parse_mode="HTML",
            reply_markup=alphabet_menu()
        )

    # =====================================================
    # БУКВА
    # =====================================================

    elif data.startswith("letter_"):

        letter = data.split("_", 1)[1]

        await query.edit_message_text(
            anime_letter_text(letter),
            parse_mode="HTML",
            reply_markup=anime_by_letter(letter)
        )

    # =====================================================
    # КАРТОЧКА «ВЕДЬМА И ЧУДОВИЩЕ»
    # =====================================================

    elif data == "anime":

        text, keyboard = anime_card()

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # =====================================================
    # СЕЗОН
    # =====================================================

    elif data == "season1":

        await query.edit_message_text(
            "📺 <b>Ведьма и чудовище</b>\n\n"
            "1 сезон • 12 серий\n\n"
            "Выбери серию:",
            parse_mode="HTML",
            reply_markup=episodes_menu()
        )

    # =====================================================
    # СЕРИЯ
    # =====================================================

    elif data.startswith("episode_"):

        episode = int(data.split("_")[1])

        title = EPISODES[episode]

        text = (
            f"🎞 <b>Серия {episode} из 12</b>\n\n"
            f"<b>{title}</b>\n\n"
            "🎙 Озвучка: AniDUB\n\n"
            "⚙️ Выбери качество:"
        )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=quality_menu(episode)
        )

    # =====================================================
    # КАЧЕСТВО
    # =====================================================

    elif data.startswith("quality_"):

        parts = data.split("_")

        episode = int(parts[1])
        quality = parts[2]

        video = (
            VIDEO_FILES
            .get(episode, {})
            .get(quality)
        )

        if not video:

            await query.answer(
                f"Видео {quality}p ещё не добавлено.",
                show_alert=True
            )

            return

        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=video,
            caption=(
                f"🎬 <b>{ANIME_TITLE}</b>\n"
                f"🎞 Серия {episode}\n"
                f"⚙️ {quality}p"
            ),
            parse_mode="HTML"
        )

    # =====================================================
    # НОВИНКИ
    # =====================================================

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
                ],
            ])
        )

    # =====================================================
    # ПОИСК
    # =====================================================

    elif data == "search":

        await query.edit_message_text(
            "🔎 <b>Поиск</b>\n\n"
            "Напиши название аниме обычным сообщением.",
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

    # =====================================================
    # ИЗБРАННОЕ
    # =====================================================

    elif data == "favorites":

        await query.edit_message_text(
            "⭐ <b>Избранное</b>\n\n"
            "Здесь будут сохранённые аниме.",
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

    # =====================================================
    # О БОТЕ
    # =====================================================

    elif data == "about":

        await query.edit_message_text(
            "ℹ️ <b>Каньон Аниме</b>\n\n"
            "🎌 Каталог аниме\n"
            "📺 Серии\n"
            "🎙 Озвучки\n"
            "⚙️ Выбор качества",
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
# ПОИСК ПО НАЗВАНИЮ
# =========================================================

async def search_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    if text.startswith("/"):
        return

    query = text.lower()

    results = []

    for letter, anime_list in ANIME_LIST.items():

        for anime in anime_list:

            if query in anime["title"].lower():

                results.append(anime)

    if not results:

        await update.message.reply_text(
            "🔎 Ничего не найдено.\n\n"
            "Попробуй другое название.",
            reply_markup=main_menu()
        )

        return

    keyboard = []

    for anime in results:

        keyboard.append([
            InlineKeyboardButton(
                anime["title"],
                callback_data=anime["callback"]
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="home"
        )
    ])

    await update.message.reply_text(
        "🔎 <b>Результаты поиска:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# WEB SERVER ДЛЯ RENDER
# =========================================================

@app.route("/")
def web():

    return "Kanyon Anime Bot is running!"


def run_server():

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )


# =========================================================
# ЗАПУСК
# =========================================================

def main():

    bot = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    # =====================================================
    # КОМАНДЫ
    # =====================================================

    bot.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    bot.add_handler(
        CommandHandler(
            "myid",
            myid
        )
    )

    # =====================================================
    # АДМИНСКИЕ КОМАНДЫ
    # =====================================================

    bot.add_handler(
        CommandHandler(
            "set",
            set_video
        )
    )

    bot.add_handler(
        CommandHandler(
            "videos",
            videos_list
        )
    )

    # =====================================================
    # КНОПКИ
    # =====================================================

    bot.add_handler(
        CallbackQueryHandler(
            buttons
        )
    )

    # =====================================================
    # ПОЛУЧЕНИЕ ВИДЕО
    # =====================================================

    bot.add_handler(
        MessageHandler(
            filters.VIDEO,
            receive_video
        )
    )

    # =====================================================
    # ПОИСК
    # =====================================================

    bot.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search_text
        )
    )

    # =====================================================
    # WEB SERVER
    # =====================================================

    threading.Thread(
        target=run_server,
        daemon=True
    ).start()

    # =====================================================
    # ЗАПУСК БОТА
    # =====================================================

    print("КАНЬОН АНИМЕ БОТ ЗАПУЩЕН!")

    bot.run_polling()


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()
