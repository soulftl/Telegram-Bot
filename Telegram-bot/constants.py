# Координаты центра Ярославля
YAROSLAVL_CENTER = {
    "lat": 57.626065,
    "lon": 39.887478
}

# Static URL for Yaroslavl city center map image
YAROSLAVL_CENTER_MAP_IMAGE_URL = f"https://static-maps.yandex.ru/1.x/?ll={YAROSLAVL_CENTER['lon']},{YAROSLAVL_CENTER['lat']}&z=12&size=600,450&l=map&pt={YAROSLAVL_CENTER['lon']},{YAROSLAVL_CENTER['lat']},pm2blm"

# Map categories for map section (keys are button texts with emoji, values are English)
MAP_CATEGORY_MAPPING = {
    "🏰 Исторический центр": "attractions",
    "🏥 Травмпункты": "trauma_centers",
    "🌳 Парки": "parks",
    "🎭 Театры": "theaters",
    "🛍️ Торговые центры": "shopping_centers"
}

# Reverse mapping from English to button texts with emoji
REVERSE_MAP_CATEGORY_MAPPING = {
    "attractions": "🏰 Исторический центр",
    "trauma_centers": "🏥 Травмпункты",
    "parks": "🌳 Парки",
    "theaters": "🎭 Театры",
    "shopping_centers": "🛍️ Торговые центры"
}

# Mapping for cleaned category names (no emoji, lowercase) to English
CLEAN_CATEGORY_NAME_MAPPING = {
    "историческийцентр": "attractions",
    "травмпункты": "trauma_centers",
    "парки": "parks",
    "театры": "theaters",
    "торговыецентры": "shopping_centers"
}

# Mapping from English category names to Russian singular forms for prompts
ENGLISH_TO_RUSSIAN_PROMPT_MAPPING = {
    "attractions": "Выберите исторический центр:",
    "trauma_centers": "Выберите травмпункт:",
    "parks": "Выберите парк:",
    "theaters": "Выберите театр:",
    "shopping_centers": "Выберите торговый центр:"
}

# Proper Russian news category names for different contexts
NEWS_CATEGORY_NAMES = {
    "administration": {
        "default": "администрации",
        "by": "администрации"
    },
    "transport": {
        "default": "транспорту",
        "by": "транспорту"
    },
    "construction": {
        "default": "ремонту и благоустройству",
        "by": "ремонту и благоустройству"
    },
    "politics": {
        "default": "политике",
        "by": "политике"
    },
    "weather": {
        "default": "погоде",
        "by": "погоде"
    },
    "culture": {
        "default": "культуре",
        "by": "культуре"
    }
}

# Proper Russian event category names for different contexts
EVENT_CATEGORY_NAMES = {
    "culture": {
        "default": "культуры",
        "by": "культуре"
    },
    "sport": {
        "default": "спорта",
        "by": "спорту"
    },
    "education": {
        "default": "образования",
        "by": "образованию"
    },
    "entertainment": {
        "default": "развлечений",
        "by": "развлечениям"
    },
    "exhibitions": {
        "default": "выставок",
        "by": "выставкам"
    },
    "concerts": {
        "default": "концертов",
        "by": "концертам"
    }
} 