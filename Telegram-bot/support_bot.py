import telebot
from telebot import types
import logging
from datetime import datetime
from support_db import SupportDB
import os

# Инициализация бота с токеном
SUPPORT_BOT_TOKEN = '8121473822:AAGJ9lwlxrt1PQiRGKzI29wSw7Ve2Gy3CMg'
bot = telebot.TeleBot(SUPPORT_BOT_TOKEN)

# Инициализация базы данных
db = SupportDB()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('support_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ID администраторов
ADMIN_IDS = [
    1666258551,  # @soulftl - админ
    858193022   # еще один админ
]

# Словарь для хранения текущих состояний пользователей (FSM - конечный автомат)
user_states = {}

# Категории обращений с эмодзи для удобства пользователей
TICKET_CATEGORIES = {
    "🐞 Ошибка в боте": "bot_error",
    "📱 Проблема с интерфейсом": "interface_issue",
    "❓ Вопрос по функционалу": "functionality_question",
    "💡 Предложение улучшений": "improvement_suggestion",
    "🆘 Другое": "other"
}

# Путь к изображениям
HELP_IMAGE_PATH = "Materials/helpTexBot.jpg"

def create_main_keyboard(is_admin=False):
    """
    Создает основную клавиатуру бота
    :param is_admin: Флаг, указывающий является ли пользователь администратором
    :return: Объект клавиатуры с основными кнопками
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.KeyboardButton("📝 Создать обращение"), types.KeyboardButton("📋 Мои обращения"))
    if is_admin:
        keyboard.row(types.KeyboardButton("👨‍💼 Панель администратора"))
    return keyboard

def create_admin_keyboard():
    """
    Создает клавиатуру для панели администратора
    :return: Объект клавиатуры с кнопками управления
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.KeyboardButton("�� Открытые обращения"))
    keyboard.row(
        types.KeyboardButton("📊 Статистика обращений"),
        types.KeyboardButton("🔍 Поиск обращения")
    )
    keyboard.row(types.KeyboardButton("🔙 Назад"))
    return keyboard

def create_category_keyboard():
    """
    Создает клавиатуру выбора категории обращения
    :return: Объект клавиатуры со списком категорий
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    categories = list(TICKET_CATEGORIES.keys())
    # Все кроме '🆘 Другое'
    main_buttons = [types.KeyboardButton(name) for name in categories if name != "🆘 Другое"]
    for i in range(0, len(main_buttons), 2):
        if i + 1 < len(main_buttons):
            keyboard.row(main_buttons[i], main_buttons[i + 1])
        else:
            keyboard.row(main_buttons[i])
    # '🆘 Другое' отдельной строкой
    keyboard.row(types.KeyboardButton("🆘 Другое"))
    # '❌ Отмена' отдельной строкой
    keyboard.row(types.KeyboardButton("❌ Отмена"))
    return keyboard

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle /start command."""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name
        
        is_admin = user_id in ADMIN_IDS
        # Send welcome photo with caption
        try:
            with open('Materials/helpTexBot.jpg', 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption="👋 Добро пожаловать в службу поддержки НовостЯР!\n\n"
                           "🤝 Я помогу вам решить любые вопросы, связанные с использованием бота.\n\n"
                           "Что я могу:\n"
                           "📝 Принять ваше обращение по любому вопросу\n"
                           "📋 Показать историю ваших обращений\n"
                           "💬 Связать вас с командой поддержки\n\n"
                           "🎯 Выберите нужное действие в меню ниже ⬇️",
                    reply_markup=create_main_keyboard(is_admin)
                )
        except Exception as e:
            logger.error(f"Error sending welcome photo: {e}")
            # Если не удалось отправить фото, отправляем только текст
            bot.send_message(
                message.chat.id,
                "👋 Добро пожаловать в службу поддержки НовостЯР!\n\n"
                "🤝 Я помогу вам решить любые вопросы, связанные с использованием бота.\n\n"
                "Что я могу:\n"
                "📝 Принять ваше обращение по любому вопросу\n"
                "📋 Показать историю ваших обращений\n"
                "💬 Связать вас с командой поддержки\n\n"
                "🎯 Выберите нужное действие в меню ниже ⬇️",
                reply_markup=create_main_keyboard(is_admin)
            )
        
        # Reset user state
        if user_id in user_states:
            del user_states[user_id]
        
        logger.info(f"User {username} (ID: {user_id}) started the support bot")
        
    except Exception as e:
        logger.error(f"Error in handle_start: {e}")
        bot.send_message(
            message.chat.id,
            "Извините, произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=create_main_keyboard()
        )

