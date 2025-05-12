import etpgrf


if __name__ == '__main__':
    # --- Пример использования ---
    print("\n--- Пример использования класса---\n")

    etpgrf.config.DEFAULT_HYP_MAX_LEN = 6

    # Определяем пользовательские правила переносов
    hyphen_settings = etpgrf.Hyphenator(langs='ru', max_unhyphenated_len=8)
    # Определяем пользовательские правила типографа

    result = hyphen_settings.hyp_in_text("Бармалейщина")
    print(result, "\n\n")
    result = hyphen_settings.hyp_in_word("Длинношеевый жираф")
    print(result, "\n\n")

    hyphen_settings2 = etpgrf.Hyphenator(langs='en', max_unhyphenated_len=8)
    result = hyphen_settings2.hyp_in_text("floccinaucinihilipilification")
    print(result, "\n\n")

    typo_ru = etpgrf.Typographer(langs='ru', mode='mixed', hyphenation=hyphen_settings)
    result = typo_ru.process(text="Какой-то длинный текст для проверки переносов. Перпердикюляция!")
    print(result, "\n\n")
    typo_ru_en = etpgrf.Typographer(langs='ru-en', mode='mixed', hyphenation=True)
    result = typo_ru_en.process(text="Расприветище, floccinaucinihilipilification. Это <i>тестовый текст для проверки расстановки</i> переносов"
                               " в словах. Миллион 100-метровошеих жирножирафов.")
    print(result, "\n\n")

    txt = ("Каждое пальто, которое мы создаём&nbsp;— это не&nbsp;просто одежда. Это"
           " вещь, в&nbsp;которой должно быть удобно жить: ходить, ждать, ехать, молчать&nbsp;и&nbsp;— главное&nbsp;—"
           " чувствовать себя собой. <b>Мы&nbsp;не&nbsp;шьём одина&shy;ковые пальто. Мы шьём ваше. </b> Ниже&nbsp;—"
           " как устроен процесс заказа.</p>")

    result = typo_ru.process(text=txt)
    print(result, "\n\n")
