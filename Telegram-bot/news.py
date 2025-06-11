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
        "exclude_keywords": []
    },
    "transport": {
        "keywords": [
            "транспорт", "автобус", "трамвай", "троллейбус", "дорога", "пробка",
            "маршрут", "остановка", "расписание", "проезд", "тариф",
            "пассажир", "перевозчик", "кондуктор", "водитель",
            "парковка", "стоянка", "разметка", "светофор", "пешеходный переход",
            "ремонт дорог", "дорожное движение", "ГИБДД", "ДПС",
            "дтп", "авария", "магистраль", "трасса", "шоссе", "перевозки", "рейс",
            "общественный транспорт", "железнодорожный", "аэропорт", "вокзал", "станция", "путь", "билет", "контроль", "движение", "перекресток"
        ],
        "exclude_keywords": [
            "администрация", "политика", "погода", "события", "ремонт", "стройка", "культура", "спорт", "ЖКХ"
        ]
    },
    "construction": {
        "keywords": [
            "ремонт", "благоустройство", "строительство", "реконструкция",
            "капитальный ремонт", "ремонт зданий",
            "строительная площадка", "подрядчик", "застройщик",
            "инфраструктура", "городская среда", "городское пространство",
            "муниципальный контракт", "госзакупка", "тендер",
            "стройка", "строительный объект", "реновация",
            "озеленение", "ландшафтный дизайн", "высадка деревьев", "посадка кустарников", "ЖКХ", "коммунальный",
            "проект", "смета", "экспертиза", "разрешение", "договор", "объект", "площадка", "работы", "материалы", "оборудование", "инженерные сети"
        ],
        "exclude_keywords": [
            "администрация", "политика", "погода", "события", "транспорт", "ДТП", "культура", "спорт"
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
            "мастер-класс", "лекция", "семинар", "презентация", "открытие", "закрытие"
        ],
        "exclude_keywords": [
            "транспорт", "погода", "политика", "администрация", "ремонт", "стройка", "ДТП", "ЖКХ"
        ]
    },
    "weather": {
        "keywords": [
            "погода", "температура", "осадки", "дождь", "снег", "ветер",
            "прогноз погоды", "метео", "метеорология", "климат",
            "мороз", "жара", "туман", "гроза", "град",
            "ураган", "шторм", "наводнение", "паводок",
            "засуха", "гололед", "атмосферное давление", "влажность", "облачность", "солнце", "метеорологический", "прогноз",
            "циклон", "антициклон", "атмосфера", "климатический", "температурный",
            "метеосводка", "гидрометцентр", "синоптик", "прогнозирование", "градус", "фаренгейт", "цельсий", "минус", "плюс"
        ],
        "exclude_keywords": [
            "БПЛА", "атака", "безопасность", "транспорт", "политика", "администрация", "события", "ремонт", "стройка", "ДТП", "ЖКХ",
            "покрышек", "кремль", "КХЛ", "телеграм", "фура"
        ]
    },
    "administration": {
        "keywords": [
            "администрация", "мэрия", "губернатор", "управление", "власти",
            "мэр", "глава", "департамент", "комитет",
            "бюджет", "финансы", "социальная защита", "образование",
            "здравоохранение", "культура", "спорт", "молодежная политика",
            "градостроительство", "благоустройство", "коммунальное хозяйство",
            "муниципальный", "городской", "областной", "постановление", "распоряжение", "программа",
            "служба", "инспекция", "фонд", "регулирование", "субсидия", "дотация", "грант", "закупка", "торги", "отчетность", "мониторинг"
        ],
        "exclude_keywords": [
            "транспорт", "погода", "спорт", "культура", "события", "ремонт", "стройка", "ДТП"
        ]
    }
}

