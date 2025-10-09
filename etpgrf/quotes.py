# etpgrf/quotes.py
# Модуль для расстановки кавычек в тексте

import regex
import logging
from .config import (LANG_RU, LANG_EN, CHAR_RU_QUOT1_OPEN, CHAR_RU_QUOT1_CLOSE, CHAR_EN_QUOT1_OPEN,
                     CHAR_EN_QUOT1_CLOSE, CHAR_RU_QUOT2_OPEN, CHAR_RU_QUOT2_CLOSE, CHAR_EN_QUOT2_OPEN,
                     CHAR_EN_QUOT2_CLOSE)
from .comutil import parse_and_validate_langs

# --- Настройки логирования ---
logger = logging.getLogger(__name__)

# Определяем стили кавычек для разных языков
# Формат: (('открывающая_ур1', 'закрывающая_ур1'), ('открывающая_ур2', 'закрывающая_ур2'))
_QUOTE_STYLES = {
    LANG_RU: ((CHAR_RU_QUOT1_OPEN, CHAR_RU_QUOT1_CLOSE), (CHAR_RU_QUOT2_OPEN, CHAR_RU_QUOT2_CLOSE)),
    LANG_EN: ((CHAR_EN_QUOT1_OPEN, CHAR_EN_QUOT1_CLOSE), (CHAR_EN_QUOT2_OPEN, CHAR_EN_QUOT2_CLOSE)),
}


class QuotesProcessor:
    """
    Обрабатывает прямые кавычки ("), превращая их в типографские
    в зависимости от языка и контекста.
    """

    def __init__(self, langs: str | list[str] | tuple[str, ...] | frozenset[str] | None = None):
        self.langs = parse_and_validate_langs(langs)

        # Выбираем стиль кавычек на основе первого поддерживаемого языка
        self.open_quote = '"'
        self.close_quote = '"'

        for lang in self.langs:
            if lang in _QUOTE_STYLES:
                self.open_quote = _QUOTE_STYLES[lang][0][0]
                self.close_quote = _QUOTE_STYLES[lang][0][1]
                logger.debug(
                    f"QuotesProcessor: выбран стиль кавычек для языка '{lang}': '{self.open_quote}...{self.close_quote}'")
                break  # Используем стиль первого найденного языка

        # Паттерн для открывающей кавычки: " перед буквой/цифрой,
        # которой предшествует пробел, начало строки или открывающая скобка.
        # (?<=^|\s|[\(\[„\"‘\']) - "просмотр назад" на начало строки... ищет пробел \s или знак из набора ([„"‘'
        # (?=\p{L})              - "просмотр вперед" на букву \p{L} (но не цифру).
        self._opening_quote_pattern = regex.compile(r'(?<=^|\s|[\(\[„\"‘\'])\"(?=\p{L})')
        # self._opening_quote_pattern = regex.compile(r'(?<=^|\s|\p{Pi}|["\'\(\)])\"(?=\p{L})')

        # Паттерн для закрывающей кавычки: " после буквы/цифры,
        # за которой следует пробел, пунктуация или конец строки.
        # (?<=\p{L}|[?!…\.])        - "просмотр назад" на букву или ?!… и точку.
        # (?=\s|[.,;:!?\)\"»”’]|\Z) - "просмотр вперед" на пробел, пунктуацию или конец строки (\Z).
        self._closing_quote_pattern = regex.compile(r'(?<=\p{L}|[?!…\.])\"(?=\s|[\.,;:!?\)\]»”’\"\']|\Z)')
        # self._closing_quote_pattern = regex.compile(r'(?<=\p{L}|\p{N})\"(?=\s|[\.,;:!?\)\"»”’]|\Z)')
        # self._closing_quote_pattern = regex.compile(r'(?<=\p{L}|[?!…])\"(?=\s|[\p{Po}\p{Pf}"\']|\Z)')

    def process(self, text: str) -> str:
        """
        Применяет правила замены кавычек к тексту.
        """
        if '"' not in text:
            # Быстрый выход, если в тексте нет прямых кавычек
            return text

        processed_text = text

        # 1. Заменяем открывающие кавычки
        # Заменяем только найденную кавычку, так как просмотр вперед не захватывает символы.
        processed_text = self._opening_quote_pattern.sub(self.open_quote, processed_text)

        # 2. Заменяем закрывающие кавычки
        processed_text = self._closing_quote_pattern.sub(self.close_quote, processed_text)

        return processed_text