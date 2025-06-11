import requests
from bs4 import BeautifulSoup
import logging
import os
from PIL import Image
from io import BytesIO
import aiohttp
import asyncio

class HistoryParser:
    def __init__(self):
        self.base_url = "https://www.yar.ru"
        self.cache_dir = "cache/history"
        os.makedirs(self.cache_dir, exist_ok=True)

    async def get_history_info(self, topic):
        """Получить информацию о конкретной исторической теме."""
        try:
            # Map topics to their respective URLs
            topic_urls = {
                "Герб": "/about/history/gerb",
                "Архитектура": "/about/history/architecture",
                "Ярослав Мудрый": "/about/history/yaroslav-mudry"
            }

            if topic not in topic_urls:
                return None

            url = self.base_url + topic_urls[topic]
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract title
                        title = soup.find('h1').text.strip()
                        
                        # Extract main content
                        content = soup.find('div', class_='content')
                        if content:
                            text = content.get_text(strip=True)
                            
                            # Extract image
                            image = content.find('img')
                            image_url = None
                            if image and 'src' in image.attrs:
                                image_url = self.base_url + image['src']
                                # Download and save image
                                image_path = os.path.join(self.cache_dir, f"{topic.lower().replace(' ', '_')}.jpg")
                                if not os.path.exists(image_path):
                                    async with session.get(image_url) as img_response:
                                        if img_response.status == 200:
                                            img_data = await img_response.read()
                                            with open(image_path, 'wb') as f:
                                                f.write(img_data)
                                            image_url = image_path

                            return {
                                'title': title,
                                'text': text,
                                'image_url': image_url
                            }
            
            return None
        except Exception as e:
            logging.error(f"Error getting history info: {e}")
            return None

    def get_test_info(self, topic):
        """Получить тестовую информацию для тем, когда сайт не доступен."""
        test_data = {
            "Герб": {
                'title': "Герб Ярославля 🐻",
                'text': (
                    "Медведь — символ силы, мужества и мудрости,\n"
                    "а секира — власти и защиты города.\n\n"
                    "⚔️ Легенда гласит, что князь Ярослав Мудрый победил медведя на месте основания города.\n"
                    "Сегодня герб — гордость ярославцев и узнаваемый символ на флаге, зданиях и сувенирах."
                ),
                'image_url': "Materials/history_city/gerb.jpg"
            },
            "Архитектура": {
                'title': "Архитектура Ярославля 🏛️",
                'text': (
                    "Здесь сочетаются древнерусское зодчество, барокко и классицизм.\n\n"
                    "✨ Главные жемчужины:\n"
                    "• Спасо-Преображенский монастырь — сердце города\n"
                    "• Церковь Ильи Пророка — шедевр с фресками\n"
                    "• Уникальные купола, белокаменные фасады и резные наличники\n\n"
                    "🏆 Исторический центр Ярославля — объект ЮНЕСКО и гордость России!"
                ),
                'image_url': "Materials/history_city/architecture.jpg"
            },
            "Ярослав Мудрый": {
                'title': "Ярослав Мудрый 👑",
                'text': (
                    "📜 В 1010 году он заложил Ярославль на месте победы над медведем.\n\n"
                    "🌟 Достижения:\n"
                    "• Создал первый свод законов — 'Русская Правда'\n"
                    "• Развивал образование, культуру и международные связи\n"
                    "• Основал города, строил храмы, укреплял Русь\n\n"
                    "🏅 Его имя — символ мудрости, справедливости и силы!"
                ),
                'image_url': "Materials/history_city/yaroslav.jpg"
            }
        }
        return test_data.get(topic) 