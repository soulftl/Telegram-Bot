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

from config import BOT_TOKEN, ADMIN_IDS, NEWS_CATEGORIES, NEWS_CATEGORY_NAMES, NEWS_STOPWORDS, NEWS_SOURCES, YAROSLAVL_CENTER, YAROSLAVL_CENTER_MAP_IMAGE_URL, MAP_CATEGORY_MAPPING, REVERSE_MAP_CATEGORY_MAPPING, CLEAN_CATEGORY_NAME_MAPPING, EVENT_CATEGORY_MAPPING, REVERSE_CATEGORY_MAPPING, REVERSE_EVENT_CATEGORY_MAPPING
from news import get_yarnews_articles, get_weather_news, get_weekly_news
from weather import get_openmeteo_weather, format_weather_message, get_weather_description, generate_temperature_graph
from events import get_events_by_category, format_event_message, event_types
from locations import get_locations_by_category, get_location_info, LOCATIONS
from about_city import YAROSLAVL_INFO
from history_parser import HistoryParser
from keyboards import create_main_keyboard, create_about_city_keyboard, create_location_keyboard, create_support_keyboard, create_admin_panel_keyboard, create_map_keyboard, create_history_keyboard, create_two_column_keyboard, create_events_keyboard

from telebot.storage import StateMemoryStorage

# Инициализация бота с хранилищем состояний
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)

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

def create_main_keyboard():
    """Create main menu keyboard."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("📰 Новости"))
    keyboard.row(
        types.KeyboardButton("🏛️ О городе"),
        types.KeyboardButton("📅 События")
    )
    keyboard.add(types.KeyboardButton("🆘 Помощь"))
    return keyboard

def create_news_keyboard():
    """Create keyboard for news section."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("📰 Общие новости"))
    keyboard.add(types.KeyboardButton("🚌 Транспорт"))
    keyboard.add(types.KeyboardButton("🏗 Строительство"))
    keyboard.add(types.KeyboardButton("🏛 Культура"))
    keyboard.add(types.KeyboardButton("🌤 Погода"))
    keyboard.add(types.KeyboardButton("🏢 Администрация"))
    keyboard.add(types.KeyboardButton("🔙 Назад"))
    return keyboard

def create_about_city_keyboard():
    """Create keyboard for About City section."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        types.KeyboardButton("🗺️ Карта Ярославля"),
        types.KeyboardButton("📚 История Ярославля")
    )
    keyboard.add(types.KeyboardButton("🔙 Назад"))
    return keyboard

def create_events_keyboard():
    """Create keyboard for events section."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        types.KeyboardButton("🎭 Культура"),
        types.KeyboardButton("⚽ Спорт")
    )
    keyboard.row(
        types.KeyboardButton("📚 Образование"),
        types.KeyboardButton("🎪 Развлечения")
    )
    keyboard.row(
        types.KeyboardButton("🖼️ Выставки"),
        types.KeyboardButton("🎵 Концерты")
    )
    keyboard.add(types.KeyboardButton("🔙 Назад"))
    return keyboard

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

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name or message.from_user.username or "гость"
    welcome_text = f"👋 Добро пожаловать в бот новостей Ярославля, {user_name}!"
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=create_main_keyboard()
    )
    save_user_state(message.chat.id, {'state': 'main_menu'})

@bot.message_handler(commands=['help'])
def handle_help(message):
    """Обработчик команды /help."""
    help_text = (
        "🤖 Я бот для жителей Ярославля. Вот что я умею:\n\n"
        "📰 Новости:\n"
        "- Показывать новости\n"
        "- Фильтровать новости по категориям\n"
        "- Отправлять ежедневные дайджесты\n\n"
        "🌤 Погода:\n"
        "- Показывать текущую погоду\n"
        "- Прогноз на день\n"
        "- Оповещения о погодных изменениях\n\n"
        "📅 События:\n"
        "- Афиша мероприятий\n"
        "- Культурные события\n"
        "- Спортивные соревнования\n\n"
        "🎯 Достижения:\n"
        "- Отслеживание активности\n"
        "- Награды за участие\n\n"
        "⚙️ Настройки:\n"
        "- Выбор категорий новостей\n"
        "- Время уведомлений\n"
        "- Язык интерфейса\n\n"
        "Используйте меню для навигации 👇"
    )
    
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    """Обработчик команды /admin."""
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔️ У вас нет доступа к этой команде.")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📊 Статистика"))
    markup.add(types.KeyboardButton("📢 Рассылка"))
    markup.add(types.KeyboardButton("⚙️ Настройки бота"))
    markup.add(types.KeyboardButton("🔙 Назад"))
    
    bot.send_message(
        message.chat.id,
        "Панель администратора",
        reply_markup=markup
    )
    save_user_state(message.chat.id, {'state': 'main_menu'})

