import os
import json
import random
import threading

from flask import Flask

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaVideo,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================================================
# НАСТРОЙКИ
# =========================================================

TOKEN = os.getenv("BOT_TOKEN", 8338656525:AAFRCZ-ZxIrgXU7GvZfjbkqL14z9jtb_wyE )

ADMIN_ID = 6502304303
)

DATA_FILE = "data.json"

app = Flask(__name__)


# =========================================================
# ПРИВЕТСТВИЯ AniFareX
# =========================================================

GREETINGS = [
    "Привет! Я AniFareX.",
    "Здарова! Что смотрим?",
    "Аниме? Погнали.",
    "Ну что, ищем?",
]


def get_greeting():
    return random.choice(GREETINGS)


# =========================================================
# ОЗВУЧКИ
# =========================================================

DUBS = {
    "anilibria": "AniLibria",
    "dreamcast": "Dream Cast",
}


# =========================================================
# СТАТУСЫ ИЗБРАННОГО
# =========================================================

STATUSES = {
    "watched": "👀 Смотрел",
    "planned": "📌 Планирую",
    "dropped": "❌ Брошено",
    "watching": "▶️ Смотрю",
}


# =========================================================
# БАЗА АНИМЕ
# =========================================================

ANIME_DATABASE = {

    "mythic_spirit": {

        "title": "Мифический дух: духовные хроники",

        "letter": "М",

        "seasons": {

            "1": {
                "title":
                    "Мифический дух: духовные хроники — 1 сезон",

                "format":
                    "Аниме сериал",

                "rating":
                    7.06,

                "year":
                    2021,

                "genres":
                    "гарем, исэкай, приключения, "
                    "реинкарнация, романтика, "
                    "фэнтези, экшен",

                "episodes":
                    12,

                "duration":
                    "23 мин./эп.",

                "description":
                    "20-летний студент Харуто Амакава "
                    "погибает в ДТП. Позже он приходит "
                    "в себя в незнакомом мире в теле "
                    "парня по имени Рио и становится "
                    "обладателем магических способностей.",
            },

            "2": {
                "title":
                    "Мифический дух: духовные хроники — 2 сезон",

                "format":
                    "Аниме сериал",

                "rating":
                    6.88,

                "year":
                    2024,

                "genres":
                    "гарем, исэкай, приключения, "
                    "реинкарнация, романтика, "
                    "фэнтези, экшен",

                "episodes":
                    12,

                "duration":
                    "23 мин./эп.",

                "description":
                    "После побега из столицы Бельтрама "
                    "Рио вместе с Селией и Аисией "
                    "спасает группу людей из Японии, "
                    "среди которых оказывается его "
                    "подруга детства Михару. Вместе "
                    "с союзниками он ищет остальных "
                    "переселенцев и способ вернуть "
                    "их домой, не забывая о главной "
                    "цели — отомстить за смерть матери.",
            },
        },
    },
}


# =========================================================
# ХРАНИЛИЩЕ
# =========================================================

DATA = {
    "favorites": {},
    "history": {},
    "videos": {},
    "recent": [],
}


def load_data():

    global DATA

    if not os.path.exists(DATA_FILE):
        return

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            loaded = json.load(f)

        if isinstance(loaded, dict):
            DATA.update(loaded)

    except Exception as e:

        print("Ошибка загрузки:", e)


def save_data():

    try:

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                DATA,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception as e:

        print("Ошибка сохранения:", e)


load_data()


# =========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================================================

def is_admin(update):

    return (
        update.effective_user
        and
        update.effective_user.id == ADMIN_ID
    )


def get_favorites(user_id):

    uid = str(user_id)

    DATA.setdefault(
        "favorites",
        {}
    )

    DATA["favorites"].setdefault(
        uid,
        {}
    )

    return DATA["favorites"][uid]