def get_yarnews_articles(category, limit_days=1, specific_date=None, week_range=False):
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
        logging.info(f"Fetching news for category: {category}")

        page_source = None

        if week_range:
            logging.info("Using Selenium for weekly news.")
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
                logging.info("Page loaded successfully with Selenium.")

                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "news-feed"))
                )
                logging.info("Initial news feed loaded with Selenium.")

                scroll_and_click_cycles = 10
                scroll_amount = 700

                logging.info(f"Starting scroll and click cycles ({scroll_and_click_cycles} cycles).")

                for cycle in range(scroll_and_click_cycles):
                    logging.info(f"Scroll/Click cycle {cycle + 1} of {scroll_and_click_cycles}")
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
                        "//div[contains(text(), 'еще новости')]"
                    ]

                    buttons = []
                    for selector in selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, selector)
                            buttons.extend(elements)
                        except Exception as e:
                            logging.debug(f"Error finding elements with selector {selector}: {str(e)}")
                            continue

                    seen = set()
                    buttons = [x for x in buttons if not (x in seen or seen.add(x))]

                    logging.info(f"Found {len(buttons)} potential 'больше новостей' buttons in cycle {cycle + 1}")

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
                                    logging.info(f"Successfully clicked button {clicked_count} using JavaScript in cycle {cycle + 1}")
                                except Exception as e1:
                                    try:
                                        from selenium.webdriver.common.action_chains import ActionChains
                                        ActionChains(driver).move_to_element(button).click().perform()
                                        clicked_count += 1
                                        logging.info(f"Successfully clicked button {clicked_count} using Actions in cycle {cycle + 1}")
                                    except Exception as e2:
                                        try:
                                            button.click()
                                            clicked_count += 1
                                            logging.info(f"Successfully clicked button {clicked_count} using direct click in cycle {cycle + 1}")
                                        except Exception as e3:
                                            logging.error(f"All click methods failed for button in cycle {cycle + 1}: {str(e1)}, {str(e2)}, {str(e3)}")
                                            continue

                                time.sleep(2)

                            else:
                                logging.debug(f"Button found but not visible/clickable in viewport in cycle {cycle + 1}")

                        except Exception as e:
                            logging.error(f"Error processing button in cycle {cycle + 1}: {str(e)}")
                            continue

                    logging.info(f"Clicked {clicked_count} 'больше новостей' buttons in cycle {cycle + 1}")

                    if clicked_count == 0 and cycle > 0:
                        logging.info("No more 'больше новостей' buttons found or clickable. Ending cycles.")
                        break

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                logging.info("Completed scroll/click cycles and scrolled to the bottom.")


                page_source = driver.page_source
                logging.info("Got final page source after all loading attempts with Selenium.")

            except TimeoutException:
                logging.error("Timeout while loading page with Selenium")
                return []
            except Exception as e:
                logging.error(f"Error during page processing with Selenium: {e}")
                return []
            finally:
                driver.quit()

        else:
            logging.info("Using requests and BeautifulSoup for recent news.")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            page_source = response.text
            logging.info("Got page source with requests.")

        soup = BeautifulSoup(page_source, 'html.parser')

        news_item_elements = soup.select(".news-feed-item")
        logging.info(f"Found {len(news_item_elements)} news items with BeautifulSoup after initial fetch.")

        if not news_item_elements:
            logging.warning("No news items found with BeautifulSoup")
            return []

        parsed_news = []
        seen_urls = set()

        for i, item_element in enumerate(news_item_elements):
            try:
                title_elem = item_element.select_one(".news-name")
                if not title_elem or not title_elem.text.strip():
                    logging.info(f"[SKIP] Article {i}: no title found.")
                    continue

                title = title_elem.text.strip()
                link = title_elem.get('href')
                if not link:
                    logging.info(f"[SKIP] Article {i} ('Ы{title}'): no link found.")
                    continue

                if not link.startswith('http'):
                    link = 'https://www.yarnews.net' + link

                if link in seen_urls:
                    logging.info(f"[SKIP] Article {i} ('{title}'): duplicate link.")
                    continue
                seen_urls.add(link)

                description = ""
                desc_selectors = [
                    ".news-excerpt",
                    ".news-text",
                    ".news-content p",
                    "p"
                ]
                for selector in desc_selectors:
                    desc_elem = item_element.select_one(selector)
                    if desc_elem and desc_elem.text.strip():
                        description = desc_elem.text.strip()
                        break

                datetime_str = None
                date_elem = item_element.select_one(".news-date")
                if not date_elem or not date_elem.text.strip():
                    logging.info(f"[SKIP] Article {i} ('{title}'): no date found.")
                    continue
                datetime_str = date_elem.text.strip()

                try:
                    event_datetime = datetime.strptime(datetime_str, "%d.%m.%Y в %H:%M")
                except ValueError:
                    try:
                        event_datetime = datetime.strptime(datetime_str, "%d.%m.%Y")
                    except ValueError:
                        logging.info(f"[SKIP] Article {i} ('{title}'): date parse error ('{datetime_str}').")
                        continue

                today = datetime.now()
                if specific_date:
                    try:
                        specific_date_dt = datetime.strptime(specific_date, "%d.%m.%Y")
                        if event_datetime.date() != specific_date_dt.date():
                            logging.info(f"[SKIP] Article {i} ('{title}'): not matching specific_date {specific_date}.")
                            continue
                    except ValueError:
                        logging.info(f"[SKIP] Article {i} ('{title}'): specific_date parse error ({specific_date}).")
                        continue
                elif week_range:
                    date_limit = today - timedelta(days=7)
                    if event_datetime.date() < date_limit.date() or event_datetime.date() > today.date():
                         logging.info(f"[SKIP] Article {i} ('{title}'): not in week range ({date_limit.date().strftime('%d.%m.%Y')} - {today.date().strftime('%d.%m.%Y')}).")
                         continue
                elif event_datetime.date() < (today - timedelta(days=limit_days)).date() or event_datetime.date() > today.date():
                    logging.info(f"[SKIP] Article {i} ('{title}'): not in last {limit_days} days.")
                    continue

                title_lower = title.lower()
                desc_lower = description.lower()

                should_exclude = False
                for exclude_keyword in exclude_keywords:
                    if exclude_keyword.lower() in title_lower or exclude_keyword.lower() in desc_lower:
                        should_exclude = True
                        logging.debug(f"Excluding article due to keyword '{exclude_keyword}' in title or description.")
                        break

                if should_exclude:
                    logging.info(f"[SKIP] Article {i} ('{title}'): contains exclude keyword.")
                    continue

                category_match = False
                for keyword in keywords:
                    if keyword.lower() in title_lower or keyword.lower() in desc_lower:
                        category_match = True
                        logging.debug(f"Category keyword match for '{keyword}' in title or description.")
                        break

                if not category_match:
                    logging.info(f"[SKIP] Article {i} ('{title}'): no category keyword match.")
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
                item_snippet = str(item_element)[:200] + "..."
                logging.error(f"Error parsing article {i} with BeautifulSoup: {e}. Item snippet: {item_snippet}")
                continue

        parsed_news.sort(key=lambda x: x["datetime"], reverse=True)
        logging.info(f"Total articles found and parsed after filtering by date and category: {len(parsed_news)}")

        if specific_date or week_range:
             return parsed_news
        else:
             return parsed_news[:3]

    except Exception as e:
        logging.error(f"Unexpected error in get_yarnews_articles: {e}")
        return []