@bot.message_handler(func=lambda message: message.text == "📝 Создать обращение")
def create_ticket(message):
    """
    Обработчик создания нового обращения
    Запускает процесс создания тикета, начиная с выбора категории
    :param message: Объект сообщения от пользователя
    """
    user_states[message.from_user.id] = {'state': 'waiting_category'}
    
    bot.send_message(
        message.chat.id,
        "Выберите категорию обращения:",
        reply_markup=create_category_keyboard()
    )

@bot.message_handler(func=lambda message: message.text in TICKET_CATEGORIES.keys())
def handle_category_selection(message):
    """Обработчик выбора категории обращения"""
    user_id = message.from_user.id
    if user_states.get(user_id, {}).get('state') != 'waiting_category':
        return

    category = TICKET_CATEGORIES[message.text]
    user_states[user_id] = {
        'state': 'waiting_ticket_subject',
        'category': category
    }
    
    bot.send_message(
        message.chat.id,
        "Опишите вашу проблему или вопрос подробно:\n\n"
        "🔹 Что конкретно не работает или беспокоит\n"
        "🔹 Когда это началось\n"
        "🔹 Какие действия приводят к проблеме\n\n"
        "Это поможет нам быстрее разобраться в ситуации! 🚀",
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).row(
            types.KeyboardButton("❌ Отмена")
        )
    )

@bot.message_handler(func=lambda message: message.text == "📋 Мои обращения")
def show_user_tickets(message):
    """Показывает список обращений пользователя"""
    tickets = db.get_user_tickets(message.from_user.id)
    
    if not tickets:
        bot.send_message(
            message.chat.id,
            "У вас пока нет обращений.",
            reply_markup=create_main_keyboard(message.from_user.id in ADMIN_IDS)
        )
        return

    for ticket in tickets:
        status_emoji = "🟢" if ticket['status'] == 'open' else "🔴"
        ticket_text = (
            f"{status_emoji} Обращение #{ticket['id']}\n"
            f"Статус: {ticket['status']}\n"
            f"Создано: {ticket['created_at']}\n"
            f"Тема: {ticket['subject']}\n\n"
            f"Для просмотра деталей отправьте: /ticket_{ticket['id']}"
        )
        bot.send_message(message.chat.id, ticket_text)

@bot.message_handler(func=lambda message: message.text == "👨‍💼 Панель администратора")
def show_admin_panel(message):
    """Показывает панель администратора."""
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "У вас нет доступа к панели администратора.")
        return
    
    bot.send_message(
        message.chat.id,
        "👨‍💼 Панель администратора\n\n"
        "Выберите действие:",
        reply_markup=create_admin_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "📨 Открытые обращения")
