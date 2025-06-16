import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

CATEGORY_KEYWORDS = {
    "general": {
        "keywords": [
            "новости", "события", "происшествия", "информация",
            "объявление", "сообщение", "репортаж", "интервью",
            "заметка", "статья", "публикация", "материал"
        ],
        "exclude_keywords": [
            "погода", "температура", "осадки", "дождь", "снег", "ветер",
            "администрация", "мэр", "губернатор", "власть", "правительство",
            "транспорт", "автобус", "троллейбус", "трамвай", "маршрут",
            "ремонт", "строительство", "благоустройство", "реконструкция",
            "культура", "искусство", "театр", "музей", "выставка", "концерт"
        ]
    },
    "transport": {
        "keywords": [
            "транспорт", "автобус", "троллейбус", "трамвай", "маршрут",
            "общественный транспорт", "пассажирский транспорт", "перевозки",
            "остановка", "расписание", "интервал", "движение",
            "такси", "каршеринг", "велосипед", "велодорожка",
            "парковка", "стоянка", "парковочное место",
            "дорожное движение", "пробка", "затор", "регулирование",
            "светофор", "пешеходный переход", "разметка", "знак"
        ],
        "exclude_keywords": [
            "погода", "температура", "осадки", "дождь", "снег", "ветер",
            "администрация", "мэр", "губернатор", "власть", "правительство",
            "ремонт", "строительство", "благоустройство", "реконструкция",
            "культура", "искусство", "театр", "музей", "выставка", "концерт"
        ]
    },
    "construction": {
        "keywords": [
            "ремонт", "благоустройство", "строительство", "реконструкция",
            "капитальный ремонт", "ремонт зданий", "строительная площадка",
            "подрядчик", "застройщик", "инфраструктура", "городская среда",
            "городское пространство", "муниципальный контракт", "госзакупка",
            "тендер", "стройка", "строительный объект", "реновация",
            "озеленение", "ландшафтный дизайн", "высадка деревьев",
            "посадка кустарников", "ЖКХ", "коммунальный",
            "проект", "смета", "экспертиза", "разрешение", "договор",
            "объект", "площадка", "работы", "материалы", "оборудование",
            "инженерные сети", "дорога", "тротуар", "асфальт", "брусчатка",
            "освещение", "фонарь", "скамейка", "урна", "детская площадка",
            "спортивная площадка", "сквер", "парк", "набережная"
        ],
        "exclude_keywords": [
            "погода", "температура", "осадки", "дождь", "снег", "ветер",
            "администрация", "мэр", "губернатор", "власть", "правительство",
            "транспорт", "автобус", "троллейбус", "трамвай", "маршрут",
            "культура", "искусство", "театр", "музей", "выставка", "концерт"
        ]
    },
    "culture": {
        "keywords": [
            "культура", "искусство", "театр", "музей", "выставка", "концерт",
            "фестиваль", "галерея", "библиотека", "литература", "кино",
            "музыка", "танец", "живопись", "скульптура", "архитектура",
            "наследие", "памятник", "история", "традиция", "ремесло",
            "народное творчество", "художник", "писатель", "актер", "режиссер",
            "творчество", "искусствовед", "культурный центр", "дворец культуры",
            "филармония", "оперетта", "балет", "опера", "фольклор", "этнография",
            "мастер-класс", "лекция", "семинар", "презентация", "открытие", "закрытие",
            "спектакль", "премьера", "дебют", "творческая встреча", "вернисаж",
            "экспозиция", "коллекция", "артефакт", "реликвия", "шедевр"
        ],
        "exclude_keywords": [
            "погода", "температура", "осадки", "дождь", "снег", "ветер",
            "администрация", "мэр", "губернатор", "власть", "правительство",
            "транспорт", "автобус", "троллейбус", "трамвай", "маршрут",
            "ремонт", "строительство", "благоустройство", "реконструкция"
        ]
    },
    "weather": {
        "keywords": [
            "погода", "температура", "осадки", "дождь", "снег", "ветер",
            "прогноз погоды", "метео", "метеорология", "климат",
            "мороз", "жара", "туман", "гроза", "град",
            "ураган", "шторм", "наводнение", "паводок",
            "засуха", "гололед", "атмосферное давление", "влажность", "облачность",
            "солнце", "метеорологический", "прогноз", "циклон", "антициклон",
            "атмосфера", "климатический", "температурный", "метеосводка",
            "гидрометцентр", "синоптик", "прогнозирование", "градус", "фаренгейт",
            "цельсий", "минус", "плюс", "осадки", "ливень", "моросящий дождь",
            "снегопад", "метель", "вьюга", "пурга", "иней", "изморозь",
            "радуга", "гром", "молния", "шквал", "буря", "тайфун"
        ],
        "exclude_keywords": [
            "администрация", "мэр", "губернатор", "власть", "правительство",
            "транспорт", "автобус", "троллейбус", "трамвай", "маршрут",
            "ремонт", "строительство", "благоустройство", "реконструкция",
            "культура", "искусство", "театр", "музей", "выставка", "концерт",
            "школьный автобус", "дорога", "яма", "асфальт", "здание", "гостиница",
            "дом", "проект", "реставрация", "благоустройство", "капитальный ремонт",
            "строительная площадка", "подрядчик", "застройщик", "инфраструктура",
            "городская среда", "городское пространство", "муниципальный контракт",
            "госзакупка", "тендер"
        ]
    },
    "administration": {
        "keywords": [
            "администрация", "мэрия", "губернатор", "управление", "власти",
            "мэр", "глава", "департамент", "комитет", "бюджет", "финансы",
            "социальная защита", "образование", "здравоохранение", "молодежная политика",
            "градостроительство", "благоустройство", "коммунальное хозяйство",
            "муниципальный", "городской", "областной", "постановление", "распоряжение",
            "программа", "служба", "инспекция", "фонд", "регулирование", "субсидия",
            "дотация", "грант", "закупка", "торги", "отчетность", "мониторинг",
            "чиновник", "чиновники", "совещание", "административный", "муниципалитет",
            "муниципалитеты", "муниципальные власти", "закон", "нормативный акт",
            "регламент", "стандарт", "требование", "проверка", "контроль",
            "надзор", "лицензия", "разрешение", "сертификат", "аккредитация"
        ],
        "exclude_keywords": [
            "погода", "температура", "осадки", "дождь", "снег", "ветер",
            "транспорт", "автобус", "троллейбус", "трамвай", "маршрут",
            "культура", "искусство", "театр", "музей", "выставка", "концерт"
        ]
    }
}

