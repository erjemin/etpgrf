# etpgrf/codec.py
# Модуль для преобразования текста между Unicode и HTML-мнемониками.

import regex
import html
from etpgrf.config import (ALL_ENTITIES, ALWAYS_MNEMONIC_IN_SAFE_MODE, MODE_MNEMONIC, MODE_MIXED)

# --- Создаем словарь для кодирования Unicode -> Mnemonic ---
# {'\u00A0': '&nbsp;', '\u2014': '&mdash;', ...}
_ENCODE_MAP = {}


for name, (uni_char, mnemonic) in ALL_ENTITIES.items():
    _ENCODE_MAP[uni_char] = mnemonic

# --- Основные функции кодека ---

def decode_to_unicode(text: str) -> str:
    """
    Преобразует все известные HTML-мнемоники в их Unicode-эквиваленты,
    используя стандартную библиотеку html.
    """
    if not text or '&' not in text:
        return text
    return html.unescape(text)


def encode_from_unicode(text: str, mode: str) -> str:
    """
    Преобразует Unicode-символы в HTML-мнемоники в соответствии с режимом.
    """
    if not text or mode not in [MODE_MNEMONIC, MODE_MIXED]:
        # В режиме 'unicode' или неизвестном режиме ничего не делаем
        return text

    # 1. Определяем, какие символы нужно заменить
    if mode == MODE_MNEMONIC:
        # В режиме 'mnemonic' заменяем все известные нам символы
        chars_to_replace = set(_ENCODE_MAP.keys())
    else:  # mode == MODE_MIXED
        # В смешанном режиме заменяем только "безопасные" символы
        # (те, что могут вызывать проблемы с отображением или переносами)
        safe_chars = {ALL_ENTITIES[name][0] for name in ALWAYS_MNEMONIC_IN_SAFE_MODE}
        chars_to_replace = set(_ENCODE_MAP.keys()) & safe_chars

    if not chars_to_replace:
        return text

    # 2. Создаем паттерн для поиска только нужных символов
    # regex.escape важен, если в наборе будут спецсимволы, например, '-'
    pattern = regex.compile(f"[{regex.escape(''.join(chars_to_replace))}]")

    # 3. Заменяем найденные символы, используя нашу карту
    return pattern.sub(lambda m: _ENCODE_MAP[m.group(0)], text)
