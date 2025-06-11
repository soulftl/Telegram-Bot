import telebot
import telebot.types as types
from datetime import datetime, timedelta
import logging
import os
import matplotlib.pyplot as plt
from io import BytesIO

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from config import BOT_TOKEN
from news import get_yarnews_articles, get_news_by_category, get_news_by_date, get_news_by_week
from weather import get_openmeteo_weather, format_weather_message, get_weather_description
from events import get_events_by_category, format_event_message, event_types
from locations import get_locations_by_category, get_location_info
from about_city import (
    YAROSLAVL_INFO, LOCATIONS, get_location_info,
    get_locations_by_category, get_distance_to_center,
    create_location_keyboard
)
from database import save_user_state, get_user_state

# Initialize bot using the standard synchronous TeleBot
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения состояний пользователей
user_states = {}

def main():
    """Main function to run the bot."""
    logger.info("Starting bot...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()

# Export bot and logger for use in other modules
__all__ = ['bot', 'logger'] 