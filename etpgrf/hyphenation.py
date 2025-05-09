import regex


def hyphenation_in_word(s: str, max_chunk: int = 14, sep: str = "-") -> str:
    """ Расстановка переносов в русском слове с учетом максимальной длины непереносимой группы.
    Переносы ставятся половинным делением слова, рекурсивно.

    :param s:         Слово, в котором надо расставить переносы
    :param max_chunk: Максимальная длина непереносимой группы символов (по умолчанию 14)
    :param sep:       Символ переноса (по умолчанию "-")
    :return:          Слово с расставленными переносами
    """

    # Проверка гласных букв
    def is_vow(let: str) -> bool:
        return let.upper() in ['А', 'О', 'И', 'Е', 'Ё', 'Э', 'Ы', 'У', 'Ю', 'Я']

    # Проверка согласных букв
    def is_cons(let: str) -> bool:
        return let.upper() in ['Б', 'В', 'Г', 'Д', 'Ж', 'З', 'К', 'Л', 'М', 'Н', 'П', 'Р', 'С', 'Т', 'Ф', 'Х', 'Ц',
                               'Ч', 'Ш', 'Щ']

    # Поиск допустимой позиции для переноса около заданного индекса
    def find_hyphen_point(word: str, start_idx: int) -> int:
        vow_indices = [i for i in range(len(word)) if is_vow(word[i])]
        if not vow_indices:
            # Если в слове нет гласных, то перенос невозможен
            return -1

        # Ищем ближайшую гласную до или после start_idx
        for i in vow_indices:
            if i >= start_idx - 2 and i + 2 < len(word):  # Проверяем, что после гласной есть минимум 2 символа
                ind = i + 1
                if (is_cons(word[ind]) or word[ind] in 'йЙ') and not is_vow(word[ind + 1]):
                    # Й -- полугласная. Перенос после неё только в случае, если дальше идет согласная
                    # (например, "бой-кий"), но запретить, если идет гласная (например, "ма-йка" не пройдет).
                    ind += 1
                if ind <= 3 or ind >= len(word) - 3:
                    # Не отделяем 3 символ с начала или конца (это некрасиво)
                    continue
                if word[ind] in 'ьЬЪъ' or word[-1] in 'ьЬЪъ':
                    # Пропускаем мягкий/твердый знак. Согласно правилам русской типографики (например, ГОСТ 7.62-2008
                    # или рекомендации по набору текста), перенос не должен разрывать слово так, чтобы мягкий или
                    # твердый знак оказывался в начале или конце строки
                    continue
                return ind
        return -1           # Не нашли подходящую позицию

    # Рекурсивное деление слова
    def split_word(word: str) -> str:
        if len(word) <= max_chunk:  # Если длина укладывается в лимит, перенос не нужен
            return word

        mid = len(word) // 2  # Середина слова
        hyphen_idx = find_hyphen_point(word, mid)  # Ищем точку переноса около середины

        if hyphen_idx == -1:  # Если не нашли точку переноса
            return word

        left_part = word[:hyphen_idx]
        right_part = word[hyphen_idx:]

        # Рекурсивно делим левую и правую части
        return split_word(left_part) + sep + split_word(right_part)

    # Основная логика
    if len(s) <= max_chunk or not any(is_vow(c) for c in s):
        # Короткое слово или без гласных
        return s

    return split_word(s)


def hyphenation_in_text(text: str, min_len_word_hyphenation: int = 14, sep: str = "") -> str:
    """ Расстановка переносов в тексте

        :param text: Строка, которую надо обработать (главный аргумент).
        :param min_len_word_hyphenation: Минимальная длина слова для расстановки переносов.
        :param sep: Символ переноса.
        :return: str:
    """
    rus_worlds = regex.findall(r'\b[а-яА-Я]+\b', text)       # ищем все русскоязычные слова в тексте
    rus_worlds = list(set(rus_worlds))                              # убираем повторяющиеся слова
    for word in rus_worlds:
        if len(word) > min_len_word_hyphenation:
            hyphenated_word = hyphenation_in_word(word, max_chunk=6, sep=sep)
            print(f'{word} -> {hyphenated_word}')
            text = text.replace(word, hyphenated_word)
    return text