def get_history(user_id):

    uid = str(user_id)

    DATA.setdefault(
        "history",
        {}
    )

    DATA["history"].setdefault(
        uid,
        []
    )

    return DATA["history"][uid]


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
                "🔥 Популярное",
                callback_data="popular"
            ),
            InlineKeyboardButton(
                "🆕 Недавно добавленные",
                callback_data="recent"
            ),
        ],

        [
            InlineKeyboardButton(
                "🎲 Случайное аниме",
                callback_data="random"
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

LETTERS = list(
    "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
)


def catalog_menu():

    keyboard = []
    row = []

    for letter in LETTERS:

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
            "🏠 Главная",
            callback_data="home"
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )


def get_anime_by_letter(letter):

    result = []

    for anime_id, anime in ANIME_DATABASE.items():

        if anime["letter"] == letter:

            result.append(
                (anime_id, anime)
            )

    return result


def anime_list_menu(letter):

    result = get_anime_by_letter(
        letter
    )

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
            "⬅️ К буквам",
            callback_data="catalog"
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )


# =========================================================
# КАРТОЧКА АНИМЕ
# =========================================================

def anime_card(anime_id):

    anime = ANIME_DATABASE.get(
        anime_id
    )

    if not anime:

        return (
            "❌ Аниме не найдено.",
            InlineKeyboardMarkup([])
        )

    text = (
        f"🎬 <b>{anime['title']}</b>\n\n"
        "📺 <b>Сезоны:</b>\n\n"
    )

    keyboard = []

    for season_id, season in anime["seasons"].items():

        text += (
            f"⭐ {season['rating']}   "
            f"📼 {season['year']}   "
            f"🎞 {season['episodes']} серий\n"
            f"📺 {season_id} сезон\n\n"
        )

        keyboard.append([

            InlineKeyboardButton(
                f"📺 {season_id} сезон",
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
            callback_data="catalog"
        )

    ])

    return (
        text,
        InlineKeyboardMarkup(
            keyboard
        )
    )


# =========================================================
# КАРТОЧКА СЕЗОНА
# =========================================================

def season_card(
    anime_id,
    season_id
):

    anime = ANIME_DATABASE.get(
        anime_id
    )

    if not anime:
        return None, None

    season = anime["seasons"].get(
        season_id
    )

    if not season:
        return None, None

    text = (

        f"🎬 <b>{season['title']}</b>\n\n"

        f"🍿 Формат: {season['format']}\n"
        f"⭐ Рейтинг: {season['rating']}\n"
        f"📼 Год: {season['year']}\n"
        f"🎬 Жанры: {season['genres']}\n"
        f"✅ Эпизодов: {season['episodes']}\n"
        f"🕓 Длительность: {season['duration']}\n\n"

        "📝 <b>Описание:</b>\n"
        f"{season['description']}\n\n"

        "🎙 <b>Выберите озвучку:</b>"
    )

    keyboard = [

        [
            InlineKeyboardButton(
                f"💾 1-{season['episodes']}  🎙 AniLibria",
                callback_data=(
                    f"dub:{anime_id}:{season_id}:anilibria"
                )
            )
        ],

        [
            InlineKeyboardButton(
                f"💾 1-{season['episodes']}  🎙 Dream Cast",
                callback_data=(
                    f"dub:{anime_id}:{season_id}:dreamcast"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ К сезонам",
                callback_data=f"anime:{anime_id}"
            )
        ],

    ]

    return (
        text,
        InlineKeyboardMarkup(
            keyboard
        )
)
  # =========================================================
# СЕРИИ
# =========================================================

def episodes_menu(
    anime_id,
    season_id,
    dub_id
):

    season = ANIME_DATABASE[
        anime_id
    ][
        "seasons"
    ][
        season_id
    ]

    keyboard = []
    row = []

    for episode in range(
        1,
        season["episodes"] + 1
    ):

        row.append(

            InlineKeyboardButton(
                f"🎞 {episode}",
                callback_data=(
                    f"episode:"
                    f"{anime_id}:"
                    f"{season_id}:"
                    f"{dub_id}:"
                    f"{episode}"
                )
            )

        )

        if len(row) == 3:

            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ К озвучкам",
            callback_data=(
                f"season:"
                f"{anime_id}:"
                f"{season_id}"
            )
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )


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
                "▶️ 720p",
                callback_data=(
                    f"quality:"
                    f"{anime_id}:"
                    f"{season_id}:"
                    f"{dub_id}:"
                    f"{episode}:720"
                )
            ),

            InlineKeyboardButton(
                "▶️ 1080p",
                callback_data=(
                    f"quality:"
                    f"{anime_id}:"
                    f"{season_id}:"
                    f"{dub_id}:"
                    f"{episode}:1080"
                )
            ),
        ],

        [
            InlineKeyboardButton(
                "⬅️ К сериям",
                callback_data=(
                    f"dub:"
                    f"{anime_id}:"
                    f"{season_id}:"
                    f"{dub_id}"
                )
            )
        ],

    ])