@bot.message_handler(func=lambda message: message.text == "🔙 Назад")
def handle_back_button(message):
    """Handle back button press."""
    user_state = get_user_state(message.chat.id)
    current_state = user_state.get('state', 'main_menu')
    
    if current_state == 'news_menu':
        bot.send_message(
            message.chat.id,
            "Выберите раздел:",
            reply_markup=create_main_keyboard()
        )
        save_user_state(message.chat.id, {'state': 'main_menu'})
    elif current_state == 'about_city_menu':
        bot.send_message(
            message.chat.id,
            "Выберите раздел:",
            reply_markup=create_main_keyboard()
        )
        save_user_state(message.chat.id, {'state': 'main_menu'})
    elif current_state == 'events_menu':
        bot.send_message(
            message.chat.id,
            "Выберите раздел:",
            reply_markup=create_main_keyboard()
        )
        save_user_state(message.chat.id, {'state': 'main_menu'})
    else:
        bot.send_message(
            message.chat.id,
            "Выберите раздел:",
            reply_markup=create_main_keyboard()
        )
        save_user_state(message.chat.id, {'state': 'main_menu'})

@bot.message_handler(func=lambda message: message.text == "📰 Новости")
def show_news_menu(message):
    """Show news menu."""
    bot.send_message(
        message.chat.id,
        "Выберите категорию новостей:",
        reply_markup=create_news_keyboard()
    )
    save_user_state(message.chat.id, {'state': 'news_menu'})

