import sqlite3
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    conn = None
    try:
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        
        # Проверяем структуру таблицы
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        logger.info("Table structure:")
        for col in columns:
            logger.info(f"Column: {col}")
        
        # Проверяем содержимое таблицы
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        logger.info(f"\nFound {len(users)} users:")
        for user in users:
            logger.info(f"User: {user}")
            
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_database() 