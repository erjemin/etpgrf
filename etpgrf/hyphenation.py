# etpgrf/hyphenation.py
# Представленные здесь алгоритмы реализуют упрощенные правила. Но эти правила лучше, чем их полное отсутствие.
# Тем более что пользователь может отключить переносы из типографа.
# Для русского языка правила реализованы лучше. Для английского дают "разумные" переносы во многих случаях, но из-за
# большого числа беззвучных согласных и их сочетаний, могут давать не совсем корректный результат.

import regex
import logging
from etpgrf.config import LANG_RU, LANG_RU_OLD, LANG_EN, KEY_SHY, ALL_ENTITIES
from etpgrf.defaults import etpgrf_settings
from etpgrf.comutil import parse_and_validate_langs, is_inside_unbreakable_segment

_RU_VOWELS_UPPER = frozenset(['А', 'О', 'И', 'Е', 'Ё', 'Э', 'Ы', 'У', 'Ю', 'Я'])
_RU_CONSONANTS_UPPER = frozenset(['Б', 'В', 'Г', 'Д', 'Ж', 'З', 'К', 'Л', 'М', 'Н', 'П', 'Р', 'С', 'Т', 'Ф', 'Х',
                                  'Ц', 'Ч', 'Ш', 'Щ'])
_RU_J_SOUND_UPPER = frozenset(['Й'])
_RU_SIGNS_UPPER = frozenset(['Ь', 'Ъ'])
_RU_OLD_VOWELS_UPPER = frozenset(['І',      # И-десятеричное (гласная)
                                  'Ѣ',      # Ять (гласная)
                                  'Ѵ'])     # Ижица (может быть и гласной, и согласной - сложный случай!)
_RU_OLD_CONSONANTS_UPPER = frozenset(['Ѳ',],)   # Фита (согласная)


_EN_VOWELS_UPPER = frozenset(['A', 'E', 'I', 'O', 'U', 'Æ', 'Œ'])
_EN_CONSONANTS_UPPER = frozenset(['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T',
                                  'V', 'W', 'X', 'Y', 'Z'])
_EN_SUFFIXES_WITHOUT_HYPHENATION_UPPER = frozenset([
        "ATION", "ITION", "UTION", "OSITY",   # 5-символьные, типа: creation, position, solution, generosity
        "ABLE", "IBLE", "MENT", "NESS",       # 4-символьные, типа: readable, visible, development, kindness
        "LESS", "SHIP", "HOOD", "TIVE",       #                     fearless, friendship, childhood, active (спорно)
        "SION", "TION",                       #                     decision, action (часто покрываются C-C или V-C-V)
        # "ING", "ED", "ER", "EST", "LY"      # совсем короткие, но распространенные, не рассматриваем.
])
_EN_UNBREAKABLE_X_GRAPHS_UPPER = frozenset(["SH", "CH", "TH", "PH", "WH", "CK", "NG", "AW",   # диграфы с согласными
                                         "TCH", "DGE", "IGH",               # триграфы
                                         "EIGH", "OUGH"])                   # квадрографы


# --- Настройки логирования ---
logger = logging.getLogger(__name__)


