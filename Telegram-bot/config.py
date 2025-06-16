import os

# Токен основного бота
BOT_TOKEN = '8088419266:AAH7VBFsngtnfrxhLEGgJqKLFVAAkon6VM4'

# Токен бота поддержки
SUPPORT_BOT_TOKEN = '8121473822:AAGJ9lwlxrt1PQiRGKzI29wSw7Ve2Gy3CMg'

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

# Alias for NEWS_CATEGORIES
CATEGORY_MAPPING = NEWS_CATEGORIES

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

# Alias for EVENTS_CATEGORIES
EVENT_CATEGORY_MAPPING = EVENTS_CATEGORIES

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
            "пожар", "ДТП", "авария", "криминал", "происшествие", "издевательство"
        ]
    },
    "transport": {
        "keywords": [
            "транспорт", "автобус", "трамвай", "троллейбус", "поезд", "дорога",
            "улица", "пробка", "маршрут", "движение", "перевозки",
            "пассажиры", "билет", "остановка", "вокзал", "метро", "ДТП", "авария"
        ],
        "negative_keywords": [
            "криминал", "происшествие", "преступление", "следствие", "суд",
            "полиция", "задержание", "убийство", "издевательство", "пожар", "взрыв", "кража", "насилие"
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
            "пожар", "ДТП", "авария", "криминал", "происшествие", "издевательство"
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
            "пожар", "ДТП", "авария", "криминал", "происшествие", "издевательство"
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

# Constants for Yaroslavl map
YAROSLAVL_CENTER = (57.626559, 39.893813)
YAROSLAVL_CENTER_MAP_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/e/ea/Yaroslavl_Center_Map.jpg"

# Path to city image
# CITY_IMAGE_PATH = "materials/city_image.jpg" # Удалено, не используется

# Mappings (Placeholders, fill with actual data if needed)
MAP_CATEGORY_MAPPING = {
    "исторический центр": "historical",
    "травмпункты": "trauma_centers",
    "парки": "parks",
    "театры": "theaters",
    "торговые центры": "shopping_centers"
}
REVERSE_MAP_CATEGORY_MAPPING = {v: k for k, v in MAP_CATEGORY_MAPPING.items()}
CLEAN_CATEGORY_NAME_MAPPING = {
    "исторический центр": "исторический центр",
    "травмпункты": "травмпунктов",
    "парки": "парков",
    "театры": "театров",
    "торговые центры": "торговых центров"
}

# Add any other missing mappings if they are used elsewhere
REVERSE_CATEGORY_MAPPING = {v: k for k, v in CATEGORY_MAPPING.items()} # Assuming CATEGORY_MAPPING exists
REVERSE_EVENT_CATEGORY_MAPPING = {v: k for k, v in EVENT_CATEGORY_MAPPING.items()} # Assuming EVENT_CATEGORY_MAPPING exists

# History topics
HISTORY_TOPICS = {
    'foundation': 'Основание города',
    'medieval': 'Средневековый период',
    'imperial': 'Императорский период',
    'soviet': 'Советский период',
    'modern': 'Современный период',
    'famous_people': 'Известные люди',
    'traditions': 'Традиции и обычаи',
    'legends': 'Легенды и мифы'
}

# Locations
LOCATIONS = {
    "attractions": {
        "category_title": "🏛️ Исторический центр Ярославля",
        "category_description": "Главные достопримечательности, памятники архитектуры и истории города.",
        "Ярославский Кремль": {
            "address": "Богоявленская площадь, 25",
            "working_hours": "Пн-Вс 09:40–18:00",
            "phone": "(4852) 40-10-85",
            "description": "Ярославский Кремль (Спасо-Преображенский монастырь) — древнейший монастырь Ярославля; основан в 1216 году. Объект Всемирного наследия ЮНЕСКО.",
            "lat": 57.6253,
            "lon": 39.8893
        },
        "Успенский собор": {
            "address": "Которосльная набережная, 2/1",
            "working_hours": "Пн-Вс 09:00–18:00",
            "phone": "(4852) 72-96-33",
            "description": "Кафедральный собор Ярославской епархии Русской православной церкви. Восстановлен на историческом месте к 1000-летию Ярославля.",
            "lat": 57.6257,
            "lon": 39.8970
        },
        "Церковь Ильи Пророка": {
            "address": "Советская площадь, 7",
            "working_hours": "Пн-Вс 09:00–18:00",
            "phone": "(4852) 30-38-60",
            "description": "Выдающийся памятник архитектуры Ярославля XVII века, украшенный фресками.",
            "lat": 57.6272,
            "lon": 39.8927
        },
        "Памятник Ярославу Мудрому": {
            "address": "Богоявленская площадь",
            "description": "Памятник основателю города Ярославу Мудрому, установлен в 1993 году.",
            "lat": 57.622459,
            "lon": 39.887001
        },
        "Стрелка": {
            "address": "Которосльная набережная",
            "description": "Стрелка — место слияния Волги и Которосли, символ Ярославля, популярное место для прогулок.",
            "lat": 57.622626,
            "lon": 39.901413
        },
        "Музей истории Ярославля": {
            "address": "Волжская наб., 17",
            "working_hours": "Ср-Вс 10:00–18:00",
            "description": "Музей истории Ярославля — экспозиции по истории города, археологии, культуре. Взрослый билет: 250 ₽, студенты/пенсионеры: 120 ₽, дети до 16 лет: бесплатно.",
            "lat": 57.625184,
            "lon": 39.895557
        }
    },
    "trauma_centers": {
        "category_title": "🏥 Травмпункты Ярославля",
        "category_description": "Адреса и контакты травмпунктов города.",
        "Травмпункт №1": {
            "address": "ул. Загородный сад, 11",
            "working_hours": "Круглосуточно",
            "phone": "(4852) 73-52-69",
            "description": "Травмпункт №1 — круглосуточная медицинская помощь.",
            "lat": 57.639066,
            "lon": 39.864055
        },
        "Травмпункт №2": {
            "address": "просп. Октября, 52",
            "working_hours": "Круглосуточно",
            "phone": "(4852) 73-56-42",
            "description": "Травмпункт №2 — круглосуточная медицинская помощь.",
            "lat": 57.637077,
            "lon": 39.862270
        },
        "Травмпункт №3": {
            "address": "ул. Носкова, 8",
            "working_hours": "Круглосуточно",
            "phone": "(4852) 45-04-09",
            "description": "Травмпункт №3 — круглосуточная медицинская помощь.",
            "lat": 57.608492,
            "lon": 39.838315
        },
        "Травмпункт №4": {
            "address": "ул. Чехова, 39",
            "working_hours": "Пн-Вс 08:00–20:00",
            "phone": "(4852) 25-07-07",
            "description": "Травмпункт №4 — медицинская помощь с 8:00 до 20:00.",
            "lat": 57.639116,
            "lon": 39.864551
        }
    },
    "parks": {
        "category_title": "🌳 Парки Ярославля",
        "category_description": "Зеленые оазисы города, идеальные для прогулок и отдыха.",
        "Юбилейный парк": {
            "address": "ул. Гоголя, 2",
            "working_hours": "Круглосуточно",
            "description": "Крупный благоустроенный парк с зонами отдыха, спортивными площадками и аттракционами.",
            "lat": 57.6069,
            "lon": 39.8519
        },
        "Парк Тысячелетия": {
            "address": "Которосльная набережная, 53",
            "working_hours": "Круглосуточно",
            "description": "Современный парк с прогулочными зонами, фонтанами и амфитеатром. Отличное место для отдыха и проведения мероприятий.",
            "lat": 57.6186,
            "lon": 39.8953
        },
        "Петропавловский парк": {
            "address": "ул. 2-я Петропавловская",
            "working_hours": "Пн-Вс 08:00–20:00",
            "description": "Один из старейших парков Ярославля, бывшая территория мануфактуры.",
            "lat": 57.599444,
            "lon": 39.845000
        },
        "Бутусовский парк": {
            "address": "ул. Пушкина, 13Б",
            "working_hours": "Круглосуточно",
            "description": "Один из старейших парков города, излюбленное место для прогулок и пикников.",
            "lat": 57.6276,
            "lon": 39.8732
        },
        "Парк Победы": {
            "address": "ул. Урицкого, 48",
            "working_hours": "Круглосуточно",
            "description": "Мемориальный комплекс, посвященный Победе в Великой Отечественной войне. Сквер, памятники, вечный огонь.",
            "lat": 57.6389,
            "lon": 39.9234
        },
        "Демидовский сквер": {
            "address": "пл. Челюскинцев",
            "working_hours": "Круглосуточно",
            "description": "Сквер в историческом центре города, особо охраняемая природная территория.",
            "lat": 57.625181,
            "lon": 39.897056
        }
    },
    "theaters": {
        "category_title": "🎭 Театры Ярославля",
        "category_description": "Информация о театрах и культурных представлениях.",
        "Волковский театр": {
            "address": "пл. Волкова, 1",
            "working_hours": "Вт-Вс 10:00–19:00",
            "phone": "(4852) 72-74-67",
            "description": "Первый русский профессиональный театр, основанный Ф. Волковым.",
            "lat": 57.6295,
            "lon": 39.8887
        },
        "ТЮЗ": {
            "address": "ул. Свободы, 23",
            "working_hours": "Вт-Вс 10:00–18:00",
            "phone": "(4852) 72-84-46",
            "description": "Ярославский театр юного зрителя, предлагает спектакли для детей и молодежи.",
            "lat": 57.6270,
            "lon": 39.8770
        },
        "Театр кукол": {
            "address": "ул. Свободы, 23",
            "working_hours": "Пн-Вс 10:00–18:00",
            "phone": "(4852) 72-63-03",
            "description": "Один из старейших театров кукол в России. Спектакли для детей и взрослых.",
            "lat": 57.625007,
            "lon": 39.879943
        },
        "Камерный театр": {
            "address": "ул. Свердлова, 9",
            "working_hours": "Пн-Вс 12:00–19:00",
            "phone": "(4852) 30-56-45",
            "description": "Современный театр, камерные постановки, авторские спектакли.",
            "lat": 57.629113,
            "lon": 39.881033
        }
    },
    "shopping_centers": {
        "category_title": "🛍️ Торговые центры Ярославля",
        "category_description": "Крупные торговые комплексы с широким выбором магазинов и развлечений.",
        "ТРЦ Аура": {
            "address": "ул. Победы, 41",
            "working_hours": "Пн-Вс 10:00–22:00",
            "phone": "(4852) 67-47-50",
            "description": "Один из крупнейших торговых центров Ярославля. Более 150 магазинов, фудкорт, развлекательный центр, детская площадка, парковка.",
            "lat": 57.6190,
            "lon": 39.8660
        },
        "ТРЦ Ривьера": {
            "address": "просп. Машиностроителей, 13А",
            "working_hours": "Пн-Вс 08:00–23:00",
            "phone": "(4852) 67-00-00",
            "description": "Магазины, кафе, кинотеатр, парковка.",
            "lat": 57.648092,
            "lon": 39.953113
        },
        "ТРЦ Вернисаж": {
            "address": "Дорожная ул., 6А",
            "working_hours": "Пн-Вс 10:00–22:00",
            "phone": "(4852) 32-22-22",
            "description": "Торговые галереи, кафе, развлечения, парковка.",
            "lat": 57.571068,
            "lon": 39.842483
        },
        "ТРЦ Космос": {
            "address": "Ленинградский просп., 49А",
            "working_hours": "Пн-Вс 10:00–21:00",
            "phone": "(4852) 58-00-00",
            "description": "Магазины, супермаркет, развлечения, парковка.",
            "lat": 57.679741,
            "lon": 39.791834
        },
        "ТРЦ РИО": {
            "address": "Тутаевское ш., 1",
            "working_hours": "Пн-Вс 09:00–21:00",
            "phone": "(4852) 67-77-77",
            "description": "Магазины, гипермаркет, развлечения, парковка.",
            "lat": 57.670166,
            "lon": 39.837681
        },
        "ТРЦ Яркий": {
            "address": "просп. Машиностроителей, 30/18",
            "working_hours": "Пн-Вс 10:00–21:00",
            "phone": "(4852) 67-88-88",
            "description": "Магазины, кафе, развлечения, парковка.",
            "lat": 57.645544,
            "lon": 39.953417
        }
    }
}