import telebot
import telebot.types as types
from datetime import datetime, timedelta
import logging
import os
import time

# Для Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from config import BOT_TOKEN, ADMIN_IDS, NEWS_CATEGORIES, NEWS_CATEGORY_NAMES, NEWS_STOPWORDS, NEWS_SOURCES, YAROSLAVL_CENTER, YAROSLAVL_CENTER_MAP_IMAGE_URL, MAP_CATEGORY_MAPPING, REVERSE_MAP_CATEGORY_MAPPING, CLEAN_CATEGORY_NAME_MAPPING, EVENT_CATEGORY_MAPPING, REVERSE_CATEGORY_MAPPING, REVERSE_EVENT_CATEGORY_MAPPING, CATEGORY_KEYWORDS, UNSPLASH_ACCESS_KEY, STATION_CODES, CITY_IMAGE_PATH, HISTORY_TOPICS, LOCATIONS, USER_STATES, USER_STATES_FILE, LOCATION_CATEGORIES, DATABASE, LOGGING
from news import get_yarnews_articles, get_weather_news, get_weekly_news
from weather import get_openmeteo_weather, format_weather_message, get_weather_description, generate_temperature_graph
from events import get_events_by_category, format_event_message, event_types
from locations import get_locations_by_category, get_location_info, LOCATIONS
from about_city import YAROSLAVL_INFO
from history_parser import HistoryParser
from keyboards import create_main_keyboard, create_about_city_keyboard, create_location_keyboard, create_support_keyboard, create_admin_panel_keyboard, create_map_keyboard, create_history_keyboard, create_two_column_keyboard, create_events_keyboard

from telebot.storage import StateMemoryStorage

import handlers

# Инициализация бота с хранилищем состояний
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)

# Импортируем обработчики сообщений после инициализации бота
handlers.setup_handlers(bot)

# Состояния бота
class BotState(telebot.State):
    MAIN_MENU = "main_menu"
    NEWS_MENU = "news_menu"
    ABOUT_CITY_MENU = "about_city_menu"
    HISTORY_MENU = "history_menu"
    TRANSPORT_MENU = "transport_menu"
    MAP_MENU = "map_menu"
    EVENTS_MENU = "events_menu"
    HELP_MENU = "help_menu"
    NEWS_CATEGORIES = "news_categories"
    WEATHER_NEWS = "weather_news"
    WEEKLY_NEWS = "weekly_news"
    DAILY_REMINDER = "daily_reminder"
    WAITING_BUS_ROUTE = "waiting_bus_route"
    WAITING_BUS_STOP = "waiting_bus_stop"
    WAITING_TRAM_ROUTE = "waiting_tram_route"
    WAITING_TRAM_STOP = "waiting_tram_stop"
    WAITING_TROLLEYBUS_ROUTE = "waiting_trolleybus_route"
    WAITING_TROLLEYBUS_STOP = "waiting_trolleybus_stop"

# Инициализация парсера истории
history_parser = HistoryParser()

# Словарь для хранения состояний пользователей
user_states = {}

def save_user_state(chat_id, state):
    """Save user state to memory."""
    user_states[chat_id] = state

def get_user_state(chat_id):
    """Get user state from memory."""
    return user_states.get(chat_id, {})

def is_admin(user_id):
    """Проверяет, является ли пользователь администратором."""
    return str(user_id) in ADMIN_IDS

def go_to_main_menu(message):
    """Возвращает пользователя в главное меню."""
    markup = create_main_keyboard()
    
    bot.send_message(
        message.chat.id,
        "Выберите раздел:",
        reply_markup=markup
    )
    save_user_state(message.chat.id, {'state': 'main_menu'})

def run_main_bot_polling():
    logger.info("Starting main bot polling...")
    bot.infinity_polling()

# Export bot and logger for use in other modules
__all__ = ['bot', 'logger']

if __name__ == '__main__':
    run_main_bot_polling() 