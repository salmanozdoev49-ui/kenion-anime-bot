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

# Добавляй сюда аниме по первой букве.
#
# Пример:
#
# "Н": [
#     {
#         "title": "Наруто",
#         "id": "naruto",
#         "year": 2002,
#         "rating": "8.3",
#         "genres": ["Экшен", "Комедия", "Сёнен"],
#         "description": "Описание аниме..."
#     }
# ]

ANIME_LIST = {
}


# =========================================================
# СЕРИИ
# =========================================================

# Пример:
#
# EPISODES = {
#     "naruto": {
#         1: "Вход в мир ниндзя",
#         2: "..."
#     }
# }

EPISODES = {
}


# =========================================================
# ВИДЕО
# =========================================================

# Структура:
#
# VIDEO_FILES = {
#     "naruto": {
#         "anilibria": {
#             1: {
#                 "720": "file_id",
#                 "1080": "file_id"
#             }
#         }
#     }
# }

VIDEO_FILES = {}


# Последнее отправленное видео администратора
PENDING_VIDEOS = {}


# =========================================================
# ОЗВУЧКИ
# =========================================================

VOICE_NAMES = {
    "anilibria": "AniLibria",
    "dreamcast": "Dream Cast",
}


# =========================================================
# ПОЛЬЗОВАТЕЛИ
# =========================================================

# Избранное
USER_FAVORITES = {}

# Последняя просмотренная серия
WATCH_PROGRESS = {}

# История просмотра
WATCH_HISTORY = {}

# Количество открытий аниме
ANIME_VIEWS = {}

# Недавно добавленные аниме
RECENT_ANIME = []


# =========================================================
# СТАТУСЫ ИЗБРАННОГО
# =========================================================

STATUS_NAMES = {
    "watched": "👀 Смотрел",
    "planned": "📋 Планирую",
    "dropped": "🚫 Брошено",
    "watching": "▶️ Смотрю",
}


# =========================================================
# ПРИВЕТСТВИЯ
# =========================================================

GREETINGS = [
    "Привет! Я AniFareX. 👋",
    "Здарова! Что смотрим? 🎬",
    "Аниме? Погнали. 🍿",
    "Ну что, ищем? 🔎",
]


# =========================================================
# ПРОВЕРКА АДМИНА
# =========================================================

def is_admin(update: Update):

    return (
        update.effective_user
        and update.effective_user.id == ADMIN_ID
    )


# =========================================================
# ПОЛЬЗОВАТЕЛЬСКИЕ ДАННЫЕ
# =========================================================

def get_user_favorites(user_id):

    if user_id not in USER_FAVORITES:

        USER_FAVORITES[user_id] = {
            "watched": set(),
            "planned": set(),
            "dropped": set(),
            "watching": set(),
        }

    return USER_FAVORITES[user_id]


def get_watch_progress(user_id):

    if user_id not in WATCH_PROGRESS:

        WATCH_PROGRESS[user_id] = {}

    return WATCH_PROGRESS[user_id]


def get_watch_history(user_id):

    if user_id not in WATCH_HISTORY:

        WATCH_HISTORY[user_id] = []

    return WATCH_HISTORY[user_id]


# =========================================================
# ПОИСК АНИМЕ ПО ID
# =========================================================

