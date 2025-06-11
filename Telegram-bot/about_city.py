import telebot.types as types
from geopy.distance import geodesic
import os
import random
import requests
from bs4 import BeautifulSoup
import logging
import json
from config import UNSPLASH_ACCESS_KEY
from locations import LOCATIONS, get_location_info, get_locations_by_category
from keyboards import create_two_column_keyboard

# Список URL-ов с фотографиями Ярославля
CITY_PHOTOS = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Yaroslavl_Spaso-Preobrazhensky_Monastery_2015-07-23.jpg/1280px-Yaroslavl_Spaso-Preobrazhensky_Monastery_2015-07-23.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Yaroslavl_Church_of_Elijah_the_Prophet_2015-07-23.jpg/1280px-Yaroslavl_Church_of_Elijah_the_Prophet_2015-07-23.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Yaroslavl_Volga_Embankment_2015-07-23.jpg/1280px-Yaroslavl_Volga_Embankment_2015-07-23.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Yaroslavl_Strelka_2015-07-23.jpg/1280px-Yaroslavl_Strelka_2015-07-23.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Yaroslavl_Assumption_Cathedral_2015-07-23.jpg/1280px-Yaroslavl_Assumption_Cathedral_2015-07-23.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Yaroslavl_Volga_Embankment_2015-07-23_2.jpg/1280px-Yaroslavl_Volga_Embankment_2015-07-23_2.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Yaroslavl_Church_of_St._Nicholas_2015-07-23.jpg/1280px-Yaroslavl_Church_of_St._Nicholas_2015-07-23.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Yaroslavl_Volga_Embankment_2015-07-23_3.jpg/1280px-Yaroslavl_Volga_Embankment_2015-07-23_3.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Yaroslavl_Volga_Embankment_2015-07-23_4.jpg/1280px-Yaroslavl_Volga_Embankment_2015-07-23_4.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Yaroslavl_Volga_Embankment_2015-07-23_5.jpg/1280px-Yaroslavl_Volga_Embankment_2015-07-23_5.jpg"
]

def get_random_city_photo():
    """Get a random photo of Yaroslavl."""
    try:
        # Сначала пробуем использовать локальное изображение
        local_image = os.path.join("materials", "yaroslavl.jpg")
        if os.path.exists(local_image):
            return local_image
        
        # Если локального изображения нет, используем случайное из списка
        return random.choice(CITY_PHOTOS)
    except Exception as e:
        logging.error(f"Error getting city photo: {e}")
        return random.choice(CITY_PHOTOS)

# Информация о Ярославле
YAROSLAVL_INFO = {
    "image_url": get_random_city_photo(),  # Будет случайно выбираться при каждом запросе
    "short_description": """🏛️ Ярославль - один из старейших городов России, основанный в 1010 году князем Ярославом Мудрым.

📍 Город расположен в центральной части России, на берегах рек Волги и Которосли.

📊 Основные факты:
• Население: около 600 000 человек
• Площадь: 205,8 км²
• Часовой пояс: UTC+3 (Московское время)""",
    "full_description": """🏆 Достижения:
• Входит в Золотое кольцо России
• Исторический центр включен в список Всемирного наследия ЮНЕСКО
• Обладает богатым культурным и историческим наследием

🏢 Современный Ярославль:
• Крупный промышленный центр
• Развитая транспортная инфраструктура
• Современные торговые центры и развлекательные комплексы
• Активная культурная жизнь

🌳 Экология:
• Множество парков и скверов
• Бережное отношение к историческому наследию
• Развитие экологических программ

🎓 Образование:
• Крупные университеты и институты
• Развитая система среднего образования
• Научно-исследовательские центры

🏥 Здравоохранение:
• Современные медицинские центры
• Развитая система здравоохранения
• Доступная медицинская помощь

🎭 Культура:
• Театры и музеи
• Фестивали и выставки
• Богатая культурная жизнь

🏛️ Историческое наследие:
• Древние храмы и монастыри
• Исторические памятники
• Уникальная архитектура

🌆 Городская среда:
• Современные районы
• Благоустроенные территории
• Комфортная городская среда"""
}

# Координаты центра Ярославля
YAROSLAVL_CENTER = {
    "lat": 57.626065,
    "lon": 39.887478
}

def get_distance_to_center(lat, lon):
    """Calculate distance from given coordinates to city center."""
    point = (lat, lon)
    center = (YAROSLAVL_CENTER['lat'], YAROSLAVL_CENTER['lon'])
    return round(geodesic(point, center).kilometers, 2)

def create_location_keyboard(category):
    """Create keyboard with locations for a given category."""
    locations = get_locations_by_category(category)
    button_texts = [name for name in locations]
    return create_two_column_keyboard(button_texts, back_button_text="🔙 Назад") 