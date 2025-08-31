# etpgrf/layout.py
# Модуль для обработки тире, специальных символов и правил их компоновки.

import regex
import logging
from etpgrf.config import LANG_RU, LANG_EN, CHAR_NBSP, CHAR_THIN_SP, CHAR_NDASH, CHAR_MDASH, CHAR_HELLIP
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
                 process_initials_and_acronyms: bool = True):
        self.langs = parse_and_validate_langs(langs)
        self.main_lang = self.langs[0] if self.langs else LANG_RU
        self.process_initials_and_acronyms = process_initials_and_acronyms

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

        # 4. Паттерны для обработки инициалов и акронимов.
        # \p{Lu} - любая заглавная буква в Unicode.

        # Правила для случаев, когда пробел УЖЕ ЕСТЬ (заменяем на неразрывный)
        # Используем ` +` (пробел) вместо `\s+`, чтобы не заменять уже вставленные тонкие пробелы.
        self._initial_to_initial_ws_pattern = regex.compile(r'(\p{Lu}\.) +(?=\p{Lu}\.)')
        self._initial_to_surname_ws_pattern = regex.compile(r'(\p{Lu}\.) +(?=\p{Lu}\p{L}{1,})')
        self._surname_to_initial_ws_pattern = regex.compile(r'(\p{Lu}\p{L}{2,}) +(?=\p{Lu}\.)')

        # Правила для случаев, когда пробела НЕТ (вставляем тонкий пробел)
        self._initial_to_initial_ns_pattern = regex.compile(r'(\p{Lu}\.)(?=\p{Lu}\.)')
        self._initial_to_surname_ns_pattern = regex.compile(r'(\p{Lu}\.)(?=\p{Lu}\p{L}{1,})')

        logger.debug(f"LayoutProcessor `__init__`. "
                     f"Langs: {self.langs}, "
                     f"Main lang: {self.main_lang}, "
                     f"Process initials and acronyms: {self.process_initials_and_acronyms}")


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
         if self.process_initials_and_acronyms:
             # Сначала вставляем тонкие пробелы там, где пробелов не было.
             processed_text = self._initial_to_initial_ns_pattern.sub(f'\\1{CHAR_THIN_SP}', processed_text)
             processed_text = self._initial_to_surname_ns_pattern.sub(f'\\1{CHAR_THIN_SP}', processed_text)

             # Затем заменяем существующие пробелы на неразрывные.
             processed_text = self._initial_to_initial_ws_pattern.sub(f'\\1{CHAR_NBSP}', processed_text)
             processed_text = self._initial_to_surname_ws_pattern.sub(f'\\1{CHAR_NBSP}', processed_text)
             processed_text = self._surname_to_initial_ws_pattern.sub(f'\\1{CHAR_NBSP}', processed_text)

         return processed_text
