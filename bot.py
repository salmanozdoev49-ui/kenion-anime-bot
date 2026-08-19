import os
import threading

from flask import Flask

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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

TOKEN = os.environ["BOT_TOKEN"]

# Твой Telegram ID
ADMIN_ID = 6502304303

app = Flask(__name__)


# =========================================================
# ДАННЫЕ АНИМЕ
# =========================================================

ANIME = {

    "mythic_spirit": {

        "title": "🧙‍♂️ Мифический дух: духовные хроники",

        "search_title": "Мифический дух: духовные хроники",

        "letter": "М",

        "rating": "7.06",

        "year": "2021",

        "format": "Аниме сериал",

        "genres": (
            "гарем, исэкай, приключения, "
            "реинкарнация, романтика, фэнтези, экшен"
        ),

        "description": (
            "20-летний студент Харуто Амакава погибает в ДТП. "
            "Позже он приходит в себя в незнакомом мире "
            "в теле парня по имени Рио и становится "
            "обладателем магических способностей."
        ),

        "seasons": {

            1: {

                "title":
                    "Мифический дух: духовные хроники — 1 сезон",

                "year": "2021",

                "rating": "7.06",

                "episodes": 12,

                "duration": "23 мин./эп.",

                "description": (
                    "20-летний студент Харуто Амакава погибает "
                    "в ДТП. Позже он приходит в себя в незнакомом "
                    "мире в теле парня по имени Рио и становится "
                    "обладателем магических способностей."
                ),
            },

            2: {

                "title":
                    "Мифический дух: духовные хроники — 2 сезон",

                "year": "2024",

                "rating": "6.88",

                "episodes": 12,

                "duration": "23 мин./эп.",

                "description": (
                    "После побега из столицы Бельтрама Рио вместе "
                    "с Селией и Аисией спасает группу людей из Японии, "
                    "среди которых оказывается его подруга детства "
                    "Михару. Вместе с союзниками он ищет остальных "
                    "переселенцев и способ вернуть их домой, не "
                    "забывая о главной цели — отомстить за смерть матери."
                ),
            },
        },
    }
}


# =========================================================
# НАЗВАНИЯ СЕРИЙ
# =========================================================

EPISODES = {

    1: {
        1: "Перерождение",
        2: "Королевская академия",
        3: "Столкновение",
        4: "Лес духов",
        5: "Путешествие",
        6: "Новая встреча",
        7: "Предназначение",
        8: "Сражение",
        9: "Возвращение",
        10: "Духовный мир",
        11: "Решение",
        12: "Новая жизнь",
    },

    2: {
        1: "Новая встреча",
        2: "Путешествие продолжается",
        3: "Группа из Японии",
        4: "Михару",
        5: "Союзники",
        6: "След переселенцев",
        7: "Новые враги",
        8: "Сражение",
        9: "Тайна прошлого",
        10: "Обещание",
        11: "Решающий бой",
        12: "Новая цель",
    }
}


# =========================================================
# ВИДЕО
#
# VIDEO_FILES:
#
# {
#   "mythic_spirit": {
#       1: {
#           1: {
#               "720": {
#                   "anilibria": "file_id"
#               }
#           }
#       }
#   }
# }
# =========================================================

VIDEO_FILES = {}


# Последнее отправленное админом видео
PENDING_VIDEOS = {}


# =========================================================
# ПОЛЬЗОВАТЕЛИ
# =========================================================

# Избранное пользователей
USER_FAVORITES = {}

# Последняя просмотренная серия
USER_CONTINUE = {}

# Поисковый режим
SEARCH_USERS = set()


# =========================================================
# ПРОВЕРКА АДМИНА
# =========================================================

def is_admin(update: Update):

    return (
        update.effective_user
        and update.effective_user.id == ADMIN_ID
    )


# =========================================================
# ПОЛУЧЕНИЕ ИЗБРАННОГО
# =========================================================

def get_user_favorites(user_id):

    if user_id not in USER_FAVORITES:

        USER_FAVORITES[user_id] = {

            "watched": [],
            "planned": [],
            "dropped": [],
            "watching": [],
        }

    return USER_FAVORITES[user_id]


