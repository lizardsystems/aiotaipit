"""Constants for aiotaipit."""
from __future__ import annotations

import logging

LOGGER = logging.getLogger(__package__)

LOG_LEVELS = {
    None: logging.WARNING,  # 0
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
}

# OAuth client ID and secret
#
# В конфигурации используются идентификатор клиента и секрет,
# используемые мобильным приложением на момент разработки.
# Если это перестанет работать, вы можете найти новые с помощью прокси-сервера MITM с мобильным приложением.
# Приложение вызовет https://cloud.meters.taipit.ru/oauth/v2/token с client_id и client_secret.
# Затем вы можете использовать эти значения во время настройки.

DEFAULT_CLIENT_ID = '1_34mi8uiv22iowgsc0wggk0c8888cc80s8gk80gco00g0gko8ko'
DEFAULT_CLIENT_SECRET = '15lkcj9ytmm8440ggsco8ogo4ockwgcg04okokcwokkk8cksk8'
GUEST_USERNAME = "guest@taipit.ru"
GUEST_PASSWORD = "guest"

DEFAULT_BASE_URL = "https://cloud.meters.taipit.ru"
DEFAULT_TOKEN_URL = "oauth/v2/token"
DEFAULT_API_URL = "api"

SECTION_CONTROLLERS = 'controllers'
SECTION_METER_TYPES = 'meterTypes'
SECTION_REGIONS = 'regions'
SECTIONS_ALL = (SECTION_REGIONS, SECTION_METER_TYPES, SECTION_CONTROLLERS)

PARAM_ID = 'id'
PARAM_ACTION = 'action'
PARAM_SECTIONS = 'sections'

GET_ENTRIES = 'getEntries'

UNKNOWN = 'Неизвестно'

METER_MODELS = {
    15: 'МТ 315 (GSM)',
    16: 'МТ 114 (Wi-Fi)',
    21: 'МТ 124 (Wi-Fi)',
    22: 'МТ 115 (GSM)',
}

REGIONS = {
    1: 'Республика Адыгея',
    2: 'Республика Башкортостан',
    3: 'Республика Бурятия',
    4: 'Республика Алтай',
    5: 'Республика Дагестан',
    6: 'Республика Ингушетия',
    7: 'Кабардино-Балкарская республика',
    8: 'Республика Калмыкия',
    9: 'Карачаево-Черкесская республика',
    10: 'Республика Карелия',
    11: 'Республика Коми',
    12: 'Республика Марий Эл',
    13: 'Республика Мордовия',
    14: 'Республика Саха (Якутия)',
    15: 'Республика Северная Осетия — Алания',
    16: 'Республика Татарстан',
    17: 'Республика Тыва',
    18: 'Удмуртская республика',
    19: 'Республика Хакасия',
    20: 'Чеченская республика',
    21: 'Чувашская республика',
    22: 'Алтайский край',
    23: 'Краснодарский край',
    24: 'Красноярский край',
    25: 'Приморский край',
    26: 'Ставропольский край',
    27: 'Хабаровский край',
    28: 'Амурская область',
    29: 'Архангельская область',
    30: 'Астраханская область',
    31: 'Белгородская область',
    32: 'Брянская область',
    33: 'Владимирская область',
    34: 'Волгоградская область',
    35: 'Вологодская область',
    36: 'Воронежская область',
    37: 'Ивановская область',
    38: 'Иркутская область',
    39: 'Калининградская область',
    40: 'Калужская область',
    41: 'Камчатский край',
    42: 'Кемеровская область',
    43: 'Кировская область',
    44: 'Костромская область',
    45: 'Курганская область',
    46: 'Курская область',
    47: 'Ленинградская область',
    48: 'Липецкая область',
    49: 'Магаданская область',
    50: 'Московская область',
    51: 'Мурманская область',
    52: 'Нижегородская область',
    53: 'Новгородская область',
    54: 'Новосибирская область',
    55: 'Омская область',
    56: 'Оренбургская область',
    57: 'Орловская область',
    58: 'Пензенская область',
    59: 'Пермский край',
    60: 'Псковская область',
    61: 'Ростовская область',
    62: 'Рязанская область',
    63: 'Самарская область',
    64: 'Саратовская область',
    65: 'Сахалинская область',
    66: 'Свердловская область',
    67: 'Смоленская область',
    68: 'Тамбовская область',
    69: 'Тверская область',
    70: 'Томская область',
    71: 'Тульская область',
    72: 'Тюменская область',
    73: 'Ульяновская область',
    74: 'Челябинская область',
    75: 'Забайкальский край',
    76: 'Ярославская область',
    77: 'Москва',
    78: 'Санкт-Петербург',
    79: 'Еврейская автономная область',
    83: 'Ненецкий автономный округ',
    86: 'Ханты-Мансийский автономный округ - Югра',
    87: 'Чукотский автономный округ',
    89: 'Ямало-Ненецкий автономный округ',
    91: 'Республика Крым',
    92: 'Севастополь'
}
SECTION_METER_TYPES_FULL = 'meterTypesFull'

TOKEN_REQUIRED_FIELDS = {'access_token', 'expires_in', 'refresh_token'}
