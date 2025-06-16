import schedule
import time
import threading
from datetime import datetime
import pytz
from telebot import types
import logging
from database import get_all_users, is_new_user
from bot_instance import bot

# Настройка логирования для отслеживания ошибок и важных событий
logger = logging.getLogger(__name__)

def send_daily_notification(bot):
    """
    Отправляет ежедневное уведомление всем пользователям о новых новостях и событиях.
    Уведомление содержит inline кнопки для быстрого перехода к новостям или событиям.
    Новые пользователи (зарегистрировавшиеся менее 24 часов назад) не получают уведомление.
    """
    try:
        # Создаем inline клавиатуру с двумя кнопками в одном ряду
        markup = types.InlineKeyboardMarkup(row_width=2)
        news_button = types.InlineKeyboardButton("📰 Новости", callback_data="daily_news")
        events_button = types.InlineKeyboardButton("📅 События", callback_data="daily_events")
        markup.add(news_button, events_button)

        # Получаем список всех пользователей из базы данных
        users = get_all_users()

        # Отправляем сообщение каждому пользователю
        for user_id in users:
            # Пропускаем новых пользователей (зарегистрировавшихся менее 24 часов назад)
            if not is_new_user(user_id):
                try:
                    bot.send_message(
                        user_id,
                        "📢 Появились новые новости и события! Хотите посмотреть?",
                        reply_markup=markup
                    )
                except Exception as e:
                    logger.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")

    except Exception as e:
        logger.error(f"Ошибка в функции send_daily_notification: {e}")

def run_scheduler(bot):
    """
    Запускает планировщик задач, который будет отправлять ежедневные уведомления.
    Планировщик работает в бесконечном цикле, проверяя каждую минуту,
    не пора ли отправить уведомления.
    """
    # Устанавливаем московское время для корректной работы с часовым поясом
    moscow_tz = pytz.timezone('Europe/Moscow')
    
    # Планируем отправку уведомлений на 12:00 МСК каждый день
    schedule.every().day.at("12:00").do(lambda: send_daily_notification(bot))
    
    # Бесконечный цикл для проверки и выполнения запланированных задач
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверяем каждую минуту

def start_scheduler(bot):
    """
    Запускает планировщик в отдельном потоке.
    Это позволяет планировщику работать параллельно с основным ботом,
    не блокируя его работу.
    """
    scheduler_thread = threading.Thread(target=lambda: run_scheduler(bot))
    scheduler_thread.daemon = True  # Поток завершится вместе с основной программой
    scheduler_thread.start() 