def get_yarnews_articles(category, limit_days=1, specific_date=None, week_range=False):
    """Fetch news articles from yarnews.net."""
    print(f"[DEBUG_PRINT] get_yarnews_articles received: category={category}, week_range={week_range}")
    logging.info(f"[NEWS] get_yarnews_articles called with category: {category}, limit_days: {limit_days}, specific_date: {specific_date}, week_range: {week_range}")

    url = "https://www.yarnews.net/"
    category_data = CATEGORY_KEYWORDS.get(category)

    if not category_data:
        logging.error(f"Category {category} not supported")
        return []

    keywords = category_data.get("keywords", [])
    exclude_keywords = category_data.get("exclude_keywords", [])

    if not keywords:
        logging.error(f"No keywords defined for category: {category}")
        return []

    try:
        page_source = None
        
        if week_range:
            # Используем Selenium для прокрутки страницы и загрузки всех новостей
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
                logging.info("[NEWS] Page loaded successfully with Selenium.")

                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "news-feed"))
                )
                logging.info("[NEWS] Initial news feed loaded with Selenium.")

                # Увеличиваем количество циклов прокрутки для новостей
                scroll_and_click_cycles = 10
                scroll_amount = 700

                logging.info(f"[NEWS] Starting scroll and click cycles ({scroll_and_click_cycles} cycles) for news.")

                for cycle in range(scroll_and_click_cycles):
                    logging.info(f"[NEWS] Scroll/Click cycle {cycle + 1} of {scroll_and_click_cycles}")
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
                            logging.debug(f"[NEWS] Error finding elements with selector {selector}: {str(e)}")
                            continue

                    seen = set()
                    buttons = [x for x in buttons if not (x in seen or seen.add(x))]

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
                                    logging.info(f"[NEWS] Successfully clicked button {clicked_count} using JavaScript in cycle {cycle + 1}")
                                except Exception as e1:
                                    try:
                                        ActionChains(driver).move_to_element(button).click().perform()
                                        clicked_count += 1
                                        logging.info(f"[NEWS] Successfully clicked button {clicked_count} using Actions in cycle {cycle + 1}")
                                    except Exception as e2:
                                        try:
                                            button.click()
                                            clicked_count += 1
                                            logging.info(f"[NEWS] Successfully clicked button {clicked_count} using direct click in cycle {cycle + 1}")
                                        except Exception as e3:
                                            logging.error(f"[NEWS] All click methods failed for button in cycle {cycle + 1}: {str(e1)}, {str(e2)}, {str(e3)}")
                                            continue
                                time.sleep(2)
                        except Exception as e:
                            logging.error(f"[NEWS] Error processing button element in cycle {cycle + 1}: {str(e)}")
                            continue

                    if clicked_count == 0 and cycle > 0:
                        logging.info("[NEWS] No more 'больше новостей' buttons found or clickable. Ending cycles.")
                        break

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                page_source = driver.page_source
                logging.info("[NEWS] Got final page source after all loading attempts with Selenium.")

            except TimeoutException:
                logging.error("[NEWS] Timeout while loading page with Selenium")
                return []
            except Exception as e:
                logging.error(f"[NEWS] Error during page processing with Selenium: {e}")
                return []
            finally:
                driver.quit()
        else:
            # Для свежих новостей используем обычный requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            page_source = response.text

        soup = BeautifulSoup(page_source, 'html.parser')
        news_items = soup.select(".news-feed-item")
        logging.info(f"[NEWS] Found {len(news_items)} news items with BeautifulSoup after initial fetch.")

        parsed_news = []
        seen_urls = set()
        today = datetime.now()
        today_str = today.strftime("%d.%m.%Y")
        yesterday = (today - timedelta(days=1)).strftime("%d.%m.%Y")

        for i, item_element in enumerate(news_items):
            try:
                title_elem = item_element.find("a", class_="news-name") or item_element.find("h2") or item_element.find("h3")
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                link = title_elem.get("href", "")
                if not link.startswith("http"):
                    link = "https://www.yarnews.net" + link

                if link in seen_urls:
                    continue
                seen_urls.add(link)

                desc_elem = item_element.find("div", class_="news-excerpt") or item_element.find("div", class_="description") or item_element.find("p")
                description = desc_elem.text.strip() if desc_elem else ""

                datetime_elem = item_element.find("span", class_="news-date") or item_element.find("span", class_="date")
                datetime_str = datetime_elem.text.strip() if datetime_elem else today_str

                try:
                    event_datetime = datetime.strptime(datetime_str, "%d.%m.%Y в %H:%M")
                except ValueError:
                    try:
                        event_datetime = datetime.strptime(datetime_str, "%d.%m.%Y")
                    except ValueError:
                        logging.info(f"[SKIP] Article {i} ('{title}'): date parse error ('{datetime_str}').")
                        continue

                # Для свежих новостей (не недельных) включаем только сегодня и вчера
                if not week_range and not specific_date:
                    if not (event_datetime.date() == today.date() or event_datetime.date() == (today - timedelta(days=1)).date()):
                        continue
                # Для недельных новостей исключаем сегодня и вчера
                elif week_range:
                    if event_datetime.date() >= today.date() - timedelta(days=1):
                        continue

                title_lower = title.lower()
                desc_lower = description.lower()

                should_exclude = False
                for exclude_keyword in exclude_keywords:
                    if exclude_keyword.lower() in title_lower or exclude_keyword.lower() in desc_lower:
                        should_exclude = True
                        break

                if should_exclude:
                    continue

                category_match = False
                for keyword in keywords:
                    if keyword.lower() in title_lower or keyword.lower() in desc_lower:
                        category_match = True
                        break

                if not category_match:
                    continue

                img_url = ""
                img_elem = item_element.select_one("img")
                if img_elem:
                    img_url = img_elem.get('src')
                    if img_url and not img_url.startswith('http'):
                        img_url = 'https://www.yarnews.net' + img_url

                news_item = {
                    "title": title,
                    "description": description,
                    "link": link,
                    "image_url": img_url,
                    "date": event_datetime.strftime("%d.%m.%Y"),
                    "datetime": event_datetime,
                    "is_yesterday": event_datetime.date() == (datetime.now() - timedelta(days=1)).date()
                }
                parsed_news.append(news_item)

            except Exception as e:
                logging.error(f"Error parsing article {i}: {e}")
                continue

        parsed_news.sort(key=lambda x: x["datetime"], reverse=True)
        
        if specific_date or week_range:
            return parsed_news
        else:
            return parsed_news[:3]  # Возвращаем только 3 самые свежие новости

    except Exception as e:
        logging.error(f"Unexpected error in get_yarnews_articles: {e}")
        return []

