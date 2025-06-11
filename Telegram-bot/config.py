import os

# Токен бота
BOT_TOKEN = '8088419266:AAH7VBFsngtnfrxhLEGgJqKLFVAAkon6VM4'

ADMIN_IDS = ['1666258551'] # Добавьте сюда ID администраторов, например: ['123456789', '987654321']

# Stable Diffusion API Key
STABLE_DIFFUSION_API_KEY = 'YOUR_STABLE_DIFFUSION_API_KEY'  # Replace with your actual API key

# Настройки API погоды
WEATHER_API_URL = 'https://api.open-meteo.com/v1/forecast'

# News categories
NEWS_CATEGORIES = {
    'general': 'Общие новости',
    'transport': 'Транспорт',
    'construction': 'Строительство',
    'culture': 'Культура',
    'weather': 'Погода',
    'administration': 'Администрация'
}

NEWS_CATEGORY_NAMES = {
    'general': 'Общие новости',
    'transport': 'Транспорт',
    'construction': 'Строительство',
    'culture': 'Культура',
    'weather': 'Погода',
    'administration': 'Администрация'
}

NEWS_STOPWORDS = [] # Добавьте сюда стоп-слова, если это необходимо
NEWS_SOURCES = [] # Добавьте сюда источники новостей, если это необходимо

# Events categories
EVENTS_CATEGORIES = {
    'theater': 'Театры',
    'exhibitions': 'Выставки',
    'concerts': 'Концерты',
    'festivals': 'Фестивали',
    'sport_events': 'Спортивные события',
    'children': 'Детские мероприятия',
    'education': 'Образовательные события',
    'other': 'Другие события'
}

# Attractions categories
ATTRACTIONS_CATEGORIES = {
    'historical': 'Исторические места',
    'museums': 'Музеи',
    'churches': 'Храмы и соборы',
    'parks': 'Парки и скверы',
    'monuments': 'Памятники',
    'architecture': 'Архитектура',
    'nature': 'Природные достопримечательности',
    'entertainment': 'Развлечения'
}

# History categories
HISTORY_CATEGORIES = {
    'foundation': 'Основание города',
    'medieval': 'Средневековый период',
    'imperial': 'Императорский период',
    'soviet': 'Советский период',
    'modern': 'Современный период',
    'famous_people': 'Известные люди',
    'traditions': 'Традиции и обычаи',
    'legends': 'Легенды и мифы'
}

# User states
USER_STATES = {
    'main_menu': 'Главное меню',
    'news': 'Новости',
    'events': 'События',
    'weather': 'Погода',
    'attractions': 'Достопримечательности',
    'history': 'История Ярославля'
}

# File to store user states
USER_STATES_FILE = 'user_states.json'

# Категории мест
LOCATION_CATEGORIES = {
    'historical': 'Исторические места',
    'cultural': 'Культурные объекты',
    'entertainment': 'Развлечения',
    'shopping': 'Шоппинг',
    'food': 'Рестораны и кафе'
}

# Настройки базы данных
DATABASE = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'yaroslavl_bot'
}

# Настройки логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'bot.log',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

YANDEX_API_KEY = 'c1ce85d9-9a90-4564-a5f1-a216250a180f'

CACHE_DIR = os.path.join(os.path.dirname(__file__), 'Materials', 'cache')
STATION_CACHE_FILE = os.path.join(CACHE_DIR, 'station_cache.json')
CACHE_DURATION = 86400

REQUEST_INTERVAL = 5
BASE_URL = "https://yatrans.ru"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
]

