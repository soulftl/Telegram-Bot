import telebot
from telebot import types
import logging
from datetime import datetime
from support_db import SupportDB
import os
from bot_instance import support_bot as bot

# Инициализация объекта для работы с базой данных обращений
db = SupportDB()

# Настройка логирования для записи событий бота в файл и вывода в консоль
logging.basicConfig(
    level=logging.INFO, # Уровень логирования: INFO (информационные сообщения и выше)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # Формат сообщений лога
    handlers=[
        logging.FileHandler('support_bot.log'), # Запись логов в файл 'support_bot.log'
        logging.StreamHandler() # Вывод логов в консоль
    ]
)
logger = logging.getLogger(__name__)

# Список ID пользователей, которым доступны функции администратора
ADMIN_IDS = [
    1666258551,  # @soulftl - главный администратор
    858193022   # еще один администратор (пример)
]

# Словарь для хранения текущих состояний пользователей (для реализации FSM - конечного автомата)
# Позволяет боту помнить, на каком шаге взаимодействия находится каждый пользователь
user_states = {}

# Категории обращений, которые пользователи могут выбрать при создании тикета
# Каждая категория имеет русское название для отображения и английский ключ для внутренней логики
TICKET_CATEGORIES = {
    "🐞 Ошибка в боте": "bot_error",
    "📱 Проблема с интерфейсом": "interface_issue",
    "❓ Вопрос по функционалу": "functionality_question",
    "💡 Предложение улучшений": "improvement_suggestion",
    "🆘 Другое": "other"
}

# Обратный маппинг для отображения категорий по их внутреннему ключу
REVERSE_TICKET_CATEGORIES = {v: k for k, v in TICKET_CATEGORIES.items()}

def create_main_keyboard(is_admin=False):
    """
    Создает основную клавиатуру для пользователя.
    Кнопки могут отличаться в зависимости от того, является ли пользователь администратором.
    :param is_admin: Флаг, указывающий, является ли текущий пользователь администратором.
    :return: Объект ReplyKeyboardMarkup с основными кнопками.
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True) # Клавиатура, которая подстраивается под размер экрана
    keyboard.row(types.KeyboardButton("📝 Создать обращение"), types.KeyboardButton("📋 Мои обращения")) # Первый ряд кнопок
    if is_admin: # Если пользователь админ, добавляем кнопку "Панель администратора"
        keyboard.row(types.KeyboardButton("🛠️ Панель администратора"))
    return keyboard

def create_admin_keyboard():
    """
    Создает клавиатуру специально для панели администратора.
    Содержит кнопки для управления обращениями.
    :return: Объект ReplyKeyboardMarkup с кнопками для администратора.
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Располагаем кнопки в соответствии с новым макетом: "Открытые обращения" и "Поиск обращения" в первом ряду
    keyboard.row(types.KeyboardButton("📨 Открытые обращения"), types.KeyboardButton("🔍 Поиск обращения"))
    # Кнопка "Отмена" в последнем ряду
    keyboard.row(types.KeyboardButton("❌ Отмена"))
    return keyboard