@bot.message_handler(func=lambda message: message.text in ["📰 Общие новости", "🚌 Транспорт", "🏗 Строительство", "🏛 Культура", "🌤 Погода", "🏢 Администрация"])
def handle_news_category(message):
    """Handle news category selection."""
    category_mapping = {
        "📰 Общие новости": "general",
        "🚌 Транспорт": "transport",
        "🏗 Строительство": "construction",
        "🏛 Культура": "culture",
        "🌤 Погода": "weather",
        "🏢 Администрация": "administration"
    }
    
    category = category_mapping.get(message.text)
    if category:
        news = get_yarnews_articles(category)
        if news:
            for article in news[:5]:  # Show only 5 most recent articles
                bot.send_message(
                    message.chat.id,
                    f"📰 *{article['title']}*\n\n{article['text']}\n\n🔗 [Читать далее]({article['url']})",
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
        else:
            bot.send_message(
                message.chat.id,
                "😔 К сожалению, новости по этой категории временно недоступны."
            )
    else:
        bot.send_message(
            message.chat.id,
            "❌ Неизвестная категория новостей."
        )

@bot.message_handler(func=lambda message: message.text == "📈 Новости за неделю")
def handle_weekly_news(message):
    """Handle weekly news request."""
    bot.send_message(message.chat.id, "Загружаю новости за неделю...⏳")
    try:
        articles = get_weekly_news()
        if articles:
            for article in articles:
                bot.send_message(
                    message.chat.id,
                    f"📰 {article['title']}\n\n{article['description']}\n\n🔗 {article['link']}",
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
        else:
            bot.send_message(message.chat.id, "К сожалению, новости за неделю не найдены.")
    except Exception as e:
        logger.error(f"Error fetching weekly news: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при получении недельных новостей.")

@bot.message_handler(func=lambda message: message.text == "🌦 Новости о погоде")
def handle_weather_news(message):
    """Handle weather news request."""
    bot.send_message(message.chat.id, "Загружаю новости о погоде...⏳")
    try:
        articles = get_weather_news()
        if articles:
            for article in articles:
                bot.send_message(
                    message.chat.id,
                    f"🌦 {article['title']}\n\n{article['description']}\n\n🔗 {article['link']}",
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
        else:
            bot.send_message(message.chat.id, "К сожалению, новости о погоде не найдены.")
    except Exception as e:
        logger.error(f"Error fetching weather news: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при получении новостей о погоде.")

@bot.message_handler(func=lambda message: message.text == "🏛️ О городе")
def show_city_info(message):
    """Show information about Yaroslavl."""
    try:
        detailed_text = (
            "🏛️ Ярославль — жемчужина Золотого кольца России\n\n"
            "📜 Основан в 1010 году князем Ярославом Мудрым\n"
            "🌟 Входит в список Всемирного наследия ЮНЕСКО\n\n"
            "🌊 Город на Волге с тысячелетней историей\n"
            "👥 Население: более 600 тысяч человек\n\n"
            "🎭 Культурная столица Поволжья:\n"
            "• Первый русский театр\n"
            "• Уникальные храмы и монастыри\n"
            "• Современные фестивали и выставки\n\n"
            "🏆 Город достижений:\n"
            "• Ведущие университеты и научные центры\n"
            "• Развитая медицина и образование\n"
            "• Современные технологии и инновации\n\n"
            "🌳 Комфортный город:\n"
            "• Зеленые парки и набережные\n"
            "• Современные районы\n"
            "• Богатая инфраструктура\n\n"
            "✨ Ярославль — где история встречается с современностью! ✨"
        )

        bot.send_message(
            message.chat.id,
            detailed_text,
            reply_markup=create_about_city_keyboard()
        )
        save_user_state(message.chat.id, {'state': 'about_city_menu'})

    except Exception as e:
        logger.error(f"Error showing city info: {e}")
        bot.reply_to(message, "Извините, произошла ошибка при получении информации о городе.")

@bot.message_handler(func=lambda message: message.text == "📅 События")
def show_events_menu(message):
    """Show events menu."""
    bot.send_message(
        message.chat.id,
        "Выберите категорию событий:",
        reply_markup=create_events_keyboard()
    )
    save_user_state(message.chat.id, {'state': 'events_menu'})

@bot.message_handler(func=lambda message: message.text in ["🎭 Культура", "⚽ Спорт", "📚 Образование", "🎪 Развлечения", "🖼️ Выставки", "🎵 Концерты"])
def handle_event_category(message):
    """Handle event category selection."""
    category = message.text
    bot.send_message(message.chat.id, f"Загружаю события категории {category}...⏳")
    try:
        events = get_events_by_category(category)
        if events:
            for event in events:
                bot.send_message(
                    message.chat.id,
                    format_event_message(event),
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
        else:
            bot.send_message(message.chat.id, f"К сожалению, события категории {category} не найдены.")
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при получении событий.")

@bot.message_handler(func=lambda message: message.text == "🆘 Помощь")
def handle_help(message):
    """Handle help request."""
    help_text = (
        "🛟 Для получения технической поддержки перейдите в наш бот поддержки:\n\n"
        "✨ @NovostYARHelpBot\n\n"
        "В боте поддержки вы можете:\n"
        "📝 Создать обращение\n"
        "📋 Просматривать свои обращения\n"
        "💬 Общаться со специалистами поддержки\n\n"
        "Мы постараемся ответить вам как можно быстрее! 🚀"
    )
    bot.send_message(message.chat.id, help_text)

# Catch-all message handler for unknown commands/messages without specific state
@bot.message_handler(func=lambda message: True, state=None)
def handle_undefined_messages(message):
    user_id = message.from_user.id
    logger.info(f"User {user_id} sent an undefined message: {message.text}")
    bot.send_message(message.chat.id, "Извините, я не понял вашу команду. Пожалуйста, используйте кнопки меню или команду /start.", reply_markup=create_main_keyboard())

# Catch-all message handler for unknown commands/messages within a state
@bot.message_handler(func=lambda message: True, state='*' # Handles all messages if state is not None
)
def handle_all_messages_with_state(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    current_state = get_user_state(chat_id).get('state', 'main_menu')
    logger.info(f"User {user_id} (State: {current_state}) sent message: {message.text}")

def run_main_bot_polling():
    """Запускает бесконечный опрос основного бота."""
    logger.info("Starting main bot polling...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Error in main bot polling: {e}")
        time.sleep(5)
        run_main_bot_polling()

def get_route_schedule(route_number, stop_name, transport_type):
    """Получение расписания для конкретного маршрута и остановки"""
    try:
        stop_name_lower = stop_name.lower().strip()
        stop_name_variants = [
            stop_name_lower,
            stop_name_lower.replace('улица', 'ул.'),
            stop_name_lower.replace('ул.', 'улица'),
            stop_name_lower.replace('улица', ''),
            stop_name_lower.replace('ул.', ''),
            f'отпр. от {stop_name_lower}',
            'конечная остановка',
            'конечная',
            'ул. чкалова',
            'улица чкалова',
            'чкалова',
            'ул чкалова',
            'улица чкалова (конечная)',
            'ул. чкалова (конечная)',
            'ул. чкалова (конечная остановка)',
            'улица чкалова (конечная остановка)',
            'ул. чкалова конечная',
            'улица чкалова конечная',
            'ул. чкалова (к)',
            'улица чкалова (к)',
            'ул. чкалова к',
            'улица чкалова к',
            'отпр. от ул. чкалова',
            'отпр. от улица чкалова'
        ]
        stop_name_variants.extend([v.capitalize() for v in stop_name_variants])
        
        logger.info(f"Варианты названия остановки для поиска: {stop_name_variants}")

        if transport_type == 'bus':
            base_url = "https://yatrans.ru/?page_id=24"
        elif transport_type == 'tram':
            base_url = "https://yatrans.ru/?page_id=249"
        elif transport_type == 'trolleybus':
            base_url = "https://yatrans.ru/?page_id=26"
        else:
            return "Неизвестный тип транспорта"

        logger.info(f"Загрузка страницы с маршрутами для {transport_type} по URL: {base_url}")

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(30)
        
        try:
            driver.get(base_url)
            logger.info("Страница загружена, ожидаем загрузку контента...")
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "raspisaniel"))
            )
            
            page_title = driver.title
            logger.info(f"Заголовок страницы: {page_title}")
            
            if "расписание" not in page_title.lower() or transport_type not in page_title.lower():
                 logger.error("Неверная страница загружена для выбора маршрута")
                 return "Ошибка загрузки страницы маршрутов"
            
            if transport_type == 'tram':
                route_links = driver.find_elements(By.CLASS_NAME, "rasp_link")
                logger.info(f"Найдено {len(route_links)} ссылок на маршруты")
                
                route_found = False
                for link in route_links:
                    link_text = link.text.strip()
                    logger.info(f"Проверяем маршрут: {link_text}")
                    if link_text == route_number or (route_number.endswith('к') and link_text == route_number[:-1]):
                        route_found = True
                        logger.info(f"Найдена ссылка для маршрута {route_number}")
                        link.click()
                        break
                
                if not route_found:
                    logger.error(f"Маршрут {route_number} не найден")
                    return f"Маршрут {route_number} не найден"
            else:
                route_link_xpath = f"//a[contains(@class, 'rasp_link') and contains(@href, 'anc={route_number}')]"
                try:
                    route_link = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, route_link_xpath))
                    )
                    logger.info(f"Найдена ссылка для маршрута {route_number}")
                    route_link.click()
                except TimeoutException:
                    logger.error(f"Timeout при поиске ссылки маршрута {route_number}")
                    return f"Маршрут {route_number} не найден"
            
            logger.info(f"Клик по ссылке маршрута {route_number}")
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "raspisaniel"))
            )
            logger.info("Контейнеры расписания загружены")
            
            page_source = driver.page_source
            logger.info("HTML-код страницы получен")
            
            soup = BeautifulSoup(page_source, 'html.parser')
            
            schedule_box = None
            for stop_var in stop_name_variants:
                try:
                    stop_element = soup.find('h4', string=lambda text: text and stop_var.lower() in text.lower())
                    if stop_element:
                        schedule_box = stop_element.find_next_sibling('div', class_='rasp-rejs_box')
                        if not schedule_box:
                            schedule_box = stop_element.find_parent('div', class_='rasp-rejs_box')
                        if schedule_box:
                            logger.info(f"Найден блок расписания для остановки: {stop_var}")
                        break
                except Exception as e:
                    logger.debug(f"Ошибка при поиске элемента остановки '{stop_var}': {e}")
            
            if not schedule_box:
                logger.warning(f"Расписание для остановки '{stop_name}' не найдено для маршрута {route_number}.")
                return f"Расписание для остановки '{stop_name}' на маршруте {route_number} не найдено."

            schedule_items = schedule_box.find_all('div', class_='rasp-rejs_time')
            
            if not schedule_items:
                logger.warning(f"Элементы расписания не найдены в блоке для остановки '{stop_name}' на маршруте {route_number}.")
                return f"Расписание для остановки '{stop_name}' на маршруте {route_number} пока недоступно."

            schedule_text = f"Расписание маршрута {route_number} на остановке \'{stop_name}\':\n"
            for item in schedule_items:
                time_text = item.get_text(strip=True)
                if time_text:
                    schedule_text += f"- {time_text}\n"
            
            return schedule_text
            
        except TimeoutException as e:
            logger.error(f"Ошибка таймаута при загрузке страницы или поиске элемента: {e}")
            return "Превышено время ожидания загрузки расписания. Попробуйте еще раз."
        except NoSuchElementException as e:
            logger.error(f"Элемент не найден на странице: {e}")
            return "Не удалось найти необходимый элемент на странице расписания. Возможно, структура сайта изменилась."
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении расписания транспорта: {e}")
            return "Произошла ошибка при получении расписания транспорта. Пожалуйста, попробуйте позже."
        finally:
            driver.quit()
            logger.info("Браузер Selenium закрыт.")
            
    except Exception as e:
        logger.error(f"Критическая ошибка в get_route_schedule: {e}")
        return "Произошла критическая ошибка при попытке получить расписание." 

if __name__ == "__main__":
    run_main_bot_polling() 