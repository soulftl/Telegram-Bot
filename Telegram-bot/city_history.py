import telebot
import telebot.types as types
import logging
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Информация о темах истории
HISTORY_TOPICS = {
    "gerb": {
        "title": "🐻 Герб Ярославля",
        "text": (
            "🐻 <b>Герб Ярославля</b>\n\n"
            "На гербе Ярославля — медведь с золотой секирой.\n"
            "Медведь — символ силы, мужества и мудрости,\n"
            "а секира — власти и защиты города.\n\n"
            "⚔ Легенда гласит, что князь Ярослав Мудрый победил медведя\n"
            "на месте основания города.\n"
            "Сегодня герб — гордость ярославцев и узнаваемый символ на\n"
            "флаге, зданиях и сувенирах!"
        )
    },
    "architecture": {
        "title": "🏛 Архитектура Ярославля",
        "text": (
            "🏛 <b>Архитектура Ярославля</b> 🏛\n\n"
            "Ярославль — музей под открытым небом!\n"
            "Здесь сочетаются древнерусское зодчество, барокко и классицизм.\n\n"
            "✨ <b>Главные жемчужины:</b>\n"
            "• Спасо-Преображенский монастырь — сердце города\n"
            "• Церковь Ильи Пророка — шедевр с фресками\n"
            "• Уникальные купола, белокаменные фасады и резные наличники\n\n"
            "🏆 Исторический центр Ярославля — объект ЮНЕСКО и гордость России!"
        )
    },
    "yaroslav": {
        "title": "👑 Ярослав Мудрый",
        "text": (
            "👑 <b>Ярослав Мудрый</b> 👑\n\n"
            "Ярослав Мудрый — основатель города, великий князь Киевский.\n"
            "В 1010 году он заложил Ярославль на месте победы над медведем.\n\n"
            "🌟 <b>Достижения:</b>\n"
            "• Создал первый свод законов — 'Русская Правда'\n"
            "• Развивал образование, культуру и международные связи\n"
            "• Основал города, строил храмы, укреплял Русь\n\n"
            "🏅 Его имя — символ мудрости, справедливости и силы!"
        )
    }
}

def get_history_keyboard():
    """Создает клавиатуру с темами истории."""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("🐻 Герб", callback_data="history_gerb"),
        types.InlineKeyboardButton("🏛 Архитектура", callback_data="history_architecture")
    )
    keyboard.row(
        types.InlineKeyboardButton("👑 Ярослав Мудрый", callback_data="history_yaroslav")
    )
    keyboard.row(
        types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_about")
    )
    return keyboard

def send_history_topic(bot, message, topic):
    """Отправляет информацию о выбранной теме истории (только текст)."""
    try:
        if topic not in HISTORY_TOPICS:
            return None
        topic_info = HISTORY_TOPICS[topic]
        bot.send_message(
            message.chat.id,
            topic_info['text'],
            parse_mode='HTML'
        )
        return topic_info
    except Exception as e:
        logger.error(f"Error in send_history_topic: {e}")
        return None 