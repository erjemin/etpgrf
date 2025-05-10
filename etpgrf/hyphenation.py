import regex

UTF = frozenset(['utf-8', 'utf-16', 'utf-32'])
MNEMO_CODE = frozenset(['mnemo', '&'])

LANGS = frozenset(['ru', 'en'])

_RU_VOWELS_UPPER = frozenset(['А', 'О', 'И', 'Е', 'Ё', 'Э', 'Ы', 'У', 'Ю', 'Я'])
_RU_CONSONANTS_UPPER = frozenset(['Б', 'В', 'Г', 'Д', 'Ж', 'З', 'К', 'Л', 'М', 'Н', 'П', 'Р', 'С', 'Т', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ'])
_RU_J_SOUND_UPPER = frozenset(['Й'])
_RU_SIGNS_UPPER = frozenset(['Ь', 'Ъ'])

_EN_VOWELS_UPPER = frozenset(['A', 'E', 'I', 'O', 'U'])
_EN_CONSONANTS_UPPER = frozenset(['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z'])


class HyphenationRule:
    """Правила расстановки переносов для разных языков.
    """
    def __init__(self,
                 langs: frozenset[str],  # Языки, которые обрабатываем в переносе слов
                 max_unhyphenated_len: int = 14,  # Максимальная длина непереносимой группы
                 min_chars_per_part: int = 3):  # Минимальная длина после переноса (хвост, который разрешено переносить)
        self.langs = langs
        self.max_unhyphenated_len = max_unhyphenated_len
        self.min_chars_per_part = min_chars_per_part

        # Внутренние языковые ресурсы, если нужны специфично для переносов
        self._vowels: frozenset = frozenset()
        self._consonants: frozenset = frozenset()
        self._j_sound_upper: frozenset = frozenset()
        self._signs_upper: frozenset = frozenset()
        self._load_language_resources_for_hyphenation() # Загружает наборы символов на основе self.langs

        self._split_memo: dict[str, str] = {} # Кеш для этого экземпляра

    def _load_language_resources_for_hyphenation(self):
        # Определяем наборы гласных, согласных и т.д. в зависимости языков.
        if "ru" in self.langs:
            self._vowels |= _RU_VOWELS_UPPER
            self._consonants |= _RU_CONSONANTS_UPPER
            self._j_sound_upper |= _RU_J_SOUND_UPPER
            self._signs_upper |= _RU_SIGNS_UPPER
        if "en" in self.langs:
            self._vowels |= _EN_VOWELS_UPPER
            self._consonants |= _EN_CONSONANTS_UPPER
        # ... и для других языков, если они поддерживаются переносами

    # --- Сюда переносятся все методы, связанные с переносами ---
    # (адаптированные версии _is_vow, _is_cons, _is_j_sound, _is_sign,
    # _hyphenate_one_word, _recursive_split_word, _find_hyphen_point_in_sub_word, _is_valid_split_point)
    # Они будут использовать self._vowels, self.hyphen_char и т.д.

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


    def hyphenation_in_word(self, word: str) -> str:
        """ Расстановка переносов в русском слове с учетом максимальной длины непереносимой группы.
        Переносы ставятся половинным делением слова, рекурсивно.

        :param word:      Слово, в котором надо расставить переносы
        :return:          Слово с расставленными переносами
        """

        # Поиск допустимой позиции для переноса около заданного индекса
        def find_hyphen_point(word_segment: str, start_idx: int) -> int:
            vow_indices = [i for i, char_w in enumerate(word_segment) if self._is_vow(char_w)]
            if not vow_indices:
                # Если в слове нет гласных, то перенос невозможен
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
                    if self._is_sign(word_segment[ind]) or self._is_sign(word_segment[-1]):
                        # Пропускаем мягкий/твердый знак. Согласно правилам русской типографики (например, ГОСТ 7.62-2008
                        # или рекомендации по набору текста), перенос не должен разрывать слово так, чтобы мягкий или
                        # твердый знак оказывался в начале или конце строки
                        continue
                    return ind
            return -1  # Не нашли подходящую позицию

        # Рекурсивное деление слова
        def split_word(word_to_split: str) -> str:
            if len(word_to_split) <= self.max_unhyphenated_len:  # Если длина укладывается в лимит, перенос не нужен
                return word_to_split

            hyphen_idx = find_hyphen_point(word_to_split, len(word_to_split) // 2)  # Ищем точку переноса около середины

            if hyphen_idx == -1:  # Если не нашли точку переноса
                return word_to_split

            left_part = word_to_split[:hyphen_idx]
            right_part = word_to_split[hyphen_idx:]

            # Рекурсивно делим левую и правую части
            return split_word(left_part) + "-­" + split_word(right_part)

        # Основная логика
        if len(word) <= self.max_unhyphenated_len or not any(self._is_vow(c) for c in word):
            # Короткое слово или без гласных "делению не подлежит", выходим из рекурсии
            return word
        return split_word(word)    # Рекурсивно делим слово на части с переносами


    def apply(self, text: str) -> str:
        """ Расстановка переносов в тексте

            :param text: Строка, которую надо обработать (главный аргумент).
            :return: str:
        """
        rus_worlds = regex.findall(r'\b[а-яА-Я]+\b', text)  # ищем все русскоязычные слова в тексте
        for word in rus_worlds:
            if len(word) > self.max_unhyphenated_len:
                hyphenated_word = self.hyphenation_in_word(word)
                print(f'{word} -> {hyphenated_word}')
                text = text.replace(word, hyphenated_word)
        return text


# --- Основной класс Typographer ---
class Typographer:
    def __init__(self,
                 langs: str | list[str] | tuple[str, ...] | frozenset[str] = 'ru',
                 code_out: str = 'mnemo',
                 hyphenation_rule: HyphenationRule | None = None,       # Перенос слов и параметры расстановки переносов
                 # glue_prepositions_rule: GluePrepositionsRule | None = None, # Для других правил
                 # ... другие модули правил ...
                 ):

        # --- Обработка и валидация параметра langs ---
        # Параметр langs может быть строкой, списком или кортежем ("ru+en", ["ru", "en"] или ("ru", "en"))
        # Для удобств в классе буду использовать только frozenset, чтобы не дублировать коды языков
        self.langs = set()
        if isinstance(langs, str):
            # Разделяем строку по любым небуквенным символам, приводим к нижнему регистру
            # и фильтруем пустые строки, которые могут появиться, если разделители идут подряд
            lang_codes = [lang.lower() for lang in regex.split(r'[^a-zA-Z]+', langs) if lang]
        elif isinstance(langs, (list, tuple)):
            lang_codes = [str(lang).lower() for lang in langs]  # Приводим к строке и нижнему регистру
        else:
            raise TypeError(f"etpgrf: 'langs' parameter must be a string, list, or tuple. Got {type(langs)}")
        if not lang_codes:
            raise ValueError("etpgrf: 'langs' parameter cannot be empty or result in an empty list of languages after parsing.")
        for code in lang_codes:
            if code not in LANGS:  # LANGS = frozenset(['ru', 'en'])
                raise ValueError(f"etpgrf: langs code '{code}' is not supported. Supported languages: {list(LANGS)}")
            self.langs.add(code)
        self.langs: frozenset[str] = frozenset(self.langs)

        # --- Обработка и валидация параметра code_out ---
        if code_out not in MNEMO_CODE | UTF:
            raise ValueError(f"etpgrf: code_out '{code_out}' is not supported. Supported codes: {MNEMO_CODE | UTF}")

        # Сохраняем переданные модули правил
        self.hyphenation_rule = hyphenation_rule

        # TODO: вынести все соответствия UTF ⇄ MNEMO_CODE в отдельный класс
        # self.hyphen_char = "­" if code_out in UTF else "&shy;" # Мягкий перенос по умолчанию

    # Конвейер для обработки текста
    def process(self, text: str) -> str:
        processed_text = text
        if self.hyphenation_rule:
            # Передаем активные языки и символ переноса, если модуль HyphenationRule
            # не получает их в своем __init__ напрямую от пользователя,
            # а конструируется с настройками по умолчанию, а потом конфигурируется.
            # В нашем примере HyphenationRule уже получает их в __init__.
            processed_text = self.hyphenation_rule.apply(processed_text)

        # if self.glue_prepositions_rule:
        #     processed_text = self.glue_prepositions_rule.apply(processed_text, non_breaking_space_char=self._get_nbsp())

        # ... вызовы других активных модулей правил ...
        return processed_text

    # def _get_nbsp(self): # Пример получения неразрывного пробела
    #     return "\u00A0" if self.code_out in UTF else "&nbsp;"

