# etpgrf/symbols.py
# Модуль для преобразования псевдографики в правильные типографские символы.

import regex
import logging
from .config import CHAR_NDASH, STR_TO_SYMBOL_REPLACEMENTS

logger = logging.getLogger(__name__)


class SymbolsProcessor:
    """
    Преобразует ASCII-последовательности (псевдографику) в семантически
    верные Unicode-символы. Работает на раннем этапе, до расстановки пробелов.
    """

    def __init__(self):
        # Для сложных замен, требующих анализа контекста (например, диапазоны),
        # по-прежнему используем регулярные выражения.
        # Паттерн для диапазонов: цифра-дефис-цифра -> цифра–цифра (среднее тире).
        # Обрабатываем арабские и римские цифры.
        self._range_pattern = regex.compile(pattern=r'(\d)-(\d)|([IVXLCDM]+)-([IVXLCDM]+)', flags=regex.IGNORECASE)

        logger.debug("SymbolsProcessor `__init__`")

    def _replace_range(self, match: regex.Match) -> str:
        # Паттерн имеет две группы: (\d)-(\d) ИЛИ ([IVX...])-([IVX...])
        if match.group(1) is not None:  # Арабские цифры
            return f'{match.group(1)}{CHAR_NDASH}{match.group(2)}'
        if match.group(3) is not None:  # Римские цифры
            return f'{match.group(3)}{CHAR_NDASH}{match.group(4)}'
        return match.group(0)  # На всякий случай


    def process(self, text: str) -> str:
        # Шаг 1: Выполняем простые замены из списка `STR_TO_SYMBOL_REPLACEMENTS` (см. config.py).
        # Этот шаг должен идти первым, чтобы пользователь мог, например,
        # использовать '---' в диапазоне '1---5', если ему это нужно.
        # В таком случае '---' заменится на '—', и правило для диапазонов
        # с дефисом уже не сработает.
        processed_text = text
        for old, new in STR_TO_SYMBOL_REPLACEMENTS:
            processed_text = processed_text.replace(old, new)

        # Шаг 2: Обрабатываем диапазоны с помощью регулярного выражения.
        # Эта замена более специфична и требует контекста (цифры вокруг дефиса).
        processed_text = self._range_pattern.sub(self._replace_range, processed_text)

        return processed_text

