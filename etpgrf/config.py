# etpgrf/conf.py
# Настройки по умолчанию и "источник правды" для типографа etpgrf
from html import entities

# === КОНФИГУРАЦИИ ===
# Режимы "отдачи" результатов обработки
MODE_UNICODE = "unicode"
MODE_MNEMONIC = "mnemonic"
MODE_MIXED = "mixed"

# Языки, поддерживаемые библиотекой
LANG_RU = 'ru'  # Русский
LANG_RU_OLD = 'ruold'  # Русская дореволюционная орфография
LANG_EN = 'en'  # Английский
SUPPORTED_LANGS = frozenset([LANG_RU, LANG_RU_OLD, LANG_EN])


# === ИСТОЧНИК ПРАВДЫ ===
# --- Базовые алфавиты: Эти константы используются как для правил переноса, так и для правил кодирования ---

# Русский алфавит
RU_VOWELS_UPPER = frozenset(['А', 'О', 'И', 'Е', 'Ё', 'Э', 'Ы', 'У', 'Ю', 'Я'])
RU_CONSONANTS_UPPER = frozenset(['Б', 'В', 'Г', 'Д', 'Ж', 'З', 'К', 'Л', 'М', 'Н', 'П', 'Р', 'С', 'Т', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ'])
RU_J_SOUND_UPPER = frozenset(['Й'])
RU_SIGNS_UPPER = frozenset(['Ь', 'Ъ'])
RU_ALPHABET_UPPER = RU_VOWELS_UPPER | RU_CONSONANTS_UPPER | RU_J_SOUND_UPPER | RU_SIGNS_UPPER
RU_ALPHABET_LOWER = frozenset([char.lower() for char in RU_ALPHABET_UPPER])
RU_ALPHABET_FULL = RU_ALPHABET_UPPER | RU_ALPHABET_LOWER

# Английский алфавит
EN_VOWELS_UPPER = frozenset(['A', 'E', 'I', 'O', 'U', 'Æ', 'Œ'])
EN_CONSONANTS_UPPER = frozenset(['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z'])
EN_ALPHABET_UPPER = EN_VOWELS_UPPER | EN_CONSONANTS_UPPER
EN_ALPHABET_LOWER = frozenset([char.lower() for char in EN_ALPHABET_UPPER])
EN_ALPHABET_FULL = EN_ALPHABET_UPPER | EN_ALPHABET_LOWER

# === КОНСТАНТЫ ДЛЯ КОДИРОВАНИЯ HTML-МНЕМНОИКОВ ===
# --- ЧЕРНЫЙ СПИСОК: Символы, которые НИКОГДА не нужно кодировать в мнемоники ---
NEVER_ENCODE_CHARS = (frozenset(['!', '#', '%', '(', ')', '*', ',', '.', '/', ':', ';', '=', '?', '@',
                                 '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '\n', '\t', '\r'])
                      | RU_ALPHABET_FULL | EN_ALPHABET_FULL)

# 2. БЕЛЫЙ СПИСОК (ДЛЯ БЕЗОПАСНОСТИ):
#    Символы, которые ВСЕГДА должны превращаться в мнемоники в "безопасных" режимах вывода. Сюда добавлены символы,
#    которые не видны, на глаз и не отличимы друг от друга в обычном тексте, или очень специфичные
SAFE_MODE_CHARS_TO_MNEMONIC = frozenset([
    '<', '>', '&', '"', '\'',
    '\u00AD',  # Мягкий перенос (Soft Hyphen) -- &shy;
    '\u00A0',  # Неразрывный пробел (Non-Breaking Space) -- &nbsp;
    '\u2002',  # Полужирный пробел (En Space) -- &ensp;
    '\u2003',  # Широкий пробел (Em Space) -- &emsp;
    '\u2007',  # Цифровой пробел -- &numsp;)
    '\u2008',  # Пунктуационный пробел -- &puncsp;
    '\u2009',  # Междусимвольный пробел -- &thinsp;'
    '\u200A',  # Толщина волоса (Hair Space) -- &hairsp;
    '\u200B',  # Негативный пробел (Negative Space) -- &NegativeThinSpace;
    '\u200C',  # Нулевая ширина (без объединения) (Zero Width Non-Joiner) -- &zwj;
    '\u200D',  # Нулевая ширина (с объединением) (Zero Width Joiner) -- &zwnj;
    '\u200E',  # Изменить направление текста на слева-направо (Left-to-Right Mark /LRE) -- &lrm;
    '\u200F',  # Изменить направление текста направо-налево (Right-to-Left Mark /RLM) -- &rlm;
    '\u205F',  # Средний пробел (Medium Mathematical Space) -- &MediumSpace;
    '\u2060',  # &NoBreak;
    '\u2062',  # &InvisibleTimes;
    '\u2063',  # &InvisibleComma;

    ])

# 3. СПИСОК ДЛЯ ЧИСЛОВОГО КОДИРОВАНИЯ: Символы без стандартного имени.
ALWAYS_ENCODE_TO_NUMERIC_CHARS = frozenset([
    '\u058F',  # Знак армянского драма (֏)
    '\u20BD',  # Знак русского рубля (₽)
    '\u20B4',  # Знак украинской гривны (₴)
    '\u20B8',  # Знак казахстанского тенге (₸)
    '\u20B9',  # Знак индийской рупии (₹)
    '\u20BC',  # Знак азербайджанского маната
    '\u20BE',  # Знак грузинский лари (₾)
])

# 4. СЛОВАРЬ ПРИОРИТЕТОВ: Кастомные и/или предпочитаемые мнемоники.
#    Некоторые utf-символы имеют несколько мнемоник, а значит для таких символов преобразование
#    в из utf во html-мнемоники может иметь несколько вариантов. Словарь приоритетов задает предпочтительное
#    преобразование. Эти правила применяются в последнюю очередь и имеют наивысший приоритет,
#    гарантируя предсказуемый результат для символов с несколькими именами.
#
#    Также можно использовать для создания исключений из "черного списка" NEVER_ENCODE_CHARS.
CUSTOM_ENCODE_MAP = {
    '\u2010': '&hyphen;',  # Для \u2010 всегда предпочитаем &hyphen;, а не &dash;
    # Исключения для букв, которые есть в алфавитах, но должны кодироваться (для обеспечения консистентности):
    # 'Æ': '&AElig;',
    # 'Œ': '&OElig;',
    # 'æ': '&aelig;',
    # 'œ': '&oelig;',
    '\u3253': '&alefsym;',   # ℵ / &alefsym / &aleph;
    '&': '&amp;',            # & / &amp; / &AMP;
    '\u2220': '&ang;',       # ∠ / &ang; / &angle;
    '\u2061': '&af;',        # &af; / &ApplyFunction;
    '\u2248': '&asymp;',     # ≈ / &asymp; / &approx; / &ap; / &thickapprox; / &thkap; / &TildeTilde;
    '\u00c5': '&Aring;',     # Å / &Aring; / &angst; /
    '\u224a': '&ape;',       # ≊ / &ape; / &&approxeq;
    '\u2305': '&barwed;',    # ⌅ / &barwed; / &barwedge;
    '\u2235': '&becaus;',    # ∵ / &becaus; / &Because; / &because;
    '\u224c': '&bcong;',     # ≌ / &backcong; / &bcong;
    '\u03f6': '&bepsi;',     # ϶ / &bepsi; / &backepsilon;
    '\u212c': '&Bscr;',      # ℬ / &Bscr; / &Bernoullis; / &bernou;
    '\u22a5': '&perp;',      # ⊥ / perp; / &bot; / &bottom; / UpTee
    '\u2035': '&bprime;',    # ‵ / &bprime; / &backprime;
    '\u02d8': '&breve;',     # ˘ / &breve; / &Breve;
    '\u223d': '&bsim;',      # ∽ / &bsim; / &backsim;
    '\u22cd': '&bsime;',     # ⋍ / &bsime; / &backsimeq;
    '\u2022': '&bull;',      # • / &bull; / &bullet;
}

# === Динамическая генерация карт преобразования ===

def _build_translation_maps() -> dict[str, str]:
    """
    Создает карту для кодирования на лету, используя все доступные источники
    из html.entities и строгий порядок приоритетов для обеспечения
    предсказуемого и детерминированного результата.
    """
    # ШАГ 1: Создаем ЕДИНУЮ и ПОЛНУЮ карту {каноническое_имя: числовой_код}.
    # Это решает проблему разных форматов и дубликатов с точкой с запятой.
    unified_name2codepoint = {}

    # Сначала обрабатываем большой исторический словарь.
    for name, codepoint in entities.name2codepoint.items():
        # Нормализуем имя СРАЗУ, убирая опциональную точку с запятой (в html.entities предусмотрено, что иногда
        # символ `;` не ставится всякими неаккуратными верстальщиками и парсерами).
        canonical_name = name.rstrip(';')
        unified_name2codepoint[canonical_name] = codepoint
    # Затем обновляем его современным стандартом html5.
    # Это гарантирует, что если мнемоника есть в обоих, будет использована версия из html5.
    for name, char in entities.html5.items():
        # НОВОЕ: Проверяем, что значение является ОДИНОЧНЫМ символом.
        # Наш кодек, основанный на str.translate, не может обрабатывать
        # мнемоники, которые соответствуют строкам из нескольких символов
        # (например, символ + вариативный селектор). Мы их игнорируем.
        if len(char) != 1:
            continue
        # Нормализуем имя СРАЗУ.
        canonical_name = name.rstrip(';')
        unified_name2codepoint[canonical_name] = ord(char)

    # Теперь у нас есть полный и консистентный словарь unified_name2codepoint.
    # На его основе строим нашу карту для кодирования.
    encode_map = {}

    # ШАГ 2: Высший приоритет. Загружаем наши кастомные правила.
    encode_map.update(CUSTOM_ENCODE_MAP)

    # ШАГ 3: Следующий приоритет. Добавляем числовое кодирование.
    for char in ALWAYS_ENCODE_TO_NUMERIC_CHARS:
        if char not in encode_map:
            encode_map[char] = f'&#{ord(char)};'

    # ШАГ 4: Низший приоритет. Заполняем все остальное из нашей
    # объединенной и нормализованной карты unified_name2codepoint.
    for name, codepoint in unified_name2codepoint.items():
        char = chr(codepoint)
        if char not in encode_map and char not in NEVER_ENCODE_CHARS:
            # Теперь 'name' - это уже каноническое имя без ';',
            # поэтому дополнительная нормализация не нужна. Код стал проще!
            encode_map[char] = f'&{name};'

    return encode_map


# Создаем карту один раз при импорте модуля.
ENCODE_MAP = _build_translation_maps()

# --- Публичный API модуля ---
def get_encode_map():
    """Возвращает готовую карту для кодирования."""
    return ENCODE_MAP