def find_anime(anime_id):

    for letter, anime_list in ANIME_LIST.items():

        for anime in anime_list:

            if anime.get("id") == anime_id:

                return anime

    return None


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
            InlineKeyboardButton(
                "▶️ Продолжить",
                callback_data="continue"
            ),
        ],
        [
            InlineKeyboardButton(
                "🎭 Жанры",
                callback_data="genres"
            ),
            InlineKeyboardButton(
                "🔥 Популярное",
                callback_data="popular"
            ),
        ],
        [
            InlineKeyboardButton(
                "🆕 Недавно добавленные",
                callback_data="recent"
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

        count = len(ANIME_LIST.get(letter, []))

        text = letter

        if count > 0:
            text += f" ({count})"

        row.append(
            InlineKeyboardButton(
                text,
                callback_data=f"letter_{letter}"
            )
        )

        if len(row) == 5:

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
                callback_data=f"anime_{anime['id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ К буквам",
            callback_data="catalog"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# КАРТОЧКА АНИМЕ
# =========================================================

def anime_card(anime_id):

    anime = find_anime(anime_id)

    if not anime:

        return (
            "❌ Аниме не найдено.",
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Назад",
                        callback_data="catalog"
                    )
                ]
            ])
        )

    genres = ", ".join(
        anime.get("genres", [])
    )

    text = (
        f"🎬 <b>{anime['title']}</b>\n\n"
        f"⭐ Рейтинг: {anime.get('rating', '—')}\n"
        f"📅 Год: {anime.get('year', '—')}\n"
        f"🎭 Жанры: {genres or '—'}\n\n"
        f"📝 <b>Описание:</b>\n"
        f"{anime.get('description', 'Описание отсутствует.')}\n\n"
        "Выбери действие:"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "📺 Сезоны",
                callback_data=f"seasons_{anime_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "⭐ Добавить в избранное",
                callback_data=f"addfav_{anime_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="catalog"
            )
        ],
    ]

    return text, InlineKeyboardMarkup(keyboard)


# =========================================================
# МЕНЮ ИЗБРАННОГО
# =========================================================