def create_category_keyboard():
    """
    Создает клавиатуру для выбора категории обращения при его создании.
    Категории располагаются по две в ряд, 'Другое' и 'Отмена' - отдельные кнопки.
    :return: Объект ReplyKeyboardMarkup с кнопками выбора категорий.
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2) # Клавиатура с двумя кнопками в ряду
    categories = list(TICKET_CATEGORIES.keys()) # Получаем список всех доступных категорий
    # Добавляем все категории, кроме '🆘 Другое', парами
    main_buttons = [types.KeyboardButton(name) for name in categories if name != "🆘 Другое"]
    for i in range(0, len(main_buttons), 2):
        if i + 1 < len(main_buttons):
            keyboard.row(main_buttons[i], main_buttons[i + 1])
        else:
            keyboard.row(main_buttons[i])
    # Добавляем '🆘 Другое' отдельной строкой
    keyboard.row(types.KeyboardButton("🆘 Другое"))
    # Добавляем '❌ Отмена' отдельной строкой для возможности прерывания действия
    keyboard.row(types.KeyboardButton("❌ Отмена"))
    return keyboard

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Обработчик команды /start.
    Приветствует нового или вернувшегося пользователя и предоставляет главное меню.
    :param message: Объект сообщения, содержащий команду /start.
    """
    try:
        user_id = message.from_user.id # Получаем ID пользователя
        username = message.from_user.username or message.from_user.first_name # Получаем имя пользователя или его username
        is_admin = user_id in ADMIN_IDS # Проверяем, является ли пользователь администратором
        # Отправляем приветственное сообщение с информацией о возможностях бота
        bot.send_message(
            message.chat.id,
            "👋 Добро пожаловать в службу поддержки НовостЯР!\n\n"
            "🤝 Я помогу вам решить любые вопросы, связанные с использованием бота.\n\n"
            "Что я могу:\n"
            "📝 Принять ваше обращение по любому вопросу\n"
            "📋 Показать историю ваших обращений\n"
            "💬 Связать вас с командой поддержки\n\n"
            "🎯 Выберите нужное действие в меню ниже ⬇️",
            reply_markup=create_main_keyboard(is_admin) # Отображаем главную клавиатуру (для админа или обычного пользователя)
        )
        
        # Сбрасываем текущее состояние пользователя, если оно было установлено
        if user_id in user_states:
            del user_states[user_id]
        
        logger.info(f"Пользователь {username} (ID: {user_id}) запустил бота поддержки") # Логируем запуск бота пользователем
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике handle_start: {e}") # Логируем ошибку
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при запуске. Пожалуйста, попробуйте позже."
        )

@bot.message_handler(func=lambda message: message.text == "📝 Создать обращение")
def create_ticket(message):
    """Обработчик кнопки "Создать обращение".
    Инициирует процесс создания нового обращения, предлагая пользователю выбрать категорию.
    :param message: Объект сообщения от пользователя.
    """
    user_states[message.from_user.id] = {'state': 'waiting_category'} # Устанавливаем состояние пользователя: ожидание категории
    
    bot.send_message(
        message.chat.id,
        "Выберите категорию обращения:", # Запрос категории
        reply_markup=create_category_keyboard() # Клавиатура с категориями
    )

@bot.message_handler(func=lambda message: message.text in TICKET_CATEGORIES.keys())
def handle_category_selection(message):
    """Обработчик выбора категории обращения.
    Сохраняет выбранную категорию и запрашивает у пользователя подробное описание проблемы.
    :param message: Объект сообщения с выбранной категорией.
    """
    user_id = message.from_user.id
    # Проверяем, находится ли пользователь в правильном состоянии для выбора категории
    if user_states.get(user_id, {}).get('state') != 'waiting_category':
        return # Если нет, игнорируем сообщение

    category = TICKET_CATEGORIES[message.text] # Получаем внутренний ключ категории по ее названию
    user_states[user_id] = {
        'state': 'waiting_ticket_subject', # Переводим пользователя в состояние ожидания темы
        'category': category # Сохраняем выбранную категорию
    }
    
    bot.send_message(
        message.chat.id,
        "Опишите вашу проблему или вопрос подробно:\n\n" # Инструкции для пользователя
        "🔹 Что конкретно не работает или беспокоит\n"
        "🔹 Когда это началось\n"
        "🔹 Какие действия приводят к проблеме\n\n"
        "Это поможет нам быстрее разобраться в ситуации! 🚀",
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).row(
            types.KeyboardButton("❌ Отмена") # Кнопка для отмены действия
        )
    )

