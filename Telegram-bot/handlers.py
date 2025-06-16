import telebot
import telebot.types as types
from datetime import datetime, timedelta
import logging
import os
import matplotlib.pyplot as plt
from io import BytesIO
import time
from database import add_user, update_last_active
from bot_instance import bot

# Словарь для хранения ID последнего сообщения с вопросом по каждой категории
last_question_message_ids = {}
# Словарь для хранения ID последнего сообщения с выбором категории новостей/событий
# last_category_message_id = {} # УДАЛЯЕМ ЭТУ СТРОКУ

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

from config import BOT_TOKEN, LOCATIONS
from news import get_yarnews_articles, get_news_by_category, get_news_by_date, get_news_by_week
from weather import get_openmeteo_weather, format_weather_message, get_weather_description, generate_hourly_temperature_graph_image
from events import get_events_by_category, format_event_message, event_types
from locations import get_locations_by_category, get_location_info
from about_city import (
    YAROSLAVL_INFO, get_location_info,
    get_locations_by_category, get_distance_to_center,
    create_location_keyboard
)
from city_history import get_history_keyboard, send_history_topic, HISTORY_TOPICS
from keyboards import create_main_keyboard, get_about_keyboard, create_weather_keyboard, create_history_keyboard # Import create_main_keyboard from keyboards.py

# Инициализация бота
# bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для маппинга русских названий категорий новостей на английские
CATEGORY_MAPPING = {
    "Администрация": "administration",
    "Транспорт": "transport",
    "Ремонт и благоустройство": "construction",
    "Политика": "politics",
    "Погода": "weather"
}

# Global mapping for map category buttons to internal keys
CATEGORY_MAP_BUTTONS_TO_KEYS = {
    "🏰 Исторический центр": "attractions",
    "🏥 Травмпункты": "trauma_centers",
    "🌳 Парки": "parks",
    "🎭 Театры": "theaters",
    "🛍️ Торговые центры": "shopping_centers"
}
REVERSE_CATEGORY_MAP_BUTTONS_TO_KEYS = {v: k for k, v in CATEGORY_MAP_BUTTONS_TO_KEYS.items()}

# Словарь для правильного отображения категорий новостей
CATEGORY_NAMES = {
    "Администрация": {
        "by": "администрации",
        "default": "администрация"
    },
    "Транспорт": {
        "by": "транспорта",
        "default": "транспорт"
    },
    "Ремонт и благоустройство": {
        "by": "ремонта и благоустройства",
        "default": "ремонт и благоустройство"
    },
    "Политика": {
        "by": "политики",
        "default": "политика"
    },
    "Погода": {
        "by": "погоды",
        "default": "погода"
    }
}

# Словарь для маппинга русских названий категорий событий на английские
EVENT_CATEGORY_MAPPING = {
    "Культура": "culture",
    "Спорт": "sport",
    "Образование": "education",
    "Развлечения": "entertainment",
    "Выставки": "exhibitions",
    "Концерты": "concerts"
}

# Словарь для правильного отображения категорий событий
EVENT_CATEGORY_NAMES = {
    "Культура": {
        "by": "культуры",
        "default": "культура"
    },
    "Спорт": {
        "by": "спорта",
        "default": "спорт"
    },
    "Образование": {
        "by": "образования",
        "default": "образование"
    },
    "Развлечения": {
        "by": "развлечений",
        "default": "развлечения"
    },
    "Выставки": {
        "by": "выставок",
        "default": "выставки"
    },
    "Концерты": {
        "by": "концертов",
        "default": "концерты"
    }
}

# Словарь для хранения состояний пользователей
user_states = {}

# Текст помощи
HELP_TEXT = (
    "⚙️ Для получения технической поддержки перейдите в наш бот поддержки:\n\n"
    "➡️ @NovostYARHelpBot ⬅️\n\n"
    "В боте поддержки вы можете:\n"
    "📄 Создать обращение\n"
    "📋 Просматривать свои обращения\n"
    "💬 Общаться со специалистами поддержки\n\n"
    "Мы постараемся ответить вам как можно быстрее! 🚀"
)

def save_user_state(user_id, state):
    """
    Сохраняет состояние пользователя
    Используется для отслеживания текущего раздела и предыдущего меню
    """
    try:
        user_states[user_id] = state
        logger.debug(f"Сохранено состояние пользователя {user_id}: {state}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении состояния пользователя {user_id}: {e}")

def get_user_state(user_id):
    """
    Получает сохраненное состояние пользователя
    Возвращает словарь с информацией о текущем разделе и предыдущем меню
    """
    try:
        return user_states.get(user_id)
    except Exception as e:
        logger.error(f"Ошибка при получении состояния пользователя {user_id}: {e}")
        return None

def clear_user_state(user_id):
    """
    Очищает сохраненное состояние пользователя
    Используется при возврате в главное меню или при завершении работы с разделом
    """
    try:
        if user_id in user_states:
            del user_states[user_id]
            logger.debug(f"Очищено состояние пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при очистке состояния пользователя {user_id}: {e}")

# create_main_keyboard function will be imported from keyboards.py

def create_about_city_keyboard():
    """DEPRECATED: Use get_about_keyboard for inline buttons."""
    pass # This function is no longer needed or will be adapted later if necessary

