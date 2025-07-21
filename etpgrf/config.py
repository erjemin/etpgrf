# etpgrf/conf.py
# Настройки по умолчанию для типографа etpgrf

# Режимы "отдачи" результатов обработки
MODE_UNICODE = "unicode"
MODE_MNEMONIC = "mnemonic"
MODE_MIXED = "mixed"
# DEFAULT_MODE = MODE_MIXED

# Языки, поддерживаемые библиотекой
LANG_RU = 'ru'  # Русский
LANG_RU_OLD = 'ruold'  # Русская дореволюционная орфография
LANG_EN = 'en'  # Английский
SUPPORTED_LANGS = frozenset([LANG_RU, LANG_RU_OLD, LANG_EN])
# Язык(и) по умолчанию, если не указаны пользователем и не заданы через ETPGRF_DEFAULT_LANGS_MODULE
# DEFAULT_LANGS = LANG_RU

# Значения по умолчанию для параметров Hyphenator
# DEFAULT_HYP_MAX_LEN = 10  # Максимальная длина слова без переносов
# DEFAULT_HYP_MIN_LEN = 3  # Минимальный "хвост" слова для переноса

# === Соответствия `unicode` и `mnemonic` для типографа

# Переносы
KEY_SHY = 'SHY'
SHY_ENTITIES = {
    KEY_SHY: ('\u00AD', '&shy;'),  # Мягкий перенос
}

# Пробелы и неразрывные пробелы
KEY_NBSP = 'NBSP'
KEY_THINSP = 'THINSP'
KEY_ENSP = 'ENSP'
KEY_EMSP = 'EMSP'
KEY_ZWNJ = 'ZWNJ'
KEY_ZWJ = 'ZWJ'
SPACE_ENTITIES = {
    KEY_NBSP:   ('\u00A0', '&nbsp;'),   # Неразрывный пробел
	KEY_THINSP: ('\u2009', '&thinsp;'), # Тонкий пробел
    KEY_ENSP:   ('\u2002', '&ensp;'),   # Полу-широкий пробел
    KEY_EMSP:   ('\u2003', '&emsp;'),   # Широкий пробел
    KEY_ZWNJ:   ('\u200C', '&zwnj;'),   # Разрывный пробел нулевой ширины (без пробела)
    KEY_ZWJ:    ('\u200D', '&zwj;'),    # Неразрывный пробел нулевой ширины
}

# Тире и дефисы
DASH_ENTITIES = {
    'NDASH':  ('\u2013', '&ndash;'),   # Cреднее тире (En dash)
    'MDASH':  ('\u2014', '&mdash;'),   # Длинное тире
    'HYPHEN':  ('\u2010', '&hyphen;'), # Обычный дефис (если нужно отличать от минуса)
    'HORBAR':  ('\u2015', '&horbar;'), # Горизонтальная линия (длинная черта)
}

# Кавычки
QUOTE_ENTITIES = {
    'QUOT':   ('\u0022', '&quot;'),      # Двойная кавычка (универсальная) -- "
    'APOS':   ('\u0027', '&apos;'),      # Апостроф (одинарная кавычка) -- '
    'LAQUO':  ('\u00AB', '&laquo;'),     # Открывающая (левая) кавычка «ёлочка» -- «
    'RAQUO':  ('\u00BB', '&raquo;'),     # Закрывающая (правая) кавычка «ёлочка» -- »
    'LDQUO':  ('\u201C', '&ldquo;'),     # Oткрывающая (левая) двойная кавычка -- “
    'RDQUO':  ('\u201D', '&rdquo;'),     # Закрывающая (правая) двойная кавычка -- ”
    'BDQUO':  ('\u2039', '&bdquo;'),     # Нижняя двойная кавычка -- „
    'LSQUO':  ('\u2018', '&lsquo;'),     # Открывающая (левая) одинарная кавычка -- ‘
    'RSQUO':  ('\u2019', '&rsquo;'),     # Закрывающая (правая) одинарная кавычка -- ’
    'SBQUO':  ('\u201A', '&sbquo;'),     # Нижняя одинарная кавычка -- ‚
    'LSAQUO': ('\u2039', '&lsaquo;'),    # Открывающая французская угловая кавычка -- ›
    'RSAQUO': ('\u203A', '&rsaquo;'),    # Закрывающая французская угловая кавычка -- ‹
}

