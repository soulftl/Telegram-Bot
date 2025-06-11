import schedule
import time
import threading
import logging
from telebot import TeleBot, types
from news import get_yarnews_articles
from config import ADMIN_IDS

# Настройка логирования для scheduler.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Глобальная переменная для экземпляра бота, который будет передан из main.py
main_bot_instance = None

def set_main_bot_instance(bot_instance):
    global main_bot_instance
    main_bot_instance = bot_instance

def send_daily_reminder():
    """Отправляет ежедневное напоминание с последними новостями."""
    if main_bot_instance is None:
        logger.error("Main bot instance not set for daily reminder.")
        return

    try:
        articles = get_yarnews_articles()
        
        if not articles:
            logger.warning("No articles found for daily reminder")
            return
    
        for user_id in ADMIN_IDS:  # Пока отправляем только админам
            try:
                main_bot_instance.send_message(
                    user_id,
                    "📰 Ежедневный дайджест новостей:\n\n" +
                    "\n\n".join([
                        f"<b>{article['title']}</b>\n{article['description']}\n🔗 <a href=\"{article['link']}\">Подробнее</a>"
                        for article in articles[:5]  # Отправляем только 5 последних новостей
                    ]),
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
            except Exception as e:
                logger.error(f"Error sending daily reminder to user {user_id}: {e}")
                continue
            
    except Exception as e:
        logger.error(f"Error in send_daily_reminder: {e}")

def run_scheduler():
    """Запускает планировщик задач."""
    logger.info("Scheduler started.")
    schedule.every().day.at("09:00").do(send_daily_reminder)
    
    while True:
        schedule.run_pending()
        time.sleep(60) 