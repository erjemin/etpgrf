# etpgrf/conf.py
# Настройки по умолчанию для типографа etpgrf
from email.header import SPACE

# Режимы "отдачи" результатов обработки
MODE_UNICODE = "unicode"
MODE_MNEMONIC = "mnemonic"
MODE_MIXED = "mixed"
DEFAULT_MODE = MODE_MIXED

# Языки, поддерживаемые библиотекой
LANG_RU = 'ru'  # Русский
LANG_EN = 'en'  # Английский
SUPPORTED_LANGS = frozenset([LANG_RU, LANG_EN])
# Язык(и) по умолчанию, если не указаны пользователем и не заданы через ETPGRF_DEFAULT_LANGS_MODULE
DEFAULT_LANGS = LANG_RU

# Значения по умолчанию для параметров Hyphenator
DEFAULT_HYP_MAX_LEN = 10  # Максимальная длина слова без переносов
DEFAULT_HYP_MIN_LEN = 3  # Минимальный "хвост" слова для переноса

# ----------------- соответствия `unicode` и `mnemonic` для типографа

# Переносы
SHY_ENTITIES = {
    'SHY': ('\u00AD', '&shy;'),  # Мягкий перенос
}

# Пробелы и неразрывные пробелы
SPACE_ENTITIES = {
    'NBSP':   ('\u00A0', '&nbsp;'),   # Неразрывный пробел
    'ZWSP':   ('\u200B', '&ZeroWidthSpace;'), # Пробел нулевой ширины (если нужен)
}

# Тире и дефисы
DASH_ENTITIES = {
    'NDASH':  ('\u2013', '&ndash;'), # Короткое тире
    'MDASH':  ('\u2014', '&mdash;'), # Длинное тире
    # 'HYPHEN': ('\u2010', '&#8208;'), # Обычный дефис (если нужно отличать от минуса)
}

# Кавычки
QUOTE_ENTITIES = {
    'LAQUO':  ('\u00AB', '&laquo;'), # «
    'RAQUO':  ('\u00BB', '&raquo;'), # »
    'LDQUO':  ('\u201C', '&ldquo;'), # “ (левая двойная)
    'RDQUO':  ('\u201D', '&rdquo;'), # ” (правая двойная)
    'LSQUO':  ('\u2018', '&lsquo;'), # ‘ (левая одинарная)
    'RSQUO':  ('\u2019', '&rsquo;'), # ’ (правая одинарная)
}

# Другие символы (пример для расширения)
SYMBOL_ENTITIES = {
    'HELLIP': ('\u2026', '&hellip;'), # Многоточие
    'COPY':   ('\u00A9', '&copy;'),   # Копирайт
    # ... стрелочки, математические символы и т.д. по мере необходимости
}

# Сущности, которые ВСЕГДА должны выводиться как мнемоники в режиме MODE_MIXED
# Указываются их ИМЕНА (ключи из словарей выше)
ALWAYS_MNEMONIC_IN_SAFE_MODE = frozenset(['SHY', 'NBSP', 'ZWSP'])