CATEGORY_KEYWORDS = {
    "weather": {
        "keywords": [
            "погода", "прогноз", "осадки", "температура", "ветер",
            "дождь", "снег", "град", "туман", "облачность",
            "ураган", "шторм", "гроза", "молния", "гром",
            "жара", "мороз", "заморозки", "оттепель", "гололед"
        ],
        "negative_keywords": [
            "пожар", "ДТП", "авария", "криминал", "происшествие"
        ]
    },
    "admin": {
        "keywords": [
            "администрация", "мэр", "губернатор", "власть", "правительство",
            "депутат", "совет", "закон", "постановление", "решение",
            "бюджет", "финансы", "налоги", "сборы", "отчет",
            "выборы", "голосование", "избирательный", "участок", "комиссия"
        ],
        "negative_keywords": [
            "пожар", "ДТП", "авария", "криминал", "происшествие"
        ]
    },
    "education": {
        "keywords": [
            "образование", "школа", "университет", "институт", "колледж",
            "ученик", "студент", "учитель", "преподаватель", "лекция",
            "экзамен", "зачет", "сессия", "диплом", "выпускной",
            "олимпиада", "конкурс", "соревнование", "наука", "исследование"
        ],
        "negative_keywords": [
            "пожар", "ДТП", "авария", "криминал", "происшествие"
        ]
    }
}

UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY"

STATION_CODES = {
    "ярославль-главный": {"code": "s9600213", "title": "Ярославль-Главный"},
    "центральный рынок": {"code": "s9600214", "title": "Центральный рынок"},
    "волгоградская": {"code": "s9600215", "title": "Волгоградская"},
    "5-й микрорайон": {"code": "s9600216", "title": "5-й микрорайон"},
    "машприбор": {"code": "s9600217", "title": "Машприбор"},
    "богоявленская площадь": {"code": "s9600218", "title": "Богоявленская площадь"},
    "осташинское": {"code": "s9600219", "title": "Осташинское"},
    "прибрежный": {"code": "s9600220", "title": "Прибрежный"},
    "улица чкалова": {"code": "s9600221", "title": "Улица Чкалова"},
    "угличская": {"code": "s9600222", "title": "Угличская"},
    "улица свердлова": {"code": "s9600223", "title": "Улица Свердлова"},
    "яшз": {"code": "s9600224", "title": "ЯШЗ"},
    "нефтестрой": {"code": "s9600225", "title": "Нефтестрой"}
}

POPULAR_STOPS = {
    "Центральный район": {
        "bus": ["Ярославль-Главный", "Центральный рынок", "Богоявленская площадь"],
        "tram": ["Улица Свердлова", "Богоявленская площадь"],
        "trolleybus": ["Ярославль-Главный", "Богоявленская площадь"]
    },
    "Красноперекопский район": {
        "bus": ["Волгоградская", "ЯШЗ"],
        "tram": ["Улица Чкалова"],
        "trolleybus": ["ЯШЗ"]
    },
    "Фрунзенский район": {
        "bus": ["5-й микрорайон", "Машприбор"],
        "tram": ["Угличская"],
        "trolleybus": ["Нефтестрой"]
    },
    "Дзержинский район": {
        "bus": ["Осташинское", "Прибрежный"],
        "tram": [],
        "trolleybus": []
    }
}

POPULAR_BUSES = {
    "1": {"title": "Волгоградская - 5-й микрорайон", "uid": "bus_1_yaroslavl"},
    "5": {"title": "Богоявленская площадь - Осташинское", "uid": "bus_5_yaroslavl"},
    "30": {"title": "Ярославль-Главный - Машприбор", "uid": "bus_30_yaroslavl"},
    "41": {"title": "Ярославль-Главный - Прибрежный", "uid": "bus_41_yaroslavl"}
}

POPULAR_TRAMS = {
    "1": {"title": "Улица Чкалова - Угличская", "uid": "tram_1_yaroslavl"},
    "5": {"title": "Богоявленская площадь - Улица Свердлова", "uid": "tram_5_yaroslavl"}
}

POPULAR_TROLLEYBUSES = {
    "1": {"title": "Ярославль-Главный - ЯШЗ", "uid": "trolleybus_1_yaroslavl"},
    "9": {"title": "Нефтестрой - Ярославль-Главный", "uid": "trolleybus_9_yaroslavl"}
}