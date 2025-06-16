import telebot
from config import BOT_TOKEN, SUPPORT_BOT_TOKEN

# Инициализация основного бота
bot = telebot.TeleBot(BOT_TOKEN)

# Инициализация бота поддержки
support_bot = telebot.TeleBot(SUPPORT_BOT_TOKEN) 