def show_open_tickets(message):
    """Показывает список открытых обращений"""
    if message.from_user.id not in ADMIN_IDS:
        return

    tickets = db.get_open_tickets()
    if not tickets:
        bot.send_message(message.chat.id, "Нет открытых обращений.")
        return

    for ticket in tickets:
        ticket_text = (
            f"🟢 Обращение #{ticket['id']}\n"
            f"От: {ticket['username']}\n"
            f"Создано: {ticket['created_at']}\n"
            f"Тема: {ticket['subject']}\n\n"
            f"Для ответа отправьте: /reply_{ticket['id']}"
        )
        bot.send_message(message.chat.id, ticket_text)

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/ticket_'))
def view_ticket(message):
    """Показывает детали обращения"""
    try:
        ticket_id = int(message.text.split('_')[1])
        ticket = db.get_ticket(ticket_id)
        
        if not ticket or (ticket['user_id'] != message.from_user.id and message.from_user.id not in ADMIN_IDS):
            bot.send_message(message.chat.id, "Обращение не найдено или у вас нет к нему доступа.")
            return

        # Формируем сообщение с деталями обращения
        status_emoji = "🟢" if ticket['status'] == 'open' else "🔴"
        ticket_text = (
            f"{status_emoji} Обращение #{ticket['id']}\n"
            f"Статус: {ticket['status']}\n"
            f"Создано: {ticket['created_at']}\n"
            f"Тема: {ticket['subject']}\n\n"
            "Переписка:\n"
        )

        # Добавляем сообщения
        for msg in ticket['messages']:
            sender = "👤 Вы" if msg['user_id'] == message.from_user.id else "👨‍💼 Поддержка"
            ticket_text += f"\n{sender} ({msg['created_at']}):\n{msg['message']}\n"

        # Добавляем инструкции для ответа
        if ticket['status'] == 'open':
            ticket_text += "\nДля ответа отправьте: /reply_{ticket_id}"

        bot.send_message(message.chat.id, ticket_text)

    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Неверный формат команды.")

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/reply_'))
def reply_to_ticket(message):
    """Обработчик ответа на обращение"""
    try:
        ticket_id = int(message.text.split('_')[1])
        ticket = db.get_ticket(ticket_id)
        
        if not ticket or (ticket['user_id'] != message.from_user.id and message.from_user.id not in ADMIN_IDS):
            bot.send_message(message.chat.id, "Обращение не найдено или у вас нет к нему доступа.")
            return

        if ticket['status'] != 'open':
            bot.send_message(message.chat.id, "Это обращение закрыто.")
            return

        user_states[message.from_user.id] = {
            'state': 'waiting_reply',
            'ticket_id': ticket_id
        }
        
        bot.send_message(
            message.chat.id,
            "Введите ваш ответ:",
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                types.KeyboardButton("🔙 Назад")
            )
        )

    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Неверный формат команды.")

@bot.message_handler(func=lambda message: message.text == "❌ Отмена")
def cancel_action(message):
    """Отмена текущего действия"""
    user_id = message.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    is_admin = user_id in ADMIN_IDS
    bot.send_message(
        message.chat.id,
        "Действие отменено.",
        reply_markup=create_main_keyboard(is_admin)
    )

