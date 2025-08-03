# etpgrf/codec.py
# Модуль для преобразования текста между Unicode и HTML-мнемониками.

import regex
import html
from . import config
# from etpgrf.config import (ALL_ENTITIES, ALWAYS_MNEMONIC_IN_SAFE_MODE, MODE_MNEMONIC, MODE_MIXED)

# --- Создаем словарь для кодирования Unicode -> Mnemonic ---
# Получаем готовую карту для кодирования один раз при импорте
_ENCODE_MAP = config.get_encode_map()
# Создаем таблицу для быстрой замены через str.translate
_TRANSLATE_TABLE = str.maketrans(_ENCODE_MAP)

#
# for name, (uni_char, mnemonic) in ALL_ENTITIES.items():
#     _ENCODE_MAP[uni_char] = mnemonic

# --- Основные функции кодека ---

def decode_to_unicode(text: str) -> str:
    """
    Преобразует все известные HTML-мнемоники и числовые коды в их
    Unicode-эквиваленты, используя стандартную библиотеку html.
    """
    if not text or '&' not in text:
        return text
    return html.unescape(text)


def encode_from_unicode(text: str, mode: str) -> str:
    """
    Преобразует Unicode-символы в HTML-мнемоники в соответствии с режимом.
    """
    if not text:
        # Если текст пустой, просто возвращаем его
        return text
    if mode == config.MODE_UNICODE:
        # В режиме 'unicode' ничего не делаем
        return text

    if mode == config.MODE_MNEMONIC:
        # В режиме 'mnemonic' заменяем все известные символы, используя
        # заранее скомпилированную таблицу для максимальной производительности.
        return text.translate(_TRANSLATE_TABLE)
    if mode == config.MODE_MIXED:
        # Создаем временную карту только для "безопасных" символов
        safe_map = {
            char: _ENCODE_MAP[char]
            for char in config.SAFE_MODE_CHARS_TO_MNEMONIC
            if char in _ENCODE_MAP
        }
        if not safe_map:
            return text
        return text.translate(str.maketrans(safe_map))

    # Возвращаем исходный текст, если режим не распознан
    return text