# =========================================================
# ХРАНЕНИЕ FILE_ID
# =========================================================

def get_video(
    anime_id,
    season_id,
    dub_id,
    episode,
    quality
):

    return (

        DATA
        .get("videos", {})
        .get(anime_id, {})
        .get(season_id, {})
        .get(dub_id, {})
        .get(str(episode), {})
        .get(str(quality))

    )


def save_video(
    anime_id,
    season_id,
    dub_id,
    episode,
    quality,
    file_id
):

    DATA.setdefault(
        "videos",
        {}
    )

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

    DATA["videos"][
        anime_id
    ][
        season_id
    ][
        dub_id
    ][
        str(episode)
    ][
        str(quality)
    ] = file_id

    save_data()


# =========================================================
# ИСТОРИЯ ПРОСМОТРА
# =========================================================

def add_history(
    user_id,
    anime_id,
    season_id,
    dub_id,
    episode
):

    history = get_history(
        user_id
    )

    history[:] = [

        x for x in history

        if not (
            x["anime_id"] == anime_id
            and
            x["season_id"] == season_id
            and
            x["dub_id"] == dub_id
        )

    ]

    history.insert(
        0,
        {
            "anime_id":
                anime_id,

            "season_id":
                season_id,

            "dub_id":
                dub_id,

            "episode":
                episode,
        }
    )

    del history[20:]

    save_data()


# =========================================================
# КНОПКИ ВНУТРИ ВИДЕО
# =========================================================

def video_keyboard(
    anime_id,
    season_id,
    dub_id,
    episode,
    quality
):

    season = ANIME_DATABASE[
        anime_id
    ][
        "seasons"
    ][
        season_id
    ]

    navigation = []

    if episode > 1:

        navigation.append(

            InlineKeyboardButton(
                f"⏮ {episode - 1}",
                callback_data=(
                    f"watch:"
                    f"{anime_id}:"
                    f"{season_id}:"
                    f"{dub_id}:"
                    f"{episode - 1}:"
                    f"{quality}"
                )
            )

        )

    navigation.append(

        InlineKeyboardButton(
            f"🔽 {episode}",
            callback_data=(
                f"episodes:"
                f"{anime_id}:"
                f"{season_id}:"
                f"{dub_id}"
            )
        )

    )

    if episode < season["episodes"]:

        navigation.append(

            InlineKeyboardButton(
                f"{episode + 1} ⏭",
                callback_data=(
                    f"watch:"
                    f"{anime_id}:"
                    f"{season_id}:"
                    f"{dub_id}:"
                    f"{episode + 1}:"
                    f"{quality}"
                )
            )

        )

    keyboard = [
        navigation,

        [
            InlineKeyboardButton(
                (
                    "✅ 720p"
                    if quality == 720
                    else "720p"
                ),
                callback_data=(
                    f"watch:"
                    f"{anime_id}:"
                    f"{season_id}:"
                    f"{dub_id}:"
                    f"{episode}:720"
                )
            ),

            InlineKeyboardButton(
                (
                    "✅ 1080p"
                    if quality == 1080
                    else "1080p"
                ),
                callback_data=(
                    f"watch:"
                    f"{anime_id}:"
                    f"{season_id}:"
                    f"{dub_id}:"
                    f"{episode}:1080"
                )
            ),
        ],

        [
            InlineKeyboardButton(
                "⭐ Избранное",
                callback_data=f"favadd:{anime_id}"
            ),

            InlineKeyboardButton(
                "🎙 Озвучка",
                callback_data=(
                    f"dub:"
                    f"{anime_id}:"
                    f"{season_id}:"
                    f"{dub_id}"
                )
            ),
        ],

        [
            InlineKeyboardButton(
                "📺 Сезоны",
                callback_data=f"anime:{anime_id}"
            ),

            InlineKeyboardButton(
                "🏠 Главная",
                callback_data="home"
            ),
        ],
    ]

    return InlineKeyboardMarkup(
        keyboard
    )


# =========================================================
# ПОДПИСЬ ВИДЕО
# =========================================================