# =========================================================
# ПРИВЕТСТВИЕ
# =========================================================

def greeting():

    return (
        "👋 <b>AniFareX</b>\n\n"
        "«Здарова! Что смотрим?»"
    )


# =========================================================
# ГЛАВНОЕ МЕНЮ
# =========================================================

def main_menu():

    keyboard = [

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
            )
        ],

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
                "ℹ️ О боте",
                callback_data="about"
            ),
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

    await update.message.reply_text(

        greeting() +

        "\n\n"
        "🎌 Добро пожаловать в каталог аниме!\n\n"
        "Выбери нужный раздел:",

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

        "🆔 <b>Твой Telegram ID:</b>\n\n"
        f"<code>{update.effective_user.id}</code>",

        parse_mode="HTML"
    )


# =========================================================
# АЛФАВИТ
# =========================================================

def alphabet_menu():

    letters = list(
        "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    )

    keyboard = []

    row = []

    for letter in letters:

        row.append(

            InlineKeyboardButton(
                letter,
                callback_data=f"letter_{letter}"
            )
        )

        if len(row) == 6:

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
# МЕНЮ СЕЗОНОВ
# =========================================================

def seasons_menu():

    keyboard = [

        [
            InlineKeyboardButton(
                "📺 1 сезон • 12 серий",
                callback_data="season_1"
            )
        ],

        [
            InlineKeyboardButton(
                "📺 2 сезон • 12 серий",
                callback_data="season_2"
            )
        ],

        [
            InlineKeyboardButton(
                "⭐ Добавить в избранное",
                callback_data="favorite_menu"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="letter_М"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# КАРТОЧКА СЕЗОНА
# =========================================================

def season_card(season):

    info = ANIME["mythic_spirit"]["seasons"][season]

    text = (

        f"<b>{info['title']}</b>\n\n"

        f"🍿 Формат: Аниме сериал\n"
        f"⭐️ Рейтинг: {info['rating']}\n"
        f"📼 Год: {info['year']}\n"

        "🎬 Жанры: гарем, исэкай, приключения, "
        "реинкарнация, романтика, фэнтези, экшен\n"

        f"✅ Эпизодов (всего): {info['episodes']}\n"
        f"🕓 Длительность: {info['duration']}\n\n"

        "📝 <b>Описание:</b>\n"
        f"{info['description']}\n\n"

        "Выбери действие:"
    )

    keyboard = [

        [
            InlineKeyboardButton(
                "🎞 Серии",
                callback_data=f"episodes_{season}"
            )
        ],

        [
            InlineKeyboardButton(
                "⭐ Добавить в избранное",
                callback_data="favorite_menu"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ К сезонам",
                callback_data="anime"
            )
        ],
    ]

    return text, InlineKeyboardMarkup(keyboard)


# =========================================================
# МЕНЮ СЕРИЙ
# =========================================================

def episodes_menu(season):

    keyboard = []

    row = []

    for episode in range(1, 13):

        row.append(

            InlineKeyboardButton(
                f"🎞 {episode}",
                callback_data=f"episode_{season}_{episode}"
            )
        )

        if len(row) == 3:

            keyboard.append(row)

            row = []

    if row:
        keyboard.append(row)

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data=f"season_{season}"
        )

    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# МЕНЮ ОЗВУЧКИ
# =========================================================

def voice_menu(season, episode):

    keyboard = [

        [
            InlineKeyboardButton(
                "💾 1-12  🎙 AniLibria",
                callback_data=(
                    f"voice_{season}_{episode}_anilibria"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "💾 1-12  🎙 Dream Cast",
                callback_data=(
                    f"voice_{season}_{episode}_dreamcast"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ К сериям",
                callback_data=f"episodes_{season}"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# МЕНЮ КАЧЕСТВА
# =========================================================

def quality_menu(
    season,
    episode,
    voice
):

    keyboard = [

        [
            InlineKeyboardButton(
                "720p",
                callback_data=(
                    f"quality_{season}_{episode}_"
                    f"{voice}_720"
                )
            ),

            InlineKeyboardButton(
                "1080p",
                callback_data=(
                    f"quality_{season}_{episode}_"
                    f"{voice}_1080"
                )
            ),
        ],

        [
            InlineKeyboardButton(
                "⬅️ К озвучкам",
                callback_data=(
                    f"episode_{season}_{episode}"
                )
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# МЕНЮ ИЗБРАННОГО
# =========================================================

def favorites_menu():

    keyboard = [

        [
            InlineKeyboardButton(
                "👀 Смотрел",
                callback_data="fav_watched"
            ),

            InlineKeyboardButton(
                "📌 Планирую",
                callback_data="fav_planned"
            ),
        ],

        [
            InlineKeyboardButton(
                "❌ Брошено",
                callback_data="fav_dropped"
            ),

            InlineKeyboardButton(
                "▶️ Смотрю",
                callback_data="fav_watching"
            ),
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
# МЕНЮ ДОБАВЛЕНИЯ В ИЗБРАННОЕ
# =========================================================

def favorite_status_menu():

    keyboard = [

        [
            InlineKeyboardButton(
                "👀 Смотрел",
                callback_data="addfav_watched"
            )
        ],

        [
            InlineKeyboardButton(
                "📌 Планирую",
                callback_data="addfav_planned"
            )
        ],

        [
            InlineKeyboardButton(
                "❌ Брошено",
                callback_data="addfav_dropped"
            )
        ],

        [
            InlineKeyboardButton(
                "▶️ Смотрю",
                callback_data="addfav_watching"
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
# ПОЛУЧЕНИЕ НАЗВАНИЯ КАТЕГОРИИ
# =========================================================

def status_name(status):

    names = {

        "watched":
            "👀 Смотрел",

        "planned":
            "📌 Планирую",

        "dropped":
            "❌ Брошено",

        "watching":
            "▶️ Смотрю",
    }

    return names.get(
        status,
        status
    )


# =========================================================
# ПРОДОЛЖИТЬ
# =========================================================

def continue_menu(user_id):

    if user_id not in USER_CONTINUE:

        return InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "⬅️ Назад",
                    callback_data="home"
                )
            ]

        ])

    item = USER_CONTINUE[user_id]

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "▶️ Продолжить просмотр",
                callback_data=(
                    f"episode_{item['season']}_"
                    f"{item['episode']}"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="home"
            )
        ]

    ])


# =========================================================
# ПОИСК
# =========================================================

def search_results(query_text):

    query_text = query_text.lower().strip()

    results = []

    for anime_id, anime in ANIME.items():

        if query_text in anime["search_title"].lower():

            results.append(anime_id)

    return results


# =========================================================
# /SEARCH
# =========================================================

async def search_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not context.args:

        SEARCH_USERS.add(
            update.effective_user.id
        )

        await update.message.reply_text(

            "🔎 <b>Поиск</b>\n\n"
            "Напиши название аниме:",

            parse_mode="HTML"
        )

        return

    query_text = " ".join(context.args)

    results = search_results(query_text)

    if not results:

        await update.message.reply_text(
            "😔 Ничего не найдено."
        )

        return

    keyboard = []

    for anime_id in results:

        keyboard.append([

            InlineKeyboardButton(
                ANIME[anime_id]["title"],
                callback_data="anime"
            )

        ])

    await update.message.reply_text(

        "🔎 <b>Результаты поиска:</b>",

        parse_mode="HTML",

        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# ПОИСК ТЕКСТОМ
# =========================================================

async def search_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id not in SEARCH_USERS:

        return

    SEARCH_USERS.discard(user_id)

    query_text = update.message.text

    results = search_results(query_text)

    if not results:

        await update.message.reply_text(
            "😔 По твоему запросу ничего не найдено.",
            reply_markup=main_menu()
        )

        return

    keyboard = []

    for anime_id in results:

        keyboard.append([

            InlineKeyboardButton(
                ANIME[anime_id]["title"],
                callback_data="anime"
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

        "Теперь укажи:\n"
        "/set СЕЗОН СЕРИЯ ОЗВУЧКА КАЧЕСТВО\n\n"

        "Пример:\n"
        "/set 1 1 anilibria 720\n\n"

        "Или:\n"
        "/set 2 5 dreamcast 1080"
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

            "❌ Неверный формат.\n\n"

            "Используй:\n"
            "/set 1 1 anilibria 720\n\n"

            "или:\n"
            "/set 2 5 dreamcast 1080"
        )

        return

    try:

        season = int(context.args[0])
        episode = int(context.args[1])

    except ValueError:

        await update.message.reply_text(
            "❌ Сезон и серия должны быть числами."
        )

        return

    voice = context.args[2].lower()
    quality = context.args[3]

    if season not in [1, 2]:

        await update.message.reply_text(
            "❌ Сезон должен быть 1 или 2."
        )

        return

    if episode < 1 or episode > 12:

        await update.message.reply_text(
            "❌ Серия должна быть от 1 до 12."
        )

        return

    if voice not in [
        "anilibria",
        "dreamcast"
    ]:

        await update.message.reply_text(

            "❌ Озвучка указана неправильно.\n\n"

            "Используй:\n"
            "anilibria\n"
            "dreamcast"
        )

        return

    if quality not in [
        "720",
        "1080"
    ]:

        await update.message.reply_text(
            "❌ Доступно только 720p или 1080p."
        )

        return

    file_id = PENDING_VIDEOS[user_id]

    if "mythic_spirit" not in VIDEO_FILES:

        VIDEO_FILES["mythic_spirit"] = {}

    if season not in VIDEO_FILES["mythic_spirit"]:

        VIDEO_FILES["mythic_spirit"][season] = {}

    if episode not in VIDEO_FILES["mythic_spirit"][season]:

        VIDEO_FILES["mythic_spirit"][season][episode] = {}

    if voice not in VIDEO_FILES["mythic_spirit"][season][episode]:

        VIDEO_FILES["mythic_spirit"][season][episode][voice] = {}

    VIDEO_FILES["mythic_spirit"][season][episode][voice][quality] = file_id

    del PENDING_VIDEOS[user_id]

    voice_name = (
        "AniLibria"
        if voice == "anilibria"
        else "Dream Cast"
    )

    await update.message.reply_text(

        "✅ <b>Видео сохранено!</b>\n\n"

        f"📺 Сезон: {season}\n"
        f"🎞 Серия: {episode}\n"
        f"🎙 Озвучка: {voice_name}\n"
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

    anime = VIDEO_FILES.get(
        "mythic_spirit",
        {}
    )

    if not anime:

        await update.message.reply_text(
            "📂 Видео пока не добавлены."
        )

        return

    text = "📂 <b>Загруженные видео</b>\n\n"

    for season in sorted(anime):

        text += f"📺 <b>Сезон {season}</b>\n"

        for episode in sorted(anime[season]):

            voices = []

            for voice in anime[season][episode]:

                voice_name = (
                    "AniLibria"
                    if voice == "anilibria"
                    else "Dream Cast"
                )

                qualities = list(
                    anime[season][episode][voice].keys()
                )

                voices.append(
                    f"{voice_name}: "
                    f"{', '.join(q + 'p' for q in qualities)}"
                )

            text += (
                f"🎞 Серия {episode} — "
                f"{'; '.join(voices)}\n"
            )

        text += "\n"

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


# =========================================================
# СОХРАНЕНИЕ ПРОСМОТРА
# =========================================================

def save_continue(
    user_id,
    season,
    episode
):

    USER_CONTINUE[user_id] = {

        "anime": "mythic_spirit",
        "season": season,
        "episode": episode,
    }


# =========================================================
# ПОКАЗ КАТАЛОГА ПО БУКВЕ
# =========================================================

async def show_letter(
    query,
    letter
):

    found = []

    for anime_id, anime in ANIME.items():

        if anime["letter"] == letter:

            found.append(anime_id)

    keyboard = []

    if found:

        for anime_id in found:

            keyboard.append([

                InlineKeyboardButton(
                    ANIME[anime_id]["title"],
                    callback_data=f"anime_{anime_id}"
                )

            ])

        text = (
            f"📚 <b>Аниме на букву «{letter}»</b>\n\n"
            "Выбери аниме:"
        )

    else:

        text = (
            f"📚 <b>Буква «{letter}»</b>\n\n"
            "😔 Аниме пока не добавлены."
        )

    keyboard.append([

        InlineKeyboardButton(
            "🔤 К алфавиту",
            callback_data="catalog"
        )

    ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ Назад",
            callback_data="home"
        )

    ])

    await query.edit_message_text(

        text,

        parse_mode="HTML",

        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# ПОКАЗ ИЗБРАННОЙ КАТЕГОРИИ
# =========================================================

async def show_favorite_category(
    query,
    user_id,
    status
):

    favorites = get_user_favorites(user_id)

    anime_ids = favorites[status]

    text = (
        f"<b>{status_name(status)}</b>\n\n"
    )

    keyboard = []

    if not anime_ids:

        text += "Здесь пока ничего нет."

    else:

        for anime_id in anime_ids:

            if anime_id not in ANIME:
                continue

            keyboard.append([

                InlineKeyboardButton(
                    ANIME[anime_id]["title"],
                    callback_data=f"anime_{anime_id}"
                )

            ])

    keyboard.append([

        InlineKeyboardButton(
            "⬅️ К избранному",
            callback_data="favorites"
        )

    ])

    await query.edit_message_text(

        text,

        parse_mode="HTML",

        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================================================
# ОБРАБОТЧИКИ КНОПОК
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

            greeting() +

            "\n\n"
            "Выбери нужный раздел:",

            parse_mode="HTML",

            reply_markup=main_menu()
        )

        return


    # =====================================================
    # ПРОДОЛЖИТЬ
    # =====================================================

    if data == "continue":

        if user_id not in USER_CONTINUE:

            await query.edit_message_text(

                "▶️ <b>Продолжить</b>\n\n"
                "Ты ещё ничего не смотрел.",

                parse_mode="HTML",

                reply_markup=continue_menu(user_id)
            )

            return

        item = USER_CONTINUE[user_id]

        await query.edit_message_text(

            "▶️ <b>Продолжить просмотр</b>\n\n"

            f"🧙‍♂️ {ANIME['mythic_spirit']['search_title']}\n"
            f"📺 Сезон: {item['season']}\n"
            f"🎞 Серия: {item['episode']}",

            parse_mode="HTML",

            reply_markup=continue_menu(user_id)
        )

        return


    # =====================================================
    # ПОПУЛЯРНОЕ
    # =====================================================

    if data == "popular":

        keyboard = [

            [
                InlineKeyboardButton(
                    "🧙‍♂️ Мифический дух: духовные хроники",
                    callback_data="anime_mythic_spirit"
                )
            ],

            [
                InlineKeyboardButton(
                    "⬅️ Назад",
                    callback_data="home"
                )
            ],
        ]

        await query.edit_message_text(

            "🔥 <b>Популярное</b>\n\n"
            "Сейчас в популярных:",

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return


    # =====================================================
    # НЕДАВНО ДОБАВЛЕННЫЕ
    # =====================================================

    if data == "recent":

        keyboard = [

            [
                InlineKeyboardButton(
                    "🧙‍♂️ Мифический дух: духовные хроники",
                    callback_data="anime_mythic_spirit"
                )
            ],

            [
                InlineKeyboardButton(
                    "⬅️ Назад",
                    callback_data="home"
                )
            ],
        ]

        await query.edit_message_text(

            "🆕 <b>Недавно добавленные</b>\n\n"
            "Последние добавленные аниме:",

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup(keyboard)
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

            reply_markup=alphabet_menu()
        )

        return


    # =====================================================
    # БУКВА
    # =====================================================

    if data.startswith("letter_"):

        letter = data.replace(
            "letter_",
            "",
            1
        )

        await show_letter(
            query,
            letter
        )

        return


    # =====================================================
    # АНИМЕ
    # =====================================================

    if data == "anime":

        text = (

            "🧙‍♂️ <b>Мифический дух: "
            "духовные хроники</b>\n\n"

            "📺 Доступно сезонов: 2\n\n"

            "Выбери сезон:"
        )

        await query.edit_message_text(

            text,

            parse_mode="HTML",

            reply_markup=seasons_menu()
        )

        return


    if data.startswith("anime_"):

        anime_id = data.replace(
            "anime_",
            "",
            1
        )

        if anime_id not in ANIME:

            await query.answer(
                "Аниме не найдено.",
                show_alert=True
            )

            return

        if anime_id == "mythic_spirit":

            text = (

                "🧙‍♂️ <b>Мифический дух: "
                "духовные хроники</b>\n\n"

                "📺 Доступно сезонов: 2\n\n"

                "Выбери сезон:"
            )

            await query.edit_message_text(

                text,

                parse_mode="HTML",

                reply_markup=seasons_menu()
            )

        return


    # =====================================================
    # СЕЗОН
    # =====================================================

    if data.startswith("season_"):

        season = int(
            data.split("_")[1]
        )

        text, keyboard = season_card(
            season
        )

        await query.edit_message_text(

            text,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return


    # =====================================================
    # СЕРИИ
    # =====================================================

    if data.startswith("episodes_"):

        season = int(
            data.split("_")[1]
        )

        await query.edit_message_text(

            f"🎞 <b>Сезон {season}</b>\n\n"
            "Выбери серию:",

            parse_mode="HTML",

            reply_markup=episodes_menu(
                season
            )
        )

        return


    # =====================================================
    # КОНКРЕТНАЯ СЕРИЯ
    # =====================================================

    if data.startswith("episode_"):

        parts = data.split("_")

        season = int(parts[1])
        episode = int(parts[2])

        title = EPISODES.get(
            season,
            {}
        ).get(
            episode,
            f"Серия {episode}"
        )

        save_continue(
            user_id,
            season,
            episode
        )

        await query.edit_message_text(

            f"🎞 <b>Серия {episode} из 12</b>\n\n"

            f"📺 Сезон: {season}\n"

            f"📝 {title}\n\n"

            "🎙 Выбери озвучку:",

            parse_mode="HTML",

            reply_markup=voice_menu(
                season,
                episode
            )
        )

        return


    # =====================================================
    # ОЗВУЧКА
    # =====================================================

    if data.startswith("voice_"):

        parts = data.split("_")

        season = int(parts[1])
        episode = int(parts[2])
        voice = parts[3]

        voice_name = (
            "AniLibria"
            if voice == "anilibria"
            else "Dream Cast"
        )

        await query.edit_message_text(

            f"🎞 <b>Серия {episode}</b>\n\n"

            f"🎙 Озвучка: <b>{voice_name}</b>\n\n"

            "⚙️ Выбери качество:",

            parse_mode="HTML",

            reply_markup=quality_menu(
                season,
                episode,
                voice
            )
        )

        return


    # =====================================================
    # КАЧЕСТВО
    # =====================================================

    if data.startswith("quality_"):

        parts = data.split("_")

        season = int(parts[1])
        episode = int(parts[2])
        voice = parts[3]
        quality = parts[4]

        video = (

            VIDEO_FILES
            .get(
                "mythic_spirit",
                {}
            )
            .get(
                season,
                {}
            )
            .get(
                episode,
                {}
            )
            .get(
                voice,
                {}
            )
            .get(
                quality
            )
        )

        if not video:

            await query.answer(

                f"Видео {quality}p пока "
                "не добавлено.",

                show_alert=True
            )

            return

        voice_name = (
            "AniLibria"
            if voice == "anilibria"
            else "Dream Cast"
        )

        await context.bot.send_video(

            chat_id=query.message.chat_id,

            video=video,

            caption=(

                f"🧙‍♂️ <b>"
                f"Мифический дух: духовные хроники"
                f"</b>\n"

                f"📺 Сезон {season}\n"

                f"🎞 Серия {episode}\n"

                f"🎙 {voice_name}\n"

                f"⚙️ {quality}p"
            ),

            parse_mode="HTML"
        )

        return


    # =====================================================
    # ДОБАВИТЬ В ИЗБРАННОЕ
    # =====================================================

    if data == "favorite_menu":

        await query.edit_message_text(

            "⭐ <b>Добавить аниме в избранное</b>\n\n"
            "Выбери статус:",

            parse_mode="HTML",

            reply_markup=favorite_status_menu()
        )

        return


    # =====================================================
    # ДОБАВЛЕНИЕ В КАТЕГОРИЮ
    # =====================================================

    if data.startswith("addfav_"):

        status = data.replace(
            "addfav_",
            "",
            1
        )

        favorites = get_user_favorites(
            user_id
        )

        anime_id = "mythic_spirit"

        # Убираем аниме из остальных категорий
        for category in favorites:

            if anime_id in favorites[category]:

                favorites[category].remove(
                    anime_id
                )

        if anime_id not in favorites[status]:

            favorites[status].append(
                anime_id
            )

        await query.edit_message_text(

            "✅ <b>Добавлено в избранное!</b>\n\n"

            f"🧙‍♂️ "
            f"{ANIME[anime_id]['search_title']}\n"

            f"Статус: {status_name(status)}",

            parse_mode="HTML",

            reply_markup=InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "⬅️ К аниме",
                        callback_data="anime"
                    )
                ],

                [
                    InlineKeyboardButton(
                        "⭐ Избранное",
                        callback_data="favorites"
                    )
                ],

            ])
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
    # КАТЕГОРИИ ИЗБРАННОГО
    # =====================================================

    favorite_callbacks = {

        "fav_watched": "watched",

        "fav_planned": "planned",

        "fav_dropped": "dropped",

        "fav_watching": "watching",
    }

    if data in favorite_callbacks:

        status = favorite_callbacks[data]

        await show_favorite_category(

            query,

            user_id,

            status
        )

        return


    # =====================================================
    # ПОИСК
    # =====================================================

    if data == "search":

        SEARCH_USERS.add(
            user_id
        )

        await query.edit_message_text(

            "🔎 <b>Поиск аниме</b>\n\n"
            "Напиши название аниме:",

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
            "🔤 Алфавитный каталог\n"
            "🔎 Поиск по названию\n"
            "⭐ Избранное\n"
            "▶️ Продолжение просмотра\n"
            "🔥 Популярное\n"
            "🆕 Недавно добавленные\n"
            "🎙 Несколько озвучек\n"
            "⚙️ 720p / 1080p\n\n"

            "Приятного просмотра! 🍿",

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
# FLASK ДЛЯ RENDER
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
# ЗАПУСК БОТА
# =========================================================

def main():

    bot = (

        Application
        .builder()
        .token(TOKEN)
        .build()
    )


    # -----------------------------------------------------
    # КОМАНДЫ
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


    bot.add_handler(

        CommandHandler(
            "search",
            search_command
        )
    )


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


    # -----------------------------------------------------
    # КНОПКИ
    # -----------------------------------------------------

    bot.add_handler(

        CallbackQueryHandler(
            buttons
        )
    )


    # -----------------------------------------------------
    # ВИДЕО
    # -----------------------------------------------------

    bot.add_handler(

        MessageHandler(
            filters.VIDEO,
            receive_video
        )
    )


    # -----------------------------------------------------
    # ТЕКСТОВЫЙ ПОИСК
    # -----------------------------------------------------

    bot.add_handler(

        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            search_text
        )
    )


    # -----------------------------------------------------
    # WEB SERVER
    # -----------------------------------------------------

    threading.Thread(

        target=run_server,

        daemon=True
    ).start()


    # -----------------------------------------------------
    # TELEGRAM
    # -----------------------------------------------------

    print(
        "AniFareX Bot запущен!"
    )

    bot.run_polling()


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()
