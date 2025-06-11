import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

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

# Dictionary mapping event keywords to their display names with emojis
event_types = {
    "концерт": "Концерт 🎵",
    "выставка": "Выставка 🖼️",
    "фестиваль": "Фестиваль 🎉",
    "праздник": "Праздник 🎊",
    "спектакль": "Спектакль 🎭",
    "кино": "Кино 🎬",
    "театр": "Театр 🎟️",
    "лекция": "Лекция 📚",
    "семинар": "Семинар 📝",
    "конференция": "Конференция 👥",
    "мастер-класс": "Мастер-класс 🎨",
    "турнир": "Турнир 🏆",
    "соревнование": "Соревнование 🏅",
    "игра": "Игра 🎮",
    "мероприятие": "Мероприятие 📅"
}

def get_events_by_category(category, limit_days=1, specific_date=None, week_range=False):
    """Fetch events from yarnews.net."""
    url = "https://www.yarnews.net/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    event_keywords = {
        "culture": {
            "keywords": [
                "выставка", "концерт", "спектакль", "театр", "музей", "галерея",
                "культурный", "творческий", "искусство", "музыкальный", "литературный", "поэтический",
                "художественный", "творческая встреча", "культурная программа", "культурное событие",
                "открытие выставки", "перформанс", "инсталляция",
                "библиотека"
            ],
            "negative_keywords": [
                "пожар", "ДТП", "авария", "криминал", "происшествие", "смерть", "убийство",
                "суд", "тюрьма", "кража", "мошенничество", "взрыв", "теракт", "нападение",
                "задержание", "расследование", "штраф", "иск", "жалоба", "скандал", "забастовка"
            ]
        },
        "sport": {
            "keywords": [
                "соревнование", "турнир", "чемпионат", "спортивный", "матч", "победа",
                "спорт", "тренировка", "сбор", "олимпиада", "спартакиада", "эстафета", "забег",
                "пробег", "кросс", "соревнования", "спортивное мероприятие",
                "спортивный праздник", "спортивный фестиваль", "спортивный турнир", "спортивные игры",
                "спортивный матч", "спортивное соревнование", "спортивный сбор", "спортивная тренировка",
                "Локомотив", "КХL", "хоккей"
            ],
            "negative_keywords": [
                "пожар", "ДТП", "авария", "криминал", "происшествие", "смерть", "убийство",
                "суд", "тюрьма", "кража", "мошенничество", "взрыв", "теракт", "нападение",
                "задержание", "расследование", "штраф", "иск", "жалоба", "скандал", "забастовка",
                "травма"
            ]
        },
        "education": {
            "keywords": [
                "лекция", "семинар", "конференция", "форум", "образование", "обучение", "курс",
                "школа", "университет", "академия", "институт", "колледж", "училище", "лицей",
                "гимназия", "образовательный", "учебный", "научный", "исследование", "проект",
                "встреча", "дискуссия", "круглый стол", "мастер-класс", "тренинг", "практикум"
            ],
            "negative_keywords": [
                "пожар", "ДТП", "авария", "криминал", "происшествие", "смерть", "убийство",
                "суд", "тюрьма", "кража", "мошенничество", "взрыв", "теракт", "нападение",
                "задержание", "расследование", "штраф", "иск", "жалоба", "скандал", "забастовка"
            ]
        },
        "entertainment": {
            "keywords": [
                "развлечение",
                "игра",
                "празднование", "торжество",
                "вечеринка", "дискотека", "карнавал", "маскарад", "бал", "праздничный", "развлекательный",
                "досуговый", "досуг", "отдых", "развлечения",
                "досуговое мероприятие", "праздничная программа", "развлекательная программа", "досуговая программа"
            ],
            "negative_keywords": [
                "пожар", "ДТП", "авария", "криминал", "происшествие", "смерть", "убийство",
                "суд", "тюрьма", "кража", "мошенничество", "взрыв", "теракт", "нападение",
                "задержание", "расследование", "штраф", "иск", "жалоба", "скандал", "забастовка"
            ]
        },
        "exhibitions": {
            "keywords": [
                "выставка", "экспозиция", "экспонат", "галерея", "музей", "художественный", "искусство",
                "картина", "скульптура", "фотография", "инсталляция", "перформанс", "арт",
                "художник", "скульптор", "фотограф", "дизайнер", "архитектор", "художественная выставка",
                "фотовыставка", "скульптурная выставка", "арт-выставка", "художественная галерея", "музейная экспозиция",
                "художественная экспозиция", "творческая выставка"
            ],
            "negative_keywords": [
                "пожар", "ДТП", "авария", "криминал", "происшествие", "смерть", "убийство",
                "суд", "тюрьма", "кража", "мошенничество", "взрыв", "теракт", "нападение",
                "задержание", "расследование", "штраф", "иск", "жалоба", "скандал", "забастовка"
            ]
        },
        "concerts": {
            "keywords": [
                "концерт", "выступление", "музыка", "музыкальный", "оркестр", "ансамбль", "группа",
                "исполнитель", "певец", "певица", "музыкант", "композитор", "дирижер", "солист",
                "вокалист", "инструменталист", "музыкальное выступление", "музыкальный концерт",
                "музыкальное мероприятие", "музыкальный фестиваль", "музыкальный праздник", "музыкальное шоу",
                "музыкальная программа", "музыкальное представление", "музыкальное действо", "музыкальное событие"
            ],
            "negative_keywords": [
                "пожар", "ДТП", "авария", "криминал", "происшествие", "смерть", "убийство",
                "суд", "тюрьма", "кража", "мошенничество", "взрыв", "теракт", "нападение",
                "задержание", "расследование", "штраф", "иск", "жалоба", "скандал", "забастовка"
            ]
        }
    }
    
    # Список слов, которые указывают на административные новости
    administrative_keywords = [
        "министр", "губернатор", "мэр", "администрация", "департамент", "управление",
        "советник", "заместитель", "руководитель", "директор", "начальник", "перевод",
        "назначение", "отставка", "увольнение", "прием", "встреча", "совещание",
        "утверждение", "проект", "строительство", "дорога", "магистраль", "трасса",
        "разработка", "планирование", "реконструкция", "ремонт", "благоустройство",
        "комиссия", "заседание", "доклад", "отчет", "решение", "постановление", "распоряжение",
        "омбудсмен", "форум",
        "конкурс", "тендер", "закупка", "госзакупка", "контракт", "муниципальный контракт",
        "бюджет", "финансы", "экономика", "инвестиции", "предприятие", "бизнес", "налог", "субсидия",
        "жкх", "коммунальный", "тариф", "услуги",
        "городской", "областной", "региональный", "районный", "муниципальный", # Re-adding with caution, rely more on other keywords
        "открытие", "закрытие", "начало", "завершение", "итоги", "планы", "перспективы",
        "создание", "развитие", "реализация", "проведение", "организация"
    ]
    
    # Общие негативные ключевые слова для всех категорий событий (для фильтрации "негативных" новостей)
    general_negative_keywords = [
        "пожар", "ДТП", "авария", "криминал", "происшествие", "смерть", "убийство",
        "суд", "тюрьма", "кража", "мошенничество", "взрыв", "теракт", "нападение",
        "задержание", "расследование", "штраф", "иск", "жалоба", "скандал", "забастовка",
        "конфликт", "протест", "запрет", "отмена", "закрытие", "ликвидация", "угроза",
        "катастрофа", "чрезвычайная ситуация", "эвакуация", "пострадавшие", "жертвы",
        "больница", "травма", "болезнь", "эпидемия", "карантин", "ограничения",
        "отключение", "прорыв", "утечка", "загрязнение", "отходы", "свалка",
        "долг", "банкротство", "убытки", "сокращение",
        "уголовное дело", "административное дело", "проверка", "расследование"
    ]
    
    category_data = event_keywords.get(category)
    keywords = category_data.get("keywords", []) if category_data else []
    # Объединяем специфичные негативные ключевые слова с общими
    negative_keywords = list(set(category_data.get("negative_keywords", []) if category_data else []).union(set(general_negative_keywords)))

    if not keywords and category:
        logging.info(f"[EVENTS] No keywords found for category: {category}. Returning empty list.")
        return []

    try:
        logging.info(f"[EVENTS] Attempting to fetch events for category: {category}, week_range: {week_range}")

        page_source = None

        if week_range:
            logging.info("[EVENTS] Using Selenium for weekly events.")
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(45)

            try:
                driver.get(url)
                logging.info("[EVENTS] Page loaded successfully with Selenium.")

                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "news-feed"))
                )
                logging.info("[EVENTS] Initial news feed loaded with Selenium.")

                # --- Combined Scroll and Click Strategy (for weekly events) ---
                scroll_and_click_cycles = 25 # Increased from 15 to 25
                scroll_amount = 700

                logging.info(f"[EVENTS] Starting scroll and click cycles ({scroll_and_click_cycles} cycles) for events.")

                for cycle in range(scroll_and_click_cycles):
                    logging.info(f"[EVENTS] Scroll/Click cycle {cycle + 1} of {scroll_and_click_cycles}")
                    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    time.sleep(3)

                    selectors = [
                        "//button[contains(@class, 'js-nexter')]",
                        "//button[contains(text(), 'больше новостей')]",
                        "//button[contains(text(), 'еще новости')]",
                        "//a[contains(@class, 'js-nexter')]",
                        "//a[contains(text(), 'больше новостей')]",
                        "//a[contains(text(), 'еще новости')]",
                        "//div[contains(@class, 'js-nexter')]",
                        "//div[contains(text(), 'больше новостей')]",
                        "//div[contains(text(), 'еще новости')]",
                    ]

                    buttons = []
                    for selector in selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, selector)
                            buttons.extend(elements)
                        except Exception as e:
                            logging.debug(f"[EVENTS] Error finding elements with selector {selector}: {str(e)}")
                            continue

                    seen = set()
                    buttons = [x for x in buttons if not (x in seen or seen.add(x))]

                    logging.info(f"[EVENTS] Found {len(buttons)} potential 'больше новостей' buttons in cycle {cycle + 1}")

                    clicked_count = 0
                    for button in buttons:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            time.sleep(1)

                            is_visible = driver.execute_script("""
                                const rect = arguments[0].getBoundingClientRect();
                                const style = window.getComputedStyle(arguments[0]);
                                return (
                                    rect.top >= 0 &&
                                    rect.left >= 0 &&
                                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                                    rect.right <= (window.innerWidth || document.documentElement.clientWidth) &&
                                    style.display !== 'none' &&
                                    style.visibility !== 'hidden' &&
                                    style.opacity !== '0'
                                );
                            """, button)

                            if is_visible:
                                try:
                                    driver.execute_script("arguments[0].click();", button)
                                    clicked_count += 1
                                    logging.info(f"[EVENTS] Successfully clicked button {clicked_count} using JavaScript in cycle {cycle + 1}")
                                except Exception as e1:
                                    try:
                                        from selenium.webdriver.common.action_chains import ActionChains
                                        ActionChains(driver).move_to_element(button).click().perform()
                                        clicked_count += 1
                                        logging.info(f"[EVENTS] Successfully clicked button {clicked_count} using Actions in cycle {cycle + 1}")
                                    except Exception as e2:
                                        try:
                                            button.click()
                                            clicked_count += 1
                                            logging.info(f"[EVENTS] Successfully clicked button {clicked_count} using direct click in cycle {cycle + 1}")
                                        except Exception as e3:
                                            logging.error(f"[EVENTS] All click methods failed for button in cycle {cycle + 1}: {str(e1)}, {str(e2)}, {str(e3)}")
                                            continue

                                time.sleep(2)

                            else:
                                logging.debug(f"[EVENTS] Button found but not visible/clickable in viewport in cycle {cycle + 1}")

                        except Exception as e:
                            logging.error(f"[EVENTS] Error processing button in cycle {cycle + 1}: {str(e)}")
                            continue

                    logging.info(f"[EVENTS] Clicked {clicked_count} 'больше новостей' buttons in cycle {cycle + 1}")

                    if clicked_count == 0 and cycle > 0:
                        logging.info("[EVENTS] No more 'больше новостей' buttons found or clickable. Ending cycles.")
                        break

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                logging.info("[EVENTS] Completed scroll/click cycles and scrolled to the bottom.")
                # --- End Combined Strategy ---

                page_source = driver.page_source
                logging.info("[EVENTS] Got final page source after all loading attempts with Selenium.")

            except TimeoutException:
                logging.error("[EVENTS] Timeout while loading page with Selenium")
                return []
            except Exception as e:
                logging.error(f"[EVENTS] Error during page processing with Selenium: {e}")
                return []
            finally:
                driver.quit()

        else:
            # Use requests and BeautifulSoup for recent events (faster)
            logging.info("[EVENTS] Using requests and BeautifulSoup for recent events.")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status() # Raise an exception for bad status codes
            page_source = response.text
            logging.info("[EVENTS] Got page source with requests.")

        soup = BeautifulSoup(page_source, 'html.parser')

        news_item_elements = soup.select(".news-feed-item") # Assuming event items also use this class
        logging.info(f"[EVENTS] Found {len(news_item_elements)} news items with BeautifulSoup after initial fetch.")

        events = []
        seen_urls = set() # Add set to track seen URLs
        today = datetime.now()
        today_str = today.strftime("%d.%m.%Y")
        yesterday = (today - timedelta(days=1)).strftime("%d.%m.%Y")

        if specific_date:
            try:
                specific_date_dt = datetime.strptime(specific_date, "%d.%m.%Y")
                date_limit = specific_date_dt
                date_max = specific_date_dt + timedelta(days=1)
                logging.info(f"[EVENTS] Filtering for specific date: {specific_date_dt.date().strftime('%d.%m.%Y')}")
            except ValueError:
                logging.error(f"[EVENTS] Invalid specific date format: {specific_date}")
                return []
        elif week_range:
            date_limit = today - timedelta(days=7)
            date_max = today # Changed from today + timedelta(days=1) to just today
            logging.info(f"[EVENTS] Filtering for week range: {date_limit.date().strftime('%d.%m.%Y')} - {date_max.date().strftime('%d.%m.%Y')}")
        else:
            date_limit = today - timedelta(days=limit_days)
            date_max = today # Changed from today + timedelta(days=1) to just today
            logging.info(f"[EVENTS] Filtering for limit_days: {limit_days} ({date_limit.date().strftime('%d.%m.%Y')} - {date_max.date().strftime('%d.%m.%Y')})")
        
        for item in news_item_elements:
            try:
                title_elem = item.find("a", class_="news-name") or item.find("h2") or item.find("h3") or item
                if not title_elem:
                    logging.debug("[EVENTS] No title element found for an item. Skipping.")
                    continue
                    
                title = title_elem.text.strip()
                link = title_elem.get("href", "")
                if not link.startswith("http"):
                    link = "https://www.yarnews.net" + link

                if link in seen_urls:
                    logging.info(f"[EVENTS] [SKIP] Event ('{title}'): duplicate link.")
                    continue # Skip duplicate events
                seen_urls.add(link)

                desc_elem = (
                    item.find("div", class_="news-excerpt") or
                    item.find("div", class_="description") or
                    item.find("p") or
                    item.find_next("p")
                )
                description = desc_elem.text.strip() if desc_elem else "Подробности по ссылке."

                # Получаем дату публикации
                pub_date_elem = (
                    item.find("span", class_="news-date") or
                    item.find("span", class_="date") or
                    item.find("time") or
                    item.find_previous("span", class_="date")
                )
                pub_date = pub_date_elem.text.strip() if pub_date_elem else today_str

                # Проверяем, что новость опубликована сегодня или вчера
                try:
                    # Parse datetime similar to news.py
                    try:
                        pub_date_dt = datetime.strptime(pub_date, "%d.%m.%Y в %H:%M")
                    except ValueError:
                        try:
                            pub_date_dt = datetime.strptime(pub_date, "%d.%m.%Y")
                        except ValueError:
                            logging.info(f"[EVENTS] [SKIP] Event ('{title}'): date parse error ('{pub_date}').")
                            continue

                    # Проверяем, что дата входит в нужный диапазон
                    if not (date_limit <= pub_date_dt <= date_max):
                        logging.info(f"[EVENTS] [SKIP] Event ('{title}'): not in date range ({date_limit.date().strftime('%d.%m.%Y')} - {date_max.date().strftime('%d.%m.%Y')}).")
                        continue

                    title_lower = title.lower()
                    desc_lower = description.lower()
                    
                    # Проверяем на административные новости (temporarily commented out for debugging)
                    is_administrative = any(keyword.lower() in title_lower or keyword.lower() in desc_lower 
                                                  for keyword in administrative_keywords)
                    if is_administrative:
                        logging.info(f"[EVENTS] [SKIP] Event ('{title}'): contains administrative keyword (filter temporarily disabled).")
                        # continue # Temporarily disabled
                    
                    # --- Проверка на негативные ключевые слова (temporarily commented out for debugging) ---
                    is_negative = False
                    for neg_keyword in negative_keywords:
                        if neg_keyword.lower() in title_lower or neg_keyword.lower() in desc_lower:
                            is_negative = True
                            logging.debug(f"[EVENTS] Excluding event due to negative keyword '{neg_keyword}' in title or description (filter temporarily disabled).")
                            break # Нашли негативное слово, можно пропустить событие
                    
                    if is_negative:
                        logging.info(f"[EVENTS] [SKIP] Event ('{title}'): contains negative keyword (filter temporarily disabled).")
                        # continue # Temporarily disabled
                    
                    # Main category matching logic: Check if the event matches keywords for the *requested* category.
                    event_matches_requested_category = False
                    if category: # A specific category is requested (e.g., 'culture', 'sport')
                        current_category_keywords = event_keywords.get(category, {}).get("keywords", [])
                        if any(keyword.lower() in title_lower or keyword.lower() in desc_lower for keyword in current_category_keywords):
                            event_matches_requested_category = True
                        else:
                            logging.info(f"[EVENTS] [SKIP] Event ('{title}'): does not match keywords for requested category '{category}'.")
                    else: # No specific category requested, include if it matches *any* event type
                        for cat_key in event_keywords: # Iterate through all known event categories
                            current_category_keywords = event_keywords.get(cat_key, {}).get("keywords", [])
                            if any(keyword.lower() in title_lower or keyword.lower() in desc_lower for keyword in current_category_keywords):
                                event_matches_requested_category = True
                                break # Found at least one matching event category
                        if not event_matches_requested_category:
                            logging.info(f"[EVENTS] [SKIP] Event ('{title}'): does not match any event category keywords (no specific category requested).")

                    if not event_matches_requested_category:
                        continue

                    # Получаем URL изображения, если есть
                    image_url = None
                    img_elem = item.find("img")
                    if img_elem and img_elem.get("src"):
                        image_url = img_elem["src"]
                        if not image_url.startswith("http"):
                            image_url = "https://www.yarnews.net" + image_url

                    event = {
                        'title': title,
                        'description': description,
                        'date': pub_date_dt.strftime("%d.%m.%Y"),
                        'time': pub_date_dt.strftime("%H:%M"),
                        'link': link,
                        'image_url': image_url
                    }

                    # Use the input 'category' to determine the display name, fallback to a generic one
                    event['display_category'] = event_types.get(category, "Мероприятие 📅") 

                    events.append(event)
                    logging.info(f"[EVENTS] Added event: '{title}' (Category: {category})")

                except ValueError:
                    logging.info(f"[EVENTS] [SKIP] Event ('{title}'): date parsing error.")
                    continue

            except Exception as e:
                logging.error(f"[EVENTS] Error processing event item (Title: '{title}'): {e}", exc_info=True)
                continue

        logging.info(f"[EVENTS] Finished processing. Total events found: {len(events)}")
        return events[:10]  # Увеличиваем количество возвращаемых событий до 10

    except requests.exceptions.RequestException as e:
        logging.error(f"[EVENTS] Request error during event fetching: {e}")
        return []
    except Exception as e:
        logging.error(f"[EVENTS] Unexpected error in get_events_by_category: {e}", exc_info=True)
        return []