@bot.message_handler(func=lambda message: message.text == "📋 Мои обращения")
def show_user_tickets(message):
    """Показывает список всех обращений, созданных текущим пользователем.
    Отображает статус, дату создания, категорию и тему каждого обращения.
    :param message: Объект сообщения от пользователя, запросившего свои обращения.
    """
    tickets = db.get_user_tickets(message.from_user.id) # Получаем все обращения пользователя из базы данных
    
    if not tickets: # Если обращений нет
        bot.send_message(
            message.chat.id,
            "У вас пока нет обращений.",
            reply_markup=create_main_keyboard(message.from_user.id in ADMIN_IDS) # Возвращаем основную клавиатуру
        )
        return

    # Проходим по каждому обращению и формируем сообщение
    for ticket in tickets:
        status_emoji = "🟢" if ticket['status'] == 'open' else "🔴" # Определяем эмодзи статуса (открыто/закрыто)
        # Получаем отображаемое название категории, используя обратный маппинг
        category_display = REVERSE_TICKET_CATEGORIES.get(ticket['category'], 'не указана')
        ticket_text = (
            f"{status_emoji} Обращение #{ticket['id']}\n" # Номер обращения и его статус
            f"Статус: {ticket['status']}\n" # Текстовый статус
            f"Создано: {str(ticket['created_at']).split('.')[0]}\n" # Дата и время создания (без микросекунд)
            f"Категория: {category_display}\n" # Категория обращения
            f"Текст: {ticket['subject']}\n\n" # Текст обращения
            f"Для просмотра деталей отправьте: /ticket_{ticket['id']}" # Инструкция для просмотра деталей
        )
        bot.send_message(message.chat.id, ticket_text) # Отправляем информацию об обращении

@bot.message_handler(func=lambda message: message.text == "🛠️ Панель администратора")
def show_admin_panel(message):
    """Показывает панель администратора.
    Доступна только пользователям с правами администратора.
    :param message: Объект сообщения от пользователя.
    """
    if message.from_user.id not in ADMIN_IDS: # Проверяем, является ли пользователь администратором
        bot.send_message(message.chat.id, "У вас нет доступа к панели администратора.")
        return
    bot.send_message(
        message.chat.id,
        "Выберите действие:", # Приглашение выбрать действие
        reply_markup=create_admin_keyboard() # Отображаем административную клавиатуру
    )

