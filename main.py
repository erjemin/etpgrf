import etpgrf


if __name__ == '__main__':
    # --- Пример использования ---
    ETPGRF_DEFAULT_LANGS = "ru"
    print("\n--- Пример использования класса---\n")
    # Определяем пользовательские правила переносов
    hyphen_settings = etpgrf.Hyphenator(langs=frozenset(['ru']), max_unhyphenated_len=8)
    # Определяем пользовательские правила типографа
    typo = etpgrf.Typographer(langs='ru', mode='mnemonic', hyphenation_rule=hyphen_settings)

    result = hyphen_settings.hyp_in_text("Бармалейщина")
    print(result, "\n\n")
    result = hyphen_settings.hyp_in_word("Длинношеевый жираф")
    print(result, "\n\n")
    result = typo.process(text="Какой-то длинный текст для проверки переносов. Перпердикюляция!")
    print(result, "\n\n")
    result = typo.process(text="Привет, World! Это <i>тестовый текст для проверки расстановки</i> переносов в словах. Миллион 100-метровошеих жирножирафов.")
    print(result, "\n\n")

    txt = ("Каждое пальто, которое мы создаём&nbsp;— это не&nbsp;просто одежда. Это"
           " вещь, в&nbsp;которой должно быть удобно жить: ходить, ждать, ехать, молчать&nbsp;и&nbsp;— главное&nbsp;—"
           " чувствовать себя собой. <b>Мы&nbsp;не&nbsp;шьём одина&shy;ковые пальто. Мы шьём ваше. </b> Ниже&nbsp;—"
           " как устроен процесс заказа.</p>")

    result = typo.process(text=txt)
    print(result, "\n\n")