def favorite_status_menu(anime_id):

    keyboard = [
        [
            InlineKeyboardButton(
                "👀 Смотрел",
                callback_data=f"status_watched_{anime_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "📋 Планирую",
                callback_data=f"status_planned_{anime_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "🚫 Брошено",
                callback_data=f"status_dropped_{anime_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "▶️ Смотрю",
                callback_data=f"status_watching_{anime_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data=f"anime_{anime_id}"
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
# МЕНЮ ОЗВУЧКИ
# =========================================================

def voice_menu(anime_id):

    keyboard = [
        [
            InlineKeyboardButton(
                "💾 1–12  🎙 AniLibria",
                callback_data=f"voice_{anime_id}_anilibria"
            )
        ],
        [
            InlineKeyboardButton(
                "💾 1–12  🎙 Dream Cast",
                callback_data=f"voice_{anime_id}_dreamcast"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data=f"anime_{anime_id}"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# СПИСОК СЕРИЙ
# =========================================================

def episodes_menu(anime_id, voice):

    keyboard = []
    row = []

    episodes = (
        EPISODES
        .get(anime_id, {})
    )

    for episode in sorted(episodes):

        row.append(
            InlineKeyboardButton(
                f"🎞 {episode}",
                callback_data=(
                    f"episode_{anime_id}_"
                    f"{voice}_{episode}"
                )
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
            callback_data=f"seasons_{anime_id}"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# КАЧЕСТВО
# =========================================================

def quality_menu(anime_id, voice, episode):

    keyboard = [
        [
            InlineKeyboardButton(
                "720p",
                callback_data=(
                    f"quality_{anime_id}_"
                    f"{voice}_{episode}_720"
                )
            ),
            InlineKeyboardButton(
                "1080p",
                callback_data=(
                    f"quality_{anime_id}_"
                    f"{voice}_{episode}_1080"
                )
            ),
        ],
        [
            InlineKeyboardButton(
                "⏮ Предыдущая",
                callback_data=(
                    f"prev_{anime_id}_"
                    f"{voice}_{episode}"
                )
            ),
            InlineKeyboardButton(
                "⏭ Следующая",
                callback_data=(
                    f"next_{anime_id}_"
                    f"{voice}_{episode}"
                )
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ К сериям",
                callback_data=(
                    f"voice_{anime_id}_{voice}"
                )
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

    greeting = random.choice(GREETINGS)

    text = (
        f"🎌 <b>AniFareX</b>\n\n"
        f"{greeting}\n\n"
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
        "Теперь используй:\n\n"
        "/set ID_АНИМЕ ОЗВУЧКА СЕРИЯ КАЧЕСТВО\n\n"
        "Например:\n"
        "/set naruto anilibria 1 720\n\n"
        "или:\n"
        "/set naruto dreamcast 1 1080"
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

    if len(context.args) != 4:

        await update.message.reply_text(
            "❌ Формат:\n\n"
            "/set ID_АНИМЕ ОЗВУЧКА СЕРИЯ КАЧЕСТВО\n\n"
            "Например:\n"
            "/set naruto anilibria 1 720"
        )

        return

    anime_id = context.args[0]
    voice = context.args[1].lower()

    try:
        episode = int(context.args[2])
    except ValueError:

        await update.message.reply_text(
            "❌ Номер серии должен быть числом."
        )

        return

    quality = context.args[3]

    if voice not in VOICE_NAMES:

        await update.message.reply_text(
            "❌ Неизвестная озвучка.\n\n"
            "Доступно:\n"
            "anilibria\n"
            "dreamcast"
        )

        return

    if quality not in ["720", "1080"]:

        await update.message.reply_text(
            "❌ Качество должно быть 720 или 1080."
        )

        return

    if episode < 1:

        await update.message.reply_text(
            "❌ Номер серии должен быть больше 0."
        )

        return

    if anime_id not in VIDEO_FILES:

        VIDEO_FILES[anime_id] = {}

    if voice not in VIDEO_FILES[anime_id]:

        VIDEO_FILES[anime_id][voice] = {}

    if episode not in VIDEO_FILES[anime_id][voice]:

        VIDEO_FILES[anime_id][voice][episode] = {}

    file_id = PENDING_VIDEOS[user_id]

    VIDEO_FILES[anime_id][voice][episode][quality] = file_id

    await update.message.reply_text(
        f"✅ Видео сохранено!\n\n"
        f"🎬 Аниме: {anime_id}\n"
        f"🎙 Озвучка: {VOICE_NAMES[voice]}\n"
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

    for anime_id in VIDEO_FILES:

        text += f"🎬 <b>{anime_id}</b>\n"

        for voice in VIDEO_FILES[anime_id]:

            text += (
                f"🎙 {VOICE_NAMES.get(voice, voice)}\n"
            )

            for episode in sorted(
                VIDEO_FILES[anime_id][voice]
            ):

                qualities = []

                for quality in ["720", "1080"]:

                    if quality in VIDEO_FILES[
                        anime_id
                    ][voice][episode]:

                        qualities.append(
                            f"{quality}p"
                        )

                text += (
                    f"  🎞 {episode}: "
                    f"{', '.join(qualities)}\n"
                )

        text += "\n"

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
            "📚 <b>Каталог</b>\n\n"
            "Выбери первую букву:",
            parse_mode="HTML",
            reply_markup=alphabet_menu()
        )


    # =====================================================
    # БУКВА
    # =====================================================

    elif data.startswith("letter_"):

        letter = data.split("_", 1)[1]

        await query.edit_message_text(
            f"🔤 <b>Аниме на букву «{letter}»</b>\n\n"
            (
                "Выбери аниме:"
                if ANIME_LIST.get(letter)
                else "😔 Пока ничего нет."
            ),
            parse_mode="HTML",
            reply_markup=anime_by_letter(letter)
        )


    # =====================================================
    # КАРТОЧКА
    # =====================================================

    elif data.startswith("anime_"):

        anime_id = data.split("_", 1)[1]

        anime = find_anime(anime_id)

        if not anime:

            await query.edit_message_text(
                "❌ Аниме не найдено.",
                reply_markup=main_menu()
            )

            return

        ANIME_VIEWS[anime_id] = (
            ANIME_VIEWS.get(anime_id, 0) + 1
        )

        text, keyboard = anime_card(
            anime_id
        )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


    # =====================================================
    # ДОБАВИТЬ В ИЗБРАННОЕ
    # =====================================================

    elif data.startswith("addfav_"):

        anime_id = data.split("_", 1)[1]

        await query.edit_message_text(
            "⭐ <b>Добавить в избранное</b>\n\n"
            "Выбери статус:",
            parse_mode="HTML",
            reply_markup=favorite_status_menu(
                anime_id
            )
        )


    # =====================================================
    # СТАТУС ИЗБРАННОГО
    # =====================================================

    elif data.startswith("status_"):

        parts = data.split("_")

        status = parts[1]
        anime_id = "_".join(parts[2:])

        favorites = get_user_favorites(
            user_id
        )

        # Убираем из остальных категорий
        for category in favorites:

            favorites[category].discard(
                anime_id
            )

        favorites[status].add(
            anime_id
        )

        anime = find_anime(anime_id)

        title = (
            anime["title"]
            if anime
            else anime_id
        )

        await query.edit_message_text(
            f"✅ <b>Добавлено в избранное!</b>\n\n"
            f"🎬 {title}\n"
            f"📌 Статус: {STATUS_NAMES[status]}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⭐ Избранное",
                        callback_data="favorites"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ К аниме",
                        callback_data=f"anime_{anime_id}"
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

        favorites = get_user_favorites(
            user_id
        )

        keyboard = []

        for anime_id in favorites[status]:

            anime = find_anime(anime_id)

            if anime:

                keyboard.append([
                    InlineKeyboardButton(
                        anime["title"],
                        callback_data=f"anime_{anime_id}"
                    )
                ])

        keyboard.append([
            InlineKeyboardButton(
                "⬅️ К избранному",
                callback_data="favorites"
            )
        ])

        if not favorites[status]:

            text = (
                f"{STATUS_NAMES[status]}\n\n"
                "📭 Здесь пока ничего нет."
            )

        else:

            text = (
                f"{STATUS_NAMES[status]}\n\n"
                "Выбери аниме:"
            )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )


    # =====================================================
    # ПРОДОЛЖИТЬ ПРОСМОТР
    # =====================================================

    elif data == "continue":

        progress = get_watch_progress(
            user_id
        )

        keyboard = []

        for anime_id, episode in progress.items():

            anime = find_anime(anime_id)

            if anime:

                keyboard.append([
                    InlineKeyboardButton(
                        f"▶️ {anime['title']} — серия {episode}",
                        callback_data=(
                            f"continue_{anime_id}"
                        )
                    )
                ])

        keyboard.append([
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="home"
            )
        ])

        if not progress:

            text = (
                "▶️ <b>Продолжить просмотр</b>\n\n"
                "📭 Ты пока ничего не смотрел."
            )

        else:

            text = (
                "▶️ <b>Продолжить просмотр</b>\n\n"
                "Выбери аниме:"
            )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )


    # =====================================================
    # ПРОДОЛЖИТЬ КОНКРЕТНОЕ АНИМЕ
    # =====================================================

    elif data.startswith("continue_"):

        anime_id = data.split("_", 1)[1]

        progress = get_watch_progress(
            user_id
        )

        episode = progress.get(
            anime_id,
            1
        )

        await query.edit_message_text(
            f"▶️ <b>Продолжить просмотр</b>\n\n"
            f"🎬 {find_anime(anime_id)['title']}\n"
            f"🎞 Следующая серия: {episode}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🎙 Выбрать озвучку",
                        callback_data=f"seasons_{anime_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Назад",
                        callback_data="continue"
                    )
                ],
            ])
        )


    # =====================================================
    # СЕЗОНЫ
    # =====================================================

    elif data.startswith("seasons_"):

        anime_id = data.split("_", 1)[1]

        anime = find_anime(anime_id)

        if not anime:

            await query.answer(
                "Аниме не найдено.",
                show_alert=True
            )

            return

        await query.edit_message_text(
            f"📺 <b>{anime['title']}</b>\n\n"
            "Выбери озвучку:",
            parse_mode="HTML",
            reply_markup=voice_menu(
                anime_id
            )
        )


    # =====================================================
    # ОЗВУЧКА
    # =====================================================

    elif data.startswith("voice_"):

        parts = data.split("_")

        anime_id = parts[1]
        voice = parts[2]

        anime = find_anime(anime_id)

        if not anime:

            await query.answer(
                "Аниме не найдено.",
                show_alert=True
            )

            return

        await query.edit_message_text(
            f"🎙 <b>{VOICE_NAMES[voice]}</b>\n\n"
            f"🎬 {anime['title']}\n\n"
            "Выбери серию:",
            parse_mode="HTML",
            reply_markup=episodes_menu(
                anime_id,
                voice
            )
        )


    # =====================================================
    # СЕРИЯ
    # =====================================================

    elif data.startswith("episode_"):

        parts = data.split("_")

        anime_id = parts[1]
        voice = parts[2]
        episode = int(parts[3])

        anime = find_anime(anime_id)

        if not anime:

            await query.answer(
                "Аниме не найдено.",
                show_alert=True
            )

            return

        title = (
            EPISODES
            .get(anime_id, {})
            .get(
                episode,
                f"Серия {episode}"
            )
        )

        await query.edit_message_text(
            f"🎞 <b>Серия {episode}</b>\n\n"
            f"{title}\n\n"
            f"🎙 {VOICE_NAMES[voice]}\n\n"
            "⚙️ Выбери качество:",
            parse_mode="HTML",
            reply_markup=quality_menu(
                anime_id,
                voice,
                episode
            )
        )


    # =====================================================
    # ПРЕДЫДУЩАЯ СЕРИЯ
    # =====================================================

    elif data.startswith("prev_"):

        parts = data.split("_")

        anime_id = parts[1]
        voice = parts[2]
        episode = int(parts[3])

        previous = episode - 1

        if previous < 1:

            await query.answer(
                "Это первая серия.",
                show_alert=True
            )

            return

        await query.edit_message_text(
            f"🎞 <b>Серия {previous}</b>\n\n"
            "⚙️ Выбери качество:",
            parse_mode="HTML",
            reply_markup=quality_menu(
                anime_id,
                voice,
                previous
            )
        )


    # =====================================================
    # СЛЕДУЮЩАЯ СЕРИЯ
    # =====================================================

    elif data.startswith("next_"):

        parts = data.split("_")

        anime_id = parts[1]
        voice = parts[2]
        episode = int(parts[3])

        episodes = EPISODES.get(
            anime_id,
            {}
        )

        next_episode = episode + 1

        if next_episode not in episodes:

            await query.answer(
                "Это последняя серия.",
                show_alert=True
            )

            return

        await query.edit_message_text(
            f"🎞 <b>Серия {next_episode}</b>\n\n"
            f"{episodes[next_episode]}\n\n"
            "⚙️ Выбери качество:",
            parse_mode="HTML",
            reply_markup=quality_menu(
                anime_id,
                voice,
                next_episode
            )
        )


    # =====================================================
    # КАЧЕСТВО
    # =====================================================

    elif data.startswith("quality_"):

        parts = data.split("_")

        anime_id = parts[1]
        voice = parts[2]
        episode = int(parts[3])
        quality = parts[4]

        video = (
            VIDEO_FILES
            .get(anime_id, {})
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

        # Сохраняем прогресс
        progress = get_watch_progress(
            user_id
        )

        progress[anime_id] = episode + 1

        # История
        history = get_watch_history(
            user_id
        )

        history.append(
            (anime_id, episode)
        )

        # Ограничиваем историю
        if len(history) > 50:

            del history[:-50]

        # Отправляем видео
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=video,
            caption=(
                f"🎬 <b>AniFareX</b>\n\n"
                f"🎞 Серия {episode}\n"
                f"🎙 {VOICE_NAMES[voice]}\n"
                f"⚙️ {quality}p"
            ),
            parse_mode="HTML"
        )


    # =====================================================
    # ЖАНРЫ
    # =====================================================

    elif data == "genres":

        genres = set()

        for anime_list in ANIME_LIST.values():

            for anime in anime_list:

                for genre in anime.get(
                    "genres",
                    []
                ):

                    genres.add(genre)

        keyboard = []

        row = []

        for genre in sorted(genres):

            row.append(
                InlineKeyboardButton(
                    genre,
                    callback_data=f"genre_{genre}"
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
                callback_data="home"
            )
        ])

        if not genres:

            text = (
                "🎭 <b>Жанры</b>\n\n"
                "Пока жанров нет."
            )

        else:

            text = (
                "🎭 <b>Жанры</b>\n\n"
                "Выбери жанр:"
            )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )


    # =====================================================
    # АНИМЕ ПО ЖАНРУ
    # =====================================================

    elif data.startswith("genre_"):

        genre = data.split("_", 1)[1]

        keyboard = []

        for anime_list in ANIME_LIST.values():

            for anime in anime_list:

                if genre in anime.get(
                    "genres",
                    []
                ):

                    keyboard.append([
                        InlineKeyboardButton(
                            anime["title"],
                            callback_data=(
                                f"anime_{anime['id']}"
                            )
                        )
                    ])

        keyboard.append([
            InlineKeyboardButton(
                "⬅️ К жанрам",
                callback_data="genres"
            )
        ])

        await query.edit_message_text(
            f"🎭 <b>{genre}</b>\n\n"
            "Выбери аниме:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )


    # =====================================================
    # ПОПУЛЯРНОЕ
    # =====================================================

    elif data == "popular":

        sorted_anime = sorted(
            ANIME_VIEWS.items(),
            key=lambda x: x[1],
            reverse=True
        )

        keyboard = []

        for anime_id, views in sorted_anime[:10]:

            anime = find_anime(
                anime_id
            )

            if anime:

                keyboard.append([
                    InlineKeyboardButton(
                        f"🔥 {anime['title']} — {views}",
                        callback_data=(
                            f"anime_{anime_id}"
                        )
                    )
                ])

        keyboard.append([
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="home"
            )
        ])

        if not sorted_anime:

            text = (
                "🔥 <b>Популярное</b>\n\n"
                "Пока статистики нет."
            )

        else:

            text = (
                "🔥 <b>Популярное</b>\n\n"
                "Самые популярные аниме:"
            )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )


    # =====================================================
    # НЕДАВНО ДОБАВЛЕННЫЕ
    # =====================================================

    elif data == "recent":

        keyboard = []

        for anime_id in reversed(
            RECENT_ANIME[-10:]
        ):

            anime = find_anime(
                anime_id
            )

            if anime:

                keyboard.append([
                    InlineKeyboardButton(
                        f"🆕 {anime['title']}",
                        callback_data=(
                            f"anime_{anime_id}"
                        )
                    )
                ])

        keyboard.append([
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="home"
            )
        ])

        if not keyboard[:-1]:

            text = (
                "🆕 <b>Недавно добавленные</b>\n\n"
                "Пока здесь ничего нет."
            )

        else:

            text = (
                "🆕 <b>Недавно добавленные</b>\n\n"
                "Свежие добавления:"
            )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )


    # =====================================================
    # ПОИСК
    # =====================================================

    elif data == "search":

        await query.edit_message_text(
            "🔎 <b>Поиск</b>\n\n"
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
            "🔤 Каталог А–Я\n"
            "🔎 Поиск\n"
            "⭐ Избранное\n"
            "▶️ Продолжение просмотра\n"
            "🎭 Жанры\n"
            "🔥 Популярное\n"
            "🆕 Недавно добавленные\n"
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
# ПОИСК ТЕКСТОМ
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

    for anime_list in ANIME_LIST.values():

        for anime in anime_list:

            title = anime[
                "title"
            ].lower()

            if query in title:

                results.append(anime)

    keyboard = []

    for anime in results:

        keyboard.append([
            InlineKeyboardButton(
                anime["title"],
                callback_data=(
                    f"anime_{anime['id']}"
                )
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="home"
        )
    ])

    if not results:

        await update.message.reply_text(
            "🔎 <b>Ничего не найдено.</b>\n\n"
            "Попробуй другое название.",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

        return

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

    # Render
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
