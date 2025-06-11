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
    "traditions": {
        "title": "🎪 Традиции Ярославля",
        "text": (
            "<b>Традиции Ярославля</b>\n\n"
            "Ярославль славится своими богатыми традициями, которые формировались на протяжении веков:\n\n"
            "🎭 <b>Театральные традиции</b>\n"
            "• Первый русский профессиональный театр\n"
            "• Фестиваль искусств «Преображение»\n"
            "• Международный театральный фестиваль\n\n"
            "🎨 <b>Ремесленные традиции</b>\n"
            "• Ярославская майолика\n"
            "• Художественная ковка\n"
            "• Резьба по дереву\n\n"
            "🎪 <b>Народные традиции</b>\n"
            "• Масленичные гуляния\n"
            "• Ярославская ярмарка\n"
            "• Праздник Дня города"
        ),
        "image": "Materials/history/traditions.jpg"
    },
    "architecture": {
        "title": "🏛 Архитектура Ярославля",
        "text": (
            "<b>Архитектура Ярославля</b>\n\n"
            "Ярославль - жемчужина Золотого кольца России, известная своей уникальной архитектурой:\n\n"
            "🏰 <b>Церковная архитектура</b>\n"
            "• Церковь Ильи Пророка\n"
            "• Спасо-Преображенский собор\n"
            "• Церковь Иоанна Предтечи\n\n"
            "🏛 <b>Гражданская архитектура</b>\n"
            "• Губернаторский дом\n"
            "• Демидовский лицей\n"
            "• Дом Болконского\n\n"
            "🏗 <b>Современная архитектура</b>\n"
            "• Ярославский вокзал\n"
            "• Концертный зал\n"
            "• Спортивные комплексы"
        ),
        "image": "Materials/history/architecture.jpg"
    },
    "yaroslav": {
        "title": "👑 Ярослав Мудрый",
        "text": (
            "<b>Ярослав Мудрый - основатель города</b>\n\n"
            "Ярослав Владимирович Мудрый (978-1054) - великий князь киевский, основатель Ярославля:\n\n"
            "👑 <b>История основания</b>\n"
            "• 1010 год - основание города\n"
            "• Легенда о медведе\n"
            "• Первая крепость\n\n"
            "📚 <b>Правление</b>\n"
            "• Расширение границ\n"
            "• Развитие культуры\n"
            "• Строительство храмов\n\n"
            "🏆 <b>Наследие</b>\n"
            "• Первый русский свод законов\n"
            "• Развитие образования\n"
            "• Международные связи"
        ),
        "image": "Materials/history/yaroslav.jpg"
    },
    "kremlin": {
        "title": "🏰 Ярославский Кремль",
        "text": (
            "<b>Ярославский Кремль</b>\n\n"
            "Спасо-Преображенский монастырь - исторический центр Ярославля:\n\n"
            "🏛 <b>Архитектура</b>\n"
            "• Спасо-Преображенский собор\n"
            "• Святые ворота\n"
            "• Звонница\n\n"
            "📚 <b>История</b>\n"
            "• Основание в XII веке\n"
            "• Оборона от поляков\n"
            "• Реставрация\n\n"
            "🎭 <b>Современность</b>\n"
            "• Музей-заповедник\n"
            "• Культурные мероприятия\n"
            "• Туристический центр"
        ),
        "image": "Materials/history/kremlin.jpg"
    }
}

def get_history_keyboard():
    """Создает клавиатуру с темами истории."""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("🎪 Традиции", callback_data="history_traditions"),
        types.InlineKeyboardButton("🏛 Архитектура", callback_data="history_architecture")
    )
    keyboard.row(
        types.InlineKeyboardButton("👑 Ярослав Мудрый", callback_data="history_yaroslav"),
        types.InlineKeyboardButton("🏰 Кремль", callback_data="history_kremlin")
    )
    keyboard.row(
        types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_about")
    )
    return keyboard

def send_history_topic(bot, message, topic):
    """Отправляет информацию о выбранной теме истории."""
    try:
        if topic not in HISTORY_TOPICS:
            return None
        
        topic_info = HISTORY_TOPICS[topic]
        
        # Проверяем наличие изображения
        image_path = topic_info.get('image')
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as photo:
                    bot.send_photo(
                        message.chat.id,
                        photo,
                        caption=topic_info['text'],
                        parse_mode='HTML'
                    )
            except Exception as photo_error:
                logger.error(f"Error sending history photo: {photo_error}")
                bot.send_message(
                    message.chat.id,
                    topic_info['text'],
                    parse_mode='HTML'
                )
        else:
            bot.send_message(
                message.chat.id,
                topic_info['text'],
                parse_mode='HTML'
            )
        
        return topic_info
        
    except Exception as e:
        logger.error(f"Error in send_history_topic: {e}")
        return None 