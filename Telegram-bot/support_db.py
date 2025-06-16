import sqlite3
import json
from datetime import datetime

class SupportDB:
    """
    Класс для работы с базой данных технической поддержки
    Обеспечивает хранение и управление обращениями пользователей
    """
    
    def __init__(self, db_file='support.db'):
        """
        Инициализация подключения к базе данных
        :param db_file: Путь к файлу базы данных SQLite
        """
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        """
        Инициализация структуры базы данных
        Создает необходимые таблицы, если они не существуют
        """
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Создание таблицы обращений
        c.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор обращения
                user_id INTEGER NOT NULL,             -- ID пользователя в Telegram
                username TEXT,                        -- Имя пользователя в Telegram
                status TEXT NOT NULL,                 -- Статус обращения (open/closed)
                created_at TIMESTAMP NOT NULL,        -- Время создания
                updated_at TIMESTAMP NOT NULL,        -- Время последнего обновления
                category TEXT,                        -- Категория обращения
                subject TEXT,                         -- Тема обращения
                priority TEXT DEFAULT 'normal'        -- Приоритет обращения
            )
        ''')
        
        # Создание таблицы сообщений
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор сообщения
                ticket_id INTEGER NOT NULL,           -- ID обращения
                user_id INTEGER NOT NULL,             -- ID отправителя
                is_admin BOOLEAN NOT NULL,            -- Флаг сообщения от администратора
                message TEXT NOT NULL,                -- Текст сообщения
                created_at TIMESTAMP NOT NULL,        -- Время отправки
                FOREIGN KEY (ticket_id) REFERENCES tickets (id) -- Связь с таблицей обращений
            )
        ''')
        
        conn.commit()
        conn.close()

    def create_ticket(self, user_id, username, category=None, subject=None):
        """
        Создание нового обращения
        :param user_id: ID пользователя в Telegram
        :param username: Имя пользователя в Telegram
        :param category: Категория обращения
        :param subject: Тема обращения
        :return: ID созданного обращения
        """
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        now = datetime.now()
        
        c.execute('''
            INSERT INTO tickets (user_id, username, status, created_at, updated_at, category, subject)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, 'open', now, now, category, subject))
        
        ticket_id = c.lastrowid
        conn.commit()
        conn.close()
        return ticket_id

    def add_message(self, ticket_id, user_id, message, is_admin=False):
        """
        Добавление сообщения к обращению
        :param ticket_id: ID обращения
        :param user_id: ID отправителя
        :param message: Текст сообщения
        :param is_admin: Флаг сообщения от администратора
        """
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        now = datetime.now()
        
        # Добавление сообщения
        c.execute('''
            INSERT INTO messages (ticket_id, user_id, message, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticket_id, user_id, message, is_admin, now))
        
        # Обновление времени последнего изменения обращения
        c.execute('''
            UPDATE tickets SET updated_at = ? WHERE id = ?
        ''', (now, ticket_id))
        
        conn.commit()
        conn.close()

    def get_ticket(self, ticket_id):
        """
        Получение информации об обращении
        :param ticket_id: ID обращения
        :return: Словарь с информацией об обращении и его сообщениями
        """
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Получение основной информации об обращении
        c.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        ticket = c.fetchone()
        
        if ticket:
            # Преобразование данных в словарь
            columns = ['id', 'user_id', 'username', 'status', 'created_at', 'updated_at', 'category', 'subject', 'priority']
            ticket_dict = dict(zip(columns, ticket))
            
            # Получение всех сообщений обращения
            c.execute('SELECT * FROM messages WHERE ticket_id = ? ORDER BY created_at', (ticket_id,))
            messages = c.fetchall()
            message_columns = ['id', 'ticket_id', 'user_id', 'is_admin', 'message', 'created_at']
            ticket_dict['messages'] = [dict(zip(message_columns, msg)) for msg in messages]
            
            conn.close()
            return ticket_dict
        
        conn.close()
        return None

    def get_user_tickets(self, user_id):
        """
        Получение всех обращений пользователя
        :param user_id: ID пользователя в Telegram
        :return: Список обращений пользователя
        """
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute('SELECT * FROM tickets WHERE user_id = ? ORDER BY updated_at DESC', (user_id,))
        tickets = c.fetchall()
        
        columns = ['id', 'user_id', 'username', 'status', 'created_at', 'updated_at', 'category', 'subject', 'priority']
        result = [dict(zip(columns, ticket)) for ticket in tickets]
        
        conn.close()
        return result

    def get_open_tickets(self):
        """
        Получение всех открытых обращений
        :return: Список открытых обращений
        """
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        c.execute('SELECT * FROM tickets WHERE status = "open" ORDER BY created_at')
        tickets = c.fetchall()
        
        columns = ['id', 'user_id', 'username', 'status', 'created_at', 'updated_at', 'category', 'subject', 'priority']
        result = [dict(zip(columns, ticket)) for ticket in tickets]
        
        conn.close()
        return result

    def close_ticket(self, ticket_id):
        """
        Закрытие обращения
        :param ticket_id: ID обращения
        """
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        now = datetime.now()
        
        c.execute('''
            UPDATE tickets 
            SET status = 'closed', updated_at = ? 
            WHERE id = ?
        ''', (now, ticket_id))
        
        conn.commit()
        conn.close()

    def reopen_ticket(self, ticket_id):
        """
        Повторное открытие закрытого обращения
        :param ticket_id: ID обращения
        """
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        now = datetime.now()
        
        c.execute('''
            UPDATE tickets 
            SET status = 'open', updated_at = ? 
            WHERE id = ?
        ''', (now, ticket_id))
        
        conn.commit()
        conn.close()

    def get_all_tickets(self):
        """
        Получение всех обращений
        :return: Список всех обращений
        """
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('SELECT * FROM tickets ORDER BY created_at')
        tickets = c.fetchall()
        columns = ['id', 'user_id', 'username', 'status', 'created_at', 'updated_at', 'category', 'subject', 'priority']
        result = [dict(zip(columns, ticket)) for ticket in tickets]
        conn.close()
        return result 