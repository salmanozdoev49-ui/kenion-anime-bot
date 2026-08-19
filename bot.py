import os
import threading
import random

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

# Пока каталог пустой.
# Когда добавишь аниме, они будут появляться
# по соответствующей букве.

ANIME_LIST = {
}


# =========================================================
# СЕРИИ
# =========================================================

EPISODES = {
}


# =========================================================
# ВИДЕО
# =========================================================

VIDEO_FILES = {
    "anilibria": {},
    "dreamcast": {},
}

PENDING_VIDEOS = {}


# =========================================================
# ОЗВУЧКИ
# =========================================================

VOICE_NAMES = {
    "anilibria": "AniLibria",
    "dreamcast": "Dream Cast",
}


# =========================================================
# ИЗБРАННОЕ
# =========================================================

USER_FAVORITES = {}


def get_user_favorites(user_id):

    if user_id not in USER_FAVORITES:

        USER_FAVORITES[user_id] = {
            "watched": set(),
            "planned": set(),
            "dropped": set(),
            "watching": set(),
        }

    return USER_FAVORITES[user_id]


STATUS_NAMES = {
    "watched": "👀 Смотрел",
    "planned": "📋 Планирую",
    "dropped": "🚫 Брошено",
    "watching": "▶️ Смотрю",
}


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
                "🔎 Поиск",
                callback_data="search"
            ),
        ],
        [
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
# АЛФАВИТ
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
# АНИМЕ ПО БУКВЕ
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

def anime_card(user_id=None):

    keyboard = [
        [
            InlineKeyboardButton(
                "📺 Сезоны",
                callback_data="season1"
            )
        ],
        [
            InlineKeyboardButton(
                "⭐ Добавить в избранное",
                callback_data="add_favorite"
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
        "<b>Карточка аниме</b>\n\n"
        "Здесь будет информация об выбранном аниме.\n\n"
        "Выбери действие:"
    )

    return text, InlineKeyboardMarkup(keyboard)


# =========================================================
# МЕНЮ СТАТУСОВ
# =========================================================

def favorite_status_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                "👀 Смотрел",
                callback_data="status_watched"
            )
        ],
        [
            InlineKeyboardButton(
                "📋 Планирую",
                callback_data="status_planned"
            )
        ],
        [
            InlineKeyboardButton(
                "🚫 Брошено",
                callback_data="status_dropped"
            )
        ],
        [
            InlineKeyboardButton(
                "▶️ Смотрю",
                callback_data="status_watching"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="anime"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# ГЛАВНОЕ МЕНЮ ИЗБРАННОГО
# =========================================================

def favorites_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                "👀 Смотрел",
                callback_data="fav_watched"
            )
        ],
        [
            InlineKeyboardButton(
                "📋 Планирую",
                callback_data="fav_planned"
            )
        ],
        [
            InlineKeyboardButton(
                "🚫 Брошено",
                callback_data="fav_dropped"
            )
        ],
        [
            InlineKeyboardButton(
                "▶️ Смотрю",
                callback_data="fav_watching"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="home"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# СПИСОК ИЗБРАННОГО
# =========================================================

def favorite_list_menu(user_id, status):

    favorites = get_user_favorites(user_id)

    keyboard = []

    for anime_id in favorites[status]:

        keyboard.append([
            InlineKeyboardButton(
                anime_id,
                callback_data=f"openfav_{anime_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ К избранному",
            callback_data="favorites"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def favorite_list_text(user_id, status):

    favorites = get_user_favorites(user_id)

    if not favorites[status]:

        return (
            f"{STATUS_NAMES[status]}\n\n"
            "📭 Здесь пока ничего нет."
        )

    return (
        f"{STATUS_NAMES[status]}\n\n"
        "Выбери аниме:"
    )


# =========================================================
# ВЫБОР ОЗВУЧКИ
# =========================================================

def voice_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                "💾 1–12  🎙 AniLibria",
                callback_data="voice_anilibria"
            )
        ],
        [
            InlineKeyboardButton(
                "💾 1–12  🎙 Dream Cast",
                callback_data="voice_dreamcast"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="anime"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# СПИСОК СЕРИЙ
# =========================================================

def episodes_menu(voice):

    keyboard = []
    row = []

    for episode in sorted(EPISODES):

        row.append(
            InlineKeyboardButton(
                f"🎞 {episode}",
                callback_data=f"episode_{voice}_{episode}"
            )
        )

        if len(row) == 2:

            keyboard.append(row)
            row = []

    if row:

        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ К озвучкам",
            callback_data="season1"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# КАЧЕСТВО
# =========================================================

def quality_menu(voice, episode):

    keyboard = [
        [
            InlineKeyboardButton(
                "720p",
                callback_data=f"quality_{voice}_{episode}_720"
            ),
            InlineKeyboardButton(
                "1080p",
                callback_data=f"quality_{voice}_{episode}_1080"
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ К сериям",
                callback_data=f"voice_{voice}"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# /START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    greetings = [
        "Привет! Я AniFareX. 👋",
        "Здарова! Что смотрим? 🎬",
        "Аниме? Погнали. 🍿",
        "Ну что, ищем? 🔎",
    ]

    greeting = random.choice(greetings)

    text = (
        f"🎌 <b>{greeting}</b>\n\n"
        "Добро пожаловать в AniFareX! 🍿\n\n"
        "Выбирай нужный раздел:"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )


# =========================================================
# /MYID
# =========================================================

async def myid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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
        "Теперь укажи озвучку, серию и качество:\n\n"
        "/set anilibria 1 720\n\n"
        "или\n\n"
        "/set dreamcast 1 1080"
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
            "❌ Сначала отправь мне видео."
        )

        return

    if len(context.args) != 3:

        await update.message.reply_text(
            "❌ Неверный формат.\n\n"
            "/set anilibria 1 720\n"
            "или\n"
            "/set dreamcast 1 1080"
        )

        return

    voice = context.args[0].lower()

    if voice not in ["anilibria", "dreamcast"]:

        await update.message.reply_text(
            "❌ Неизвестная озвучка.\n\n"
            "Используй anilibria или dreamcast."
        )

        return

    try:

        episode = int(context.args[1])

    except ValueError:

        await update.message.reply_text(
            "❌ Номер серии должен быть числом."
        )

        return

    quality = context.args[2]

    if episode < 1:

        await update.message.reply_text(
            "❌ Номер серии должен быть больше 0."
        )

        return

    if quality not in ["720", "1080"]:

        await update.message.reply_text(
            "❌ Качество должно быть 720 или 1080."
        )

        return

    file_id = PENDING_VIDEOS[user_id]

    if episode not in VIDEO_FILES[voice]:

        VIDEO_FILES[voice][episode] = {}

    VIDEO_FILES[voice][episode][quality] = file_id

    await update.message.reply_text(
        f"✅ Видео сохранено!\n\n"
        f"🎙 {VOICE_NAMES[voice]}\n"
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

    text = "📂 <b>Добавленные видео</b>\n\n"

    found = False

    for voice in ["anilibria", "dreamcast"]:

        text += f"🎙 <b>{VOICE_NAMES[voice]}</b>\n"

        for episode in sorted(VIDEO_FILES[voice]):

            qualities = []

            for quality in ["720", "1080"]:

                if quality in VIDEO_FILES[voice][episode]:

                    qualities.append(
                        f"{quality}p"
                    )

            text += (
                f"🎞 Серия {episode}: "
                f"{', '.join(qualities)}\n"
            )

            found = True

        text += "\n"

    if not found:

        text = "📂 Видео пока не добавлены."

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

    user_id = query.from_user.id


    # =====================================================
    # ГЛАВНАЯ
    # =====================================================

    if data == "home":

        await query.edit_message_text(
            "🎌 <b>AniFareX</b>\n\n"
            "Выбирай нужный раздел:",
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
    # КАРТОЧКА
    # =====================================================

    elif data == "anime":

        text, keyboard = anime_card(user_id)

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


    # =====================================================
    # ИЗБРАННОЕ — ДОБАВИТЬ
    # =====================================================

    elif data == "add_favorite":

        await query.edit_message_text(
            "⭐ <b>Добавить в избранное</b>\n\n"
            "Выбери статус:",
            parse_mode="HTML",
            reply_markup=favorite_status_menu()
        )


    # =====================================================
    # СТАТУС
    # =====================================================

    elif data.startswith("status_"):

        status = data.split("_", 1)[1]

        favorites = get_user_favorites(user_id)

        # Убираем это аниме из других категорий
        for category in favorites:

            favorites[category].discard(
                "Текущее аниме"
            )

        favorites[status].add(
            "Текущее аниме"
        )

        await query.edit_message_text(
            f"✅ <b>Аниме добавлено!</b>\n\n"
            f"Статус: {STATUS_NAMES[status]}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⭐ В избранное",
                        callback_data="favorites"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Назад",
                        callback_data="anime"
                    )
                ],
            ])
        )


    # =====================================================
    # ИЗБРАННОЕ
    # =====================================================

    elif data == "favorites":

        await query.edit_message_text(
            "⭐ <b>Моё избранное</b>\n\n"
            "Выбери категорию:",
            parse_mode="HTML",
            reply_markup=favorites_menu()
        )


    # =====================================================
    # КАТЕГОРИЯ ИЗБРАННОГО
    # =====================================================

    elif data.startswith("fav_"):

        status = data.split("_", 1)[1]

        await query.edit_message_text(
            favorite_list_text(
                user_id,
                status
            ),
            parse_mode="HTML",
            reply_markup=favorite_list_menu(
                user_id,
                status
            )
        )


    # =====================================================
    # СЕЗОНЫ
    # =====================================================

    elif data == "season1":

        await query.edit_message_text(
            "📺 <b>Выбор сезона</b>\n\n"
            "1 сезон",
            parse_mode="HTML",
            reply_markup=voice_menu()
        )


    # =====================================================
    # ANILIBRIA
    # =====================================================

    elif data == "voice_anilibria":

        await query.edit_message_text(
            "🎙 <b>AniLibria</b>\n\n"
            "💾 1–12 серий\n\n"
            "Выберите серию:",
            parse_mode="HTML",
            reply_markup=episodes_menu(
                "anilibria"
            )
        )


    # =====================================================
    # DREAM CAST
    # =====================================================

    elif data == "voice_dreamcast":

        await query.edit_message_text(
            "🎙 <b>Dream Cast</b>\n\n"
            "💾 1–12 серий\n\n"
            "Выберите серию:",
            parse_mode="HTML",
            reply_markup=episodes_menu(
                "dreamcast"
            )
        )


    # =====================================================
    # СЕРИЯ
    # =====================================================

    elif data.startswith("episode_"):

        parts = data.split("_")

        voice = parts[1]
        episode = int(parts[2])

        title = EPISODES.get(
            episode,
            f"Серия {episode}"
        )

        await query.edit_message_text(
            f"🎞 <b>Серия {episode}</b>\n\n"
            f"<b>{title}</b>\n\n"
            f"🎙 Озвучка: <b>{VOICE_NAMES[voice]}</b>\n\n"
            "⚙️ Выберите качество:",
            parse_mode="HTML",
            reply_markup=quality_menu(
                voice,
                episode
            )
        )


    # =====================================================
    # ВОЗВРАТ К ОЗВУЧКЕ
    # =====================================================

    elif data.startswith("voice_"):

        voice = data.split("_", 1)[1]

        await query.edit_message_text(
            f"🎙 <b>{VOICE_NAMES[voice]}</b>\n\n"
            "Выберите серию:",
            parse_mode="HTML",
            reply_markup=episodes_menu(
                voice
            )
        )


    # =====================================================
    # КАЧЕСТВО
    # =====================================================

    elif data.startswith("quality_"):

        parts = data.split("_")

        voice = parts[1]
        episode = int(parts[2])
        quality = parts[3]

        video = (
            VIDEO_FILES
            .get(voice, {})
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
                f"🎬 <b>AniFareX</b>\n"
                f"🎞 Серия {episode}\n"
                f"🎙 {VOICE_NAMES[voice]}\n"
                f"⚙️ {quality}p"
            ),
            parse_mode="HTML"
        )


    # =====================================================
    # ПОИСК
    # =====================================================

    elif data == "search":

        await query.edit_message_text(
            "🔎 <b>Поиск по названию</b>\n\n"
            "Напиши название или часть названия аниме.",
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
            "ℹ️ <b>AniFareX</b>\n\n"
            "🎌 Каталог аниме\n"
            "🔤 Каталог по алфавиту\n"
            "🔎 Поиск по названию\n"
            "⭐ Избранное\n"
            "📺 Сезоны и серии\n"
            "🎙 Озвучки\n"
            "⚙️ 720p / 1080p",
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
# ПОИСК
# =========================================================

async def search_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    if not update.message.text:
        return

    text = update.message.text.strip()

    if text.startswith("/"):
        return

    query = text.lower()

    results = []

    for letter, anime_list in ANIME_LIST.items():

        for anime in anime_list:

            clean_title = anime["title"].lower()

            if query in clean_title:

                results.append(anime)

    if not results:

        await update.message.reply_text(
            "🔎 <b>Ничего не найдено.</b>\n\n"
            "Попробуй другое название.",
            parse_mode="HTML",
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
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# =========================================================
# WEB SERVER ДЛЯ RENDER
# =========================================================

@app.route("/")
def web():

    return "AniFareX Bot is running!"


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

    # Обычные команды
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

    # Админские команды
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

    # Кнопки
    bot.add_handler(
        CallbackQueryHandler(
            buttons
        )
    )

    # Получение видео
    bot.add_handler(
        MessageHandler(
            filters.VIDEO,
            receive_video
        )
    )

    # Поиск
    bot.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search_text
        )
    )

    # Render Web Server
    threading.Thread(
        target=run_server,
        daemon=True
    ).start()

    print(
        "AniFareX BOT ЗАПУЩЕН!"
    )

    bot.run_polling()


if __name__ == "__main__":
    main()
