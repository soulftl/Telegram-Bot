import threading
import logging
from handlers import bot as main_bot, setup_handlers
from support_bot import bot as support_bot
from scheduler import start_scheduler
from database import init_db

# Настройка логирования для записи всех событий бота
# Логи сохраняются в файл bot.log и выводятся в консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_main_bot():
    """Запускает основной Telegram-бот."""
    try:
        # Инициализируем базу данных для хранения информации о пользователях
        init_db()
        
        # Настраиваем все обработчики команд и сообщений
        setup_handlers(main_bot)
        
        # Запускаем планировщик для отправки ежедневных уведомлений
        start_scheduler(main_bot)
        
        # Запускаем бота в режиме постоянного опроса новых сообщений
        logger.info("Запуск основного бота...")
        print("🤖 Основной бот запущен и готов к работе!")
        main_bot.polling(none_stop=True)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        print(f"❌ Ошибка при запуске бота: {e}")

def run_support_bot():
    """Запускает бота поддержки."""
    try:
        logger.info("Запуск бота поддержки...") # Логируем начало запуска
        print("🛟 Бот поддержки запущен и готов к работе!") # Выводим сообщение в консоль
        support_bot.infinity_polling(none_stop=True) # Запускаем бесконечный опрос новых сообщений
    except Exception as e:
        logger.error(f"Ошибка в боте поддержки: {e}") # Логируем ошибку
        print(f"❌ Ошибка в боте поддержки: {e}") # Выводим ошибку в консоль

def main():
    """
    Основная функция запуска бота.
    Выполняет следующие действия:
    1. Инициализирует базу данных
    2. Настраивает обработчики команд и сообщений
    3. Запускает планировщик ежедневных уведомлений
    4. Запускает бота в режиме постоянного опроса
    """
    try:
        # Создаем отдельные потоки выполнения для каждого бота
        main_thread = threading.Thread(target=run_main_bot, name="MainBot")
        support_thread = threading.Thread(target=run_support_bot, name="SupportBot")

        # Запускаем созданные потоки
        main_thread.start()
        support_thread.start()

        # Ожидаем завершения работы обоих потоков (боты будут работать бесконечно, пока не будут остановлены)
        main_thread.join()
        support_thread.join()

    except Exception as e:
        logger.error(f"Критическая ошибка при запуске потоков: {e}") # Логируем критическую ошибку
        print(f"❌ Критическая ошибка: {e}") # Выводим критическую ошибку в консоль

if __name__ == "__main__":
    # Убеждаемся, что код выполняется только при прямом запуске файла
    main()
