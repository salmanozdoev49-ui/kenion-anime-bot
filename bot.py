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

        "title": "Мифический дух: духовные хроники",

        "seasons": {

            1: {
                "title": "Мифический дух: духовные хроники — 1 сезон",
                "rating": "7.06",
                "year": "2021",
                "episodes": 12,
                "duration": "23 мин./эп.",
                "genres": (
                    "гарем, исэкай, приключения, "
                    "реинкарнация, романтика, фэнтези, экшен"
                ),
                "description": (
                    "20-летний студент Харуто Амакава погибает в ДТП. "
                    "Позже он приходит в себя в незнакомом мире "
                    "в теле парня по имени Рио и становится обладателем "
                    "магических способностей."
                ),
            },

            2: {
                "title": "Мифический дух: духовные хроники — 2 сезон",
                "rating": "6.88",
                "year": "2024",
                "episodes": 12,
                "duration": "23 мин./эп.",
                "genres": (
                    "гарем, исэкай, приключения, "
                    "реинкарнация, романтика, фэнтези, экшен"
                ),
                "description": (
                    "После побега из столицы Бельтрама Рио вместе "
                    "с Селией и Аисией спасает группу людей из Японии, "
                    "среди которых оказывается его подруга детства Михару. "
                    "Вместе с союзниками он ищет остальных переселенцев "
                    "и способ вернуть их домой, не забывая о главной цели — "
                    "отомстить за смерть матери."
                ),
            },

        },
    },
}


# =========================================================
# ВИДЕО
# =========================================================

# Структура:
#
# VIDEO_FILES[anime_id][season][episode][quality][voice] = file_id
#
VIDEO_FILES = {}

# Последнее отправленное администратором видео
PENDING_VIDEOS = {}


# =========================================================
# ИЗБРАННОЕ
# =========================================================

# Структура:
#
# FAVORITES[user_id] = {
#     "watching": [],
#     "planned": [],
#     "watched": [],
#     "dropped": []
# }
#
FAVORITES = {}


# =========================================================
# ПОИСК
# =========================================================

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
# ПОЛУЧИТЬ ИЗБРАННОЕ ПОЛЬЗОВАТЕЛЯ
# =========================================================

def get_user_favorites(user_id):

    if user_id not in FAVORITES:

        FAVORITES[user_id] = {
            "watched": [],
            "planned": [],
            "dropped": [],
            "watching": [],
        }

    return FAVORITES[user_id]


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
# КАТАЛОГ — БУКВЫ
# =========================================================

