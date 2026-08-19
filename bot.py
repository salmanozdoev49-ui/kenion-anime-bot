import os
import json
import random
import threading
import atexit

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
ADMIN_ID = 6502304303

app = Flask(__name__)

# =========================================================
# СОХРАНЕНИЕ
# =========================================================

DATA_FILE = "anime_data.json"


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "favorites": {},
            "history": {},
            "videos": {},
        }


DATA = load_data()


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(DATA, f, ensure_ascii=False, indent=2)


atexit.register(save_data)


# =========================================================
# АНИМЕ
# =========================================================

ANIME_DATABASE = {

    "mythic_spirit": {
        "title": "Мифический дух: духовные хроники",
        "letter": "М",

        "genres": (
            "гарем, исэкай, приключения, реинкарнация, "
            "романтика, фэнтези, экшен"
        ),

        "seasons": {

            "1": {
                "title": "Мифический дух: духовные хроники 1 сезон",
                "rating": "7.06",
                "year": "2021",
                "episodes": 12,
                "duration": "23 мин./эп.",
                "description": (
                    "20-летний студент Харуто Амакава погибает в ДТП. "
                    "Позже он приходит в себя в незнакомом мире в теле "
                    "парня по имени Рио и становится обладателем "
                    "магических способностей."
                ),
            },

            "2": {
                "title": "Мифический дух: духовные хроники 2 сезон",
                "rating": "6.88",
                "year": "2024",
                "episodes": 12,
                "duration": "23 мин./эп.",
                "description": (
                    "После побега из столицы Бельтрама Рио вместе с "
                    "Селией и Аисией спасает группу людей из Японии, "
                    "среди которых оказывается его подруга детства "
                    "Михару. Вместе с союзниками он ищет остальных "
                    "переселенцев и способ вернуть их домой, не забывая "
                    "о главной цели — отомстить за смерть матери."
                ),
            },
        },
    },
}


# =========================================================
# ОЗВУЧКИ
# =========================================================

DUBS = {
    "anilibria": "AniLibria",
    "dreamcast": "Dream Cast",
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
# ПРИВЕТСТВИЯ
# =========================================================

GREETINGS = [
    "👋 Привет! Я AniFareX.",
    "😎 Здарова! Что смотрим?",
    "🔥 Аниме? Погнали.",
    "🔎 Ну что, ищем?",
]


def greeting():
    return random.choice(GREETINGS)


# =========================================================
# ГЛАВНОЕ МЕНЮ
# =========================================================

def main_menu():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "📚 Каталог",
                callback_data="catalog"
            ),
            InlineKeyboardButton(
                "⭐ Избранное",
                callback_data="favorites"
            ),
        ],

        [
            InlineKeyboardButton(
                "🔎 Поиск",
                callback_data="search"
            ),
            InlineKeyboardButton(
                "🎲 Случайное аниме",
                callback_data="random"
            ),
        ],

        [
            InlineKeyboardButton(
                "▶️ Продолжить",
                callback_data="continue"
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
    ])


# =========================================================
# КАТАЛОГ
# =========================================================

ALPHABET = list(
    "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
)


