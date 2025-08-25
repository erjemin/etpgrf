# etpgrf/layout.py
# Модуль для обработки тире, специальных символов и правил их компоновки.

import regex
import logging
from etpgrf.config import LANG_RU, LANG_EN, CHAR_NBSP, CHAR_NDASH, CHAR_MDASH, CHAR_HELLIP
from etpgrf.comutil import parse_and_validate_langs

# --

# --- Настройки логирования ---
logger = logging.getLogger(__name__)


class LayoutProcessor:
    """
    Обрабатывает тире, псевдографику (например, … -> © и тому подобные) и применяет
    правила расстановки пробелов в зависимости от языка (для тире язык важен, так как.
    Правила типографики различаются для русского и английского языков).
    Предполагается, что на вход уже поступает текст с правильными типографскими
    символами тире (— и –).
    """

    def __init__(self,
                 langs: str | list[str] | tuple[str, ...] | frozenset[str] | None = None,
                 process_initials: bool = True):
        self.langs = parse_and_validate_langs(langs)
        self.main_lang = self.langs[0] if self.langs else LANG_RU
        self.process_initials = process_initials

        # 1. Паттерн для длинного (—) или среднего (–) тире, окруженного пробелами.
        # (?<=\S) и (?=\S) гарантируют, что тире находится между словами, а не в начале/конце строки.
        # self._dash_pattern = regex.compile(rf'(?<=\S)\s+([{CHAR_MDASH}{CHAR_NDASH}])\s+(?=\S)')
        # (?<=[\p{L}\p{Po}\p{Pf}"\']) - просмотр назад на букву, пунктуацию или кавычку.
        self._dash_pattern = regex.compile(rf'(?<=[\p{{L}}\p{{Po}}\p{{Pf}}"\'])\s+([{CHAR_MDASH}{CHAR_NDASH}])\s+(?=\S)')

        # 2. Паттерн для многоточия, за которым следует пробел и слово.
        # Ставит неразрывный пробел после многоточия, чтобы не отрывать его от следующего слова.
        # (?=[\p{L}\p{N}]) - просмотр вперед на букву или цифру.
        self._ellipsis_pattern = regex.compile(rf'({CHAR_HELLIP})\s+(?=[\p{{L}}\p{{N}}])')

        # 3. Паттерн для отрицательных чисел.
        # Ставит неразрывный пробел перед знаком минус, если за минусом идет цифра (неразрывный пробел
        # заменяет обычный). Это предотвращает "отлипание" знака от числа при переносе строки.
        # (?<!\d) - негативный просмотр назад, чтобы правило не срабатывало для бинарного минуса
        #           в выражениях типа "10 - 5".
        self._negative_number_pattern = regex.compile(r'(?<!\d)\s+-(\d+)')

        # 4. Паттерны для обработки инициалов.
        # \p{Lu} - любая заглавная буква в Unicode.
        # Этот паттерн находит пробел между фамилией и следующим за ней инициалом.
        self._surname_initial_pattern = regex.compile(r'(\p{Lu}\p{L}{1,})\s+(?=\p{Lu}\.)')
        # Этот паттерн находит пробел между инициалом и следующим за ним инициалом или фамилией.
        # (?=\p{Lu}[\p{L}.]) - просмотр вперед на заглавную букву, за которой идет или буква (фамилия), или точка (инициал).
        self._initial_pattern = regex.compile(r'(\p{Lu}\.)\s+(?=\p{Lu}[\p{L}.])')

        logger.debug(f"LayoutProcessor `__init__`. "
                     f"Langs: {self.langs}, "
                     f"Main lang: {self.main_lang}, "
                     f"Process initials: {self.process_initials}")


    def _replace_dash_spacing(self, match: regex.Match) -> str:
        """Callback-функция для расстановки пробелов вокруг тире с учетом языка."""
        dash = match.group(1)  # Получаем сам символ тире (— или –)
        if self.main_lang == LANG_EN:
            # Для английского языка — слитно, без пробелов.
            return dash
        # По умолчанию (и для русского) — отбивка пробелами.
        return f'{CHAR_NBSP}{dash} '


    def process(self, text: str) -> str:
         """Применяет правила компоновки к тексту."""
         # Порядок применения правил важен.
         processed_text = text

         # 1. Обработка пробелов вокруг тире.
         processed_text = self._dash_pattern.sub(self._replace_dash_spacing, processed_text)

         # 2. Обработка пробела после многоточия.
         processed_text = self._ellipsis_pattern.sub(f'\\1{CHAR_NBSP}', processed_text)

         # 3. Обработка пробела перед отрицательными числами/минусом.
         processed_text = self._negative_number_pattern.sub(f'{CHAR_NBSP}-\\1', processed_text)

         # 4. Обработка инициалов (если включено).
         if self.process_initials:
             # Сначала связываем фамилию с первым инициалом (Пушкин А. -> Пушкин{NBSP}А.)
             processed_text = self._surname_initial_pattern.sub(f'\\1{CHAR_NBSP}', processed_text)
             # Затем связываем инициалы между собой и с фамилией (А. С. Пушкин -> А.{NBSP}С.{NBSP}Пушкин)
             processed_text = self._initial_pattern.sub(f'\\1{CHAR_NBSP}', processed_text)

         return processed_text
