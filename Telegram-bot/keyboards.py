import telebot.types as types
from config import (
    NEWS_CATEGORIES,
    EVENTS_CATEGORIES,
    ATTRACTIONS_CATEGORIES,
    HISTORY_CATEGORIES,
    LOCATIONS
)

def create_main_keyboard():
    """Create main menu keyboard."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.KeyboardButton("📰 Новости"))
    keyboard.row(
        types.KeyboardButton("🏛️ О городе"),
        types.KeyboardButton("📅 События")
    )
    keyboard.row(types.KeyboardButton("🆘 Помощь"))
    return keyboard

def create_news_keyboard():
    """Create news categories keyboard."""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="📰 Общие новости", callback_data="news_general"))
    keyboard.add(types.InlineKeyboardButton(text="🚌 Транспорт", callback_data="news_transport"))
    keyboard.add(types.InlineKeyboardButton(text="🏗 Строительство", callback_data="news_construction"))
    keyboard.add(types.InlineKeyboardButton(text="🏛 Культура", callback_data="news_culture"))
    keyboard.add(types.InlineKeyboardButton(text="🏢 Администрация", callback_data="news_administration"))
    keyboard.add(types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
    return keyboard

def create_events_keyboard():
    """Create events categories keyboard."""
    keyboard = types.InlineKeyboardMarkup()
    for category, name in EVENTS_CATEGORIES.items():
        keyboard.add(types.InlineKeyboardButton(text=name, callback_data=f"events_{category}"))
    keyboard.add(types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
    return keyboard

def create_weather_keyboard():
    """Create weather keyboard with options for current weather and weather news."""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton(text="Узнать погоду", callback_data="show_weather"),
        types.InlineKeyboardButton(text="Новости о погоде", callback_data="weather_news")
    )
    return keyboard

def create_attractions_keyboard():
    """Create attractions categories keyboard."""
    keyboard = types.InlineKeyboardMarkup()
    for category, name in ATTRACTIONS_CATEGORIES.items():
        keyboard.add(types.InlineKeyboardButton(text=name, callback_data=f"attractions_{category}"))
    keyboard.add(types.InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
    return keyboard

def create_history_keyboard():
    """Создает ReplyKeyboardMarkup для тем истории Ярославля."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        types.KeyboardButton("🐻 Герб"),
        types.KeyboardButton("🏛 Архитектура"),
        types.KeyboardButton("👑 Ярослав Мудрый")
    )
    keyboard.add(types.KeyboardButton("🔙 Назад"))
    return keyboard

def get_about_keyboard():
    """Create reply keyboard for About City section."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        types.KeyboardButton("🗺️ Карта Ярославля"),
        types.KeyboardButton("📜 История Ярославля")
    )
    keyboard.add(types.KeyboardButton("🔙 Назад"))
    return keyboard

def create_two_column_keyboard(button_texts, back_button_text=None):
    """Create a keyboard with two columns of buttons."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Add buttons in pairs
    for i in range(0, len(button_texts), 2):
        row = [types.KeyboardButton(button_texts[i])]
        if i + 1 < len(button_texts):
            row.append(types.KeyboardButton(button_texts[i + 1]))
        markup.row(*row)
    
    # Add back button if specified
    if back_button_text:
        markup.add(types.KeyboardButton(back_button_text))
    
    return markup

def create_inline_keyboard(buttons_data):
    """Create an inline keyboard with the given buttons data."""
    markup = types.InlineKeyboardMarkup()
    
    for button_text, callback_data in buttons_data:
        markup.add(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
    
    return markup

def create_about_city_keyboard():
    """Создает клавиатуру для раздела 'О городе'."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🗺️ Карта Ярославля", callback_data="map"),
        types.InlineKeyboardButton("📜 История Ярославля", callback_data="history"),
        types.InlineKeyboardButton("🏛️ Достопримечательности", callback_data="attractions"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
    )
    return keyboard

def create_location_keyboard(category):
    """Создает клавиатуру для выбора мест в указанной категории."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for location_name in LOCATIONS[category]:
        keyboard.add(types.InlineKeyboardButton(location_name, callback_data=f"location_{location_name}"))
    keyboard.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_map"))
    return keyboard

def create_support_keyboard():
    """Создает клавиатуру для раздела поддержки."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("📞 Связаться с поддержкой", callback_data="contact_support"),
        types.InlineKeyboardButton("❓ Часто задаваемые вопросы", callback_data="faq"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
    )
    return keyboard

def create_admin_panel_keyboard():
    """Создает клавиатуру для панели администратора."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
        types.InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
    )
    return keyboard

def create_map_keyboard():
    """Создает клавиатуру для раздела карты."""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🏰 Исторический центр", callback_data="map_historical"),
        types.InlineKeyboardButton("🏥 Травмпункты", callback_data="map_trauma_centers"),
        types.InlineKeyboardButton("🌳 Парки", callback_data="map_parks"),
        types.InlineKeyboardButton("🎭 Театры", callback_data="map_theaters"),
        types.InlineKeyboardButton("🛍️ Торговые центры", callback_data="map_shopping_centers"),
        types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_about")
    )
    return keyboard