@bot.message_handler(func=lambda message: message.text == "📨 Открытые обращения")
def show_open_tickets(message):
    """Показывает список всех открытых обращений для администраторов.
    Отображает информацию о каждом открытом тикете.
    :param message: Объект сообщения от администратора.
    """
    if message.from_user.id not in ADMIN_IDS: # Проверяем права доступа
        return

    tickets = db.get_open_tickets() # Получаем список открытых обращений из базы данных
    if not tickets: # Если нет открытых обращений
        bot.send_message(message.chat.id, "Нет открытых обращений.")
        return

    # Проходим по каждому открытому обращению и формируем сообщение
    for ticket in tickets:
        category_display = REVERSE_TICKET_CATEGORIES.get(ticket['category'], 'не указана') # Получаем отображаемое название категории
        ticket_text = (
            f"🟢 Обращение #{ticket['id']}\n" # Номер обращения и статус
            f"От: {ticket['username']}\n" # От кого обращение
            f"Создано: {str(ticket['created_at']).split('.')[0]}\n" # Дата и время создания
            f"Категория: {category_display}\n" # Категория
            f"Текст: {ticket['subject']}\n\n" # Текст обращения
            f"Для ответа отправьте: /reply_{ticket['id']}" # Инструкция для ответа
        )
        bot.send_message(message.chat.id, ticket_text) # Отправляем информацию об обращении

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/ticket_'))
def view_ticket(message):
    """Показывает подробные детали конкретного обращения по его ID.
    Включает всю переписку по обращению.
    :param message: Объект сообщения, содержащий команду /ticket_ID.
    """
    try:
        ticket_id = int(message.text.split('_')[1]) # Извлекаем ID обращения из команды
        ticket = db.get_ticket(ticket_id) # Получаем данные обращения из базы данных
        
        # Проверяем наличие обращения и права доступа к нему
        if not ticket or (ticket['user_id'] != message.from_user.id and message.from_user.id not in ADMIN_IDS):
            bot.send_message(message.chat.id, "Обращение не найдено или у вас нет к нему доступа.")
            return

        # Формируем сообщение с деталями обращения
        status_emoji = "🟢" if ticket['status'] == 'open' else "🔴" # Эмодзи статуса
        category_display = REVERSE_TICKET_CATEGORIES.get(ticket['category'], 'не указана') # Отображаемое название категории
        ticket_text = (
            f"{status_emoji} Обращение #{ticket['id']}\n" # Номер и статус
            f"Статус: {ticket['status']}\n" # Текстовый статус
            f"От: {ticket['username']}\n" # От кого обращение
            f"Создано: {str(ticket['created_at']).split('.')[0]}\n" # Дата и время создания
            f"Категория: {category_display}\n" # Категория
            f"Текст: {ticket['subject']}\n\n" # Текст
            "Переписка:\n" # Заголовок для переписки
        )

        # Добавляем все сообщения из переписки по данному обращению
        for msg in ticket['messages']:
            sender = "👤 Вы" if msg['user_id'] == message.from_user.id else "👨‍💼 Поддержка" # Определяем отправителя сообщения
            ticket_text += f"\n{sender} ({str(msg['created_at']).split('.')[0]}):\n{msg['message']}\n" # Форматируем и добавляем сообщение

        # Добавляем инструкции для ответа, если обращение открыто
        if ticket['status'] == 'open':
            ticket_text += f"\nДля ответа отправьте: /reply_{ticket['id']}" # Инструкция для ответа

        bot.send_message(message.chat.id, ticket_text)

    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Неверный формат команды.")

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/reply_'))
def reply_to_ticket(message):
    """Обработчик команды /reply_ID.
    Позволяет пользователю или администратору ответить на существующее обращение.
    :param message: Объект сообщения, содержащий команду /reply_ID.
    """
    try:
        ticket_id = int(message.text.split('_')[1]) # Извлекаем ID обращения
        ticket = db.get_ticket(ticket_id) # Получаем информацию об обращении
        
        # Проверяем, существует ли обращение и имеет ли пользователь к нему доступ
        if not ticket or (ticket['user_id'] != message.from_user.id and message.from_user.id not in ADMIN_IDS):
            bot.send_message(message.chat.id, "Обращение не найдено или у вас нет к нему доступа.")
            return

        # Проверяем, что обращение открыто
        if ticket['status'] != 'open':
            bot.send_message(message.chat.id, "Это обращение закрыто.")
            return

        user_states[message.from_user.id] = { # Устанавливаем состояние пользователя для ожидания ответа
            'state': 'waiting_reply',
            'ticket_id': ticket_id
        }
        
        bot.send_message(
            message.chat.id,
            "Введите ваш ответ:", # Запрос ответа
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                types.KeyboardButton("❌ Отмена") # Кнопка для отмены ответа
            )
        )

    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Неверный формат команды. Используйте /reply_ID_обращения.")

@bot.message_handler(func=lambda message: message.text == "❌ Отмена")
def cancel_action(message):
    """Обработчик кнопки "Отмена".
    Сбрасывает текущее состояние пользователя и возвращает его в главное меню.
    :param message: Объект сообщения от пользователя.
    """
    user_id = message.from_user.id
    if user_id in user_states: # Если у пользователя было активное состояние
        del user_states[user_id] # Удаляем состояние
    is_admin = user_id in ADMIN_IDS # Проверяем, является ли пользователь администратором
    bot.send_message(
        message.chat.id,
        "Действие отменено.",
        reply_markup=create_main_keyboard(is_admin) # Возвращаем основную клавиатуру
    )

@bot.message_handler(func=lambda message: message.text == "🔙 Назад")
def handle_back_button(message):
    """Обработчик кнопки 'Назад'.
    Возвращает пользователя в главное меню.
    :param message: Объект сообщения от пользователя.
    """
    # Проверяем, является ли пользователь администратором, чтобы отобразить правильную клавиатуру
    if message.from_user.id in ADMIN_IDS:
        bot.send_message(
            message.chat.id,
            "Выберите действие:",
            reply_markup=create_main_keyboard(is_admin=True)
        )
    else:
        bot.send_message(
            message.chat.id,
            "Выберите действие:",
            reply_markup=create_main_keyboard()
        )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'waiting_ticket_search')