# --- Класс Hyphenator (расстановка переносов) ---
class Hyphenator:
    """Правила расстановки переносов для разных языков.
    """
    def __init__(self,
                 langs: str | list[str] | tuple[str, ...] | frozenset[str] | None = None,
                 max_unhyphenated_len: int | None = None,  # Максимальная длина непереносимой группы
                 min_tail_len: int | None = None):  # Минимальная длина после переноса (хвост, который разрешено переносить)
        self.langs: frozenset[str] = parse_and_validate_langs(langs)
        self.max_unhyphenated_len = etpgrf_settings.hyphenation.MAX_UNHYPHENATED_LEN if max_unhyphenated_len is None else max_unhyphenated_len
        self.min_chars_per_part = etpgrf_settings.hyphenation.MIN_TAIL_LEN if min_tail_len is None else min_tail_len
        if self.min_chars_per_part < 2:
            # Минимальная длина хвоста должна быть >= 2, иначе вылезаем за индекс в английских словах
            raise ValueError(f"etpgrf: минимальная длина хвоста (min_tail_len) должна быть >= 2,"
                             f" а не {self.min_chars_per_part}")
        if self.max_unhyphenated_len <= self.min_chars_per_part:
            # Максимальная длина непереносимой группы должна быть больше минимальной длины хвоста
            raise ValueError(f"etpgrf: максимальная длина непереносимой группы (max_unhyphenated_len) "
                             f"должна быть больше минимальной длины хвоста (min_tail_len), "
                             f"а не {self.max_unhyphenated_len} >= {self.min_chars_per_part}")

        # Внутренние языковые ресурсы, если нужны специфично для переносов
        self._vowels: frozenset = frozenset()
        self._consonants: frozenset = frozenset()
        self._j_sound_upper: frozenset = frozenset()
        self._signs_upper: frozenset = frozenset()
        self._ru_alphabet_upper: frozenset = frozenset()
        self._en_alphabet_upper: frozenset = frozenset()
        # Загружает наборы символов на основе self.langs
        self._load_language_resources_for_hyphenation()
        # Так как внутри типографа кодировка html, то символ переноса независим от режима
        self._split_code: str = ALL_ENTITIES[KEY_SHY][0]
        # ...
        logger.debug(f"Hyphenator `__init__`. Langs: {self.langs},"
                     f" Max unhyphenated_len: {self.max_unhyphenated_len},"
                     f" Min chars_per_part: {self.min_chars_per_part}")

    def _load_language_resources_for_hyphenation(self):
        # Определяем наборы гласных, согласных и т.д. в зависимости языков.
        if LANG_RU in self.langs:
            self._vowels |= _RU_VOWELS_UPPER
            self._consonants |= _RU_CONSONANTS_UPPER
            self._j_sound_upper |= _RU_J_SOUND_UPPER
            self._signs_upper |= _RU_SIGNS_UPPER
            self._ru_alphabet_upper |= self._vowels | self._consonants | self._j_sound_upper | self._signs_upper
        if LANG_RU_OLD in self.langs:
            self._vowels |= _RU_VOWELS_UPPER | _RU_OLD_VOWELS_UPPER
            self._consonants |= _RU_CONSONANTS_UPPER | _RU_OLD_CONSONANTS_UPPER
            self._j_sound_upper |= _RU_J_SOUND_UPPER
            self._signs_upper |= _RU_SIGNS_UPPER
            self._ru_alphabet_upper |= self._vowels | self._consonants | self._j_sound_upper | self._signs_upper
        if LANG_EN in self.langs:
            self._vowels |= _EN_VOWELS_UPPER
            self._consonants |= _EN_CONSONANTS_UPPER
            self._en_alphabet_upper |= _EN_VOWELS_UPPER | _EN_CONSONANTS_UPPER
        # ... и для других языков, если они поддерживаются переносами


    # Проверка гласных букв
    def _is_vow(self, char: str) -> bool:
        return char.upper() in self._vowels


    # Проверка согласных букв
    def _is_cons(self, char: str) -> bool:
        return char.upper() in self._consonants


    # Проверка полугласной буквы "й"
    def _is_j_sound(self, char: str) -> bool:
        return char.upper() in self._j_sound_upper


    # Проверка мягкого/твердого знака
    def _is_sign(self, char: str) -> bool:
        return char.upper() in self._signs_upper


    def hyp_in_word(self, word: str) -> str:
        """ Расстановка переносов в русском слове с учетом максимальной длины непереносимой группы.
        Переносы ставятся половинным делением слова, рекурсивно.

        :param word:      Слово, в котором надо расставить переносы
        :return:          Слово с расставленными переносами
        """
        # 1. ОБЩИЕ ПРОВЕРКИ
        # TODO: возможно, для скорости, надо сделать проверку на пробелы и другие разделители, которых не должно быть
        if not word:
            # Добавим явную проверку на пустую строку
            return ""
        if len(word) <= self.max_unhyphenated_len or not any(self._is_vow(c) for c in word):
            # Если слово короткое или не содержит гласных, перенос не нужен
            return word
        logger.debug(f"Hyphenator: word: `{word}` // langs: {self.langs} // max_unhyphenated_len: {self.max_unhyphenated_len} // min_tail_len: {self.min_chars_per_part}")
        # 2. ОБНАРУЖЕНИЕ ЯЗЫКА И ПОДКЛЮЧЕНИЕ ЯЗЫКОВОЙ ЛОГИКИ
        # Поиск вхождения букв строки (слова) через `frozenset` -- O(1). Это быстрее регулярного выражения -- O(n)
        # 2.1. Проверяем RU и RU_OLD (правила одинаковые, но разные наборы букв)
        if (LANG_RU in self.langs or LANG_RU_OLD in self.langs) and frozenset(word.upper()) <= self._ru_alphabet_upper:
            # Пользователь подключил русскую логику, и слово содержит только русские буквы
            logger.debug(f"`{word}` -- use `{LANG_RU}` or `{LANG_RU_OLD}` rules")
            # Поиск допустимой позиции для переноса около заданного индекса
            def find_hyphen_point_ru(word_segment: str, start_idx: int) -> int:
                vow_indices = [i for i, char_w in enumerate(word_segment) if self._is_vow(char_w)]
                # Если в слове нет гласных, то перенос невозможен
                if not vow_indices:
                    return -1
                # Ищем ближайшую гласную до или после start_idx
                for i in vow_indices:
                    if i >= start_idx - self.min_chars_per_part and i + self.min_chars_per_part < len(word_segment):
                        # Проверяем, что после гласной есть минимум символов "хвоста"
                        ind = i + 1
                        # 1. Не отделяем "хвостов" с начала или конца (это некрасиво)
                        if ind <= self.min_chars_per_part or ind >= len(word_segment) - self.min_chars_per_part:
                            continue
                        # 2. Пропускаем мягкий/твердый знак, если перенос начинается или заканчивается
                        # на них (правило из ГОСТ 7.62-2008)
                        if self._is_sign(word_segment[ind]) or (ind > 0 and self._is_sign(word_segment[ind-1])):
                            continue
                        # 3. Провека на `Й` (полугласная). Перенос после неё только в случае, если дальше идет
                        #    согласная (например, "бой-кий"), но запретить, если идет гласная (например,
                        #    "ма-йка" не переносится).
                        if (self._is_cons(word_segment[ind]) or self._is_j_sound(word_segment[ind])) and not self._is_vow(word_segment[ind + 1]):
                            ind += 1
                        return ind
                return -1  # Не нашли подходящую позицию

            # Рекурсивное деление слова
            def split_word_ru(word_to_split: str) -> str:
                # Если длина укладывается в лимит, перенос не нужен
                if len(word_to_split) <= self.max_unhyphenated_len:
                    return word_to_split
                # Ищем точку переноса около середины
                hyphen_idx = find_hyphen_point_ru(word_to_split, len(word_to_split) // 2)
                # Если не нашли точку переноса
                if hyphen_idx == -1:
                    return word_to_split
                # Разделяем слово на две части (до и после точки переноса)
                left_part = word_to_split[:hyphen_idx]
                right_part = word_to_split[hyphen_idx:]
                # Рекурсивно делим левую и правую части и соединяем их через символ переноса
                return split_word_ru(left_part) + self._split_code + split_word_ru(right_part)

            # Основная логика
            return split_word_ru(word)    # Рекурсивно делим слово на части с переносами

        # 2.2. Проверяем EN
        elif LANG_EN in self.langs and frozenset(word.upper()) <= self._en_alphabet_upper:
            # Пользователь подключил английскую логику, и слово содержит только английские буквы
            logger.debug(f"`{word}` -- use `{LANG_EN}` rules")
            # --- Начало логики для английского языка (заглушка) ---
            # ПРИМЕЧАНИЕ: правила переноса в английском языке основаны на слогах, и их точное определение без словаря
            # слогов или сложного алгоритма (вроде Knuth-Liang) — непростая задача. Здесь реализована упрощенная
            # логика и поиск потенциальных точек переноса основан на простых правилах: между согласными, или между
            # гласной и согласной. Метод половинного деления и рекурсии (поиск переносов о середины слова).

            # Функция для поиска допустимой позиции для переноса около заданного индекса
            # Ищет точку переноса, соблюдая min_chars_per_part и простые правила
            def find_hyphen_point_en(word_segment: str, start_idx: int) -> int:
                word_len = len(word_segment)
                min_part = self.min_chars_per_part

                # Определяем диапазон допустимых индексов для переноса
                # Индекс 'i' - это точка разреза. word_segment[:i] и word_segment[i:] должны быть не короче min_part.
                # i >= min_part
                # word_len - i >= min_part => i <= word_len - min_part
                valid_split_indices = [i for i in range(min_part, word_len - min_part + 1)]

                if not valid_split_indices:
                    # Нет ни одного места, где можно поставить перенос, соблюдая min_part
                    logger.debug(f"No valid split indices for '{word_segment}' within min_part={min_part}")
                    return -1

                # Сортируем допустимые индексы по удаленности от start_idx (середины)
                # Это реализует поиск "около центра"
                valid_split_indices.sort(key=lambda i: abs(i - start_idx))

                # Проверяем каждый потенциальный индекс переноса по упрощенным правилам
                for i in valid_split_indices:
                    # Упрощенные правила английского переноса (основаны на частых паттернах, не на слогах):
                    # 1. Запрет переноса между гласными
                    if self._is_vow(word_segment[i - 1]) and self._is_vow(word_segment[i]):
                        logger.debug(
                            f"Skipping V-V split point at index {i} in '{word_segment}' ({word_segment[i - 1]}{word_segment[i]})")
                        continue  # Переходим к следующему кандидату i

                    # 2. Запрет переноса ВНУТРИ неразрывных диграфов/триграфов и т.д.
                    if is_inside_unbreakable_segment(word_segment=word_segment,
                                                     split_index=i,
                                                     unbreakable_set=_EN_UNBREAKABLE_X_GRAPHS_UPPER):
                        logger.debug(f"Skipping unbreakable segment at index {i} in '{word_segment}'")
                        continue

                    # 3. Перенос между двумя согласными (C-C), например, 'but-ter', 'subjec-tive'
                    #    Точка переноса - индекс i. Проверяем символы word[i-1] и word[i].
                    if self._is_cons(word_segment[i - 1]) and self._is_cons(word_segment[i]):
                        logger.debug(f"Found C-C split point at index {i} in '{word_segment}'")
                        return i

                    # 4. Перенос перед одиночной согласной между двумя гласными (V-C-V), например, 'ho-tel', 'ba-by'
                    #    Точка переноса - индекс i (перед согласной). Проверяем word[i-1], word[i], word[i+1].
                    #    Требуется как минимум 3 символа для этого паттерна.
                    if i < word_len - 1 and \
                            self._is_vow(word_segment[i - 1]) and self._is_cons(word_segment[i]) and self._is_vow(
                        word_segment[i + 1]):
                        logger.debug(f"Found V-C-V (split before C) split point at index {i} in '{word_segment}'")
                        return i

                    # 5. Перенос после одиночной согласной между двумя гласными (V-C-V), например, 'riv-er', 'fin-ish'
                    #    Точка переноса - индекс i (после согласной). Проверяем word[i-2], word[i-1], word[i].
                    #    Требуется как минимум 3 символа для этого паттерна.
                    if i < word_len and \
                            self._is_vow(word_segment[i - 2]) and self._is_cons(word_segment[i - 1]) and \
                            self._is_vow(word_segment[i]):
                        logger.debug(f"Found V-C-V (split after C) split point at index {i} in '{word_segment}'")
                        return i

                    # 6. Правила для распространенных суффиксов (перенос ПЕРЕД суффиксом)
                    if word_segment[i:].upper() in _EN_SUFFIXES_WITHOUT_HYPHENATION_UPPER:
                        logger.debug(f"Found suffix '-{word_segment[i:]}' split point at index {i} in '{word_segment}'")
                        return i

                # Если ни одна подходящая точка переноса не найдена в допустимом диапазоне
                logger.debug(f"No suitable hyphen point found for '{word_segment}' near center.")
                return -1

            # Рекурсивная функция для деления слова на части с переносами
            def split_word_en(word_to_split: str) -> str:
                # Базовый случай рекурсии: если часть слова достаточно короткая, не делим ее дальше
                if len(word_to_split) <= self.max_unhyphenated_len:
                    return word_to_split

                # Ищем точку переноса около середины текущей части слова
                hyphen_idx = find_hyphen_point_en(word_to_split, len(word_to_split) // 2)

                # Если подходящая точка переноса не найдена, возвращаем часть слова как есть
                if hyphen_idx == -1:
                    return word_to_split

                # Рекурсивно обрабатываем обе части и объединяем их символом переноса
                return (split_word_en(word_to_split[:hyphen_idx]) +
                        self._split_code + split_word_en(word_to_split[hyphen_idx:]))

            # --- Конец логики для английского языка ---
            return split_word_en(word)
        else:
            # кстати "слова" в которых есть пробелы или другие разделители, тоже попадают сюда
            logger.debug(f"`{word}` -- use `UNDEFINE` rules")
            return word


    def hyp_in_text(self, text: str) -> str:
        """ Расстановка переносов в тексте

            :param text: Строка, которую надо обработать (главный аргумент).
            :return: str: Строка с расставленными переносами.
        """

        # 1. Определяем функцию, которая будет вызываться для каждого найденного слова
        def replace_word_with_hyphenated(match_obj):
            # Модуль regex автоматически передает сюда match_obj для каждого совпадения.
            # Чтобы получить `слово` из 'совпадения' делаем .group() или .group(0).
            word_to_process = match_obj.group(0)
            # И оправляем это слово на расстановку переносов (внутри hyp_in_word уже есть все проверки).
            hyphenated_word = self.hyp_in_word(word_to_process)

            # ============= Для отладки (слова в которых появились переносы) ==================
            if word_to_process != hyphenated_word:
                logger.debug(f"hyp_in_text: '{word_to_process}' -> '{hyphenated_word}'")

            return hyphenated_word

        # 2. regex.sub() -- поиск с заменой. Ищем по паттерну `r'\b\p{L}+\b'`  (`\b` - граница слова;
        #                   `\p{L}` - любая буква Unicode; `+` - одно или более вхождений).
        #                    Второй аргумент - это наша функция replace_word_with_hyphenated.
        #                    regex.sub вызовет ее для каждого найденного слова, передав match_obj.
        processed_text = regex.sub(pattern=r'\b\p{L}+\b', repl=replace_word_with_hyphenated, string=text)

        return processed_text


