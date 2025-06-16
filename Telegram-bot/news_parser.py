import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import pytz
import os
from telebot.types import InputFile
import logging

class NewsParser:
    def __init__(self):
        self.base_url = "https://yaroslavl-region.ru"
        # Координаты Ярославля
        self.latitude = 57.6261
        self.longitude = 39.8845
        # URL для OpenMeteo API
        self.weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={self.latitude}&longitude={self.longitude}&current=temperature_2m,relative_humidity_2m,weather_code,apparent_temperature&daily=weather_code,temperature_2m_max&timezone=Europe%2FMoscow&forecast_days=2"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.moscow_tz = pytz.timezone('Europe/Moscow')
        # Get the absolute path to the Materials/weather directory
        self.weather_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Materials', 'weather'))
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        # Коды погоды OpenMeteo и их соответствие нашим иконкам
        self.weather_codes = {
            0: {'condition': 'clear', 'description': 'ясно'},
            1: {'condition': 'partly-cloudy', 'description': 'малооблачно'},
            2: {'condition': 'partly-cloudy', 'description': 'облачно с прояснениями'},
            3: {'condition': 'cloudy', 'description': 'пасмурно'},
            45: {'condition': 'fog', 'description': 'туман'},
            48: {'condition': 'fog', 'description': 'туман с инеем'},
            51: {'condition': 'light-rain', 'description': 'легкая морось'},
            53: {'condition': 'rain', 'description': 'умеренная морось'},
            55: {'condition': 'rain', 'description': 'сильная морось'},
            56: {'condition': 'sleet', 'description': 'ледяная морось'},
            57: {'condition': 'sleet', 'description': 'сильная ледяная морось'},
            61: {'condition': 'light-rain', 'description': 'небольшой дождь'},
            63: {'condition': 'rain', 'description': 'умеренный дождь'},
            65: {'condition': 'heavy-rain', 'description': 'сильный дождь'},
            66: {'condition': 'sleet', 'description': 'ледяной дождь'},
            67: {'condition': 'sleet', 'description': 'сильный ледяной дождь'},
            71: {'condition': 'light-snow', 'description': 'небольшой снег'},
            73: {'condition': 'snow', 'description': 'умеренный снег'},
            75: {'condition': 'snow', 'description': 'сильный снег'},
            77: {'condition': 'snow', 'description': 'снежные зерна'},
            80: {'condition': 'light-rain', 'description': 'небольшой ливень'},
            81: {'condition': 'rain', 'description': 'умеренный ливень'},
            82: {'condition': 'heavy-rain', 'description': 'сильный ливень'},
            85: {'condition': 'light-snow', 'description': 'небольшой снежный ливень'},
            86: {'condition': 'snow', 'description': 'сильный снежный ливень'},
            95: {'condition': 'thunderstorm', 'description': 'гроза'},
            96: {'condition': 'thunderstorm', 'description': 'гроза с градом'},
            99: {'condition': 'thunderstorm', 'description': 'сильная гроза с градом'}
        }
        
        # Обновляем словарь для соответствия кодов погоды
        self.weather_icons = {
            'clear': {
                'emoji': '☀️',
                'gif': os.path.join(self.weather_dir, 'sunny.gif')
            },
            'partly-cloudy': {
                'emoji': '🌤',
                'gif': os.path.join(self.weather_dir, 'partly_cloudy.gif')
            },
            'cloudy': {
                'emoji': '☁️',
                'gif': os.path.join(self.weather_dir, 'cloudy.gif')
            },
            'overcast': {
                'emoji': '☁️',
                'gif': os.path.join(self.weather_dir, 'cloudy.gif')
            },
            'light-rain': {
                'emoji': '🌧',
                'gif': os.path.join(self.weather_dir, 'rain.gif')
            },
            'rain': {
                'emoji': '🌧',
                'gif': os.path.join(self.weather_dir, 'rain.gif')
            },
            'heavy-rain': {
                'emoji': '🌧',
                'gif': os.path.join(self.weather_dir, 'rain.gif')
            },
            'thunderstorm': {
                'emoji': '⛈',
                'gif': os.path.join(self.weather_dir, 'storm.gif')
            },
            'light-snow': {
                'emoji': '❄️',
                'gif': os.path.join(self.weather_dir, 'snow.gif')
            },
            'snow': {
                'emoji': '❄️',
                'gif': os.path.join(self.weather_dir, 'snow.gif')
            },
            'sleet': {
                'emoji': '🌨',
                'gif': os.path.join(self.weather_dir, 'snow.gif')
            },
            'fog': {
                'emoji': '🌫',
                'gif': os.path.join(self.weather_dir, 'fog.gif')
            },
            'default': {
                'emoji': '🌤',
                'gif': os.path.join(self.weather_dir, 'partly_cloudy.gif')
            }
        }

    def get_weather_icon(self, weather_condition):
        return self.weather_icons.get(weather_condition, self.weather_icons['default'])

    def get_weather(self):
        try:
            # Получаем текущую погоду
            response = requests.get(self.weather_url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            # Текущая погода
            current = data['current']
            current_temp = round(current['temperature_2m'])
            feels_like = round(current['apparent_temperature'])
            weather_code = current['weather_code']
            weather_info = self.weather_codes.get(weather_code, {'condition': 'default', 'description': 'неизвестно'})
            current_desc = weather_info['description']
            weather_condition = weather_info['condition']

            # Прогноз на завтра
            tomorrow_temp = round(data['daily']['temperature_2m_max'][1])
            tomorrow_weather_code = data['daily']['weather_code'][1]
            tomorrow_weather_info = self.weather_codes.get(tomorrow_weather_code, {'condition': 'default', 'description': 'неизвестно'})
            tomorrow_desc = tomorrow_weather_info['description']
            tomorrow_condition = tomorrow_weather_info['condition']

            # Получаем текущую дату и дату завтра
            current_date = datetime.now(self.moscow_tz).strftime('%d.%m.%y')
            tomorrow_date = (datetime.now(self.moscow_tz) + timedelta(days=1)).strftime('%d.%m.%y')

            # Получаем иконки для текущей погоды и завтра
            current_weather_icon = self.get_weather_icon(weather_condition)
            tomorrow_weather_icon = self.get_weather_icon(tomorrow_condition)
            
            weather_text = (
                f"📅 {current_date}\n"
                f"🌡 Текущая температура: {current_temp}°C\n"
                f"🌡 Ощущается как: {feels_like}°C\n"
                f"{current_weather_icon['emoji']} {current_desc.capitalize()}\n\n"
                f"📅 {tomorrow_date}\n"
                f"🌡 Температура: {tomorrow_temp}°C\n"
                f"{tomorrow_weather_icon['emoji']} {tomorrow_desc.capitalize()}"
            )

            return [{
                'text': weather_text,
                'current_weather_gif': InputFile(current_weather_icon['gif'])
            }]

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error while fetching weather: {e}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"API response: {e.response.text}")
            return self.get_test_weather()
        except Exception as e:
            self.logger.error(f"Unexpected error while fetching weather: {e}")
            return self.get_test_weather()

    def get_test_weather(self):
        weather_icon = self.weather_icons['clear']  # Используем солнечную иконку
        current_date = datetime.now(self.moscow_tz).strftime('%d.%m.%y')
        tomorrow_date = (datetime.now(self.moscow_tz) + timedelta(days=1)).strftime('%d.%m.%y')
        
        return [{
            "text": (
                f"📅 {current_date}\n"
                "🌡 Текущая температура: +21°C\n"
                "🌡 Ощущается как: +20°C\n"
                "☀️ Ясно\n\n"
                f"📅 {tomorrow_date}\n"
                "🌡 Температура: +22°C\n"
                "☀️ Ясно"
            ),
            "current_weather_gif": InputFile(weather_icon['gif'])
        }]

    def get_news_by_category(self, category):
        try:
            if category == "🌤 Погода":
                return self.get_weather()

            # Получаем текущую дату в московском часовом поясе
            current_date = datetime.now(self.moscow_tz)
            week_ago = current_date - timedelta(days=7)
            
            # Маппинг категорий на URL-пути сайта
            category_urls = {
                "🏢 Администрация": "https://city-yar.ru/news/",
                "🚗 Транспорт": "https://city-yar.ru/news/transport/",
                "🏗️ Строительство": "https://city-yar.ru/news/construction/",
                "📋🖋 Политика": "https://city-yar.ru/news/politics/",
                "🏢 Городские события": "https://city-yar.ru/news/",
                "🎭 Культурная жизнь": "https://city-yar.ru/news/",
                "📢 Анонсы": "https://city-yar.ru/news/"
            }

            url = category_urls.get(category, "https://city-yar.ru/news/")
            self.logger.info(f"Fetching news from URL: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'  # Explicitly set encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.find_all('div', class_='news-item')
            
            if not news_items:
                self.logger.warning(f"No news items found for category: {category}")
                return []
            
            news_list = []
            for item in news_items:
                title = item.find('h3').text.strip()
                date_elem = item.find('div', class_='news-date')
                date_str = date_elem.text.strip() if date_elem else current_date.strftime('%Y-%m-%d')
                
                # Convert date string to datetime object
                try:
                    if '-' in date_str:
                        item_date = datetime.strptime(date_str, '%Y-%m-%d')
                    else:
                        item_date = datetime.strptime(date_str, '%d.%m.%y')
                except ValueError:
                    continue
                
                # Skip news older than a week if we're getting weekly news
                if category == "📰 Новости за неделю" and item_date < week_ago:
                    continue
                
                link = item.find('a')['href']
                if not link.startswith('http'):
                    link = 'https://city-yar.ru' + link
                
                # Получаем описание новости
                description = item.find('div', class_='news-excerpt')
                text = description.text.strip() if description else "Подробности по ссылке"
                
                news_list.append({
                    "title": title,
                    "date": date_str,
                    "text": text,
                    "link": link
                })
            
            return news_list
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error while fetching news: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing news: {e}")
            return []

    def get_test_news(self, category):
        # Тестовые данные на случай, если сайт недоступен
        current_date = datetime.now(self.moscow_tz).strftime('%d.%m.%y')
        news = {
            "🏢 Администрация": [
                {
                    "title": "В Ярославле обсудили развитие городской инфраструктуры",
                    "date": current_date,
                    "text": "В администрации города прошло совещание по развитию городской инфраструктуры. "
                           "Обсуждены вопросы модернизации дорог и благоустройства.",
                    "link": "https://yaroslavl-region.ru/news/1"
                }
            ],
            "🚗 Транспорт": [
                {
                    "title": "Изменения в работе общественного транспорта",
                    "date": current_date,
                    "text": "С 1 апреля вводится новый маршрут автобуса №45. "
                           "Изменятся интервалы движения троллейбусов маршрута №1.",
                    "link": "https://yaroslavl-region.ru/news/2"
                }
            ],
            "🏗️ Строительство": [
                {
                    "title": "Новый жилой комплекс в Ярославле",
                    "date": current_date,
                    "text": "Началось строительство нового жилого комплекса 'Ярославский' в Заволжском районе. "
                           "Комплекс будет включать 5 многоэтажных домов, детский сад, школу и спортивный центр. "
                           "Общая площадь жилых помещений составит более 50 000 квадратных метров. "
                           "Сдача первого этапа строительства запланирована на конец 2025 года. "
                           "В комплексе будут предусмотрены подземный паркинг, зоны отдыха и современные детские площадки.",
                    "link": "https://yaroslavl-region.ru/news/3"
                }
            ],
            "📋🖋 Политика": [
                {
                    "title": "Заседание городской думы",
                    "date": current_date,
                    "text": "На заседании городской думы Ярославля были приняты важные решения по развитию города. "
                           "Депутаты одобрили новый бюджет города на 2024 год, который предусматривает "
                           "значительные инвестиции в развитие инфраструктуры, образования и здравоохранения.",
                    "link": "https://yaroslavl-region.ru/news/4"
                }
            ]
        }
        return news.get(category, [])

    def format_news_message(self, news_list):
        if not news_list:
            return "К сожалению, новости по данной категории временно недоступны."
        
        message = "📰 Новости:\n\n"
        for news in news_list:
            # Convert date format if it's in YYYY-MM-DD format
            date = news['date']
            try:
                if '-' in date:
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    date = date_obj.strftime('%d.%m.%y')
            except:
                pass  # Keep original date if conversion fails
            
            message += f"📌 {news['title']}\n"
            message += f"📅 {date}\n"
            message += f"📝 {news['text']}\n"
            message += f"🔗 Подробнее: {news['link']}\n"
            message += f"Источник: <a href='{news['link']}'>ЯрНовости</a>\n"
        
        return message

    def get_events(self):
        try:
            url = "https://city-yar.ru/events/"
            self.logger.info(f"Fetching events from URL: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'  # Explicitly set encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            event_items = soup.find_all('div', class_='event-item')
            
            if not event_items:
                self.logger.warning("No events found")
                return []
                
            events = []
            for item in event_items[:5]:  # Берем только 5 последних событий
                title = item.find('h3').text.strip()
                date_elem = item.find('div', class_='event-date')
                date = date_elem.text.strip() if date_elem else "Дата не указана"
                link = item.find('a')['href']
                if not link.startswith('http'):
                    link = 'https://city-yar.ru' + link
                
                # Получаем краткое описание события
                description = item.find('div', class_='event-text')
                text = description.text.strip() if description else "Подробности по ссылке"
                
                events.append({
                    "title": title,
                    "date": date,
                    "text": text,
                    "link": link
                })
            
            return events
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error while fetching events: {e}")
            return self.get_test_events()
        except Exception as e:
            self.logger.error(f"Error parsing events: {e}")
            return self.get_test_events()

    def get_test_events(self):
        # Тестовые данные на случай, если сайт недоступен
        current_date = datetime.now(self.moscow_tz).strftime('%d.%m.%y')
        next_week_date = (datetime.now(self.moscow_tz) + timedelta(days=7)).strftime('%d.%m.%y')
        return [
            {
                "title": "Фестиваль 'Ярославль - город будущего'",
                "date": current_date,
                "text": "В Ярославле пройдет фестиваль 'Ярославль - город будущего'. "
                       "В программе: выставки, мастер-классы, концерты и многое другое.",
                "link": "https://city-yar.ru/events/1"
            },
            {
                "title": "Спортивный марафон 'Ярославль - город спорта'",
                "date": next_week_date,
                "text": "В Ярославле пройдет спортивный марафон 'Ярославль - город спорта'. "
                       "Участие могут принять все желающие.",
                "link": "https://city-yar.ru/events/2"
            }
        ] 

    def get_events_by_category(self, category):
        try:
            # Маппинг категорий на URL-пути сайта
            category_urls = {
                "🎭 Культура": "https://city-yar.ru/events/culture/",
                "🎪 Спорт": "https://city-yar.ru/events/sport/",
                "🎓 Образование": "https://city-yar.ru/events/education/"
            }

            url = category_urls.get(category, "https://city-yar.ru/events/")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            event_items = soup.find_all('div', class_='event-item')
            
            if not event_items:
                return []
                
            events = []
            for item in event_items[:5]:  # Берем только 5 последних событий
                title = item.find('h3').text.strip()
                date_elem = item.find('div', class_='event-date')
                date = date_elem.text.strip() if date_elem else "Дата не указана"
                link = item.find('a')['href']
                if not link.startswith('http'):
                    link = 'https://city-yar.ru' + link
                
                # Получаем краткое описание события
                description = item.find('div', class_='event-text')
                text = description.text.strip() if description else "Подробности по ссылке"
                
                events.append({
                    "title": title,
                    "date": date,
                    "text": text,
                    "link": link
                })
            
            return events
            
        except Exception as e:
            print(f"Ошибка при получении событий: {e}")
            return self.get_test_events_by_category(category)

    def get_test_events_by_category(self, category):
        # Тестовые данные на случай, если сайт недоступен
        current_date = datetime.now(self.moscow_tz).strftime('%d.%m.%y')
        next_week_date = (datetime.now(self.moscow_tz) + timedelta(days=7)).strftime('%d.%m.%y')
        two_weeks_date = (datetime.now(self.moscow_tz) + timedelta(days=14)).strftime('%d.%m.%y')
        test_events = {
            "🎭 Культура": [
                {
                    "title": "Фестиваль 'Ярославль - город будущего'",
                    "date": current_date,
                    "text": "В Ярославле пройдет фестиваль 'Ярославль - город будущего'. "
                           "В программе: выставки, мастер-классы, концерты и многое другое.",
                    "link": "https://city-yar.ru/events/1"
                }
            ],
            "🎪 Спорт": [
                {
                    "title": "Спортивный марафон 'Ярославль - город спорта'",
                    "date": next_week_date,
                    "text": "В Ярославле пройдет спортивный марафон 'Ярославль - город спорта'. "
                           "Участие могут принять все желающие.",
                    "link": "https://city-yar.ru/events/2"
                }
            ],
            "🎓 Образование": [
                {
                    "title": "Образовательный форум 'Ярославль - город знаний'",
                    "date": two_weeks_date,
                    "text": "В Ярославле пройдет образовательный форум 'Ярославль - город знаний'. "
                           "В программе: лекции, мастер-классы, дискуссии и многое другое.",
                    "link": "https://city-yar.ru/events/3"
                }
            ]
        }
        return test_events.get(category, []) 