def search_ticket_process(message):
    """Обработчик процесса поиска обращения по ID для администраторов.
    Принимает введенный ID и отображает детали обращения или сообщение об ошибке.
    :param message: Объект сообщения с введенным ID обращения.
    """
    if message.text == "❌ Отмена": # Если администратор отменил поиск
        user_states.pop(message.from_user.id, None) # Удаляем состояние поиска
        bot.send_message(
            message.chat.id,
            "Выберите действие:",
            reply_markup=create_admin_keyboard() # Возвращаем административную клавиатуру
        )
        return

    try:
        ticket_id = int(message.text.strip()) # Преобразуем текст сообщения в числовой ID
        ticket = db.get_ticket(ticket_id) # Получаем обращение из базы данных
        
        if not ticket: # Если обращение не найдено
            # Отправляем более подробное сообщение, если обращение не найдено
            if len(str(ticket_id)) > 5: # Эвристика: если ID слишком длинный, возможно, ввели ID пользователя
                bot.send_message(
                    message.chat.id,
                    "Обращение с таким ID не найдено. Возможно, вы ввели ID пользователя вместо номера обращения. Пожалуйста, введите номер обращения (например, 1, 2, 3):",
                    reply_markup=create_admin_keyboard()
                )
            else:
                bot.send_message(
                    message.chat.id,
                    "Обращение с таким ID не найдено.",
                    reply_markup=create_admin_keyboard()
                )
        else:
            # Формируем сообщение с деталями найденного обращения
            status_emoji = "🟢" if ticket['status'] == 'open' else "🔴" # Эмодзи статуса
            category_display = REVERSE_TICKET_CATEGORIES.get(ticket['category'], 'не указана') # Отображаемое название категории
            ticket_text = (
                f"{status_emoji} Обращение #{ticket['id']}\n" # Номер обращения и статус
                f"Статус: {ticket['status']}\n" # Текстовый статус
                f"От: {ticket['username']}\n" # Отправитель
                f"Создано: {str(ticket['created_at']).split('.')[0]}\n" # Дата и время создания
                f"Категория: {category_display}\n" # Категория
                f"Текст: {ticket['subject']}\n\n" # Текст
                "Переписка:\n" # Заголовок для переписки
            )
            
            # Добавляем все сообщения из переписки
            for msg in ticket['messages']:
                sender = "👤 Пользователь" if not msg['is_admin'] else "👨‍💼 Поддержка" # Определяем, кто отправил сообщение
                ticket_text += f"\n{sender} ({str(msg['created_at']).split('.')[0]}):\n{msg['message']}\n" # Форматируем и добавляем сообщение
            
            bot.send_message(
                message.chat.id,
                ticket_text,
                reply_markup=create_admin_keyboard() # Возвращаем административную клавиатуру
            )
    except ValueError:
        # Если введенный ID не является числом
        bot.send_message(
            message.chat.id,
            "Некорректный ID обращения. Введите числовой ID (например, 1, 2, 3).",
            reply_markup=create_admin_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в search_ticket_process: {e}") # Логируем другие ошибки
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при поиске обращения. Попробуйте позже.",
            reply_markup=create_admin_keyboard()
        )
    
    user_states.pop(message.from_user.id, None) # Очищаем состояние пользователя после обработки запроса