def get_news_by_category(category):
    return get_yarnews_articles(category, limit_days=2)

def get_news_by_date(category, date):
    return get_yarnews_articles(category, specific_date=date)

def get_news_by_week(category):
    try:
        logging.info(f"[NEWS] Starting get_news_by_week for category: {category}")

        today = datetime.now()
        week_ago = today - timedelta(days=7)

        logging.info(f"[NEWS] Getting news from {week_ago.strftime('%d.%m.%Y')} to {today.strftime('%d.%m.%Y')}")

        news_list = get_yarnews_articles(category, week_range=True)
        logging.info(f"[NEWS] Retrieved {len(news_list)} news articles for the week (after fetching and initial filtering)")

        if not news_list:
            logging.warning(f"[NEWS] No news found for category {category} in the last week")
            return []

        news_list.sort(key=lambda x: x["datetime"], reverse=True)
        logging.info(f"[NEWS] Sorted weekly news list, total articles: {len(news_list)}")

        return news_list

    except Exception as e:
        logging.error(f"[NEWS] Error in get_news_by_week: {e}", exc_info=True)
        return []

def get_weekly_news():
    logger.info("Fetching weekly news using get_yarnews_articles with week_range=True")
    articles = get_yarnews_articles(category="administration", week_range=True)
    return articles

def get_weather_news():
    logger.info("Fetching weather news using get_yarnews_articles with category='weather'")
    articles = get_yarnews_articles(category="weather", limit_days=7)
    return articles