def get_events_by_date(date):
    """Get events for a specific date."""
    return get_events_by_category(None, specific_date=date)

def get_events_by_week():
    """Get events for the next week."""
    return get_events_by_category(None, limit_days=7, week_range=True)

def format_event_message(event):
    """Format event message for display."""
    try:
        # Format message to include title, description, and source link
        title = event.get('title', 'Нет заголовка')
        description = event.get('description', 'Нет описания')
        date = event.get('date', 'Дата не указана')
        link = event.get('link', '')
        location = event.get('location', '')

        text = f"*{title}*\n\n"
        if description:
            text += f"{description}\n\n" # Добавляем двойной перенос строки
        text += f"Дата: {date}\n"
        if location:
            text += f"Место: {location}\n"
        # Изменяем ссылку на источник на прямую ссылку события
        text += f"\nИсточник: <a href='{link}'>ЯрНовости</a>"
        return text
    except Exception as e:
        logging.error(f"Error formatting event message: {e}")
        # Fallback to just source link if formatting fails
        return f"Источник: <a href=\"{event['link']}\">yarnews.net</a>"

# Для тестовых данных (если парсинг не работает)
def get_test_events_by_category(category):
    test_data = {
        "culture": [
            {
                "title": "Тестовое культурное событие",
                "date": "01.01.2025",
                "text": "Описание тестового культурного события.",
                "link": "https://example.com/culture-event",
                "image_url": ""
            }
        ],
        "sport": [
            {
                "title": "Тестовое спортивное событие",
                "date": "02.01.2025",
                "text": "Описание тестового спортивного события.",
                "link": "https://example.com/sport-event",
                "image_url": ""
            }
        ],
        "education": [
            {
                "title": "Тестовое образовательное событие",
                "date": "03.01.2025",
                "text": "Описание тестового образовательного события.",
                "link": "https://example.com/education-event",
                "image_url": ""
            }
        ]
    }
    return test_data.get(category, []) 