# Символы валют
CURRENCY_ENTITIES = {
    'DOLLAR': ('\u0024', '&dollar;'),  # Доллар
    'CENT':   ('\u00A2', '&cent;'),    # Цент
    'POUND':  ('\u00A3', '&pound;'),   # Фунт стерлингов
    'CURREN': ('\u00A4', '&curren;'),  # Знак валюты (обычно используется для обозначения "без конкретной валюты")
    'YEN':    ('\u00A5', '&yen;'),     # Йена
    'EURO':   ('\u20AC', '&euro;'),    # Евро
    'RUBLE':  ('\u20BD', '&#8381;'),   # Российский рубль (₽)
}

# Математические символы
KEY_LT = 'LT'
KEY_GT = 'GT'
MATH_ENTITIES = {
    KEY_LT: ('\u00B7', '&lt;'),        # Меньше (<)
    KEY_GT: ('\u00B7', '&gt;'),        # Больше (>)
    'PLUS':   ('\u002B', '&plus;'),    # Плюс (+)
    'MINUS':  ('\u2212', '&minus;'),   # Минус (−)
    'MULTIPLY': ('\u00D7', '&times;'), # Умножение (×)
    'DIVIDE': ('\u00F7', '&divide;'),  # Деление (÷)
    'EQUALS': ('\u003D', '&equals;'),  # Равно (=)
    'NOT_EQUAL': ('\u2260', '&ne;'),   # Не равно (≠)
    'PLUSMN': ('\u00B1', '&plusmn;'), # Плюс-минус (±)
    'LESS_EQUAL': ('\u2264', '&le;'),  # Меньше или равно (≤)
    'GREATER_EQUAL': ('\u2265', '&ge;'),  # Больше или равно (≥)
    'APPROX_EQUAL': ('\u2245', '&cong;'),  # Приблизительно равно (≅)
    'APPROX_EQ': ('\u2245', '&approxeq;'),  # Приблизительно равно (≅)
    'APPROX': ('\u2248', '&asymp;'),   # Приблизительно равно (≈)
}

# Другие символы (пример для расширения)
KEY_AMP = 'AMP'
SYMBOL_ENTITIES = {
    KEY_AMP: ('\u0026', '&smp;'),        #Амперсанд (&)
    'HELLIP': ('\u2026', '&hellip;'), # Многоточие
    'COPY':   ('\u00A9', '&copy;'),   # Копирайт
    # ... стрелочки, математические символы и т.д. по мере необходимости
}

# --- Сборка и валидация ---

# 1. Создаем единый словарь всех сущностей для удобного доступа
ALL_ENTITIES = {
    **SHY_ENTITIES, **SPACE_ENTITIES, **DASH_ENTITIES, **MATH_ENTITIES,
    **QUOTE_ENTITIES, **CURRENCY_ENTITIES, **SYMBOL_ENTITIES
}

# Сущности, которые ВСЕГДА должны выводиться как мнемоники в режиме MODE_MIXED
# Указываются их ИМЕНА (ключи из словарей выше).
# NOTE: Повторное использование магических строк 'SHY', 'NBSP' и т.д. не создает новый объект в памяти. Умный Python
#       когда видит одинаковую строку в коде применяет интернирование строк (string interning).
ALWAYS_MNEMONIC_IN_SAFE_MODE = frozenset([KEY_AMP, KEY_LT, KEY_GT, KEY_SHY, KEY_NBSP, KEY_ZWNJ, KEY_ZWJ])

