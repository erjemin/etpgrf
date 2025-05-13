import regex
from etpgrf.config import LANG_RU, LANG_EN, SHY_ENTITIES, MODE_UNICODE
from etpgrf.defaults import etpgrf_settings
from etpgrf.comutil import parse_and_validate_mode, parse_and_validate_langs

_RU_VOWELS_UPPER = frozenset(['А', 'О', 'И', 'Е', 'Ё', 'Э', 'Ы', 'У', 'Ю', 'Я'])
_RU_CONSONANTS_UPPER = frozenset(['Б', 'В', 'Г', 'Д', 'Ж', 'З', 'К', 'Л', 'М', 'Н', 'П', 'Р', 'С', 'Т', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ'])
_RU_J_SOUND_UPPER = frozenset(['Й'])
_RU_SIGNS_UPPER = frozenset(['Ь', 'Ъ'])
_RU_OLD_I_DESYAT = frozenset(['І']) # И-десятеричное
_RU_OLD_YAT = frozenset(['Ѣ'])      # Ять
_RU_OLD_FITA = frozenset(['Ѳ'])     # Фита
_RU_OLD_IZHITSA = frozenset(['Ѵ'])  # Ижица (может быть и гласной, и согласной - сложный случай!)


_EN_VOWELS_UPPER = frozenset(['A', 'E', 'I', 'O', 'U', 'Æ', 'Œ'])
_EN_CONSONANTS_UPPER = frozenset(['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z'])


class Hyphenator:
    """Правила расстановки переносов для разных языков.
    """
    def __init__(self,
                 langs: str | list[str] | tuple[str, ...] | frozenset[str] | None = None,
                 mode: str = None,  # Режим обработки текста
                 max_unhyphenated_len: int | None = None,  # Максимальная длина непереносимой группы
                 min_tail_len: int | None = None):  # Минимальная длина после переноса (хвост, который разрешено переносить)
        self.langs: frozenset[str] = parse_and_validate_langs(langs)
        self.mode: str = parse_and_validate_mode(mode)
        self.max_unhyphenated_len = etpgrf_settings.hyphenation.MAX_UNHYPHENATED_LEN if max_unhyphenated_len is None else max_unhyphenated_len
        self.min_chars_per_part = etpgrf_settings.hyphenation.MIN_TAIL_LEN if min_tail_len is None else min_tail_len

        # Внутренние языковые ресурсы, если нужны специфично для переносов
        self._vowels: frozenset = frozenset()
        self._consonants: frozenset = frozenset()
        self._j_sound_upper: frozenset = frozenset()
        self._signs_upper: frozenset = frozenset()
        self._ru_alphabet_upper: frozenset = frozenset()
        self._en_alphabet_upper: frozenset = frozenset()
        # Загружает наборы символов на основе self.langs
        self._load_language_resources_for_hyphenation()
        # Определяем символ переноса в зависимости от режима
        self._split_code: str = SHY_ENTITIES['SHY'][0] if self.mode == MODE_UNICODE else SHY_ENTITIES['SHY'][1]
        print(f"========={self.max_unhyphenated_len}===========")


    def _load_language_resources_for_hyphenation(self):
        # Определяем наборы гласных, согласных и т.д. в зависимости языков.
        if LANG_RU in self.langs:
            self._vowels |= _RU_VOWELS_UPPER
            self._consonants |= _RU_CONSONANTS_UPPER
            self._j_sound_upper |= _RU_J_SOUND_UPPER
            self._signs_upper |= _RU_SIGNS_UPPER
            self._ru_alphabet_upper |= _RU_VOWELS_UPPER | _RU_CONSONANTS_UPPER | _RU_SIGNS_UPPER | _RU_J_SOUND_UPPER
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
        print("слово:", word, " // mode:", self.mode, " // langs:", self.langs)
        # 2. ОБНАРУЖЕНИЕ ЯЗЫКА И ПОДКЛЮЧЕНИЕ ЯЗЫКОВОЙ ЛОГИКИ
        # Поиск вхождения букв строки (слова) через `frozenset` -- O(1). Это быстрее регулярного выражения -- O(n)
        # 2.1. Проверяем RU
        if LANG_RU in self.langs and frozenset(word.upper()) <= self._ru_alphabet_upper:
            # Пользователь подключил русскую логику, и слово содержит только русские буквы
            print(f"#### Applying Russian rules to: {word}")
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
                        if (self._is_cons(word_segment[ind]) or self._is_j_sound(word_segment[ind])) and not self._is_vow(word_segment[ind + 1]):
                            # Й -- полугласная. Перенос после неё только в случае, если дальше идет согласная
                            # (например, "бой-кий"), но запретить, если идет гласная (например, "ма-йка" не переносится).
                            ind += 1
                        if ind <= self.min_chars_per_part or ind >= len(word_segment) - self.min_chars_per_part:
                            # Не отделяем 3 символ с начала или конца (это некрасиво)
                            continue
                        if self._is_sign(word_segment[ind]) or (ind > 0 and self._is_sign(word_segment[ind-1])):
                            # Пропускаем мягкий/твердый знак, если перенос начинается или заканчивается на них (ГОСТ 7.62-2008)
                            continue
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
            print(f"#### Applying English rules to: {word}") # Для отладки
            # --- Начало логики для английского языка (заглушка) ---
            # ПРИМЕЧАНИЕ: Это очень упрощенная заглушка.
            def find_hyphen_point_en(word_segment: str) -> int:
                for i in range(self.min_chars_per_part, len(word_segment) - self.min_chars_per_part):
                    if self._is_vow(word_segment[i - 1]) and self._is_cons(word_segment[i]):
                        if len(word_segment[:i]) >= self.min_chars_per_part and \
                                len(word_segment[i:]) >= self.min_chars_per_part:
                            return i
                return -1

            def split_word_en(word_to_split: str) -> str:
                if len(word_to_split) <= self.max_unhyphenated_len:
                    return word_to_split
                hyphen_idx = find_hyphen_point_en(word_to_split)
                if hyphen_idx != -1:
                    return word_to_split[:hyphen_idx] + self._split_code + word_to_split[hyphen_idx:]
                return word_to_split
            # --- Конец логики для английского языка ---
            return split_word_en(word)
        else:
            # кстати "слова" в которых есть пробелы или другие разделители, тоже попадают сюда
            print("!!!!ФИГНЯ")
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
            print(f"hyp_in_text: '{word_to_process}'", end="")
            if word_to_process != hyphenated_word:
                print(f" -> '{hyphenated_word}'")
            else:
                print(" (no change)")

            return hyphenated_word

        # 2. regex.sub() -- поиск с заменой. Ищем по паттерну `r'\b\p{L}+\b'`  (`\b` - граница слова;
        #                   `\p{L}` - любая буква Unicode; `+` - одно или более вхождений).
        #                    Второй аргумент - это наша функция replace_word_with_hyphenated.
        #                    regex.sub вызовет ее для каждого найденного слова, передав match_obj.
        processed_text = regex.sub(pattern=r'\b\p{L}+\b', repl=replace_word_with_hyphenated, string=text)

        return processed_text