@bot.message_handler(func=lambda message: message.text == "🔍 Поиск обращения")
def search_ticket_start(message):
    """Обработчик кнопки "Поиск обращения" для администраторов.
    Запрашивает у администратора ID обращения для последующего поиска.
    :param message: Объект сообщения от администратора.
    """
    if message.from_user.id not in ADMIN_IDS: # Проверяем права доступа
        bot.send_message(message.chat.id, "У вас нет доступа к поиску обращений.")
        return

    user_states[message.from_user.id] = {'state': 'waiting_ticket_search'} # Устанавливаем состояние ожидания ID
    cancel_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_keyboard.row(types.KeyboardButton("❌ Отмена")) # Кнопка для отмены
    bot.send_message(
        message.chat.id,
        "Введите ID обращения для поиска:",
        reply_markup=cancel_keyboard
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """
    Универсальный обработчик для всех текстовых сообщений, которые не были перехвачены другими обработчиками.
    Его логика зависит от текущего состояния пользователя.
    :param message: Объект сообщения от пользователя.
    """
    user_id = message.from_user.id
    state = user_states.get(user_id, {}).get('state') # Получаем текущее состояние пользователя

    if state == 'waiting_ticket_subject':
        # Логика для создания нового обращения, когда пользователь ввел тему
        ticket_id = db.create_ticket(
            user_id=user_id,
            username=message.from_user.username or f"user_{user_id}",
            category=user_states[user_id].get('category'),  # Добавляем категорию из состояния пользователя
            subject=message.text[:100]  # Ограничение длины темы до 100 символов
        )
        
        # Сохраняем первое сообщение пользователя как часть обращения
        db.add_message(ticket_id, user_id, message.text)
        
        # Отправляем пользователю подтверждение создания обращения
        bot.send_message(
            message.chat.id,
            f"✅ Обращение #{ticket_id} создано!\n\n"
            "Мы рассмотрим ваш вопрос в ближайшее время.",
            reply_markup=create_main_keyboard(user_id in ADMIN_IDS)
        )
        
        # Уведомляем всех администраторов о новом обращении
        for admin_id in ADMIN_IDS:
            try:
                # Получаем отображаемое название категории для уведомления администратора
                category_for_admin = user_states[user_id].get('category', 'не указана') # Получаем категорию из user_states
                logger.debug(f"[ADMIN NOTIFICATION] User state category: {category_for_admin}")
                category_display_admin = REVERSE_TICKET_CATEGORIES.get(category_for_admin, 'не указана') # Преобразуем в отображаемый текст
                logger.debug(f"[ADMIN NOTIFICATION] Display category: {category_display_admin}")
                bot.send_message(
                    admin_id,
                    f"📩 Новое обращение #{ticket_id}\n"
                    f"От: {message.from_user.username or f'user_{user_id}'}\n"
                    f"Категория: {category_display_admin}\n" # Включаем категорию в уведомление для админа
                    f"Текст: {message.text[:100]}\n\n"
                    f"Для ответа отправьте: /reply_{ticket_id}"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления администратору {admin_id}: {e}", exc_info=True)
        
        # Очищаем состояние пользователя после завершения создания обращения
        del user_states[user_id]

    elif state == 'waiting_reply':
        # Логика для добавления ответа к существующему обращению
        ticket_id = user_states[user_id]['ticket_id'] # Получаем ID обращения, на которое отвечает пользователь
        is_admin = user_id in ADMIN_IDS # Проверяем, является ли отправитель ответа администратором
        
        # Сохраняем ответ в базе данных, помечая, кто его отправил (пользователь или админ)
        db.add_message(ticket_id, user_id, message.text, is_admin=is_admin)
        
        # Получаем обновленную информацию о тикете
        ticket = db.get_ticket(ticket_id)
        
        # Определяем ID получателя уведомления (пользователь, если отвечал админ, или первый админ, если отвечал пользователь)
        recipient_id = ticket['user_id'] if is_admin else next(iter(ADMIN_IDS), None)
        if recipient_id:
            try:
                sender_type = "Поддержка" if is_admin else "Пользователь" # Определяем тип отправителя для уведомления
                bot.send_message(
                    recipient_id,
                    f"📩 Новый ответ в обращении #{ticket_id}\n"
                    f"{sender_type}: {message.text}\n\n"
                    f"Для ответа отправьте: /reply_{ticket_id}"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления получателю {recipient_id}: {e}")
        
        # Подтверждаем отправку ответа пользователю, который его отправил
        bot.send_message(
            message.chat.id,
            "✅ Ваш ответ отправлен!",
            reply_markup=create_main_keyboard(is_admin)
        )
        
        # Очищаем состояние пользователя после отправки ответа
        del user_states[user_id]

# Запуск бота в режиме бесконечного опроса, чтобы он постоянно проверял новые сообщения
if __name__ == "__main__":
    logger.info("Бот поддержки запущен") # Логируем запуск бота
    bot.infinity_polling() 