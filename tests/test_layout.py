# tests/test _layout.py
# Тестирует модуль LayoutProcessor. Проверяет обработку тире и специальных символов в тексте.

import pytest
from etpgrf.layout import LayoutProcessor
from etpgrf.config import CHAR_NBSP, CHAR_HELLIP

LAYOUT_TEST_CASES = [
    # --- Длинное тире (—) для русского языка ---
    ('ru', 'Слово — слово', f'Слово{CHAR_NBSP}— слово'),
    ('ru', 'В начале — слово', f'В начале{CHAR_NBSP}— слово'),
    ('ru', 'Слово — в конце.', f'Слово{CHAR_NBSP}— в конце.'),
    ('ru-en', 'Слово — слово', f'Слово{CHAR_NBSP}— слово'),  # Приоритет у 'ru'

    # --- Длинное тире (—) для английского языка ---
    ('en', 'Word — word', 'Word—word'),
    ('en', 'Start — word', 'Start—word'),
    ('en', 'Word — end.', 'Word—end.'),
    ('en-ru', 'Word — word', 'Word—word'),  # Приоритет у 'en'

    # --- Среднее тире (–) также должно обрабатываться ---
    ('ru', 'Слово – слово', f'Слово{CHAR_NBSP}– слово'),
    ('en', 'Word – word', 'Word–word'),

# --- Случаи тире рядом с пунктуацией и кавычками ---
    ('ru', 'Да, — сказал он', f'Да,{CHAR_NBSP}— сказал он'),
    ('en', 'Yes, — he said', 'Yes,—he said'),
    ('ru', '«Слово», — сказал он', f'«Слово»,{CHAR_NBSP}— сказал он'),
    ('en', '“Word,” — he said', '“Word,”—he said'),
    ('ru', 'Слово! — воскликнул он.', f'Слово!{CHAR_NBSP}— воскликнул он.'),
    ('en', 'Word! — he exclaimed.', 'Word!—he exclaimed.'),
    # Тире после закрывающей кавычки
    ('ru', '«Слово» — это важно.', f'«Слово»{CHAR_NBSP}— это важно.'),
    ('en', '“Word” — is important.', '“Word”—is important.'),

    # --- Случаи, которые не должны меняться ---
    ('ru', 'слово—слово', 'слово—слово'),  # Уже слитно, не трогаем
    ('en', 'word—word', 'word—word'),  # Уже слитно, не трогаем
    ('ru', "что-нибудь такое", "что-нибудь такое"),  # Дефис, а не минус
    ('ru', "что-нибудь такое", "что-нибудь такое"),  # Минус
    ('ru', "что-\nнибудь такое", "что-\nнибудь такое"),  # Минус
    ('ru', ' — слово', ' — слово'),  # Пробел в начале строки, не трогаем
    ('en', ' — word', ' — word'),  # Пробел в начале строки, не трогаем
    ('ru', 'слово — ', 'слово — '),  # Пробел в конце строки, не трогаем
    ('en', 'word — ', 'word — '),  # Пробел в конце строки, не трогаем
    ('ru', '1941–1945', '1941–1945'),  # Диапазон без пробелов (через короткое тире) не трогаем
    ('ru', '1941—1945', '1941—1945'),  # Диапазон (через длинное тире) не трогаем
    ('ru', '1941-1945', '1941-1945'),  # Диапазон (через дефис/минус) не трогаем (будет преобразован в SymbolsProcessor)
    ('ru', '1 — 2', '1 — 2'),  # Диапазон с пробелами (цифры!) не трогаем
    ('ru', '1 - 2', '1 - 2'),  # Математика (минус) не трогаем

    # --- Многоточие ---
    ('ru', f"Что это{CHAR_HELLIP} \n \t не знаю.", f"Что это{CHAR_HELLIP}{CHAR_NBSP}не знаю."),
    ('ru', f"Что это{CHAR_HELLIP} не знаю.", f"Что это{CHAR_HELLIP}{CHAR_NBSP}не знаю."),
    ('ru', f"Что это{CHAR_HELLIP} 123.", f"Что это{CHAR_HELLIP}{CHAR_NBSP}123."),
    (f'ru', f"Что это{CHAR_HELLIP}", f"Что это{CHAR_HELLIP}"),  # Не меняется в конце
    (f'ru', f"Что это{CHAR_HELLIP}   ", f"Что это{CHAR_HELLIP}   "),  # Не меняется в конце
    (f'ru', f"1{CHAR_HELLIP}2{CHAR_HELLIP}3{CHAR_HELLIP}4{CHAR_HELLIP}5, я иду тебя искать!",
            f"1{CHAR_HELLIP}2{CHAR_HELLIP}3{CHAR_HELLIP}4{CHAR_HELLIP}5, я иду тебя искать!"),
    (f'ru', f"1{CHAR_HELLIP}2{CHAR_HELLIP}3{CHAR_HELLIP}4{CHAR_HELLIP}5{CHAR_HELLIP} я иду тебя искать!",
            f"1{CHAR_HELLIP}2{CHAR_HELLIP}3{CHAR_HELLIP}4{CHAR_HELLIP}5{CHAR_HELLIP}{CHAR_NBSP}я иду тебя искать!"),

    # --- Отрицательные числа ---
    ('ru', "температура -10 градусов", f"температура{CHAR_NBSP}-10 градусов"),
    ('ru', "от -5 до +5", f"от{CHAR_NBSP}-5 до +5"),
    ('ru', "в диапазоне ( -10, 10)", f"в диапазоне ({CHAR_NBSP}-10, 10)"), # Пробел после скобки

    # --- Случаи, которые не должны меняться (отрицательные числа) ---
    ('ru', "10 - 5 = 5", "10 - 5 = 5"),  # Бинарный минус не трогаем
    ('ru', "слово-10", "слово-10"), # Дефис, а не минус
    ('ru', "1-2-3-4-5, я иду тебя искать", "1-2-3-4-5, я иду тебя искать"), # Дефис, а не минус

    # --- Инициалы (должны обрабатываться по умолчанию) ---
    ('ru', "А. С. Пушкин", f"А.{CHAR_NBSP}С.{CHAR_NBSP}Пушкин"),
    ('ru', "А.С. Пушкин", f"А.С.{CHAR_NBSP}Пушкин"),
    ('ru', "Пушкин А. С.", f"Пушкин{CHAR_NBSP}А.{CHAR_NBSP}С."),
    ('ru', "Пушкин А.С.", f"Пушкин{CHAR_NBSP}А.С."),
    ('en', "J. R. R. Tolkien", f"J.{CHAR_NBSP}R.{CHAR_NBSP}R.{CHAR_NBSP}Tolkien"),
    ('en', "J.R.R. Tolkien", f"J.R.R.{CHAR_NBSP}Tolkien"),
    ('en', "Tolkien J. R. R.", f"Tolkien{CHAR_NBSP}J.{CHAR_NBSP}R.{CHAR_NBSP}R."),
    ('en', "Tolkien J.R.R.", f"Tolkien{CHAR_NBSP}J.R.R."),
    ('ru', "Это был В. Высоцкий.", f"Это был В.{CHAR_NBSP}Высоцкий."),
    ('ru', "Высоцкий В. С. был гением.", f"Высоцкий{CHAR_NBSP}В.{CHAR_NBSP}С. был гением."),

    # --- Инициалы (проверка отключения опции) ---
    # ('ru', "А. С. Пушкин", "А. С. Пушкин", False),
    # ('ru', "Пушкин А. С.", "Пушкин А. С.", False),

    # --- Комбинированные случаи ---
    ('ru', f"Да — это так{CHAR_HELLIP} а может и нет. Счёт -10.",
     f"Да{CHAR_NBSP}— это так{CHAR_HELLIP}{CHAR_NBSP}а может и нет. Счёт{CHAR_NBSP}-10."),
    ('ru', f"По мнению А. С. Пушкина — это...", f"По мнению А.{CHAR_NBSP}С.{CHAR_NBSP}Пушкина{CHAR_NBSP}— это..."),

]


@pytest.mark.parametrize("lang, input_string, expected_output", LAYOUT_TEST_CASES)
def test_layout_processor(lang, input_string, expected_output):
    """Проверяет работу LayoutProcessor в изоляции."""
    processor = LayoutProcessor(langs=lang)
    actual_output = processor.process(input_string)
    assert actual_output == expected_output