def get_news_by_category(category):
    return get_yarnews_articles(category, limit_days=2)

def get_news_by_date(category, date):
    return get_yarnews_articles(category, specific_date=date)

def get_news_by_week(category):
    try:
        logging.info(f"Starting get_news_by_week for category: {category}")

        today = datetime.now()
        week_ago = today - timedelta(days=7)

        logging.info(f"Getting news from {week_ago.strftime('%d.%m.%Y')} to {today.strftime('%d.%m.%Y')}")

        news_list = get_yarnews_articles(category, week_range=True)
        logging.info(f"Retrieved {len(news_list)} news articles for the week (after fetching and initial filtering)")

        if not news_list:
            logging.warning(f"No news found for category {category} in the last week")
            return []

        filtered_news = [
            news for news in news_list
            if news["datetime"].date() not in [today.date(), (today - timedelta(days=1)).date()]
        ]
        logging.info(f"Filtered weekly news (excluding today/yesterday): {len(filtered_news)}")

        filtered_news.sort(key=lambda x: x["datetime"], reverse=True)
        logging.info(f"Filtered and sorted weekly news list, total articles: {len(filtered_news)}")

        return filtered_news

    except Exception as e:
        logging.error(f"Error in get_news_by_week: {e}")
        return []

def get_weekly_news():
    logger.info("Fetching weekly news using get_yarnews_articles with week_range=True")
    articles = get_yarnews_articles(category="administration", week_range=True)
    return articles

def get_weather_news():
    logger.info("Fetching weather news using get_yarnews_articles with category='weather'")
    articles = get_yarnews_articles(category="weather", limit_days=7)
    return articles