def video_caption(
    anime_id,
    season_id,
    dub_id,
    episode,
    quality
):

    anime = ANIME_DATABASE[
        anime_id
    ]

    season = anime[
        "seasons"
    ][
        season_id
    ]

    return (

        f"🎬 <b>{anime['title']}</b>\n\n"

        f"📺 {season_id} сезон • "
        f"Серия {episode} из {season['episodes']}\n"

        f"🎙 Озвучка: "
        f"{DUBS[dub_id]}\n"

        f"⚙️ Качество: {quality}p"

    )


# =========================================================
# ИЗБРАННОЕ
# =========================================================

def favorites_menu():

    keyboard = []

    for status, name in STATUSES.items():

        keyboard.append([

            InlineKeyboardButton(
                name,
                callback_data=f"favlist:{status}"
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


def status_menu(anime_id):

    keyboard = []

    for status, name in STATUSES.items():

        keyboard.append([

            InlineKeyboardButton(
                name,
                callback_data=(
                    f"status:"
                    f"{anime_id}:"
                    f"{status}"
                )
            )

        ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data=f"anime:{anime_id}"
        )

    ])

    return InlineKeyboardMarkup(
        keyboard
    )


# =========================================================
# ПРОДОЛЖИТЬ
# =========================================================

def continue_menu(user_id):

    keyboard = []

    for item in get_history(user_id):

        anime = ANIME_DATABASE.get(
            item["anime_id"]
        )

        if not anime:
            continue

        keyboard.append([

            InlineKeyboardButton(

                (
                    f"▶️ {anime['title']} — "
                    f"{item['season_id']} сезон, "
                    f"{item['episode']} серия"
                ),

                callback_data=(
                    f"resume:"
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

    items = []

    for anime_id, anime in ANIME_DATABASE.items():

        ratings = [

            s["rating"]

            for s in anime["seasons"].values()

        ]

        rating = (
            sum(ratings) / len(ratings)
            if ratings
            else 0
        )

        items.append(
            (
                anime_id,
                anime,
                rating
            )
        )

    items.sort(
        key=lambda x: x[2],
        reverse=True
    )

    keyboard = []

    for anime_id, anime, rating in items:

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

    recent = DATA.get(
        "recent",
        []
    )

    keyboard = []

    for anime_id in recent:

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

    # Если список пустой,
    # показываем имеющиеся аниме.

    if not keyboard:

        for anime_id, anime in ANIME_DATABASE.items():

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
# УДАЛЕНИЕ СТАРОГО СООБЩЕНИЯ
# =========================================================

async def replace_message(
    query,
    text,
    keyboard
):

    try:

        await query.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    except Exception:

        try:

            await query.message.delete()

            await query.message.chat.send_message(
                text,
                parse_mode="HTML",
                reply_markup=keyboard
            )

        except Exception as e:

            print(
                "Ошибка замены:",
                e
            )


# =========================================================
# ОТПРАВИТЬ ПЕРВОЕ ВИДЕО
# =========================================================

async def send_first_video(
    query,
    context,
    anime_id,
    season_id,
    dub_id,
    episode,
    quality
):

    video = get_video(
        anime_id,
        season_id,
        dub_id,
        episode,
        quality
    )

    if not video:

        await query.answer(
            f"❌ {quality}p ещё не добавлено.",
            show_alert=True
        )

        return

    add_history(
        query.from_user.id,
        anime_id,
        season_id,
        dub_id,
        episode
    )

    message = await context.bot.send_video(

        chat_id=query.message.chat_id,

        video=video,

        caption=video_caption(
            anime_id,
            season_id,
            dub_id,
            episode,
            quality
        ),

        parse_mode="HTML",

        reply_markup=video_keyboard(
            anime_id,
            season_id,
            dub_id,
            episode,
            quality
        )

    )

    # Удаляем меню выбора качества,
    # чтобы в чате осталось только видео.

    try:
        await query.message.delete()
    except Exception:
        pass


# =========================================================
# ГЛАВНОЕ ИЗМЕНЕНИЕ:
# МЕНЯЕМ ВИДЕО В ТОМ ЖЕ СООБЩЕНИИ
# =========================================================

async def edit_video(
    query,
    anime_id,
    season_id,
    dub_id,
    episode,
    quality
):

    video = get_video(
        anime_id,
        season_id,
        dub_id,
        episode,
        quality
    )

    if not video:

        await query.answer(
            f"❌ {quality}p для этой серии "
            "ещё не добавлено.",
            show_alert=True
        )

        return

    add_history(
        query.from_user.id,
        anime_id,
        season_id,
        dub_id,
        episode
    )

    media = InputMediaVideo(

        media=video,

        caption=video_caption(
            anime_id,
            season_id,
            dub_id,
            episode,
            quality
        ),

        parse_mode="HTML"

    )

    try:

        await query.message.edit_media(

            media=media,

            reply_markup=video_keyboard(
                anime_id,
                season_id,
                dub_id,
                episode,
                quality
            )

        )

    except Exception as e:

        print(
            "Ошибка edit_media:",
            e
        )

        await query.answer(
            "❌ Не удалось переключить видео.",
            show_alert=True
        )


# =========================================================
# КНОПКИ
# =========================================================

async def button_handler(
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

        await replace_message(

            query,

            (
                "🎌 <b>AniFareX</b>\n\n"
                f"«{get_greeting()}»\n\n"
                "🍿 Выбери нужный раздел:"
            ),

            main_menu()

        )

        return


    # =====================================================
    # КАТАЛОГ
    # =====================================================

    if data == "catalog":

        await replace_message(

            query,

            (
                "📚 <b>Каталог</b>\n\n"
                "Выбери букву:"
            ),

            catalog_menu()

        )

        return


    # =====================================================
    # БУКВА
    # =====================================================

    if data.startswith("letter:"):

        letter = data.split(
            ":",
            1
        )[1]

        anime_list = get_anime_by_letter(
            letter
        )

        if not anime_list:

            await replace_message(

                query,

                (
                    f"🔤 <b>{letter}</b>\n\n"
                    "Аниме пока нет."
                ),

                InlineKeyboardMarkup([

                    [
                        InlineKeyboardButton(
                            "⬅️ К буквам",
                            callback_data="catalog"
                        )
                    ]

                ])

            )

            return

        await replace_message(

            query,

            (
                f"🔤 <b>Аниме на букву {letter}</b>\n\n"
                "Выбери:"
            ),

            anime_list_menu(letter)

        )

        return


    # =====================================================
    # АНИМЕ
    # =====================================================

    if data.startswith("anime:"):

        anime_id = data.split(
            ":",
            1
        )[1]

        text, keyboard = anime_card(
            anime_id
        )

        await replace_message(
            query,
            text,
            keyboard
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

        await replace_message(
            query,
            text,
            keyboard
        )

        return


    # =====================================================
    # ОЗВУЧКА
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

        await replace_message(

            query,

            (
                f"🎙 <b>{DUBS[dub_id]}</b>\n\n"
                f"🎬 {season['title']}\n\n"
                "Выбери серию:"
            ),

            episodes_menu(
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

        season = ANIME_DATABASE[
            anime_id
        ][
            "seasons"
        ][
            season_id
        ]

        await replace_message(

            query,

            (
                f"🎬 <b>{season['title']}</b>\n\n"
                f"🎞 Серия {episode} "
                f"из {season['episodes']}\n"
                f"🎙 {DUBS[dub_id]}\n\n"
                "⚙️ Выбери качество:"
            ),

            quality_menu(
                anime_id,
                season_id,
                dub_id,
                episode
            )

        )

        return


    # =====================================================
    # ПЕРВОЕ ВИДЕО
    # =====================================================

    if data.startswith("quality:"):

        parts = data.split(":")

        anime_id = parts[1]
        season_id = parts[2]
        dub_id = parts[3]
        episode = int(parts[4])
        quality = int(parts[5])

        await send_first_video(

            query,
            context,

            anime_id,
            season_id,
            dub_id,
            episode,
            quality

        )

        return


    # =====================================================
    # ПЕРЕКЛЮЧЕНИЕ ВИДЕО
    # =====================================================

    if data.startswith("watch:"):

        parts = data.split(":")

        anime_id = parts[1]
        season_id = parts[2]
        dub_id = parts[3]
        episode = int(parts[4])
        quality = int(parts[5])

        await edit_video(

            query,

            anime_id,
            season_id,
            dub_id,
            episode,
            quality

        )

        return


    # =====================================================
    # СПИСОК СЕРИЙ ИЗ ВИДЕО
    # =====================================================

    if data.startswith("episodes:"):

        parts = data.split(":")

        anime_id = parts[1]
        season_id = parts[2]
        dub_id = parts[3]

        await replace_message(

            query,

            (
                f"🎙 <b>{DUBS[dub_id]}</b>\n\n"
                "Выбери серию:"
            ),

            episodes_menu(
                anime_id,
                season_id,
                dub_id
            )

        )

        return


    # =====================================================
    # ИЗБРАННОЕ
    # =====================================================

    if data == "favorites":

        await replace_message(

            query,

            (
                "⭐ <b>Избранное</b>\n\n"
                "Выбери категорию:"
            ),

            favorites_menu()

        )

        return


    # =====================================================
    # ДОБАВИТЬ В ИЗБРАННОЕ
    # =====================================================

    if data.startswith("favadd:"):

        anime_id = data.split(
            ":",
            1
        )[1]

        anime = ANIME_DATABASE.get(
            anime_id
        )

        if not anime:
            return

        await replace_message(

            query,

            (
                f"⭐ <b>{anime['title']}</b>\n\n"
                "Выбери статус:"
            ),

            status_menu(
                anime_id
            )

        )

        return


    # =====================================================
    # СТАТУС
    # =====================================================

    if data.startswith("status:"):

        parts = data.split(":")

        anime_id = parts[1]
        status = parts[2]

        favorites = get_favorites(
            query.from_user.id
        )

        favorites[anime_id] = status

        save_data()

        await replace_message(

            query,

            (
                "✅ <b>Добавлено!</b>\n\n"
                f"🎬 {ANIME_DATABASE[anime_id]['title']}\n"
                f"📌 Статус: {STATUSES[status]}"
            ),

            InlineKeyboardMarkup([

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
                ]

            ])

        )

        return
          # =====================================================
    # СПИСОК ИЗБРАННОГО
    # =====================================================

    if data.startswith("favlist:"):

        status = data.split(
            ":",
            1
        )[1]

        favorites = get_favorites(
            query.from_user.id
        )

        keyboard = []

        for anime_id, saved_status in favorites.items():

            if saved_status != status:
                continue

            anime = ANIME_DATABASE.get(
                anime_id
            )

            if not anime:
                continue

            keyboard.append([

                InlineKeyboardButton(
                    f"🎬 {anime['title']}",
                    callback_data=f"anime:{anime_id}"
                )

            ])

        if not keyboard:

            text = (

                f"{STATUSES[status]}\n\n"
                "Здесь пока ничего нет."

            )

        else:

            text = (

                f"<b>{STATUSES[status]}</b>\n\n"
                "Выбери аниме:"

            )

        keyboard.append([

            InlineKeyboardButton(
                "⬅️ К избранному",
                callback_data="favorites"
            )

        ])

        await replace_message(

            query,

            text,

            InlineKeyboardMarkup(
                keyboard
            )

        )

        return


    # =====================================================
    # ПРОДОЛЖИТЬ
    # =====================================================

    if data == "continue":

        history = get_history(
            query.from_user.id
        )

        if not history:

            await replace_message(

                query,

                (
                    "▶️ <b>Продолжить просмотр</b>\n\n"
                    "История пока пустая."
                ),

                InlineKeyboardMarkup([

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

        await replace_message(

            query,

            (
                "▶️ <b>Продолжить просмотр</b>\n\n"
                "Выбери:"
            ),

            continue_menu(
                query.from_user.id
            )

        )

        return


    # =====================================================
    # ВОЗОБНОВИТЬ
    # =====================================================

    if data.startswith("resume:"):

        parts = data.split(":")

        anime_id = parts[1]
        season_id = parts[2]
        dub_id = parts[3]
        episode = int(parts[4])

        quality = 720

        if not get_video(
            anime_id,
            season_id,
            dub_id,
            episode,
            quality
        ):

            quality = 1080

        if not get_video(
            anime_id,
            season_id,
            dub_id,
            episode,
            quality
        ):

            await query.answer(
                "❌ Видео этой серии нет.",
                show_alert=True
            )

            return

        await send_first_video(

            query,
            context,

            anime_id,
            season_id,
            dub_id,
            episode,
            quality

        )

        return


    # =====================================================
    # ПОПУЛЯРНОЕ
    # =====================================================

    if data == "popular":

        await replace_message(

            query,

            (
                "🔥 <b>Популярное</b>\n\n"
                "Выбери аниме:"
            ),

            popular_menu()

        )

        return


    # =====================================================
    # НЕДАВНО ДОБАВЛЕННЫЕ
    # =====================================================

    if data == "recent":

        await replace_message(

            query,

            (
                "🆕 <b>Недавно добавленные</b>\n\n"
                "Выбери аниме:"
            ),

            recent_menu()

        )

        return


    # =====================================================
    # СЛУЧАЙНОЕ
    # =====================================================

    if data == "random":

        if not ANIME_DATABASE:

            await query.answer(
                "Каталог пуст.",
                show_alert=True
            )

            return

        anime_id = random.choice(
            list(
                ANIME_DATABASE.keys()
            )
        )

        text, keyboard = anime_card(
            anime_id
        )

        await replace_message(

            query,

            "🎲 <b>Случайное аниме</b>\n\n"
            + text,

            keyboard

        )

        return


    # =====================================================
    # ПОИСК
    # =====================================================

    if data == "search":

        context.user_data[
            "searching"
        ] = True

        await replace_message(

            query,

            (
                "🔎 <b>Поиск</b>\n\n"
                "Напиши название аниме."
            ),

            InlineKeyboardMarkup([

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

        await replace_message(

            query,

            (
                "ℹ️ <b>AniFareX</b>\n\n"

                "📚 Каталог\n"
                "🔎 Поиск\n"
                "⭐ Избранное\n"
                "👀 Статусы просмотра\n"
                "▶️ Продолжить\n"
                "🔥 Популярное\n"
                "🆕 Недавно добавленные\n"
                "🎲 Случайное аниме\n"
                "🎙 Несколько озвучек\n"
                "⚙️ 720p / 1080p\n\n"

                "🍿 Приятного просмотра!"
            ),

            InlineKeyboardMarkup([

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
# START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data[
        "searching"
    ] = False

    await update.message.reply_text(

        (
            "🎌 <b>AniFareX</b>\n\n"
            f"«{get_greeting()}»\n\n"
            "🍿 Добро пожаловать!\n\n"
            "Выбери раздел:"
        ),

        parse_mode="HTML",

        reply_markup=main_menu()

    )


# =========================================================
# ПОИСК
# =========================================================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text

    if not context.user_data.get(
        "searching"
    ):
        return

    context.user_data[
        "searching"
    ] = False

    text_lower = text.lower()

    results = []

    for anime_id, anime in ANIME_DATABASE.items():

        if text_lower in anime["title"].lower():

            results.append(
                (anime_id, anime)
            )

    if not results:

        await update.message.reply_text(

            (
                "🔎 <b>Ничего не найдено</b>\n\n"
                f"По запросу «{text}» "
                "ничего нет."
            ),

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
                        "🏠 Главная",
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
            "🏠 Главная",
            callback_data="home"
        )

    ])

    await update.message.reply_text(

        (
            "🔎 <b>Результаты поиска</b>\n\n"
            f"Запрос: «{text}»"
        ),

        parse_mode="HTML",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )

    )


# =========================================================
# АДМИН: ПОЛУЧИТЬ ВИДЕО
# =========================================================

PENDING_VIDEO = {}


async def receive_video(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ Нет доступа."
        )

        return

    video = update.message.video

    if not video:
        return

    PENDING_VIDEO[
        update.effective_user.id
    ] = video.file_id

    await update.message.reply_text(

        (
            "✅ Видео получено!\n\n"

            "Теперь отправь команду:\n\n"

            "/set mythic_spirit 1 anilibria 1 720\n\n"

            "Где:\n"
            "1 — сезон\n"
            "anilibria — озвучка\n"
            "1 — серия\n"
            "720 — качество\n\n"

            "Для 1080p:\n"
            "/set mythic_spirit 1 anilibria 1 1080"
        )

    )


# =========================================================
# АДМИН: СОХРАНИТЬ ВИДЕО
# =========================================================

async def set_video(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ Нет доступа."
        )

        return

    user_id = update.effective_user.id

    if user_id not in PENDING_VIDEO:

        await update.message.reply_text(
            "❌ Сначала отправь видео."
        )

        return

    if len(context.args) != 5:

        await update.message.reply_text(

            (
                "❌ Формат:\n\n"
                "/set ANIME SEASON DUB EPISODE QUALITY\n\n"
                "Пример:\n"
                "/set mythic_spirit 1 anilibria 1 720"
            )

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
            "❌ Аниме не найдено."
        )

        return

    if season_id not in ANIME_DATABASE[
        anime_id
    ][
        "seasons"
    ]:

        await update.message.reply_text(
            "❌ Сезон не найден."
        )

        return

    if dub_id not in DUBS:

        await update.message.reply_text(
            "❌ Неизвестная озвучка."
        )

        return

    if quality not in [
        720,
        1080
    ]:

        await update.message.reply_text(
            "❌ Используй только 720 или 1080."
        )

        return

    max_episode = ANIME_DATABASE[
        anime_id
    ][
        "seasons"
    ][
        season_id
    ][
        "episodes"
    ]

    if episode < 1 or episode > max_episode:

        await update.message.reply_text(

            f"❌ Серия должна быть "
            f"от 1 до {max_episode}."

        )

        return

    file_id = PENDING_VIDEO[
        user_id
    ]

    save_video(

        anime_id,
        season_id,
        dub_id,
        episode,
        quality,
        file_id

    )

    # Добавляем в недавно добавленные.

    recent = DATA.setdefault(
        "recent",
        []
    )

    if anime_id in recent:

        recent.remove(
            anime_id
        )

    recent.insert(
        0,
        anime_id
    )

    del recent[20:]

    save_data()

    del PENDING_VIDEO[
        user_id
    ]

    await update.message.reply_text(

        (
            "✅ <b>Сохранено!</b>\n\n"
            f"🎬 {ANIME_DATABASE[anime_id]['title']}\n"
            f"📺 {season_id} сезон\n"
            f"🎙 {DUBS[dub_id]}\n"
            f"🎞 Серия {episode}\n"
            f"⚙️ {quality}p"
        ),

        parse_mode="HTML"

    )


# =========================================================
# АДМИН: УДАЛИТЬ ВИДЕО
# =========================================================

async def delete_video(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):

        await update.message.reply_text(
            "❌ Нет доступа."
        )

        return

    if len(context.args) != 5:

        await update.message.reply_text(

            (
                "Формат:\n"
                "/delete mythic_spirit 1 anilibria 1 720"
            )

        )

        return

    anime_id = context.args[0]
    season_id = context.args[1]
    dub_id = context.args[2]
    episode = context.args[3]
    quality = context.args[4]

    try:

        del DATA[
            "videos"
        ][
            anime_id
        ][
            season_id
        ][
            dub_id
        ][
            episode
        ][
            quality
        ]

        save_data()

        await update.message.reply_text(
            "🗑 Видео удалено."
        )

    except Exception:

        await update.message.reply_text(
            "❌ Такое видео не найдено."
        )


# =========================================================
# СОХРАНИТЬ
# =========================================================

async def save_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not is_admin(update):
        return

    save_data()

    await update.message.reply_text(
        "💾 Всё сохранено."
    )


# =========================================================
# WEB SERVER
# =========================================================

@app.route("/")
def index():

    return "AniFareX is running!"


@app.route("/health")
def health():

    return {
        "status": "ok"
    }


def run_web():

    port = int(
        os.getenv(
            "PORT",
            "10000"
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

    application = (

        Application
        .builder()
        .token(TOKEN)
        .build()

    )

    application.add_handler(

        CommandHandler(
            "start",
            start
        )

    )

    application.add_handler(

        CommandHandler(
            "set",
            set_video
        )

    )

    application.add_handler(

        CommandHandler(
            "delete",
            delete_video
        )

    )

    application.add_handler(

        CommandHandler(
            "save",
            save_command
        )

    )

    application.add_handler(

        CallbackQueryHandler(
            button_handler
        )

    )

    application.add_handler(

        MessageHandler(
            filters.VIDEO,
            receive_video
        )

    )

    application.add_handler(

        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            text_handler
        )

    )

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    print(
        "AniFareX запущен!"
    )

    application.run_polling()


if __name__ == "__main__":

    main()
  
