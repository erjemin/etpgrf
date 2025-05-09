import etpgrf


if __name__ == '__main__':
    text_in = 'Привет, World! Это <i>тестовый текст для проверки расстановки</i> переносов в словах. Миллион 1000000'
    result = etpgrf.hyphenation.hyphenation_in_text(text_in, min_len_word_hyphenation=8, sep='-')
    print(result)