def alphabet_menu():

    letters = [
        "А", "Б", "В", "Г", "Д", "Е", "Ё",
        "Ж", "З", "И", "Й", "К", "Л", "М",
        "Н", "О", "П", "Р", "С", "Т", "У",
        "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Ъ",
        "Ы", "Ь", "Э", "Ю", "Я",
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
# МЕНЮ СЕЗОНОВ
# =========================================================

def seasons_menu():

    keyboard = []

    for season_number, season in ANIME["mythic_spirit"]["seasons"].items():

        keyboard.append([
            InlineKeyboardButton(
                f"📺 {season_number} сезон • "
                f"{season['episodes']} серий",
                callback_data=f"season_{season_number}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⭐ Добавить в избранное",
            callback_data="favorite_menu"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ К списку аниме",
            callback_data="letter_М"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# КАРТОЧКА СЕЗОНА
# =========================================================

def season_card(season_number):

    season = ANIME["mythic_spirit"]["seasons"][season_number]

    text = (
        f"<b>{season['title']}</b>\n\n"

        f"🍿 Формат: Аниме сериал\n"
        f"⭐️ Рейтинг: {season['rating']}\n"
        f"📼 Год: {season['year']}\n"
        f"🎬 Жанры: {season['genres']}\n"
        f"✅ Эпизодов (всего): {season['episodes']}\n"
        f"🕓 Длительность: {season['duration']}\n\n"

        f"📝 <b>Описание:</b>\n"
        f"{season['description']}\n\n"

        "Выбери действие:"
    )

    keyboard = [

        [
            InlineKeyboardButton(
                f"🎞 {season['episodes']} серий",
                callback_data=f"episodes_{season_number}"
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
# СПИСОК СЕРИЙ
# =========================================================

def episodes_menu(season_number):

    season = ANIME["mythic_spirit"]["seasons"][season_number]

    keyboard = []
    row = []

    for episode in range(1, season["episodes"] + 1):

        row.append(
            InlineKeyboardButton(
                f"🎞 {episode}",
                callback_data=(
                    f"episode_{season_number}_{episode}"
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
            "⬅️ К сезону",
            callback_data=f"season_{season_number}"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# МЕНЮ ОЗВУЧЕК
# =========================================================

def voice_menu(season_number, episode):

    keyboard = [

        [
            InlineKeyboardButton(
                f"💾 1-{ANIME['mythic_spirit']['seasons'][season_number]['episodes']} "
                "🎙 AniLibria",
                callback_data=(
                    f"voice_{season_number}_{episode}_anilibria"
                )
            )
        ],

        [
            InlineKeyboardButton(
                f"💾 1-{ANIME['mythic_spirit']['seasons'][season_number]['episodes']} "
                "🎙 Dream Cast",
                callback_data=(
                    f"voice_{season_number}_{episode}_dreamcast"
                )
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ К сериям",
                callback_data=f"episodes_{season_number}"
            )
        ],

    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# МЕНЮ КАЧЕСТВА
# =========================================================

def quality_menu(season_number, episode, voice):

    keyboard = [

        [
            InlineKeyboardButton(
                "720p",
                callback_data=(
                    f"quality_{season_number}_"
                    f"{episode}_{voice}_720"
                )
            ),

            InlineKeyboardButton(
                "1080p",
                callback_data=(
                    f"quality_{season_number}_"
                    f"{episode}_{voice}_1080"
                )
            ),
        ],

        [
            InlineKeyboardButton(
                "⬅️ К озвучкам",
                callback_data=(
                    f"episode_{season_number}_{episode}"
                )
            )
        ],

    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# ИЗБРАННОЕ — КАТЕГОРИИ
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
# ПОЛУЧЕНИЕ НАЗВАНИЯ АНИМЕ
# =========================================================

def anime_name():

    return ANIME["mythic_spirit"]["title"]


# =========================================================
# /START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        greeting() + "\n\n" + "Выбери нужный раздел:",
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
# ПОИСК — ЗАПРОС
# =========================================================

async def search_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    SEARCH_USERS.add(update.effective_user.id)

    await update.message.reply_text(
        "🔎 <b>Поиск аниме</b>\n\n"
        "Напиши название аниме:",
        parse_mode="HTML"
    )


# =========================================================
# ПОИСК — ОБРАБОТКА ТЕКСТА
# =========================================================

async def search_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id not in SEARCH_USERS:
        return

    query = update.message.text.lower().strip()

    SEARCH_USERS.discard(user_id)

    title = anime_name()

    if query in title.lower() or title.lower() in query:

        keyboard = InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    f"🧙 {title}",
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

        await update.message.reply_text(
            "🔎 <b>Результат поиска:</b>\n\n"
            f"🎌 {title}",
            parse_mode="HTML",
            reply_markup=keyboard
        )

    else:

        await update.message.reply_text(
            "😔 Ничего не найдено.\n\n"
            "Попробуй другое название."
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
        "Теперь укажи:\n\n"
        "/set СЕЗОН СЕРИЯ ОЗВУЧКА КАЧЕСТВО\n\n"
        "Например:\n"
        "/set 1 1 anilibria 720\n\n"
        "Или:\n"
        "/set 2 5 dreamcast 1080"
    )


# =========================================================
# /SET — СОХРАНЕНИЕ ВИДЕО
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
            "Озвучки:\n"
            "anilibria\n"
            "dreamcast\n\n"
            "Качество:\n"
            "720\n"
            "1080"
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

    if voice not in ["anilibria", "dreamcast"]:

        await update.message.reply_text(
            "❌ Неизвестная озвучка.\n\n"
            "Используй:\n"
            "anilibria\n"
            "dreamcast"
        )
        return

    if quality not in ["720", "1080"]:

        await update.message.reply_text(
            "❌ Доступно только:\n"
            "720\n"
            "1080"
        )
        return

    file_id = PENDING_VIDEOS[user_id]

    VIDEO_FILES.setdefault(
        "mythic_spirit",
        {}
    )

    VIDEO_FILES["mythic_spirit"].setdefault(
        season,
        {}
    )

    VIDEO_FILES["mythic_spirit"][season].setdefault(
        episode,
        {}
    )

    VIDEO_FILES["mythic_spirit"][season][episode].setdefault(
        quality,
        {}
    )

    VIDEO_FILES["mythic_spirit"][season][episode][quality][voice] = file_id

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
            "❌ У тебя нет прав для этой команды."
        )
        return

    if "mythic_spirit" not in VIDEO_FILES:

        await update.message.reply_text(
            "📂 Видео пока не добавлены."
        )
        return

    text = "📂 <b>Добавленные видео</b>\n\n"

    anime_data = VIDEO_FILES["mythic_spirit"]

    for season in sorted(anime_data):

        text += f"📺 <b>Сезон {season}</b>\n"

        for episode in sorted(anime_data[season]):

            qualities = []

            for quality in ["720", "1080"]:

                if quality in anime_data[season][episode]:

                    voices = anime_data[season][episode][quality]

                    for voice in voices:

                        voice_name = (
                            "AniLibria"
                            if voice == "anilibria"
                            else "Dream Cast"
                        )

                        qualities.append(
                            f"{quality}p {voice_name}"
                        )

            text += (
                f"🎞 Серия {episode}: "
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

    # =====================================================
    # ГЛАВНАЯ
    # =====================================================

    if data == "home":

        await query.edit_message_text(
            greeting() + "\n\n"
            "Выбери нужный раздел:",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    # =====================================================
    # КАТАЛОГ
    # =====================================================

    elif data == "catalog":

        await query.edit_message_text(
            "📚 <b>Каталог</b>\n\n"
            "Выбери первую букву названия:",
            parse_mode="HTML",
            reply_markup=alphabet_menu()
        )

    # =====================================================
    # БУКВА
    # =====================================================

    elif data.startswith("letter_"):

        letter = data.replace("letter_", "")

        # Сейчас в каталоге только одно аниме.
        # Оно начинается на М.
        if letter == "М":

            keyboard = [

                [
                    InlineKeyboardButton(
                        "🧙 Мифический дух: духовные хроники",
                        callback_data="anime"
                    )
                ],

                [
                    InlineKeyboardButton(
                        "⬅️ К буквам",
                        callback_data="catalog"
                    )
                ],

            ]

            await query.edit_message_text(
                f"🔤 <b>Аниме на букву «{letter}»</b>\n\n"
                "Выбери аниме:",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        else:

            await query.edit_message_text(
                f"🔤 <b>Буква «{letter}»</b>\n\n"
                "😔 Аниме пока не добавлены.",
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

    # =====================================================
    # КАРТОЧКА АНИМЕ
    # =====================================================

    elif data == "anime":

        text = (
            "🧙 <b>Мифический дух: духовные хроники</b>\n\n"
            "📺 Доступно сезонов: 2\n"
            "🎬 По 12 серий в каждом сезоне\n\n"
            "Выбери сезон:"
        )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=seasons_menu()
        )

    # =====================================================
    # СЕЗОН
    # =====================================================

    elif data.startswith("season_"):

        season = int(data.split("_")[1])

        text, keyboard = season_card(season)

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # =====================================================
    # СЕРИИ
    # =====================================================

    elif data.startswith("episodes_"):

        season = int(data.split("_")[1])

        season_info = ANIME["mythic_spirit"]["seasons"][season]

        await query.edit_message_text(
            f"📺 <b>{season_info['title']}</b>\n\n"
            f"Выбери серию:",
            parse_mode="HTML",
            reply_markup=episodes_menu(season)
        )

    # =====================================================
    # СЕРИЯ
    # =====================================================

    elif data.startswith("episode_"):

        parts = data.split("_")

        season = int(parts[1])
        episode = int(parts[2])

        title = ANIME["mythic_spirit"]["seasons"][season]["title"]

        await query.edit_message_text(
            f"🎞 <b>{title}</b>\n\n"
            f"Серия: {episode}\n\n"
            "🎙 <b>Выберите озвучку:</b>",
            parse_mode="HTML",
            reply_markup=voice_menu(season, episode)
        )

    # =====================================================
    # ОЗВУЧКА
    # =====================================================

    elif data.startswith("voice_"):

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
            "⚙️ <b>Выберите качество:</b>",
            parse_mode="HTML",
            reply_markup=quality_menu(
                season,
                episode,
                voice
            )
        )

    # =====================================================
    # КАЧЕСТВО
    # =====================================================

    elif data.startswith("quality_"):

        parts = data.split("_")

        season = int(parts[1])
        episode = int(parts[2])
        voice = parts[3]
        quality = parts[4]

        video = (
            VIDEO_FILES
            .get("mythic_spirit", {})
            .get(season, {})
            .get(episode, {})
            .get(quality, {})
            .get(voice)
        )

        if not video:

            await query.answer(
                f"Видео {quality}p ещё не добавлено.",
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
                "🎬 <b>Мифический дух: духовные хроники</b>\n"
                f"📺 Сезон: {season}\n"
                f"🎞 Серия: {episode}\n"
                f"🎙 {voice_name}\n"
                f"⚙️ {quality}p"
            ),
            parse_mode="HTML"
        )

    # =====================================================
    # ИЗБРАННОЕ
    # =====================================================

    elif data == "favorites":

        await query.edit_message_text(
            "⭐ <b>Избранное</b>\n\n"
            "Выбери категорию:",
            parse_mode="HTML",
            reply_markup=favorites_menu()
        )

    # =====================================================
    # ДОБАВИТЬ В ИЗБРАННОЕ
    # =====================================================

    elif data == "favorite_menu":

        await query.edit_message_text(
            "⭐ <b>Добавить аниме в избранное</b>\n\n"
            "Куда добавить «Мифический дух: духовные хроники»?",
            parse_mode="HTML",
            reply_markup=favorite_status_menu()
        )

    # =====================================================
    # ДОБАВЛЕНИЕ В КАТЕГОРИЮ
    # =====================================================

    elif data.startswith("addfav_"):

        status = data.replace("addfav_", "")

        user_id = query.from_user.id

        favorites = get_user_favorites(user_id)

        if "mythic_spirit" not in favorites[status]:

            favorites[status].append("mythic_spirit")

        names = {
            "watched": "👀 Смотрел",
            "planned": "📌 Планирую",
            "dropped": "❌ Брошено",
            "watching": "▶️ Смотрю",
        }

        await query.edit_message_text(
            "✅ <b>Добавлено в избранное!</b>\n\n"
            f"🧙 Мифический дух: духовные хроники\n"
            f"📁 Категория: {names[status]}",
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
                        callback_data="anime"
                    )
                ],
            ])
        )

    # =====================================================
    # КАТЕГОРИИ ИЗБРАННОГО
    # =====================================================

    elif data.startswith("fav_"):

        status = data.replace("fav_", "")

        user_id = query.from_user.id

        favorites = get_user_favorites(user_id)

        names = {
            "watched": "👀 Смотрел",
            "planned": "📌 Планирую",
            "dropped": "❌ Брошено",
            "watching": "▶️ Смотрю",
        }

        anime_list = favorites.get(status, [])

        if not anime_list:

            text = (
                f"{names[status]}\n\n"
                "📭 Здесь пока ничего нет."
            )

        else:

            text = (
                f"{names[status]}\n\n"
                "🧙 Мифический дух: духовные хроники"
            )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⭐ К избранному",
                        callback_data="favorites"
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
    # НОВИНКИ — УБРАНЫ
    # =====================================================

    # Кнопки "Новинки" здесь специально нет.

    # =====================================================
    # ПОИСК
    # =====================================================

    elif data == "search":

        SEARCH_USERS.add(query.from_user.id)

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

    # =====================================================
    # О БОТЕ
    # =====================================================

    elif data == "about":

        await query.edit_message_text(
            "ℹ️ <b>AniFareX</b>\n\n"
            "🎌 Каталог аниме\n"
            "📺 Сезоны и серии\n"
            "🎙 Несколько озвучек\n"
            "⚙️ 720p / 1080p\n"
            "⭐ Избранное\n"
            "🔎 Поиск по названию",
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
    # Команды
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

    # -----------------------------------------------------
    # Админские команды
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
            videos_list
        )
    )

    # -----------------------------------------------------
    # Кнопки
    # -----------------------------------------------------

    bot.add_handler(
        CallbackQueryHandler(
            buttons
        )
    )

    # -----------------------------------------------------
    # Получение видео
    # -----------------------------------------------------

    bot.add_handler(
        MessageHandler(
            filters.VIDEO,
            receive_video
        )
    )

    # -----------------------------------------------------
    # Поиск текстом
    # -----------------------------------------------------

    bot.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search_text
        )
    )

    # -----------------------------------------------------
    # Render Web Server
    # -----------------------------------------------------

    threading.Thread(
        target=run_server,
        daemon=True
    ).start()

    # -----------------------------------------------------
    # Telegram
    # -----------------------------------------------------

    bot.run_polling()


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()