def catalog_menu():

    keyboard = []
    row = []

    for letter in ALPHABET:

        row.append(
            InlineKeyboardButton(
                letter,
                callback_data=f"letter:{letter}"
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


def anime_for_letter(letter):

    result = []

    for anime_id, anime in ANIME_DATABASE.items():

        if anime["letter"] == letter:
            result.append(
                (anime_id, anime)
            )

    return result


def anime_list_menu(letter):

    keyboard = []

    for anime_id, anime in anime_for_letter(letter):

        keyboard.append([
            InlineKeyboardButton(
                f"🎬 {anime['title']}",
                callback_data=f"anime:{anime_id}"
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

    anime = ANIME_DATABASE.get(anime_id)

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

    keyboard = []

    for season_id, season in anime["seasons"].items():

        keyboard.append([
            InlineKeyboardButton(
                f"📺 {season_id} сезон • "
                f"{season['episodes']} серий",
                callback_data=(
                    f"season:{anime_id}:{season_id}"
                )
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⭐ Добавить в избранное",
            callback_data=f"favadd:{anime_id}"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data=f"letter:{anime['letter']}"
        )
    ])

    text = (
        f"<b>{anime['title']}</b>\n\n"
        f"🎬 Жанры: {anime['genres']}\n\n"
        "Выбери сезон:"
    )

    return (
        text,
        InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# КАРТОЧКА СЕЗОНА
# =========================================================

def season_card(anime_id, season_id):

    anime = ANIME_DATABASE.get(anime_id)

    if not anime:
        return None, None

    season = anime["seasons"].get(season_id)

    if not season:
        return None, None

    text = (
        f"<b>{season['title']}</b>\n\n"
        "🍿 Формат: Аниме сериал\n"
        f"⭐️ Рейтинг: {season['rating']}\n"
        f"📼 Год: {season['year']}\n"
        f"🎬 Жанры: {anime['genres']}\n"
        f"✅ Эпизодов (всего): {season['episodes']}\n"
        f"🕓 Длительность: {season['duration']}\n\n"
        "📝 <b>Описание:</b>\n"
        f"{season['description']}\n\n"
        "Выбери действие:"
    )

    keyboard = [

        [
            InlineKeyboardButton(
                "🎙 Выбрать озвучку",
                callback_data=(
                    f"dubs:{anime_id}:{season_id}"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "⭐ В избранное",
                callback_data=f"favadd:{anime_id}"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data=f"anime:{anime_id}"
            )
        ],
    ]

    return (
        text,
        InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# МЕНЮ ОЗВУЧЕК
# =========================================================

def dubs_menu(anime_id, season_id):

    episodes = ANIME_DATABASE[
        anime_id
    ]["seasons"][
        season_id
    ]["episodes"]

    keyboard = []

    for dub_id, dub_name in DUBS.items():

        keyboard.append([
            InlineKeyboardButton(
                f"💾 1-{episodes}  🎙 {dub_name}",
                callback_data=(
                    f"dub:{anime_id}:"
                    f"{season_id}:{dub_id}"
                )
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data=(
                f"season:{anime_id}:{season_id}"
            )
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# МЕНЮ СЕРИЙ
# =========================================================

def episodes_menu(
    anime_id,
    season_id,
    dub_id
):

    episodes = ANIME_DATABASE[
        anime_id
    ]["seasons"][
        season_id
    ]["episodes"]

    keyboard = []
    row = []

    for episode in range(1, episodes + 1):

        row.append(
            InlineKeyboardButton(
                f"🎞 {episode}",
                callback_data=(
                    f"episode:{anime_id}:"
                    f"{season_id}:{dub_id}:"
                    f"{episode}"
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
            callback_data=(
                f"dubs:{anime_id}:{season_id}"
            )
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# КАЧЕСТВО
# =========================================================

def quality_menu(
    anime_id,
    season_id,
    dub_id,
    episode
):

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "720p",
                callback_data=(
                    f"quality:{anime_id}:"
                    f"{season_id}:{dub_id}:"
                    f"{episode}:720"
                )
            ),

            InlineKeyboardButton(
                "1080p",
                callback_data=(
                    f"quality:{anime_id}:"
                    f"{season_id}:{dub_id}:"
                    f"{episode}:1080"
                )
            ),
        ],

        [
            InlineKeyboardButton(
                "⬅️ К сериям",
                callback_data=(
                    f"episodes:{anime_id}:"
                    f"{season_id}:{dub_id}"
                )
            )
        ],
    ])


# =========================================================
# ИЗБРАННОЕ
# =========================================================

STATUSES = {
    "watched": "✅ Смотрел",
    "planned": "📌 Планирую",
    "dropped": "❌ Брошено",
    "watching": "👀 Смотрю",
}


def get_favorites(user_id):

    uid = str(user_id)

    if uid not in DATA["favorites"]:
        DATA["favorites"][uid] = {}

    return DATA["favorites"][uid]


def favorite_status_menu(anime_id):

    keyboard = []

    for status, name in STATUSES.items():

        keyboard.append([
            InlineKeyboardButton(
                name,
                callback_data=(
                    f"status:{anime_id}:{status}"
                )
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data=f"anime:{anime_id}"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def favorites_menu():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "✅ Смотрел",
                callback_data="favlist:watched"
            ),
            InlineKeyboardButton(
                "📌 Планирую",
                callback_data="favlist:planned"
            ),
        ],

        [
            InlineKeyboardButton(
                "❌ Брошено",
                callback_data="favlist:dropped"
            ),
            InlineKeyboardButton(
                "👀 Смотрю",
                callback_data="favlist:watching"
            ),
        ],

        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="home"
            )
        ],
    ])
  # =========================================================
# /START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Сбрасываем режим поиска
    context.user_data["searching"] = False

    text = (
        "🎌 <b>AniFareX</b>\n\n"
        f"{greeting()}\n\n"
        "🍿 Добро пожаловать в каталог аниме!\n\n"
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

async def myid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        f"🆔 Твой Telegram ID:\n"
        f"{update.effective_user.id}"
    )


# =========================================================
# ИЗБРАННОЕ — ДОБАВЛЕНИЕ
# =========================================================

async def add_to_favorite(
    query,
    user_id,
    anime_id,
    status
):

    favorites = get_favorites(user_id)

    favorites[anime_id] = status

    save_data()

    anime = ANIME_DATABASE.get(anime_id)

    if not anime:
        return

    status_name = STATUSES.get(
        status,
        "⭐ Избранное"
    )

    await query.edit_message_text(
        f"⭐ <b>{anime['title']}</b>\n\n"
        f"Статус: {status_name}\n\n"
        "Аниме добавлено в избранное.",
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
                    callback_data=f"anime:{anime_id}"
                )
            ],

        ])
    )


# =========================================================
# ИЗБРАННОЕ — СПИСОК
# =========================================================

async def show_favorite_list(
    query,
    user_id,
    status
):

    favorites = get_favorites(user_id)

    result = []

    for anime_id, anime_status in favorites.items():

        if anime_status == status:

            anime = ANIME_DATABASE.get(
                anime_id
            )

            if anime:
                result.append(
                    (anime_id, anime)
                )

    status_name = STATUSES.get(
        status,
        "⭐ Избранное"
    )

    if not result:

        await query.edit_message_text(
            f"{status_name}\n\n"
            "Здесь пока ничего нет.",
            reply_markup=InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "⬅️ К избранному",
                        callback_data="favorites"
                    )
                ],

            ])
        )

        return

    keyboard = []

    for anime_id, anime in result:

        keyboard.append([

            InlineKeyboardButton(
                f"🎬 {anime['title']}",
                callback_data=f"anime:{anime_id}"
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ К избранному",
            callback_data="favorites"
        )

    ])

    await query.edit_message_text(
        f"<b>{status_name}</b>\n\n"
        "Выбери аниме:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# =========================================================
# ИСТОРИЯ ПРОСМОТРА
# =========================================================

def get_history(user_id):

    uid = str(user_id)

    if uid not in DATA["history"]:
        DATA["history"][uid] = []

    return DATA["history"][uid]


def add_history(
    user_id,
    anime_id,
    season_id,
    dub_id,
    episode
):

    history = get_history(user_id)

    item = {
        "anime_id": anime_id,
        "season_id": season_id,
        "dub_id": dub_id,
        "episode": episode,
    }

    # Удаляем старую запись этого аниме,
    # чтобы не было дубликатов
    history[:] = [
        x for x in history
        if not (
            x["anime_id"] == anime_id
            and x["season_id"] == season_id
            and x["dub_id"] == dub_id
        )
    ]

    history.insert(
        0,
        item
    )

    # Храним максимум 20 записей
    del history[20:]

    save_data()


# =========================================================
# ПРОДОЛЖИТЬ ПРОСМОТР
# =========================================================

def continue_menu(user_id):

    history = get_history(user_id)

    keyboard = []

    for item in history:

        anime = ANIME_DATABASE.get(
            item["anime_id"]
        )

        if not anime:
            continue

        season = anime["seasons"].get(
            item["season_id"]
        )

        if not season:
            continue

        dub_name = DUBS.get(
            item["dub_id"],
            item["dub_id"]
        )

        keyboard.append([

            InlineKeyboardButton(
                (
                    f"▶️ {anime['title']} — "
                    f"{item['season_id']} сезон, "
                    f"{item['episode']} серия "
                    f"({dub_name})"
                ),
                callback_data=(
                    f"continue:"
                    f"{item['anime_id']}:"
                    f"{item['season_id']}:"
                    f"{item['dub_id']}:"
                    f"{item['episode']}"
                )
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="home"
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )


# =========================================================
# ПОПУЛЯРНОЕ
# =========================================================

def popular_menu():

    keyboard = []

    # Пока рейтинг строится из данных каталога
    anime_list = []

    for anime_id, anime in ANIME_DATABASE.items():

        ratings = []

        for season in anime["seasons"].values():

            try:
                ratings.append(
                    float(season["rating"])
                )
            except ValueError:
                pass

        average = (
            sum(ratings) / len(ratings)
            if ratings
            else 0
        )

        anime_list.append(
            (
                anime_id,
                anime,
                average
            )
        )

    anime_list.sort(
        key=lambda x: x[2],
        reverse=True
    )

    for anime_id, anime, rating in anime_list:

        keyboard.append([

            InlineKeyboardButton(
                f"🔥 {anime['title']} • {rating:.2f}",
                callback_data=f"anime:{anime_id}"
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="home"
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )


# =========================================================
# НЕДАВНО ДОБАВЛЕННЫЕ
# =========================================================

def recent_menu():

    keyboard = []

    # Порядок можно менять:
    # первый элемент считается самым новым

    recent_ids = list(
        ANIME_DATABASE.keys()
    )[::-1]

    for anime_id in recent_ids:

        anime = ANIME_DATABASE.get(
            anime_id
        )

        if not anime:
            continue

        keyboard.append([

            InlineKeyboardButton(
                f"🆕 {anime['title']}",
                callback_data=f"anime:{anime_id}"
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="home"
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )


# =========================================================
# СЛУЧАЙНОЕ АНИМЕ
# =========================================================

def get_random_anime():

    if not ANIME_DATABASE:
        return None

    return random.choice(
        list(
            ANIME_DATABASE.keys()
        )
    )


# =========================================================
# ПОИСК
# =========================================================

def search_anime(text):

    text = text.lower().strip()

    result = []

    for anime_id, anime in ANIME_DATABASE.items():

        title = anime["title"].lower()

        if text in title:

            result.append(
                (anime_id, anime)
            )

    return result


# =========================================================
# ПОЛУЧЕНИЕ ВИДЕО
# =========================================================

def get_video(
    anime_id,
    season_id,
    dub_id,
    episode,
    quality
):

    videos = DATA.get(
        "videos",
        {}
    )

    anime_videos = videos.get(
        anime_id,
        {}
    )

    season_videos = anime_videos.get(
        season_id,
        {}
    )

    dub_videos = season_videos.get(
        dub_id,
        {}
    )

    episode_videos = dub_videos.get(
        str(episode),
        {}
    )

    return episode_videos.get(
        str(quality)
    )


# =========================================================
# СОХРАНЕНИЕ ВИДЕО
# =========================================================

def save_video(
    anime_id,
    season_id,
    dub_id,
    episode,
    quality,
    file_id
):

    if "videos" not in DATA:
        DATA["videos"] = {}

    DATA["videos"].setdefault(
        anime_id,
        {}
    )

    DATA["videos"][anime_id].setdefault(
        season_id,
        {}
    )

    DATA["videos"][anime_id][season_id].setdefault(
        dub_id,
        {}
    )

    DATA["videos"][anime_id][season_id][dub_id].setdefault(
        str(episode),
        {}
    )

    DATA["videos"][anime_id][season_id][dub_id][
        str(episode)
    ][str(quality)] = file_id

    save_data()


# =========================================================
# ОЖИДАЮЩИЕ ВИДЕО АДМИНА
# =========================================================

PENDING_VIDEOS = {}


# =========================================================
# ПОЛУЧЕНИЕ ВИДЕО ОТ АДМИНА
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

        "/set ANIME SEASON DUB EPISODE QUALITY\n\n"

        "Например:\n"

        "/set mythic_spirit 1 anilibria 1 720\n\n"

        "Доступные озвучки:\n"

        "🎙 anilibria\n"

        "🎙 dreamcast\n\n"

        "Доступное качество:\n"

        "⚙️ 720\n"

        "⚙️ 1080"

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
            "❌ У тебя нет прав."
        )

        return

    user_id = update.effective_user.id

    if user_id not in PENDING_VIDEOS:

        await update.message.reply_text(
            "❌ Сначала отправь мне видео."
        )

        return

    if len(context.args) != 5:

        await update.message.reply_text(

            "❌ Неверный формат.\n\n"

            "/set ANIME SEASON DUB EPISODE QUALITY\n\n"

            "Пример:\n"

            "/set mythic_spirit 1 anilibria 1 720"

        )

        return

    anime_id = context.args[0]
    season_id = context.args[1]
    dub_id = context.args[2]

    try:
        episode = int(
            context.args[3]
        )

        quality = int(
            context.args[4]
        )

    except ValueError:

        await update.message.reply_text(
            "❌ Серия и качество должны быть числами."
        )

        return

    if anime_id not in ANIME_DATABASE:

        await update.message.reply_text(
            "❌ Такое аниме не найдено."
        )

        return

    if season_id not in ANIME_DATABASE[
        anime_id
    ]["seasons"]:

        await update.message.reply_text(
            "❌ Такой сезон не найден."
        )

        return

    if dub_id not in DUBS:

        await update.message.reply_text(
            "❌ Неизвестная озвучка.\n\n"
            "Используй:\n"
            "anilibria\n"
            "dreamcast"
        )

        return

    max_episode = ANIME_DATABASE[
        anime_id
    ]["seasons"][
        season_id
    ]["episodes"]

    if episode < 1 or episode > max_episode:

        await update.message.reply_text(
            f"❌ Серия должна быть от 1 до {max_episode}."
        )

        return

    if quality not in [720, 1080]:

        await update.message.reply_text(
            "❌ Доступно только 720p или 1080p."
        )

        return

    file_id = PENDING_VIDEOS[user_id]

    save_video(
        anime_id,
        season_id,
        dub_id,
        episode,
        quality,
        file_id
    )

    del PENDING_VIDEOS[user_id]

    await update.message.reply_text(

        "✅ <b>Видео сохранено!</b>\n\n"

        f"🎬 {ANIME_DATABASE[anime_id]['title']}\n"
        f"📺 Сезон: {season_id}\n"
        f"🎙 Озвучка: {DUBS[dub_id]}\n"
        f"🎞 Серия: {episode}\n"
        f"⚙️ Качество: {quality}p",

        parse_mode="HTML"
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
            "❌ У тебя нет прав."
        )

        return

    videos = DATA.get(
        "videos",
        {}
    )

    if not videos:

        await update.message.reply_text(
            "📂 Видео пока не добавлены."
        )

        return

    text = "📂 <b>Добавленные видео</b>\n\n"

    for anime_id, seasons in videos.items():

        anime = ANIME_DATABASE.get(
            anime_id
        )

        title = (
            anime["title"]
            if anime
            else anime_id
        )

        text += f"🎬 <b>{title}</b>\n"

        for season_id, dubs in seasons.items():

            text += f"📺 {season_id} сезон\n"

            for dub_id, episodes in dubs.items():

                dub_name = DUBS.get(
                    dub_id,
                    dub_id
                )

                text += (
                    f"🎙 {dub_name}: "
                    f"{len(episodes)} серий\n"
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

    # =====================================================
    # ГЛАВНОЕ МЕНЮ
    # =====================================================

    if data == "home":

        context.user_data["searching"] = False

        await query.edit_message_text(
            f"🎌 <b>AniFareX</b>\n\n"
            f"{greeting()}\n\n"
            "🍿 Выбери нужный раздел:",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

        return

    # =====================================================
    # КАТАЛОГ
    # =====================================================

    if data == "catalog":

        await query.edit_message_text(
            "📚 <b>Каталог</b>\n\n"
            "Выбери первую букву названия:",
            parse_mode="HTML",
            reply_markup=catalog_menu()
        )

        return

    # =====================================================
    # БУКВА
    # =====================================================

    if data.startswith("letter:"):

        letter = data.split(":", 1)[1]

        anime_list = anime_for_letter(
            letter
        )

        if not anime_list:

            await query.edit_message_text(
                f"🔤 <b>Буква {letter}</b>\n\n"
                "Аниме на эту букву пока нет.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "⬅️ К буквам",
                            callback_data="catalog"
                        )
                    ]
                ])
            )

            return

        await query.edit_message_text(
            f"🔤 <b>Аниме на букву {letter}</b>\n\n"
            "Выбери аниме:",
            parse_mode="HTML",
            reply_markup=anime_list_menu(letter)
        )

        return

    # =====================================================
    # КАРТОЧКА АНИМЕ
    # =====================================================

    if data.startswith("anime:"):

        anime_id = data.split(":", 1)[1]

        text, keyboard = anime_card(
            anime_id
        )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

        return

    # =====================================================
    # СЕЗОН
    # =====================================================

    if data.startswith("season:"):

        parts = data.split(":")

        anime_id = parts[1]
        season_id = parts[2]

        text, keyboard = season_card(
            anime_id,
            season_id
        )

        if text is None:

            await query.answer(
                "❌ Сезон не найден.",
                show_alert=True
            )

            return

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

        return

    # =====================================================
    # ВЫБОР ОЗВУЧКИ
    # =====================================================

    if data.startswith("dubs:"):

        parts = data.split(":")

        anime_id = parts[1]
        season_id = parts[2]

        anime = ANIME_DATABASE.get(
            anime_id
        )

        if not anime:
            return

        season = anime["seasons"].get(
            season_id
        )

        if not season:
            return

        await query.edit_message_text(

            f"🎙 <b>{season['title']}</b>\n\n"
            "Выбери озвучку:\n\n"
            f"💾 1-{season['episodes']}  🎙 AniLibria\n"
            f"💾 1-{season['episodes']}  🎙 Dream Cast",

            parse_mode="HTML",

            reply_markup=dubs_menu(
                anime_id,
                season_id
            )
        )

        return

    # =====================================================
    # ВЫБРАННАЯ ОЗВУЧКА
    # =====================================================

    if data.startswith("dub:"):

        parts = data.split(":")

        anime_id = parts[1]
        season_id = parts[2]
        dub_id = parts[3]

        anime = ANIME_DATABASE.get(
            anime_id
        )

        if not anime:
            return

        season = anime["seasons"].get(
            season_id
        )

        if not season:
            return

        dub_name = DUBS.get(
            dub_id,
            dub_id
        )

        await query.edit_message_text(

            f"🎙 <b>{dub_name}</b>\n\n"
            f"🎬 {season['title']}\n\n"
            "Выбери серию:",

            parse_mode="HTML",

            reply_markup=episodes_menu(
                anime_id,
                season_id,
                dub_id
            )
        )

        return

    # =====================================================
    # СЕРИИ
    # =====================================================

    if data.startswith("episodes:"):

        parts = data.split(":")

        anime_id = parts[1]
        season_id = parts[2]
        dub_id = parts[3]

        anime = ANIME_DATABASE.get(
            anime_id
        )

        if not anime:
            return

        season = anime["seasons"].get(
            season_id
        )

        if not season:
            return

        await query.edit_message_text(

            f"🎙 <b>{DUBS.get(dub_id, dub_id)}</b>\n\n"
            f"📺 {season['title']}\n\n"
            "Выбери серию:",

            parse_mode="HTML",

            reply_markup=episodes_menu(
                anime_id,
                season_id,
                dub_id
            )
        )

        return

    # =====================================================
    # СЕРИЯ
    # =====================================================

    if data.startswith("episode:"):

        parts = data.split(":")

        anime_id = parts[1]
        season_id = parts[2]
        dub_id = parts[3]
        episode = int(parts[4])

        anime = ANIME_DATABASE.get(
            anime_id
        )

        if not anime:
            return

        season = anime["seasons"].get(
            season_id
        )

        if not season:
            return

        dub_name = DUBS.get(
            dub_id,
            dub_id
        )

        text = (

            f"🎞 <b>Серия {episode} "
            f"из {season['episodes']}</b>\n\n"

            f"🎬 {anime['title']}\n"
            f"📺 Сезон: {season_id}\n"
            f"🎙 Озвучка: {dub_name}\n\n"

            "⚙️ Выбери качество:"
        )

        await query.edit_message_text(

            text,

            parse_mode="HTML",

            reply_markup=quality_menu(
                anime_id,
                season_id,
                dub_id,
                episode
            )
        )

        return

    # =====================================================
    # КАЧЕСТВО
    # =====================================================

    if data.startswith("quality:"):

        parts = data.split(":")

        anime_id = parts[1]
        season_id = parts[2]
        dub_id = parts[3]
        episode = int(parts[4])
        quality = int(parts[5])

        video = get_video(
            anime_id,
            season_id,
            dub_id,
            episode,
            quality
        )

        if not video:

            await query.answer(

                f"❌ Серия в качестве "
                f"{quality}p пока не добавлена.",

                show_alert=True
            )

            return

        # Сохраняем просмотр
        add_history(
            query.from_user.id,
            anime_id,
            season_id,
            dub_id,
            episode
        )

        anime = ANIME_DATABASE.get(
            anime_id
        )

        dub_name = DUBS.get(
            dub_id,
            dub_id
        )

        await context.bot.send_video(

            chat_id=query.message.chat_id,

            video=video,

            caption=(

                f"🎬 <b>{anime['title']}</b>\n"
                f"📺 {season_id} сезон\n"
                f"🎞 Серия {episode}\n"
                f"🎙 {dub_name}\n"
                f"⚙️ {quality}p"

            ),

            parse_mode="HTML"
        )

        return

    # =====================================================
    # ДОБАВИТЬ В ИЗБРАННОЕ
    # =====================================================

    if data.startswith("favadd:"):

        anime_id = data.split(":", 1)[1]

        anime = ANIME_DATABASE.get(
            anime_id
        )

        if not anime:
            return

        await query.edit_message_text(

            f"⭐ <b>{anime['title']}</b>\n\n"
            "Куда добавить аниме?",

            parse_mode="HTML",

            reply_markup=favorite_status_menu(
                anime_id
            )
        )

        return

    # =====================================================
    # ВЫБОР СТАТУСА ИЗБРАННОГО
    # =====================================================

    if data.startswith("status:"):

        parts = data.split(":")

        anime_id = parts[1]
        status = parts[2]

        if status not in STATUSES:

            await query.answer(
                "❌ Неизвестный статус.",
                show_alert=True
            )

            return

        await add_to_favorite(

            query,

            query.from_user.id,

            anime_id,

            status
        )

        return

    # =====================================================
    # ИЗБРАННОЕ
    # =====================================================

    if data == "favorites":

        await query.edit_message_text(

            "⭐ <b>Избранное</b>\n\n"
            "Выбери категорию:",

            parse_mode="HTML",

            reply_markup=favorites_menu()
        )

        return

    # =====================================================
    # СПИСОК ИЗБРАННОГО
    # =====================================================

    if data.startswith("favlist:"):

        status = data.split(":", 1)[1]

        if status not in STATUSES:

            await query.answer(
                "❌ Неизвестный статус.",
                show_alert=True
            )

            return

        await show_favorite_list(

            query,

            query.from_user.id,

            status
        )

        return

    # =====================================================
    # ПРОДОЛЖИТЬ ПРОСМОТР
    # =====================================================

    if data == "continue":

        history = get_history(
            query.from_user.id
        )

        if not history:

            await query.edit_message_text(

                "▶️ <b>Продолжить просмотр</b>\n\n"
                "Ты пока ничего не смотрел.",

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            "📚 Каталог",
                            callback_data="catalog"
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

            return

        await query.edit_message_text(

            "▶️ <b>Продолжить просмотр</b>\n\n"
            "Выбери, что продолжить:",

            parse_mode="HTML",

            reply_markup=continue_menu(
                query.from_user.id
            )
        )

        return

    # =====================================================
    # ОТКРЫТЬ ПРОДОЛЖЕНИЕ
    # =====================================================

    if data.startswith("continue:"):

        parts = data.split(":")

        anime_id = parts[1]
        season_id = parts[2]
        dub_id = parts[3]
        episode = int(parts[4])

        anime = ANIME_DATABASE.get(
            anime_id
        )

        if not anime:
            return

        season = anime["seasons"].get(
            season_id
        )

        if not season:
            return

        await query.edit_message_text(

            f"▶️ <b>Продолжить просмотр</b>\n\n"

            f"🎬 {anime['title']}\n"
            f"📺 {season_id} сезон\n"
            f"🎙 {DUBS.get(dub_id, dub_id)}\n"
            f"🎞 Серия {episode}\n\n"

            "Выбери качество:",

            parse_mode="HTML",

            reply_markup=quality_menu(
                anime_id,
                season_id,
                dub_id,
                episode
            )
        )

        return

    # =====================================================
    # ПОПУЛЯРНОЕ
    # =====================================================

    if data == "popular":

        await query.edit_message_text(

            "🔥 <b>Популярное</b>\n\n"
            "Самые популярные аниме:",

            parse_mode="HTML",

            reply_markup=popular_menu()
        )

        return

    # =====================================================
    # НЕДАВНО ДОБАВЛЕННЫЕ
    # =====================================================

    if data == "recent":

        await query.edit_message_text(

            "🆕 <b>Недавно добавленные</b>\n\n"
            "Последние добавленные аниме:",

            parse_mode="HTML",

            reply_markup=recent_menu()
        )

        return

    # =====================================================
    # СЛУЧАЙНОЕ АНИМЕ
    # =====================================================

    if data == "random":

        anime_id = get_random_anime()

        if not anime_id:

            await query.answer(
                "❌ В каталоге пока нет аниме.",
                show_alert=True
            )

            return

        text, keyboard = anime_card(
            anime_id
        )

        await query.edit_message_text(

            "🎲 <b>Случайное аниме</b>\n\n"
            + text,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    # =====================================================
    # ПОИСК
    # =====================================================

    if data == "search":

        context.user_data["searching"] = True

        await query.edit_message_text(

            "🔎 <b>Поиск аниме</b>\n\n"
            "Напиши название аниме сообщением.\n\n"
            "Например:\n"
            "Мифический дух\n"
            "Наруто\n"
            "Блич",

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

        return

    # =====================================================
    # О БОТЕ
    # =====================================================

    if data == "about":

        await query.edit_message_text(

            "ℹ️ <b>AniFareX</b>\n\n"

            "🎌 Каталог аниме\n"
            "🔤 Каталог по буквам\n"
            "🔎 Поиск по названию\n"
            "⭐ Избранное\n"
            "👀 Статусы просмотра\n"
            "▶️ Продолжить просмотр\n"
            "🔥 Популярное\n"
            "🆕 Недавно добавленные\n"
            "🎲 Случайное аниме\n"
            "🎙 Несколько озвучек\n"
            "⚙️ 720p / 1080p\n\n"

            "🍿 Приятного просмотра!",

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

        return
      # =========================================================
# ТЕКСТОВЫЕ СООБЩЕНИЯ
# =========================================================

async def text_messages(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text

    if not text:
        return

    # -----------------------------------------------------
    # ПОИСК
    # -----------------------------------------------------

    if context.user_data.get("searching"):

        context.user_data["searching"] = False

        results = search_anime(text)

        if not results:

            await update.message.reply_text(

                "🔎 <b>Результаты поиска</b>\n\n"
                f"По запросу «{text}» ничего не найдено.",

                parse_mode="HTML",

                reply_markup=InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            "🔎 Новый поиск",
                            callback_data="search"
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

            return

        keyboard = []

        for anime_id, anime in results:

            keyboard.append([

                InlineKeyboardButton(
                    f"🎬 {anime['title']}",
                    callback_data=f"anime:{anime_id}"
                )

            ])

        keyboard.append([

            InlineKeyboardButton(
                "🔎 Новый поиск",
                callback_data="search"
            )

        ])

        keyboard.append([

            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="home"
            )

        ])

        await update.message.reply_text(

            "🔎 <b>Результаты поиска</b>\n\n"
            f"По запросу: «{text}»\n\n"
            "Выбери аниме:",

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return


# =========================================================
# /SAVE
# =========================================================

async def save_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ У тебя нет прав."
        )

        return

    save_data()

    await update.message.reply_text(
        "💾 <b>Данные сохранены.</b>",
        parse_mode="HTML"
    )


# =========================================================
# /STATS
# =========================================================

async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ У тебя нет прав."
        )

        return

    users = len(
        DATA.get("favorites", {})
    )

    anime_count = len(
        ANIME_DATABASE
    )

    videos = DATA.get(
        "videos",
        {}
    )

    video_count = 0

    for anime_data in videos.values():

        for season_data in anime_data.values():

            for dub_data in season_data.values():

                for episode_data in dub_data.values():

                    video_count += len(
                        episode_data
                    )

    history_count = 0

    for history in DATA.get(
        "history",
        {}
    ).values():

        history_count += len(
            history
        )

    await update.message.reply_text(

        "📊 <b>Статистика AniFareX</b>\n\n"

        f"👥 Пользователей: {users}\n"
        f"🎬 Аниме в каталоге: {anime_count}\n"
        f"🎞 Загруженных видео: {video_count}\n"
        f"▶️ Записей просмотра: {history_count}",

        parse_mode="HTML"
    )


# =========================================================
# /ADDANIME
# =========================================================

async def add_anime_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ У тебя нет прав."
        )

        return

    await update.message.reply_text(

        "🛠 <b>Добавление аниме</b>\n\n"

        "Каталог сейчас хранится прямо в коде.\n\n"

        "Чтобы добавить новый тайтл, "
        "добавь его в словарь ANIME_DATABASE.\n\n"

        "После изменения кода используй:\n"
        "/save",

        parse_mode="HTML"
    )


# =========================================================
# /ANIME_LIST
# =========================================================

async def anime_list_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ У тебя нет прав."
        )

        return

    if not ANIME_DATABASE:

        await update.message.reply_text(
            "📚 Каталог пуст."
        )

        return

    text = "📚 <b>Аниме в каталоге</b>\n\n"

    for anime_id, anime in ANIME_DATABASE.items():

        text += (
            f"🎬 <b>{anime['title']}</b>\n"
            f"🆔 {anime_id}\n"
            f"🔤 Буква: {anime['letter']}\n"
            f"📺 Сезонов: {len(anime['seasons'])}\n\n"
        )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


# =========================================================
# /VIDEOS
# =========================================================

async def videos_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ У тебя нет прав."
        )

        return

    videos = DATA.get(
        "videos",
        {}
    )

    if not videos:

        await update.message.reply_text(
            "📂 Видео пока не добавлены."
        )

        return

    text = "📂 <b>Добавленные видео</b>\n\n"

    for anime_id, seasons in videos.items():

        anime = ANIME_DATABASE.get(
            anime_id
        )

        title = (
            anime["title"]
            if anime
            else anime_id
        )

        text += f"🎬 <b>{title}</b>\n"

        for season_id, dubs in seasons.items():

            text += (
                f"📺 {season_id} сезон\n"
            )

            for dub_id, episodes in dubs.items():

                dub_name = DUBS.get(
                    dub_id,
                    dub_id
                )

                qualities_count = 0

                for episode_data in episodes.values():

                    qualities_count += len(
                        episode_data
                    )

                text += (
                    f"🎙 {dub_name}: "
                    f"{qualities_count} файлов\n"
                )

        text += "\n"

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


# =========================================================
# WEB SERVER ДЛЯ RENDER
# =========================================================

@app.route("/")
def web():

    return "AniFareX Bot is running!"


@app.route("/health")
def health():

    return {
        "status": "ok",
        "bot": "AniFareX"
    }


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
# ОБРАБОТКА ОШИБОК
# =========================================================

async def error_handler(
    update,
    context
):

    print(
        "Ошибка:",
        context.error
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

    # -----------------------------------------------------
    # ОБЫЧНЫЕ КОМАНДЫ
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # АДМИНСКИЕ КОМАНДЫ
    # -----------------------------------------------------

    bot.add_handler(
        CommandHandler(
            "set",
            set_video
        )
    )

    bot.add_handler(
        CommandHandler(
            "videos",
            videos_admin
        )
    )

    bot.add_handler(
        CommandHandler(
            "save",
            save_command
        )
    )

    bot.add_handler(
        CommandHandler(
            "stats",
            stats
        )
    )

    bot.add_handler(
        CommandHandler(
            "addanime",
            add_anime_command
        )
    )

    bot.add_handler(
        CommandHandler(
            "anime_list",
            anime_list_admin
        )
    )

    # -----------------------------------------------------
    # КНОПКИ
    # -----------------------------------------------------

    bot.add_handler(
        CallbackQueryHandler(
            buttons
        )
    )

    # -----------------------------------------------------
    # ПОЛУЧЕНИЕ ВИДЕО
    # -----------------------------------------------------

    bot.add_handler(
        MessageHandler(
            filters.VIDEO,
            receive_video
        )
    )

    # -----------------------------------------------------
    # ОБЫЧНЫЙ ТЕКСТ / ПОИСК
    # -----------------------------------------------------

    bot.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            text_messages
        )
    )

    # -----------------------------------------------------
    # ОШИБКИ
    # -----------------------------------------------------

    bot.add_error_handler(
        error_handler
    )

    # -----------------------------------------------------
    # WEB SERVER
    # -----------------------------------------------------

    threading.Thread(
        target=run_server,
        daemon=True
    ).start()

    print(
        "AniFareX запущен..."
    )

    # -----------------------------------------------------
    # TELEGRAM
    # -----------------------------------------------------

    bot.run_polling()


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()
