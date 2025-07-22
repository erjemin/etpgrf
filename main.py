import etpgrf
import logging

if __name__ == '__main__':
    # --- Пример использования ---
    print("\n--- Пример использования класса---\n")
    # меняем настройки логирования
    etpgrf.defaults.etpgrf_settings.logging_settings.LEVEL = logging.INFO
    etpgrf.logger.update_etpgrf_log_level_from_settings()  # Обновляем уровень логирования из настроек

    # Меняем настройки по умолчанию для переносов
    etpgrf.defaults.etpgrf_settings.hyphenation.MAX_UNHYPHENATED_LEN = 8

    # Определяем пользовательские правила переносов
    hyphen_settings = etpgrf.Hyphenator(langs='ru', max_unhyphenated_len=8)

    # Проверяем переносы в словах
    result = hyphen_settings.hyp_in_text("Бармалейщина")
    print(result, "\n\n")

    # Проверяем переносы в словах, но "подсовываем" текст с пробелами
    result = hyphen_settings.hyp_in_word("Длинношеевый жираф")
    print(result, "\n\n")

    # Проверяем переносы в английских словах
    hyphen_settings2 = etpgrf.Hyphenator(langs='en', max_unhyphenated_len=8)
    result = hyphen_settings2.hyp_in_text("floccinaucinihilipilification")
    print(result, "\n\n")

    # Определяем пользовательские правила типографа
    typo_ru = etpgrf.Typographer(langs='ru', mode='unicode', hyphenation=hyphen_settings)
    result = typo_ru.process(text="Какой-то длинный текст для проверки переносов. Перпердикюляция!")
    print(result, "\n\n")

    # Проверяем переносы в смешанном тексте (русский + английский)
    typo_ru_en = etpgrf.Typographer(langs='ru-en', mode='mixed', hyphenation=True)
    result = typo_ru_en.process(text="Расприветище, floccinaucinihilipilification. Это <i>тестовый текст для проверки расстановки</i> переносов"
                               " в словах. Миллион 100-метровошеих жирножирафов.")
    print(result, "\n\n")



    # Меняем настройки по умолчанию для переносов
    etpgrf.defaults.etpgrf_settings.LANGS = "ru"
    etpgrf.defaults.etpgrf_settings.hyphenation.MAX_UNHYPHENATED_LEN = 8
    etpgrf.defaults.etpgrf_settings.unbreakables = True
    txt = ("В самом сердце Санкт-Петербурга — там, где старинные фасады спорят с неоном вывесок — мелькнуло"
           " пятно алого. Это было пальто от КейтБлаш, сшитое на заказ для перформанс-художницы Серафимы-Лукреции"
           " Д’Анжу-Палладиновой.\n"
           "\n"
           "— Что-то среднее между коконом и пламенем, — прошептала девушка в очках-авиаторах, снимая его"
           " на свой смартфон.\n"
           "\n"
           "Пальто (а точнее — то самое, из осенне-зимней коллекции 2025) мгновенно стало мемом. В блогах"
           " писали: «Серафима Лу ваяет мрачные киберпанк-инсталляций в стиле милитари, а в жизни обычная"
           " модница». На спине — вышивка шёлком в стиле Энди Уорхола -- \"пингвин парящий в закатном море\".\n"
           "\n"
           "Вдруг — бац! — порыв ветра раскрыл полы, обнажив подклад-трансформер: «днём — офис, вечером — клуб».")
    result = typo_ru.process(text=txt)
    print(result, "\n-----\n\n-----")

    # Проверяем переносы в смешанном тексте (русский + английский)
    txt = ("It was a chilly autumn afternoon when Anna finally received her custom-made KATEBLASH coat."
           " “I can’t believe how perfectly it fits!” she exclaimed, wrapping the soft, woolen fabric tightly"
           " around her shoulders.\n"
           "\n"
           "The coat - designed with unique check patterns and a detachable hood - was more than just a garment."
           " It was a statement of style and comfort, crafted with care and precision. Anna remembered the"
           " fitting session vividly: “The tailor said, ‘This coat will keep you style through even the coldest"
           " things winter throws at you.’”\n"
           "\n"
           "Her friend Mark raised an eyebrow: “Only you would get a coat with such an elaborate"
           " design - and those fancy oughtstanding stitches! Sounds like your coat has more personality"
           " than some people I know!”\n"
           "\n"
           "As they walked down the street, Anna noticed how the coat’s tailored cut moved gracefully with her."
           " The consideration of every detail - from the choice of fabric to the delicate embroidery - made it"
           " clear that this was no ordinary coat.\n"
           "\n"
           "Later, over coffee, Anna joked, “I told the tailor, ‘Make it so I never want to take it off.’ "
           "Looks like they succeeded!")
    etpgrf.defaults.etpgrf_settings.hyphenation.MAX_UNHYPHENATED_LEN = 6
    typo_en = etpgrf.Typographer(langs='en', hyphenation=True)
    result = typo_en.process(text=txt)
    print(result, "\n\n--------------\n\n")

    # Проверяем если есть HTML-тегов
    txt = ("<p>As they walked down the street, Anna noticed how the coat’s tailored cut moved gracefully with her."
           " The consideration of every detail&nbsp;- from the <i>choice of fabric</i> to the delicate embroidery - made it"
           " clear that this was no ordinary coat.</p><style>body { font-family: Arial; }</style>")
    typo_en = etpgrf.Typographer(langs='en', process_html=True, hyphenation=True)
    result = typo_en.process(text=txt)
    print(result, "\n\n--------------\n\n")




