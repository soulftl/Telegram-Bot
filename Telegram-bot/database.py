import json
import os
import logging
import sqlite3
from config import CACHE_DIR, STATION_CACHE_FILE
import datetime

# Настройка логгера
logger = logging.getLogger('database')
logger.setLevel(logging.INFO)

# Создаем обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Создаем форматтер
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(console_handler)

# Initialize user states dictionary
user_states = {}

def init_db():
    """
    Создает базу данных и необходимые таблицы при первом запуске бота.
    Если база данных уже существует, просто подключается к ней.
    """
    try:
        # Подключаемся к базе данных (создаст файл users.db, если его нет)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Создаем таблицу пользователей со следующими полями:
        # user_id - уникальный идентификатор пользователя в Telegram
        # username - имя пользователя в Telegram (опционально)
        # first_name - имя пользователя
        # last_name - фамилия пользователя (опционально)
        # registration_date - дата и время первой регистрации
        # last_active - дата и время последней активности
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                registration_date TIMESTAMP,
                last_active TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")

def add_user(user_id, username=None, first_name=None, last_name=None):
    """
    Добавляет нового пользователя в базу данных.
    Если пользователь уже существует, обновляет его информацию.
    
    Args:
        user_id (int): ID пользователя в Telegram
        username (str, optional): Имя пользователя в Telegram
        first_name (str, optional): Имя пользователя
        last_name (str, optional): Фамилия пользователя
    """
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Получаем текущее время для записи даты регистрации и последней активности
        current_time = datetime.now()
        
        # Используем INSERT OR IGNORE, чтобы не перезаписывать существующих пользователей
        cursor.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, last_name, registration_date, last_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, current_time, current_time))
        
        conn.commit()
        conn.close()
        logger.info(f"Пользователь {user_id} добавлен в базу данных")
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя в базу данных: {e}")

def update_last_active(user_id):
    """
    Обновляет время последней активности пользователя.
    Вызывается при каждом взаимодействии пользователя с ботом.
    
    Args:
        user_id (int): ID пользователя в Telegram
    """
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        current_time = datetime.now()
        cursor.execute('''
            UPDATE users 
            SET last_active = ? 
            WHERE user_id = ?
        ''', (current_time, user_id))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка при обновлении времени активности пользователя: {e}")

def get_all_users():
    """
    Получает список ID всех пользователей из базы данных.
    Используется для отправки ежедневных уведомлений.
    
    Returns:
        list: Список ID пользователей
    """
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM users')
        users = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Ошибка при получении списка пользователей: {e}")
        return []

