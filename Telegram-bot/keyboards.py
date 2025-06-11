from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import (
    NEWS_CATEGORIES,
    EVENTS_CATEGORIES,
    ATTRACTIONS_CATEGORIES,
    HISTORY_CATEGORIES
)

def create_main_keyboard():
    """Create main menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(text="🗺 Карта", callback_data="map"),
            InlineKeyboardButton(text="📰 Новости", callback_data="news")
        ],
        [
            InlineKeyboardButton(text="🎭 События", callback_data="events"),
            InlineKeyboardButton(text="🌤 Погода", callback_data="weather")
        ],
        [
            InlineKeyboardButton(text="🏛 Достопримечательности", callback_data="attractions"),
            InlineKeyboardButton(text="📚 История Ярославля", callback_data="history")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_news_keyboard():
    """Create news categories keyboard."""
    keyboard = [
        [InlineKeyboardButton(text="📰 Общие новости", callback_data="news_general")],
        [InlineKeyboardButton(text="🚌 Транспорт", callback_data="news_transport")],
        [InlineKeyboardButton(text="🏗 Строительство", callback_data="news_construction")],
        [InlineKeyboardButton(text="🏛 Культура", callback_data="news_culture")],
        [InlineKeyboardButton(text="🌤 Погода", callback_data="news_weather")],
        [InlineKeyboardButton(text="🏢 Администрация", callback_data="news_administration")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_events_keyboard():
    """Create events categories keyboard."""
    keyboard = []
    for category, name in EVENTS_CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(text=name, callback_data=f"events_{category}")])
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_weather_keyboard():
    """Create weather keyboard."""
    keyboard = [
        [InlineKeyboardButton(text="🌡 Текущая погода", callback_data="weather_current")],
        [InlineKeyboardButton(text="📅 Прогноз на 3 дня", callback_data="weather_forecast")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_attractions_keyboard():
    """Create attractions categories keyboard."""
    keyboard = []
    for category, name in ATTRACTIONS_CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(text=name, callback_data=f"attractions_{category}")])
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_history_keyboard():
    """Create history categories keyboard."""
    keyboard = []
    for category, name in HISTORY_CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(text=name, callback_data=f"history_{category}")])
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)