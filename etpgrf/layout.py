# etpgrf/layout.py
# Модуль для обработки тире, специальных символов и правил их компоновки.

import regex
import logging
from etpgrf.config import (LANG_RU, LANG_EN, CHAR_NBSP, CHAR_THIN_SP, CHAR_NDASH, CHAR_MDASH, CHAR_HELLIP,
                           DEFAULT_POST_UNITS, DEFAULT_PRE_UNITS, DEFAULT_COMPLEX_UNITS)
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
                 process_initials_and_acronyms: bool = True,
                 process_units: bool | str | list[str] = True,
                 process_complex_units: bool | list[str] = True):

        self.langs = parse_and_validate_langs(langs)
        self.main_lang = self.langs[0] if self.langs else LANG_RU
        self.process_initials_and_acronyms = process_initials_and_acronyms
        self.process_units = process_units
        self.process_complex_units = process_complex_units
        # 1. Паттерн для длинного (—) или среднего (–) тире, окруженного пробелами.
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

        # 5. Паттерны для единиц измерения.
        self._post_units_pattern = None
        self._pre_units_pattern = None
        if self.process_units:
            post_units = list(DEFAULT_POST_UNITS)
            pre_units = list(DEFAULT_PRE_UNITS)
            # Проверяем и добавляем пользовательские единицы измерения
            custom_units = []

            # Обработка составных единиц: "склеиваем" их тонкой шпацией и добавляем в общий список
            if self.process_complex_units:
                complex_units_to_process = list(DEFAULT_COMPLEX_UNITS)
                if isinstance(self.process_complex_units, (list, tuple, set)):
                    complex_units_to_process.extend(self.process_complex_units)

                # "Склеиваем" пробелы внутри составных единиц и добавляем в общий список
                post_units.extend([unit.replace(' ', CHAR_THIN_SP) for unit in complex_units_to_process])

            if isinstance(self.process_units, str):
                # Если кастомные единицы заданы строкой, разбиваем по пробелам
                custom_units = self.process_units.split()
            elif isinstance(self.process_units, (list, tuple, set)):
                # Если кастомные единицы заданы списком/кортежем/множеством, просто конвертируем в список
                custom_units = list(self.process_units)

            if custom_units:
                post_units.extend(custom_units)

            if post_units:
                # [\d.,]+ - число, возможно, с точкой или запятой
                # Используем негативный просмотр вперед (?!), чтобы убедиться, что за единицей
                # не следует другая буква. Это надежнее, чем \b, особенно для единиц,
                # оканчивающихся на точку (например, "г.").
                post_pattern_str = r'(\d[\d.,]*)\s+(' + '|'.join(regex.escape(u) for u in post_units) + r')(?![\p{L}\p{N}])'
                self._post_units_pattern = regex.compile(post_pattern_str)

            if pre_units:
                # Используем негативный просмотр назад (?<!), чтобы убедиться, что перед единицей
                # нет буквы. \b здесь не работает для символов типа "№" или "$".
                pre_pattern_str = r'(?<![\p{L}\p{N}])(' + '|'.join(regex.escape(u) for u in pre_units) + r')\s+(\d[\d.,]*)'
                self._pre_units_pattern = regex.compile(pre_pattern_str)

        # 6. Паттерн для связи единиц-умножителей (тыс., млн.) со следующей единицей.
        # Ищет умножитель, за которым может быть точка, а затем пробел.
        multiplier_units = ['тыс', 'млн', 'млрд']
        self._unit_multiplier_pattern = regex.compile(r'((' + '|'.join(multiplier_units) + r')\.?)\s+')

        logger.debug(f"LayoutProcessor `__init__`. "
                     f"Langs: {self.langs}, "
                     f"Main lang: {self.main_lang}, "
                     f"Process initials and acronyms: {self.process_initials_and_acronyms}, "
                     f"Process units: {bool(self.process_units)}, "
                     f"Process complex units: {bool(self.process_complex_units)}")

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

         # 5. Обработка единиц измерения (если включено).
         if self.process_units and self._unit_multiplier_pattern:
             processed_text = self._unit_multiplier_pattern.sub(r'\1' + CHAR_NBSP, processed_text)

         # 6. Обработка единиц измерения (простых и составных).
         if self.process_units:
             if self._post_units_pattern:
                 processed_text = self._post_units_pattern.sub(f'\\1{CHAR_NBSP}\\2', processed_text)
             if self._pre_units_pattern:
                 processed_text = self._pre_units_pattern.sub(f'\\1{CHAR_NBSP}\\2', processed_text)


         return processed_text