def is_new_user(user_id):
    """
    Проверяет, является ли пользователь новым (зарегистрировался менее 24 часов назад).
    Используется для определения, нужно ли отправлять ему ежедневные уведомления.
    
    Args:
        user_id (int): ID пользователя в Telegram
        
    Returns:
        bool: True если пользователь новый, False если нет
    """
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Получаем дату регистрации пользователя
        cursor.execute('''
            SELECT registration_date 
            FROM users 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        # Если пользователь не найден, считаем его новым
        if not result:
            return True
            
        # Вычисляем разницу между текущим временем и временем регистрации
        registration_time = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')
        time_diff = datetime.now() - registration_time
        return time_diff.total_seconds() < 86400  # 24 часа в секундах
    except Exception as e:
        logger.error(f"Ошибка при проверке нового пользователя: {e}")
        return True  # В случае ошибки считаем пользователя новым

def save_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """Save user to database."""
    conn = None
    try:
        logger.info(f"Attempting to save user: ID={user_id}, username={username}, first_name={first_name}, last_name={last_name}")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if user:
            logger.info(f"User {user_id} already exists in database with data: {user}")
            # Update user info
            cursor.execute('''
                UPDATE users 
                SET username = ?, first_name = ?, last_name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (username, first_name, last_name, user_id))
            logger.info(f"Updated user {user_id} information")
        else:
            logger.info(f"User {user_id} not found, creating new record")
            # Insert new user
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            logger.info(f"Created new user record for user {user_id}")
        
        conn.commit()
        logger.info(f"Successfully saved user {user_id} to database")
        
        # Verify the save
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        saved_user = cursor.fetchone()
        logger.info(f"Verified saved user data: {saved_user}")
        
    except Exception as e:
        logger.error(f"Error saving user {user_id} to database: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_all_user_ids():
    """Get all user IDs from database."""
    conn = None
    try:
        logger.info("Attempting to retrieve all user IDs from database")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM users')
        users = cursor.fetchall()
        
        user_ids = [user[0] for user in users]
        logger.info(f"Retrieved {len(user_ids)} users from database: {user_ids}")
        
        return user_ids
    except Exception as e:
        logger.error(f"Error retrieving users from database: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def load_cache(cache_file):
    """Load data from cache file if it exists and is not expired."""
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading cache from {cache_file}: {e}")
    return {}

def save_cache(cache_file, data):
    """Save data to cache file."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error saving cache to {cache_file}: {e}")

def save_user_state(chat_id, state):
    """Save user state to database."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        state_json = json.dumps(state, ensure_ascii=False)
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, state)
            VALUES (?, ?)
        ''', (chat_id, state_json))
        conn.commit()
        logger.debug(f"User {chat_id} state saved: {state_json}")
    except Exception as e:
        logger.error(f"Error saving user state for {chat_id}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def get_user_state(chat_id):
    """Get user state from database."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT state FROM users WHERE user_id = ?', (chat_id,))
        result = cursor.fetchone()
        if result and result[0]:
            state = json.loads(result[0])
            logger.debug(f"User {chat_id} state retrieved: {state}")
            return state
        logger.debug(f"No state found for user {chat_id}")
        return {}
    except Exception as e:
        logger.error(f"Error retrieving user state for {chat_id}: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def update_user_state(chat_id, new_state_data):
    """Update user state in database."""
    current_state = get_user_state(chat_id)
    current_state.update(new_state_data)
    save_user_state(chat_id, current_state)

def ensure_users_table():
    """Ensure users table exists with correct structure."""
    conn = None
    try:
        logger.info("Checking users table structure...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                state TEXT
            )
        ''')
        
        # Define all expected columns with their types and default values
        expected_columns = {
            'user_id': 'INTEGER PRIMARY KEY',
            'username': 'TEXT',
            'first_name': 'TEXT',
            'last_name': 'TEXT',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'state': 'TEXT',
            'first_start_time': 'TIMESTAMP'
        }

        # Check for missing columns and add them
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        for column_name, column_definition in expected_columns.items():
            if column_name not in existing_columns:
                # For simplicity, we are adding columns without NOT NULL or UNIQUE constraints
                # and without default values for existing rows unless specified.
                # If `first_start_time` is missing, it implies older schema, so we should add it without default.
                if column_name == 'first_start_time':
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_definition.replace('TIMESTAMP', '').strip()}")
                else:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_definition}")
                logger.warning(f"Added missing column: {column_name}")

        conn.commit()
        logger.info("Users table structure verified")
    except Exception as e:
        logger.error(f"Error ensuring users table: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Get database connection."""
    return sqlite3.connect('bot.db')

def is_user_new(user_id: int) -> bool:
    """Check if user was registered today."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        today = datetime.date.today().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ? AND DATE(created_at) = ?', (user_id, today))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        logger.error(f"Error checking if user {user_id} is new: {e}")
        return False
    finally:
        if conn:
            conn.close()

def set_user_first_start_time(user_id: int):
    """Set the first start time for a user."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET first_start_time = CURRENT_TIMESTAMP WHERE user_id = ? AND first_start_time IS NULL', (user_id,))
        conn.commit()
    except Exception as e:
        logger.error(f"Error setting first start time for user {user_id}: {e}")
    finally:
        if conn:
            conn.close()

# Call this function when module is imported
ensure_users_table() 