@bot.message_handler(func=lambda message: message.text == "🔙 Назад")
def handle_back_button(message):
    """Обработчик кнопки 'Назад'."""
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

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """
    Обработчик всех остальных сообщений
    Обрабатывает сообщения в зависимости от текущего состояния пользователя
    :param message: Объект сообщения от пользователя
    """
    user_id = message.from_user.id
    state = user_states.get(user_id, {}).get('state')

    if state == 'waiting_ticket_subject':
        # Создание нового обращения
        ticket_id = db.create_ticket(
            user_id=user_id,
            username=message.from_user.username or f"user_{user_id}",
            subject=message.text[:100]  # Ограничение длины темы
        )
        
        # Сохранение первого сообщения в обращении
        db.add_message(ticket_id, user_id, message.text)
        
        # Отправка подтверждения пользователю
        bot.send_message(
            message.chat.id,
            f"✅ Обращение #{ticket_id} создано!\n\n"
            "Мы рассмотрим ваш вопрос в ближайшее время.",
            reply_markup=create_main_keyboard(user_id in ADMIN_IDS)
        )
        
        # Уведомление администраторов о новом обращении
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(
                    admin_id,
                    f"📩 Новое обращение #{ticket_id}\n"
                    f"От: {message.from_user.username or f'user_{user_id}'}\n"
                    f"Тема: {message.text[:100]}\n\n"
                    f"Для ответа отправьте: /reply_{ticket_id}"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления администратору {admin_id}: {e}")
        
        # Очистка состояния пользователя
        del user_states[user_id]

    elif state == 'waiting_reply':
        # Добавление ответа к существующему обращению
        ticket_id = user_states[user_id]['ticket_id']
        is_admin = user_id in ADMIN_IDS
        
        # Сохранение ответа в базе данных
        db.add_message(ticket_id, user_id, message.text, is_admin=is_admin)
        
        # Получение информации о тикете
        ticket = db.get_ticket(ticket_id)
        
        # Уведомление получателя о новом ответе
        recipient_id = ticket['user_id'] if is_admin else next(iter(ADMIN_IDS), None)
        if recipient_id:
            try:
                sender_type = "Поддержка" if is_admin else "Пользователь"
                bot.send_message(
                    recipient_id,
                    f"📩 Новый ответ в обращении #{ticket_id}\n"
                    f"{sender_type}: {message.text}\n\n"
                    f"Для ответа отправьте: /reply_{ticket_id}"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления получателю {recipient_id}: {e}")
        
        # Подтверждение отправки ответа
        bot.send_message(
            message.chat.id,
            "✅ Ваш ответ отправлен!",
            reply_markup=create_main_keyboard(is_admin)
        )
        
        # Очистка состояния пользователя
        del user_states[user_id]

@bot.message_handler(func=lambda message: message.text == "📊 Статистика обращений")
def show_ticket_stats(message):
    """Показывает статистику обращений для администратора."""
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "У вас нет доступа к статистике.")
        return

    try:
        all_tickets = db.get_all_tickets()
        open_tickets = db.get_open_tickets()
        closed_tickets = [t for t in all_tickets if t['status'] == 'closed']
        today = datetime.now().date()
        today_tickets = [t for t in all_tickets if str(t['created_at']).startswith(str(today))]

        stats_text = (
            "📊 Статистика обращений:\n\n"
            f"📝 Всего обращений: {len(all_tickets)}\n"
            f"🟢 Открытых: {len(open_tickets)}\n"
            f"🔴 Закрытых: {len(closed_tickets)}\n"
            f"📅 За сегодня: {len(today_tickets)}\n\n"
            "Выберите действие:"
        )

        bot.send_message(
            message.chat.id,
            stats_text,
            reply_markup=create_admin_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in show_ticket_stats: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при получении статистики. Попробуйте позже.",
            reply_markup=create_admin_keyboard()
        )

@bot.message_handler(func=lambda message: message.text == "🔍 Поиск обращения")
def search_ticket_start(message):
    """Запрашивает у администратора ID обращения для поиска."""
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "У вас нет доступа к поиску обращений.")
        return

    user_states[message.from_user.id] = {'state': 'waiting_ticket_search'}
    bot.send_message(
        message.chat.id,
        "Введите ID обращения для поиска:",
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).row(
            types.KeyboardButton("🔙 Назад")
        )
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'waiting_ticket_search')
def search_ticket_process(message):
    """Показывает детали обращения по введённому ID."""
    if message.text == "🔙 Назад":
        user_states.pop(message.from_user.id, None)
        bot.send_message(
            message.chat.id,
            "Выберите действие:",
            reply_markup=create_admin_keyboard()
        )
        return

    try:
        ticket_id = int(message.text.strip())
        ticket = db.get_ticket(ticket_id)
        
        if not ticket:
            bot.send_message(
                message.chat.id,
                "Обращение с таким ID не найдено.",
                reply_markup=create_admin_keyboard()
            )
        else:
            status_emoji = "🟢" if ticket['status'] == 'open' else "🔴"
            ticket_text = (
                f"{status_emoji} Обращение #{ticket['id']}\n"
                f"Статус: {ticket['status']}\n"
                f"Создано: {ticket['created_at']}\n"
                f"Тема: {ticket['subject']}\n\n"
                "Переписка:\n"
            )
            
            for msg in ticket['messages']:
                sender = "👤 Пользователь" if not msg['is_admin'] else "👨‍💼 Поддержка"
                ticket_text += f"\n{sender} ({msg['created_at']}):\n{msg['message']}\n"
            
            bot.send_message(
                message.chat.id,
                ticket_text,
                reply_markup=create_admin_keyboard()
            )
    except ValueError:
        bot.send_message(
            message.chat.id,
            "Некорректный ID обращения. Введите числовой ID.",
            reply_markup=create_admin_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in search_ticket_process: {e}")
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при поиске обращения. Попробуйте позже.",
            reply_markup=create_admin_keyboard()
        )
    
    user_states.pop(message.from_user.id, None)

# Запуск бота в режиме бесконечного опроса
if __name__ == "__main__":
    logger.info("Support bot started")
    bot.infinity_polling() 