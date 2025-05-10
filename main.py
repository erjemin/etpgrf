import etpgrf
from etpgrf.hyphenation import HyphenationRule, Typographer


if __name__ == '__main__':
    # --- Пример использования ---
    print("\n--- Пример использования класса---\n")
    # Определяем пользовательские правила переносов
    hyphen_settings = HyphenationRule(langs=frozenset(['ru']), max_unhyphenated_len=8)
    # Определяем пользовательские правила типографа
    typo = Typographer(langs='ru', code_out='utf-8', hyphenation_rule=hyphen_settings)

    result = hyphen_settings.apply(text="Бармалейщина")
    print(result, "\n\n")
    result = typo.process(text="Какой-то длинный текст для проверки переносов. Перпердикюляция!")
    print(result, "\n\n")
    result = typo.process(text="Привет, World! Это <i>тестовый текст для проверки расстановки</i> переносов в словах. Миллион 100-метровошеих жирножирафов.")
    print(result, "\n\n")