def setup_handlers(bot):
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        """
        Обработчик команды /start - первое взаимодействие пользователя с ботом.
        Выполняет следующие действия:
        1. Регистрирует пользователя в базе данных
        2. Отправляет приветственное сообщение
        3. Показывает главное меню с основными функциями бота
        """
        try:
            user_id = message.chat.id
            # Добавляем пользователя в базу данных с его информацией из Telegram
            add_user(
                user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            
            # Отправляем приветственное сообщение с описанием возможностей бота
            bot.send_message(
                message.chat.id,
                f"👋 Добро пожаловать в бот новостей Ярославля, {message.from_user.first_name}!\n\n"
                "Здесь вы можете узнать о новостях города, погоде, событиях и достопримечательностях.",
                reply_markup=create_main_keyboard()
            )
            
            # Сбрасываем состояние пользователя
            clear_user_state(user_id)
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике handle_start: {e}")
            bot.send_message(
                message.chat.id,
                "Произошла ошибка при запуске. Пожалуйста, попробуйте позже."
            )

    @bot.message_handler(commands=['help'])
    def handle_help_command(message):
        """
        Обработчик команды /help
        Показывает справочную информацию о боте
        """
        try:
            # Отправляем сообщение со справкой
            with open('Materials/helpPhoto.jpg', 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=HELP_TEXT,
                    parse_mode='HTML',
                    reply_markup=create_main_keyboard()
                )
        except Exception as e:
            logger.error(f"Ошибка в обработчике команды /help: {e}")
            bot.send_message(
                message.chat.id,
                "Произошла ошибка при загрузке справки. Пожалуйста, попробуйте позже.",
                reply_markup=create_main_keyboard()
            )

    @bot.message_handler(func=lambda message: message.text == "🔙 Назад")
    def handle_back_button(message):
        """
        Обработчик кнопки "Назад" - возвращает пользователя в предыдущее меню
        """
        try:
            user_id = message.chat.id
            user_state = get_user_state(user_id)
            logger.debug(f"handle_back_button: user_state for {user_id}: {user_state}")

            if not user_state:
                bot.send_message(user_id, "Главное меню:", reply_markup=create_main_keyboard())
                clear_user_state(user_id)
                logger.debug(f"handle_back_button: No user_state, returning to main menu for {user_id}")
                return

            current_state = user_state.get('state')
            prev_menu = user_state.get('prev_menu')
            logger.debug(f"handle_back_button: current_state={current_state}, prev_menu={prev_menu} for {user_id}")
            
            if current_state == 'location_info': # Из информации о конкретном месте
                category_key = user_state.get('category')
                if category_key:
                    # Возвращаемся к меню выбора категории карты
                    show_map(message, initial_load=False)
                    logger.debug(f"handle_back_button: Returning to map for {user_id}")
                else:
                    logger.error(f"Category key not found in state for user {user_id} when in location_info.")
                    show_map(message, initial_load=False) # Fallback
                    logger.debug(f"handle_back_button: Fallback to map for {user_id}")
            
            elif current_state == 'category_places': # Из меню выбора категории мест
                show_map(message, initial_load=False)
                logger.debug(f"handle_back_button: Returning to category places for {user_id}")

            elif current_state == 'map_options': # Из начального меню карты (с категориями)
                handle_about_city(message)
                logger.debug(f"handle_back_button: Returning to about city from map options for {user_id}")
            
            elif current_state == 'about_city_menu': # Из меню "О городе"
                bot.send_message(user_id, "Главное меню:", reply_markup=create_main_keyboard())
                clear_user_state(user_id)
                logger.debug(f"handle_back_button: Returning to main menu from about city for {user_id}")
            
            elif current_state == 'history_menu': # Из меню истории
                if prev_menu == 'about_city_menu':
                    handle_about_city(message)
                    logger.debug(f"handle_back_button: Returning to about city from history for {user_id}")
                else:
                    bot.send_message(user_id, "Главное меню:", reply_markup=create_main_keyboard())
                    clear_user_state(user_id)
                    logger.debug(f"handle_back_button: Returning to main menu from history (no prev_menu) for {user_id}")

            else:
                # Если состояние не определено или 'idle', возвращаемся в главное меню
                bot.send_message(user_id, "Главное меню:", reply_markup=create_main_keyboard())
                clear_user_state(user_id)
                logger.debug(f"handle_back_button: Unknown state ({current_state}), returning to main menu for {user_id}")

        except Exception as e:
            logger.error(f"Ошибка в обработчике кнопки 'Назад': {e}")
            bot.send_message(user_id, "Произошла ошибка при возврате. Возвращаюсь в главное меню.", reply_markup=create_main_keyboard())
            clear_user_state(user_id) # Очищаем состояние при ошибке
            logger.error(f"handle_back_button: Exception occurred, returning to main menu for {user_id}")

    @bot.message_handler(func=lambda message: message.text == "🗺️ Карта Ярославля")
    def show_map(message, initial_load=True):
        """
        Показывает опции карты с различными категориями мест
        Позволяет пользователю выбрать интересующую категорию для просмотра на карте
        """
        logger.debug(f"Пользователь {message.chat.id} выбрал 'Карта Ярославля'")
        try:
            if initial_load:
                # Отправляем геолокацию центра Ярославля
                bot.send_location(
                    chat_id=message.chat.id,
                    latitude=57.626559,
                    longitude=39.893813
                )
                
                # Отправляем первое текстовое сообщение
                bot.send_message(
                    chat_id=message.chat.id,
                    text="📍 Центр Ярославля"
                )

            # Создаем клавиатуру с категориями
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("🏰 Исторический центр"))
            markup.row(types.KeyboardButton("🏥 Травмпункты"), types.KeyboardButton("🌳 Парки"))
            markup.row(types.KeyboardButton("🎭 Театры"), types.KeyboardButton("🛍️ Торговые центры"))
            markup.add(types.KeyboardButton("🔙 Назад")) # Кнопка "Назад" для возврата к меню "О городе"
            
            # Отправляем второе текстовое сообщение с клавиатурой категорий
            bot.send_message(
                chat_id=message.chat.id,
                text="Выберите категорию для просмотра мест:",
                reply_markup=markup
            )

            # Сохраняем состояние как map_options
            save_user_state(message.chat.id, {'menu': 'map_options', 'state': 'map', 'prev_menu': 'about_city_menu'})
            logger.debug(f"Map menu displayed for user {message.chat.id}")
        except Exception as e:
            logger.error(f"Ошибка в обработчике карты: {e}")
            bot.send_message(
                message.chat.id,
                text="Произошла ошибка при загрузке карты. Пожалуйста, попробуйте позже.",
                reply_markup=create_main_keyboard()
            )

    @bot.message_handler(
        func=lambda message: message.text in CATEGORY_MAP_BUTTONS_TO_KEYS.keys())
    def show_category_menu(message, category_key=None, send_category_info=True):
        """Shows category menu for places."""
        
        # Определяем ключ категории
        if category_key is None:
            category_key = CATEGORY_MAP_BUTTONS_TO_KEYS[message.text]
            current_button_text = message.text # Сохраняем исходный текст кнопки для display_name
        else:
            current_button_text = REVERSE_CATEGORY_MAP_BUTTONS_TO_KEYS.get(category_key)
            if current_button_text is None:
                logger.error(f"Не удалось найти текст кнопки для ключа категории: {category_key}")
                return # Или обработать ошибку

        # Получаем заголовок и описание категории из LOCATIONS
        category_info = LOCATIONS.get(category_key, {})
        category_title = category_info.get('category_title')
        category_description = category_info.get('category_description')

        # Если есть заголовок и описание и флаг send_category_info установлен, отправляем их
        if send_category_info and category_title and category_description:
            bot.send_message(
                chat_id=message.chat.id,
                text=f"{category_title}\n\n{category_description}",
                parse_mode='HTML'
            )
        
        # Get all places for the category, excluding metadata keys
        places = [key for key in LOCATIONS[category_key].keys() if key not in ['category_title', 'category_description']]
        
        # Create keyboard with places, using row_width=2 for better layout
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        # Add places in pairs
        for i in range(0, len(places), 2):
            row = [types.KeyboardButton(places[i])]
            if i + 1 < len(places):
                row.append(types.KeyboardButton(places[i + 1]))
            markup.row(*row)
        
        # Add back button
        markup.add(types.KeyboardButton("🔙 Назад"))
        
        # Get proper display name for the category
        display_name = {
            "🏰 Исторический центр": "достопримечательность",
            "🏥 Травмпункты": "травмпункт",
            "🌳 Парки": "парк",
            "🎭 Театры": "театр",
            "🛍️ Торговые центры": "торговый центр"
        }[current_button_text]
        
        bot.send_message(message.chat.id, f"Выберите {display_name}:", reply_markup=markup)
        # Сохраняем состояние пользователя для навигации назад
        save_user_state(message.chat.id, {'menu': 'category_places', 'prev_menu': 'map_options', 'category': category_key})

    @bot.message_handler(func=lambda message: message.text == "📞 Контакты")
    def handle_contacts(message):
        """
        Показывает контактную информацию о боте
        Включает ссылки на социальные сети и контактные данные
        """
        try:
            # Формируем текст с контактной информацией
            contacts_text = (
                "📞 <b>Контактная информация:</b>\n\n"
                "🌐 <b>Официальный сайт:</b>\n"
                "• <a href=\"https://city-yaroslavl.ru\">city-yaroslavl.ru</a>\n\n"
                " <b>Социальные сети:</b>\n"
                "• <a href=\"https://vk.com/cityyaroslavl\">ВКонтакте</a>\n"
                "• <a href=\"https://t.me/cityyaroslavl\">Telegram</a>\n"
                "• <a href=\"https://ok.ru/cityyaroslavl\">Одноклассники</a>\n\n"
                "📧 <b>Электронная почта:</b>\n"
                "• info@city-yaroslavl.ru\n\n"
                "📞 <b>Телефон:</b>\n"
                "• +7 (4852) 40-40-40\n\n"
                "🏢 <b>Адрес:</b>\n"
                "• г. Ярославль, ул. Свободы, 2"
            )

            # Отправляем сообщение с контактной информацией
            bot.send_message(
                message.chat.id,
                contacts_text,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике контактов: {e}")
            bot.send_message(
                message.chat.id,
                "Произошла ошибка при загрузке контактной информации. Пожалуйста, попробуйте позже.",
                reply_markup=create_main_keyboard()
            )

    @bot.message_handler(func=lambda message: message.text == "📍 Расположение")
    def handle_location(message):
        """
        Показывает информацию о расположении бота
        Отправляет карту с отметкой местоположения
        """
        try:
            # Координаты центра Ярославля
            latitude = 57.6261
            longitude = 39.893813

            # Отправляем сообщение с картой
            bot.send_location(
                message.chat.id,
                latitude,
                longitude,
                reply_markup=create_main_keyboard()
            )
            # Отправляем дополнительную информацию
            bot.send_message(
                message.chat.id,
                " <b>Центр Ярославля</b>\n\n"
                "Мы находимся в самом сердце города, на пересечении главных улиц.\n"
                "Добраться до нас можно:\n"
                "• На общественном транспорте\n"
                "• На автомобиле\n"
                "• Пешком от центральной площади",
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Ошибка в обработчике расположения: {e}")
            bot.send_message(
                message.chat.id,
                "Произошла ошибка при отправке информации о расположении. Пожалуйста, попробуйте позже.",
                reply_markup=create_main_keyboard()
            )

    @bot.message_handler(func=lambda message: message.text == "🆘 Помощь")
    def handle_help(message):
        """
        Показывает справочную информацию о боте
        Включает описание основных функций и инструкции по использованию
        """
        try:
            # Отправляем сообщение со справкой
            with open('Materials/helpPhoto.jpg', 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=HELP_TEXT,
                    parse_mode='HTML',
                    reply_markup=create_main_keyboard()
                )
        except Exception as e:
            logger.error(f"Ошибка в обработчике справки: {e}")
            bot.send_message(
                message.chat.id,
                "Произошла ошибка при загрузке справки. Пожалуйста, попробуйте позже.",
                reply_markup=create_main_keyboard()
            )

    @bot.message_handler(func=lambda message: message.text == "📰 Новости")
    def show_news_categories(message):
        """
        Показывает категории новостей для выбора и создает клавиатуру с доступными категориями
        """
        logger.debug(f"Пользователь {message.chat.id} выбрал 'Новости'")

        # Создаем клавиатуру для выбора категорий новостей
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(
            types.KeyboardButton("🏢 Администрация"),
            types.KeyboardButton("🚗 Транспорт")
        )
        markup.add(types.KeyboardButton("🛠️ Ремонт и благоустройство"))
        markup.row(
            types.KeyboardButton("📋 Политика"),
            types.KeyboardButton("🌤 Погода")
        )
        markup.add(types.KeyboardButton("🔙 Назад"))
        
        bot.send_message(
            message.chat.id,
            "Выберите категорию новостей:",
            reply_markup=markup
        )
        save_user_state(message.chat.id, {'state': 'news_categories'})
        logger.debug(f"Меню категорий новостей отображено для пользователя {message.chat.id}")

    @bot.message_handler(func=lambda message: message.text == "🌤 Погода")
    def handle_weather(message):
        """
        Обработчик кнопки погоды - показывает опции для получения информации о погоде
        """
        logger.debug(f"handle_weather вызван сообщением: '{message.text}'")
        try:
            weather_keyboard = create_weather_keyboard()
            bot.send_message(
                message.chat.id,
                "Выберите, что вы хотите узнать о погоде:",
                reply_markup=weather_keyboard
            )
            save_user_state(message.chat.id, {'state': 'weather_menu'})
        except Exception as e:
            logger.error(f"Ошибка в обработчике handle_weather: {e}")
            bot.send_message(
                message.chat.id,
                "Произошла ошибка при загрузке меню погоды. Пожалуйста, попробуйте позже.",
                reply_markup=create_main_keyboard()
            )

    @bot.message_handler(func=lambda message: message.text in ["🏢 Администрация", "🚗 Транспорт", "🛠️ Ремонт и благоустройство", "📋 Политика"])
    def show_news(message):
        """
        Показывает новости по выбранной пользователем категории
        Загружает последние новости и предлагает посмотреть новости за неделю
        """
        logger.debug(f"show_news вызван сообщением: '{message.text}'")
        # Извлекаем чистое название категории без эмодзи
        category_name = message.text.split(" ", 1)[1] if " " in message.text else message.text
        # Преобразуем русское название категории в ключ для запроса данных
        category_key = CATEGORY_MAPPING.get(category_name)

        if not category_key:
            bot.send_message(message.chat.id, "Извините, эта категория новостей пока недоступна.")
            return

        try:
            # Получаем новости по выбранной категории
            news_items = get_yarnews_articles(category_key)
            
            if news_items:
                # Получаем правильное склонение названия категории для отображения в сообщении
                proper_category_by = CATEGORY_NAMES.get(category_name, {}).get('by', category_name.lower())
                bot.send_message(message.chat.id, f"🗞️ Последние новости {proper_category_by}:", parse_mode='HTML')

                # Отправляем каждую новость отдельным сообщением
                for news in news_items:
                    message_text = (
                        f"<b>{news['title']}</b>\n\n"
                        f"{news['description']}\n\n"
                        f"Источник: <a href=\"{news['link']}\">YarNews</a>"
                    )
                    bot.send_message(
                        message.chat.id,
                        message_text,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )

                # Добавляем кнопку для просмотра новостей за неделю
                keyboard = types.InlineKeyboardMarkup()
                weekly_news_button = types.InlineKeyboardButton("Новости за неделю", callback_data=f"news_week_{category_name}")
                keyboard.add(weekly_news_button)
                question_message = bot.send_message(
                    chat_id=message.chat.id,
                    text="👀 Хотите посмотреть новости за последнюю неделю?",
                    reply_markup=keyboard
                )
                last_question_message_ids[message.chat.id] = question_message.message_id

            else:
                # Если новостей по категории нет
                message_text = (
                    f"😔 Пока нет новых новостей по категории {CATEGORY_NAMES[category_name]['default']}.\n\n"
                    f"👀 Хотите посмотреть новости за последнюю неделю?"
                )
                keyboard = types.InlineKeyboardMarkup()
                weekly_news_button = types.InlineKeyboardButton("Новости за неделю", callback_data=f"news_week_{category_name}")
                keyboard.add(weekly_news_button)
                question_message = bot.send_message(message.chat.id, message_text, reply_markup=keyboard, parse_mode='HTML')
                last_question_message_ids[message.chat.id] = question_message.message_id

        except Exception as e:
            proper_category = CATEGORY_NAMES.get(category_name, {}).get("by", "этой категории")
            logger.error(f"Ошибка в show_news: {e}")
            bot.send_message(message.chat.id, f"Произошла ошибка при получении новостей {proper_category}. Пожалуйста, попробуйте позже.")

    @bot.message_handler(func=lambda message: message.text == "📅 События")
    def show_event_categories(message):
        """
        Показывает пользователю меню с доступными категориями событий
        Позволяет выбрать интересующую тему для просмотра мероприятий
        """
        # Создаем пользовательскую клавиатуру для выбора категорий событий
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(
            types.KeyboardButton("🎭 Культура"),
            types.KeyboardButton("⚽ Спорт")
        )
        markup.row(
            types.KeyboardButton("📚 Образование"),
            types.KeyboardButton("🎪 Развлечения")
        )
        markup.row(
            types.KeyboardButton("🖼️ Выставки"),
            types.KeyboardButton("🎵 Концерты")
        )
        markup.add(types.KeyboardButton("🔙 Назад"))
        
        bot.send_message(
            message.chat.id,
            "Выберите категорию событий:",
            reply_markup=markup
        )
        save_user_state(message.chat.id, {'state': 'event_categories'})

    @bot.message_handler(func=lambda message: message.text in ["🎭 Культура", "⚽ Спорт", "📚 Образование", "🎪 Развлечения", "🖼️ Выставки", "🎵 Концерты"])
    def show_events(message):
        """
        Показывает события по выбранной пользователем категории
        Загружает ближайшие события и предлагает посмотреть события за неделю
        """
        try:
            # Извлекаем чистое название категории без эмодзи
            category_name = message.text.split(" ", 1)[1]
            
            # Преобразуем русское название категории в ключ для запроса данных
            category_key = EVENT_CATEGORY_MAPPING.get(category_name)
            
            if not category_key:
                bot.reply_to(message, f"Произошла ошибка при определении категории событий.")
                return

            # Получаем до 3 ближайших событий за последние 2 дня
            recent_events = get_events_by_category(category_key, limit_days=2)[:3]

            # Получаем правильное склонение названия категории для отображения в сообщении
            proper_category_by = EVENT_CATEGORY_NAMES[category_name]["by"]
            proper_category_default = EVENT_CATEGORY_NAMES[category_name]["default"]

            if recent_events:
                bot.send_message(message.chat.id, f"📅 Ближайшие события {proper_category_by}:", parse_mode='HTML')

                for event in recent_events:
                    message_text = format_event_message(event)
                    bot.send_message(message.chat.id, message_text, parse_mode="HTML", disable_web_page_preview=False)

                # Добавляем кнопку для просмотра событий за неделю
                keyboard = types.InlineKeyboardMarkup()
                weekly_events_button = types.InlineKeyboardButton("События за неделю", callback_data=f"event_week_{category_name}")
                keyboard.add(weekly_events_button)

                question_message = bot.send_message(
                    message.chat.id,
                    f"👀 Хотите посмотреть события за последнюю неделю?",
                    reply_markup=keyboard
                )
                last_question_message_ids[message.chat.id] = question_message.message_id

            else:
                # Если событий по категории нет
                message_text = (
                    f"😔 Пока нет новых событий по категории {proper_category_default}.\n\n"
                    f"👀 Хотите посмотреть события за последнюю неделю?"
                )
                keyboard = types.InlineKeyboardMarkup()
                weekly_events_button = types.InlineKeyboardButton("События за неделю", callback_data=f"event_week_{category_name}")
                keyboard.add(weekly_events_button)
                question_message = bot.send_message(message.chat.id, message_text, reply_markup=keyboard, parse_mode='HTML')
                last_question_message_ids[message.chat.id] = question_message.message_id

        except Exception as e:
            proper_category = EVENT_CATEGORY_NAMES.get(category_name, {}).get("by", "этой категории")
            logger.error(f"Ошибка в show_events: {e}")
            bot.send_message(message.chat.id, f"Произошла ошибка при получении событий {proper_category}. Пожалуйста, попробуйте позже.")

    @bot.message_handler(func=lambda message: message.text == "🏛️ О городе")
    def handle_about_city(message):
        """
        Обработчик кнопки "О городе" - показывает основную информацию о Ярославле
        """
        try:
            about_city_text = (
                "Ярославль — жемчужина Золотого кольца России\n"
                "🏛 Основан в 1010 году князем Ярославом Мудрым\n"
                "UNESCO Входит в список Всемирного наследия ЮНЕСКО\n"
                "🌊 Город на Волге с тысячелетней историей\n"
                "👥 Население: более 600 тысяч человек\n\n"
                "🏆 Культурная столица Поволжья:\n"
                "• Первый русский театр\n"
                "• Уникальные храмы и монастыри\n"
                "• Современные фестивали и выставки\n\n"
                "🏅 Город достижений:\n"
                "• Ведущие университеты и научные центры\n"
                "• Развитая медицина и образование\n"
                "• Современные технологии и инновации\n\n"
                "🌳 Комфортный город:\n"
                "• Зеленые парки и набережные\n"
                "• Современные районы\n"
                "• Богатая инфраструктура\n\n"
                "✨ Ярославль — где история встречается с современностью! ✨"
            )
            logger.debug(f"about_city_text length: {len(about_city_text)}")

            photo_path = "Materials/yaroslavl.jpg"
            with open(photo_path, "rb") as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=about_city_text,
                    parse_mode='HTML'
                )
            # Отправляем отдельное сообщение с выбором темы и инлайн-клавиатурой
            theme_message_text = "Выберите тему:"
            about_keyboard = get_about_keyboard()
            logger.debug(f"theme_message_text: '{theme_message_text}' (length: {len(theme_message_text)})")
            logger.debug(f"about_keyboard: {about_keyboard}")

            bot.send_message(
                message.chat.id,
                theme_message_text,
                reply_markup=about_keyboard
            )
            save_user_state(message.chat.id, {'state': 'about_city_menu'})
            logger.info(f"User {message.chat.id} state saved as 'about_city_menu'.")
            
        except Exception as e:
            logger.error(f"Error in handle_about_city: {e}")
            bot.send_message(
                message.chat.id,
                "Произошла ошибка при загрузке информации о городе. Пожалуйста, попробуйте позже.",
                reply_markup=create_main_keyboard()
            )
            logger.error(f"Sent error message to user {message.chat.id}.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith(('news_week_', 'event_week_')))
    def handle_week_button(call):
        """
        Обработчик кнопки 'Новости/События за неделю'
        Показывает новости или события за последнюю неделю по выбранной категории
        """
        try:
            # Отвечаем на callback-запрос, чтобы убрать крутящийся индикатор на кнопке
            bot.answer_callback_query(call.id)
            
            # Получаем тип (новости/события) и категорию из callback_data
            action_type, _, category_name = call.data.split('_')
            
            # Удаляем сообщение с вопросом
            try:
                if call.message.chat.id in last_question_message_ids:
                    bot.delete_message(
                        chat_id=call.message.chat.id,
                        message_id=last_question_message_ids[call.message.chat.id]
                    )
                    del last_question_message_ids[call.message.chat.id]
            except Exception as e:
                logger.debug(f"Error deleting question message: {e}")

            # Отправляем сообщение о загрузке
            loading_message = bot.send_message(
                call.message.chat.id,
                f"⏳ {'Загружаю новости' if action_type == 'news' else 'Загружаю события'}   ",
                reply_markup=None
            )
            message_id_to_delete = loading_message.message_id

            # Анимация загрузки
            dots_animation_frames = ["", ".", "..", "..."]
            # 4 цикла * 4 кадра * 0.3 сек = 4.8 секунд
            for _ in range(4):
                for frame in dots_animation_frames:
                    current_loading_text = f"⏳ {'Загружаю новости' if action_type == 'news' else 'Загружаю события'}{frame}"
                    try:
                        bot.edit_message_text(
                            current_loading_text,
                            chat_id=call.message.chat.id,
                            message_id=message_id_to_delete,
                            reply_markup=None
                        )
                    except telebot.apihelper.ApiTelegramException as e:
                        if "message is not modified" in str(e):
                            logger.debug(f"Message not modified: {e}")
                        else:
                            raise e
                    time.sleep(0.3)

            if action_type == 'news':
                # Получаем новости за неделю для выбранной категории
                mapped_category_name = CATEGORY_MAPPING.get(category_name)
                if not mapped_category_name:
                    logger.error(f"[HANDLER] Failed to map news category: {category_name}. Using original name.")
                    mapped_category_name = category_name

                logger.info(f"[HANDLER] Fetching news for week. Original category: {category_name}, Mapped category: {mapped_category_name}")
                news_items = get_news_by_week(mapped_category_name)
                
                if news_items:
                    # Удаляем сообщение о загрузке
                    bot.delete_message(chat_id=call.message.chat.id, message_id=message_id_to_delete)
                    
                    # Отправляем заголовок
                    bot.send_message(
                        call.message.chat.id,
                        f"📑 Последние новости {CATEGORY_NAMES[category_name]['by']} за последнюю неделю:",
                        parse_mode='HTML'
                    )
                    
                    # Отправляем каждую новость отдельным сообщением
                    for news in news_items:
                        message_text = (
                            f"<b>{news['title']}</b>\n\n"
                            f"{news['description']}\n\n"
                            f"Источник: <a href=\"{news['link']}\">YarNews</a>"
                        )
                        bot.send_message(
                            call.message.chat.id,
                            message_text,
                            parse_mode='HTML',
                            disable_web_page_preview=False
                        )
                else:
                    # Удаляем сообщение о загрузке, если новости не найдены
                    bot.delete_message(chat_id=call.message.chat.id, message_id=message_id_to_delete)
                    bot.send_message(
                        call.message.chat.id,
                        f"😔 Нет последних новостей по категории {CATEGORY_NAMES[category_name]['default']} за последнюю неделю"
                    )
                # После обработки новостей всегда показываем кнопку возврата к категориям
                show_news_categories(call.message)
                
            elif action_type == 'event':
                # Получаем события за неделю для выбранной категории
                mapped_category_name = EVENT_CATEGORY_MAPPING.get(category_name)
                if not mapped_category_name:
                    logger.error(f"[HANDLER] Failed to map event category: {category_name}. Using original name.")
                    mapped_category_name = category_name

                logger.info(f"[HANDLER] Fetching events for week. Original category: {category_name}, Mapped category: {mapped_category_name}")
                events = get_events_by_category(mapped_category_name, week_range=True)
                
                if events:
                    # Удаляем сообщение о загрузке
                    bot.delete_message(chat_id=call.message.chat.id, message_id=message_id_to_delete)
                    
                    # Отправляем заголовок
                    bot.send_message(
                        call.message.chat.id,
                        f"📅 События {EVENT_CATEGORY_NAMES[category_name]['by']} за последнюю неделю:",
                        parse_mode='HTML'
                    )
                    
                    # Отправляем каждое событие отдельным сообщением
                    for event in events:
                        message_text = format_event_message(event)
                        bot.send_message(
                            call.message.chat.id,
                            message_text,
                            parse_mode='HTML',
                            disable_web_page_preview=False
                        )
                else:
                    # Удаляем сообщение о загрузке, если события не найдены
                    bot.delete_message(chat_id=call.message.chat.id, message_id=message_id_to_delete)
                    bot.send_message(
                        call.message.chat.id,
                        f"😔 Нет последних событий по категории {EVENT_CATEGORY_NAMES[category_name]['default']} за последнюю неделю"
                    )
                # После обработки событий всегда показываем кнопку возврата к категориям
                show_event_categories(call.message)
            
            # Отвечаем на callback-запрос, чтобы убрать крутящийся индикатор на кнопке
            bot.answer_callback_query(call.id)

        except Exception as e:
            logger.error(f"Ошибка в handle_week_button: {e}")
            # В случае ошибки, также удаляем сообщение о загрузке, если оно было отправлено
            if 'message_id_to_delete' in locals():
                try:
                    bot.delete_message(chat_id=call.message.chat.id, message_id=message_id_to_delete)
                except Exception as delete_error:
                    logger.error(f"Ошибка при удалении сообщения о загрузке в обработчике handle_week_button: {delete_error}")
            bot.answer_callback_query(
                call.id,
                "Произошла ошибка при получении данных. Пожалуйста, попробуйте позже."
            )
            # Отправляем сообщение об ошибке пользователю
            bot.send_message(
                call.message.chat.id,
                "Произошла ошибка при получении данных. Пожалуйста, попробуйте позже."
            )
            # После ошибки также показываем соответствующие категории, чтобы пользователь мог продолжить работу
            if action_type == 'news':
                show_news_categories(call.message)
            elif action_type == 'event':
                show_event_categories(call.message)

    @bot.callback_query_handler(func=lambda call: call.data in ["show_weather", "weather_news"])
    def handle_weather_callback(call):
        """
        Обработчик callback-кнопок, связанных с погодой (прогноз или новости о погоде)
        """
        try:
            # Отвечаем на callback-запрос, чтобы убрать индикатор загрузки на кнопке
            bot.answer_callback_query(call.id)

            # Удаляем исходное сообщение с инлайн-клавиатурой
            try:
                bot.delete_message(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
            except Exception as e:
                logger.debug(f"Не удалось удалить исходное сообщение о погоде: {e}")

            if call.data == "show_weather":
                # Получаем текущий прогноз погоды
                weather_data = get_openmeteo_weather()
                if weather_data:
                    # Получаем текстовое описание погодных условий
                    weather_description = get_weather_description(weather_data['current']['weathercode'])
                    
                    # Форматируем полученные данные о погоде
                    weather_message = format_weather_message(weather_data)
                    
                    # Создаем клавиатуру для навигации
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.row(
                        types.KeyboardButton("🏢 Администрация"),
                        types.KeyboardButton("🚗 Транспорт")
                    )
                    markup.add(types.KeyboardButton("🛠️ Ремонт и благоустройство"))
                    markup.row(
                        types.KeyboardButton("📋 Политика"),
                    )
                    markup.add(types.KeyboardButton("🔙 Назад"))
                    
                    # Определяем путь к GIF-анимации
                    weather_code = weather_data['current']['weathercode']
                    gif_path = f"materials/weather/{weather_code}.gif"
                    
                    try:
                        # Пытаемся отправить GIF-анимацию с подписью о погоде
                        with open(gif_path, 'rb') as gif:
                            bot.send_animation(
                                chat_id=call.message.chat.id,
                                animation=gif,
                                caption=weather_message,
                                reply_markup=markup
                            )
                    except FileNotFoundError:
                        # Если GIF не найден, отправляем только текстовое сообщение
                        bot.send_message(
                            chat_id=call.message.chat.id,
                            text=weather_message,
                            reply_markup=markup
                        )
                    
                    # Генерируем и отправляем график температуры
                    hourly_chart_image = generate_hourly_temperature_graph_image(weather_data['hourly'])
                    if hourly_chart_image:
                        bot.send_photo(
                            call.message.chat.id,
                            hourly_chart_image,
                            caption="📊 График температуры на сегодня:"
                        )

                else:
                    # Сообщение, если не удалось получить данные о погоде
                    bot.send_message(
                        call.message.chat.id,
                        "Извините, не удалось получить прогноз погоды 😔",
                        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton("🔙 Назад"))
                    )
                # Возвращаемся в меню категорий новостей
                show_news_categories(call.message)
            
            elif call.data == "weather_news":
                # Получаем новости о погоде
                weather_news = get_yarnews_articles("weather", limit_days=2) 
                
                # Получаем правильное склонение для категории "Погода"
                proper_category_by = CATEGORY_NAMES.get("Погода", {}).get('by', "погоде")

                if weather_news:
                    # Отправляем заголовок для новостей о погоде
                    bot.send_message(
                        chat_id=call.message.chat.id,
                        text=f"🗞️ Последние новости {proper_category_by}:", 
                        parse_mode='HTML'
                    )
                    
                    # Отправляем каждую новость отдельным сообщением
                    for news in weather_news:
                        message_text = (
                            f"<b>{news['title']}</b>\n\n"
                            f"{news['description']}\n\n"
                            f"Источник: <a href=\"{news['link']}\">YarNews</a>"
                        )
                        bot.send_message(
                            call.message.chat.id,
                            message_text,
                            parse_mode='HTML',
                            disable_web_page_preview=False
                        )

                else:
                    # Сообщение, если нет новостей о погоде
                    message_text_no_news = (
                        f"😔 Пока нет новых новостей по категории {CATEGORY_NAMES["Погода"]['default']}.\n\n"
                    )
                    bot.send_message(
                        chat_id=call.message.chat.id,
                        text=message_text_no_news,
                        parse_mode='HTML'
                    )
                
                # Добавляем кнопку для просмотра недельных новостей о погоде
                keyboard = types.InlineKeyboardMarkup()
                weekly_news_button = types.InlineKeyboardButton(
                    "Новости за неделю",
                    callback_data="news_week_Погода"
                )
                keyboard.add(weekly_news_button)
                
                # Отправляем сообщение с вопросом и кнопкой
                question_message = bot.send_message(
                    chat_id=call.message.chat.id,
                    text="👀 Хотите посмотреть новости за последнюю неделю?", 
                    reply_markup=keyboard
                )
                last_question_message_ids[call.message.chat.id] = question_message.message_id

                # Убираем возврат в меню категорий новостей
                # show_news_categories(call.message)

        except Exception as e:
            logger.error(f"Ошибка в обработчике callback-кнопок погоды: {e}")
            bot.send_message(
                call.message.chat.id,
                "Произошла ошибка при получении данных. Пожалуйста, попробуйте позже."
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("history_"))
    def handle_history_topic(call):
        """
        Обработчик для инлайн-кнопок выбора темы истории
        Показывает информацию о гербе, архитектуре или Ярославе Мудром
        """
        # Извлекаем ключ темы из callback_data
        topic_key = call.data.split('_', 1)[1]
        # Получаем текст истории по ключу
        history_text = HISTORY_TOPICS.get(topic_key, "Информация по этой теме пока недоступна.")
        # Отправляем текст истории пользователю
        bot.send_message(call.message.chat.id, history_text, parse_mode='HTML')
        logger.info(f"Отправлена тема истории {topic_key} пользователю {call.message.chat.id}.")
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_about")
    def handle_back_to_about(call):
        """
        Обработчик кнопки "Назад" для возврата из раздела истории к меню "О городе"
        """
        # Удаляем предыдущую инлайн-клавиатуру
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None) 
        handle_about_city(call.message)
        bot.answer_callback_query(call.id)

    @bot.message_handler(func=lambda message: message.text == "📜 История Ярославля")
    def handle_history_button(message):
        """
        Обработчик кнопки "История Ярославля"
        Показывает меню для выбора конкретной темы по истории города
        """
        try:
            logger.debug(f"Пользователь {message.chat.id} выбрал 'История Ярославля' из ReplyKeyboardMarkup.")
            history_keyboard = create_history_keyboard()
            bot.send_message(
                message.chat.id,
                "Выберите тему истории:",
                reply_markup=history_keyboard
            )
            save_user_state(message.chat.id, {'state': 'history_menu', 'prev_menu': 'about_city_menu'})
        except Exception as e:
            logger.error(f"Ошибка в обработчике handle_history_button (message_handler): {e}")
            bot.send_message(message.chat.id, "Произошла ошибка при загрузке истории. Пожалуйста, попробуйте позже.")

    @bot.message_handler(func=lambda message: message.text in ["🐻 Герб", "🏛 Архитектура", "👑 Ярослав Мудрый"])
    def handle_history_message(message):
        """
        Обработчик обычных кнопок тем истории
        Отправляет текст и изображение по выбранной теме
        """
        # Словарь для сопоставления текста кнопки с ключом темы
        history_topic_mapping = {
            "🐻 Герб": "gerb",
            "🏛 Архитектура": "architecture",
            "👑 Ярослав Мудрый": "yaroslav"
        }
        topic_key = history_topic_mapping.get(message.text)

        if topic_key and topic_key in HISTORY_TOPICS:
            history_text = HISTORY_TOPICS.get(topic_key)["text"]
            # Определяем путь к изображению для выбранной темы
            photo_paths = {
                "gerb": "Materials/history_city/gerb.jpg",
                "architecture": "Materials/history_city/architecture.jpg",
                "yaroslav": "Materials/history_city/yaroslav.jpg"
            }
            photo_path = photo_paths.get(topic_key)
            if photo_path:
                # Если изображение есть, отправляем его с текстом в качестве подписи
                with open(photo_path, "rb") as photo:
                    bot.send_photo(message.chat.id, photo, caption=history_text, parse_mode='HTML')
            else:
                # Если изображения нет, отправляем только текст
                bot.send_message(message.chat.id, history_text, parse_mode='HTML')
            logger.info(f"Отправлена тема истории {topic_key} пользователю {message.chat.id}.")
            
            # После отправки информации по теме, снова показываем меню выбора темы истории
            history_keyboard = create_history_keyboard()
            bot.send_message(
                message.chat.id,
                "Выберите тему истории:",
                reply_markup=history_keyboard
            )
            save_user_state(message.chat.id, {'state': 'history_menu', 'prev_menu': 'about_city_menu'})
        else:
            # Сообщение, если тема не найдена
            bot.send_message(message.chat.id, "Информация по этой теме пока недоступна.")
            logger.warning(f"Тема истории не найдена для текста сообщения: {message.text}")

    @bot.message_handler(func=lambda message: any(
        message.text in LOCATIONS[cat] for cat in LOCATIONS
    ))
    def show_location_info(message):
        """
        Показывает подробную информацию о выбранном месте
        Включает адрес, режим работы, телефон, описание и ссылку на карту
        """
        # Словарь эмодзи для различных категорий мест
        category_emojis = {
            'shopping_centers': '🛍️',
            'attractions': '🏛️',
            'parks': '🌳',
            'theaters': '🎭',
            'trauma_centers': '🏥',
        }
        # Словарь с приглашениями для выбора следующего места по категории
        category_prompts = {
            'attractions': 'Выберите исторический центр:',
            'trauma_centers': 'Выберите травмпункт:',
            'parks': 'Выберите парк:',
            'theaters': 'Выберите театр:',
            'shopping_centers': 'Выберите торговый центр:'
        }
        # Проходим по всем категориям мест
        for category, places in LOCATIONS.items():
            if message.text in places:
                data = places[message.text]
                emoji = category_emojis.get(category, '📍')
                text = f"{emoji} <b>{message.text}</b>\n"
                # Добавляем адрес, если он есть
                if 'address' in data:
                    text += f"Адрес: {data['address']}\n"
                # Добавляем режим работы, если он есть
                if 'working_hours' in data:
                    text += f"Режим: {data['working_hours']}\n"
                # Добавляем телефон, если он есть
                if 'phone' in data:
                    text += f"Тел: {data['phone']}\n"
                # Добавляем информацию (описание), если оно есть
                if 'description' in data:
                    text += f"\nℹ️ <b>Информация:</b>\n"
                    desc = data['description']
                    # Если описание уже содержит маркеры пунктов или переводы строк, обрабатываем его как список
                    if any(sep in desc for sep in ['•', '\n', ';']):
                        lines = [l.strip('• ').strip() for l in desc.replace(';', '\n').split('\n') if l.strip()]
                    else:
                        lines = [l.strip() for l in desc.split(',') if l.strip()]
                    for line in lines:
                        text += f"• {line}\n"
                # Добавляем ссылку на Яндекс.Карты, если есть координаты
                if 'lat' in data and 'lon' in data:
                    yandex_url = f"https://yandex.ru/maps/?ll={data['lon']}%2C{data['lat']}&z=16&pt={data['lon']},{data['lat']},pm2rdm"
                    text += f"\n🗺️ <a href=\"{yandex_url}\">Показать на карте</a>"
                # Отправляем сформированное сообщение с информацией о месте
                bot.send_message(message.chat.id, text, parse_mode='HTML', disable_web_page_preview=False)
                # После информации о месте выводим приглашение выбрать что-то еще из той же категории
                prompt = category_prompts.get(category, "Выберите место:")
                bot.send_message(message.chat.id, prompt)
                # Сохраняем состояние пользователя
                save_user_state(message.chat.id, {'menu': 'location_info', 'prev_menu': 'category_places', 'category': category})
                break

    @bot.callback_query_handler(func=lambda call: call.data in ["daily_news", "daily_events"])
    def handle_daily_notification_buttons(call):
        """
        Обработчик нажатий на кнопки в ежедневном уведомлении.
        При нажатии на кнопку:
        - "Новости" - показывает категории новостей
        - "События" - показывает категории событий
        После нажатия удаляет inline клавиатуру из сообщения.
        """
        try:
            if call.data == "daily_news":
                show_news_categories(call.message)
            elif call.data == "daily_events":
                show_event_categories(call.message)
            
            # Удаляем inline клавиатуру после нажатия, чтобы пользователь не мог нажать кнопку повторно
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике кнопок ежедневного уведомления: {e}")
            bot.answer_callback_query(
                call.id,
                "Произошла ошибка. Пожалуйста, попробуйте позже.",
                show_alert=True
            )

    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        """
        Обработчик всех сообщений пользователя.
        Обновляет время последней активности пользователя в базе данных
        при каждом его взаимодействии с ботом.
        """
        try:
            update_last_active(message.chat.id)
        except Exception as e:
            logger.error(f"Ошибка при обновлении времени активности: {e}")

# Экспортируем объекты bot и logger для использования в других модулях проекта
__all__ = ['bot', 'logger'] 