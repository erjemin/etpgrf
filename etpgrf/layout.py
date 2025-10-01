# etpgrf/layout.py
# Модуль для обработки тире, специальных символов и правил их компоновки.

import regex
import logging
from etpgrf.config import (LANG_RU, LANG_EN, CHAR_NBSP, CHAR_THIN_SP, CHAR_NDASH, CHAR_MDASH, CHAR_HELLIP,
                           CHAR_UNIT_SEPARATOR, DEFAULT_POST_UNITS, DEFAULT_PRE_UNITS, UNIT_MATH_OPERATORS,
                           ABBR_COMMON_FINAL)

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
                 process_units: bool | str | list[str] = True):

        self.langs = parse_and_validate_langs(langs)
        self.main_lang = self.langs[0] if self.langs else LANG_RU
        self.process_initials_and_acronyms = process_initials_and_acronyms
        self.process_units = process_units
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

        # Вся логика обработки финальных сокращений перенесена в метод process для надежной итеративной обработки

        # 6. Паттерн, описывающий "число" - арабское (включая десятичные дроби через запятую или точку) ИЛИ римское.
        # Для римских цифр используется \b, чтобы не спутать 'I' с частью слова.
        self._NUMBER_PATTERN = r'(?:\d[\d.,]*|\b[IVXLCDM]+\b)'

        # 7. Паттерны для единиц измерения (простые и составные).
        self._post_units_pattern = None
        self._pre_units_pattern = None
        self._complex_unit_pattern = None
        self._math_unit_pattern = None
        if self.process_units:
            all_post_units = list(DEFAULT_POST_UNITS)
            # Добавляем кастомные единицы, если они есть
            if isinstance(self.process_units, str):
                all_post_units.extend(self.process_units.split())
            elif isinstance(self.process_units, (list, tuple, set)):
                all_post_units.extend(self.process_units)

            # Единая проверка безопасности: удаляем все единицы, содержащие временный разделитель.
            safe_units = [unit for unit in all_post_units if CHAR_UNIT_SEPARATOR not in unit]
            if len(safe_units) != len(all_post_units):
                logger.warning(f"One or more units contained the reserved separator ('{CHAR_UNIT_SEPARATOR}') and were ignored.")

            # Создаем паттерны только из безопасных единиц
            if safe_units:
                sorted_units = sorted(safe_units, key=len, reverse=True)
                units_pattern_part_full = '|'.join(map(regex.escape, sorted_units))
                units_pattern_part_clean = '|'.join(map(regex.escape, [u.replace('.', '') for u in sorted_units]))

                # Простые единицы: число + единица
                self._post_units_pattern = regex.compile(rf'({self._NUMBER_PATTERN})\s+({units_pattern_part_full})(?!\w)')
                # Составные единицы: ищет пару "единица." + "единица"
                self._complex_unit_pattern = regex.compile(r'\b(' + units_pattern_part_clean + r')\.(\s*)('
                                                           + units_pattern_part_clean + r')(?!\w)')
                # Математические операции между единицами
                math_ops_pattern = '|'.join(map(regex.escape, UNIT_MATH_OPERATORS))
                self._math_unit_pattern = regex.compile(
                    r'\b(' + units_pattern_part_clean + r')\s*(' + math_ops_pattern + r')\s*('
                    + units_pattern_part_clean + r')(?!\w)')

            # Паттерн для пред-позиционных единиц
            self._pre_units_pattern = regex.compile(
                r'(?<![\p{L}\p{N}])(' + '|'.join(map(regex.escape, DEFAULT_PRE_UNITS)) + rf')\s+({self._NUMBER_PATTERN})')

        logger.debug(f"LayoutProcessor `__init__`. "
                     f"Langs: {self.langs}, "
                     f"Main lang: {self.main_lang}, "
                     f"Process initials and acronyms: {self.process_initials_and_acronyms}, "
                     f"Process units: {bool(self.process_units)}")

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

         # 4. Обработка финальных сокращений (т.д., т.п. и т.д.)
         # Шаг 1: "Склеиваем" многосоставные сокращения временным разделителем.
         temp_processed_text = processed_text
         for abbr in ABBR_COMMON_FINAL:
             if ' ' in abbr: # Обрабатываем только многосоставные
                 pattern = regex.escape(abbr).replace(r'\ ', r'\s*')
                 replacement = abbr.replace(' ', CHAR_UNIT_SEPARATOR)
                 temp_processed_text = regex.sub(pattern, replacement, temp_processed_text, flags=regex.IGNORECASE)

         # Шаг 2: Ставим неразрывный пробел перед всеми финальными сокращениями (уже "склеенными").
         # Создаем паттерн из всех вариантов - и простых, и "склеенных".
         glued_abbrs = [a.replace(' ', CHAR_UNIT_SEPARATOR) for a in ABBR_COMMON_FINAL]
         all_final_abbrs_pattern = '|'.join(map(regex.escape, sorted(glued_abbrs, key=len, reverse=True)))
         nbsp_pattern = regex.compile(r'(\s)(' + all_final_abbrs_pattern + r')(?=[.,!?]|\s|$)', flags=regex.IGNORECASE)
         processed_text = nbsp_pattern.sub(fr'{CHAR_NBSP}\2', temp_processed_text)

         # Шаг 3: Заменяем временный разделитель на правильную тонкую шпацию.
         processed_text = processed_text.replace(CHAR_UNIT_SEPARATOR, CHAR_THIN_SP)

         # 5. Обработка инициалов и акронимов (если включено).
         if self.process_initials_and_acronyms:
             # Сначала вставляем тонкие пробелы там, где пробелов не было.
             processed_text = self._initial_to_initial_ns_pattern.sub(f'\\1{CHAR_THIN_SP}', processed_text)
             processed_text = self._initial_to_surname_ns_pattern.sub(f'\\1{CHAR_THIN_SP}', processed_text)

             # Затем заменяем существующие пробелы на неразрывные.
             processed_text = self._initial_to_initial_ws_pattern.sub(f'\\1{CHAR_NBSP}', processed_text)
             processed_text = self._initial_to_surname_ws_pattern.sub(f'\\1{CHAR_NBSP}', processed_text)
             processed_text = self._surname_to_initial_ws_pattern.sub(f'\\1{CHAR_NBSP}', processed_text)

         # 6. Обработка единиц измерения (если включено).
         if self.process_units:
             if self._complex_unit_pattern:
                # Шаг 1: "Склеиваем" все составные единицы с помощью временного разделителя.
                # Цикл безопасен, так как мы заменяем пробелы на непробельный символ, и паттерн не найдет себя снова.
                while self._complex_unit_pattern.search(processed_text):
                    processed_text = self._complex_unit_pattern.sub(
                        fr'\1.{CHAR_UNIT_SEPARATOR}\3', processed_text, count=1)

             if self._math_unit_pattern:
                 # processed_text = self._math_unit_pattern.sub(r'\1/\2', processed_text)
                 processed_text = self._math_unit_pattern.sub(r'\1\2\3', processed_text)
             # И только потом привязываем простые единицы к числам
             if self._post_units_pattern:
                 processed_text = self._post_units_pattern.sub(f'\\1{CHAR_NBSP}\\2', processed_text)
             if self._pre_units_pattern:
                 processed_text = self._pre_units_pattern.sub(f'\\1{CHAR_NBSP}\\2', processed_text)

             # Шаг 2: Заменяем все временные разделители на правильную тонкую шпацию.
             processed_text = processed_text.replace(CHAR_UNIT_SEPARATOR, CHAR_THIN_SP)

         return processed_text
