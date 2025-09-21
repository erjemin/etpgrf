# tests/test _layout.py
# Тестирует модуль LayoutProcessor. Проверяет обработку тире и специальных символов в тексте.

import pytest
from etpgrf.layout import LayoutProcessor, CHAR_THIN_SP
from etpgrf.config import CHAR_NBSP, CHAR_HELLIP, CHAR_THIN_SP

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
    ('ru', "в диапазоне (-10, 10)", f"в диапазоне (-10, 10)"),  # Без пробела после скобки

    # --- Инициалы (должны обрабатываться по умолчанию) ---
    # Разные комбинации пробелов
    ('ru', "А. С. Пушкин", f"А.{CHAR_NBSP}С.{CHAR_NBSP}Пушкин"),
    ('ru', "А.С. Пушкин", f"А.{CHAR_THIN_SP}С.{CHAR_NBSP}Пушкин"),
    ('ru', "А.С.Пушкин", f"А.{CHAR_THIN_SP}С.{CHAR_THIN_SP}Пушкин"),
    ('en', "J. R. R. Tolkien", f"J.{CHAR_NBSP}R.{CHAR_NBSP}R.{CHAR_NBSP}Tolkien"),
    ('en', "J.R.R. Tolkien", f"J.{CHAR_THIN_SP}R.{CHAR_THIN_SP}R.{CHAR_NBSP}Tolkien"),
    ('ru', "Пушкин А. С.", f"Пушкин{CHAR_NBSP}А.{CHAR_NBSP}С."),
    ('ru', "Пушкин А.С.", f"Пушкин{CHAR_NBSP}А.{CHAR_THIN_SP}С."),
    ('en', "Tolkien J. R. R.", f"Tolkien{CHAR_NBSP}J.{CHAR_NBSP}R.{CHAR_NBSP}R."),
    ('en', "Tolkien J.R.R.", f"Tolkien{CHAR_NBSP}J.{CHAR_THIN_SP}R.{CHAR_THIN_SP}R."),
    # Один инициал
    ('ru', "Это был В. Высоцкий.", f"Это был В.{CHAR_NBSP}Высоцкий."),
    ('ru', "Высоцкий В. был гением.", f"Высоцкий{CHAR_NBSP}В. был гением."),
    # Акронимы (бонус)
    ('ru', "Сделано в С.Ш.А.", f"Сделано в С.{CHAR_THIN_SP}Ш.{CHAR_THIN_SP}А."),
    ('ru', "Сделано в С. Ш. А.", f"Сделано в С.{CHAR_NBSP}Ш.{CHAR_NBSP}А."),
    ('en', "На замке стояло клеймо «Made in U. S. A.»",  f"На замке стояло клеймо «Made in U.{CHAR_NBSP}S.{CHAR_NBSP}A.»"),
    # Никаких изменений, если пробелы другого типа
    ('ru', "А.\u200DС.\u200AПушкин", "А.\u200DС.\u200AПушкин"),
    ('ru', "Пушкин А.\u200AС.", f"Пушкин{CHAR_NBSP}А.\u200AС."),
    ('en', "J.\u200DR.\u200DR.\u200ATolkien", "J.\u200DR.\u200DR.\u200ATolkien"),
    ('en', "Tolkien J.\u200AR.\u200AR.", f"Tolkien{CHAR_NBSP}J.\u200AR.\u200AR."),

    # --- Единицы измерения (по умолчанию) ---
    ('ru', "Радиус Солнца — около 696.340 км", f"Радиус Солнца{CHAR_NBSP}— около 696.340{CHAR_NBSP}км"),
    ('ru', "5 кг.", f"5{CHAR_NBSP}кг."),
    ('ru', "Доработки проекта стоили 100 тыс. руб.", f"Доработки проекта стоили 100{CHAR_NBSP}тыс.{CHAR_THIN_SP}руб."),
    ('ru', "№ 5", f"№{CHAR_NBSP}5"),
    ('ru', "Договор № 504/2025А", f"Договор №{CHAR_NBSP}504/2025А"),
    ('ru+en', "Доплата за багаж $ 45.50", f"Доплата за багаж ${CHAR_NBSP}45.50"),
    ('ru+en', "Инвестиции составили $2.5 млн.", f"Инвестиции составили $2.5{CHAR_NBSP}млн."),
    ('ru+en', "Инвестиции составили $ 2.5 млн.", f"Инвестиции составили ${CHAR_NBSP}2.5{CHAR_NBSP}млн."),
    # Сложные единицы (склеиваются тонкой шпацией, привязываются к числу неразрывным пробелом)
    # ('ru', "Дом 120 кв.м. / Участок 6 сот.", f"Дом 120{CHAR_NBSP}кв.м. / Участок 6{CHAR_NBSP}сот."),
    # ('ru', "Гробик кладут в ямку 2 кв. м.", f"Гробик кладут в ямку 2 кв. м."),
    ('ru', "IV-X вв.", f"IV-X{CHAR_NBSP}вв."),
    ('ru', "IV в. н. э.", f"IV{CHAR_NBSP}в.{CHAR_THIN_SP}н.{CHAR_THIN_SP}э."),
    ('ru+en', "Хаммурапи (1792 - 1750 до н. э.)",
             f"Хаммурапи (1792 - 1750 до н.{CHAR_THIN_SP}э.)"),

    # Составные и математические единицы
    ('ru', "Площадь 120 кв. м.", f"Площадь 120{CHAR_NBSP}кв.{CHAR_THIN_SP}м."),
    ('ru', "Площадь 130 кв.м.", f"Площадь 130{CHAR_NBSP}кв.{CHAR_THIN_SP}м."),
    ('ru', f"Площадь 140  {CHAR_NBSP} кв.{CHAR_NBSP}м.", f"Площадь 140{CHAR_NBSP}кв.{CHAR_THIN_SP}м."),
    ('ru', "Площадь 150 тыс. кв. км.", f"Площадь 150{CHAR_NBSP}тыс.{CHAR_THIN_SP}кв.{CHAR_THIN_SP}км."),
    ('ru', "Скорость 90 км/ч", f"Скорость 90{CHAR_NBSP}км/ч"),
    ('ru', "Скорость 90 км / ч", f"Скорость 90{CHAR_NBSP}км/ч"),
    ('ru', "В 500 г. н. э.", f"В 500{CHAR_NBSP}г.{CHAR_THIN_SP}н.{CHAR_THIN_SP}э."),
    ('ru', "Пластинка 45 мин. об.", f"Пластинка 45{CHAR_NBSP}мин.{CHAR_THIN_SP}об."),
    ('ru', "Пластинка 45 об. мин.", f"Пластинка 45{CHAR_NBSP}об.{CHAR_THIN_SP}мин."),
    ('ru', "За окном 15°C", f"За окном 15°C"),
    ('ru', "За окном 15 °C", f"За окном 15{CHAR_NBSP}°C"),
    ('ru', "HiFi 20 Гц - 20 кГц", f"HiFi 20{CHAR_NBSP}Гц - 20{CHAR_NBSP}кГц"),

    # Сложные единицы (склеиваются тонкой шпацией, привязываются к числу неразрывным пробелом)
    ('ru', "Дом 120 кв.м. / Участок 6 сот.", f"Дом 120{CHAR_NBSP}кв.{CHAR_THIN_SP}м. / Участок 6{CHAR_NBSP}сот."),
    # ('ru', "Гробик кладут в ямку 2 кв. м.", f"Гробик кладут в ямку 2 кв. м."),
    ('ru', "500 до н. э.", f"500 до н.{CHAR_THIN_SP}э."),
    ('ru+en', "Хаммурапи (1792 - 1750 до н. э.)", f"Хаммурапи (1792 - 1750 до н.{CHAR_THIN_SP}э.)"),

    # --- Комбинированные случаи ---
    ('ru', f"Да — это так{CHAR_HELLIP} а может и нет. Счёт -10.",
           f"Да{CHAR_NBSP}— это так{CHAR_HELLIP}{CHAR_NBSP}а может и нет. Счёт{CHAR_NBSP}-10."),
    ('ru', f"По мнению А.С.Пушкина — это...", f"По мнению А.{CHAR_THIN_SP}С.{CHAR_THIN_SP}Пушкина{CHAR_NBSP}— это..."),
    ('ru', f"К моменту смерти (1837 г.) А.С. Пушкин был должен 135.833 руб.: 92.500 руб. частным лицам и 43.333 руб."
           f" царской казне.",
           f"К моменту смерти (1837{CHAR_NBSP}г.) А.{CHAR_THIN_SP}С.{CHAR_NBSP}Пушкин был должен"
           f" 135.833{CHAR_NBSP}руб.: 92.500{CHAR_NBSP}руб. частным лицам и 43.333{CHAR_NBSP}руб."
           f" царской казне."),

]


@pytest.mark.parametrize("lang, input_string, expected_output", LAYOUT_TEST_CASES
)
def test_layout_processor_default(lang, input_string, expected_output):
    """Проверяет работу LayoutProcessor в изоляции."""
    processor = LayoutProcessor(langs=lang)
    actual_output = processor.process(input_string)
    assert actual_output == expected_output


# Тесты для проверки работы с кастомными опциями
LAYOUT_OPTIONS_TEST_CASES = [
    # --- Отключение правил ---
    # Отключение обработки единиц измерения
    ('ru', "10 км", "10 км", {'process_units': False}),
    ('ru', "№ 5", "№ 5", {'process_units': False}),
    ('ru', "100 тыс. руб.", "100 тыс. руб.", {'process_units': False}),
    # Отключение обработки инициалов
    ('ru', "А. С. Пушкин", "А. С. Пушкин", {'process_initials_and_acronyms': False}),
    ('ru', "Пушкин А.С.", "Пушкин А.С.", {'process_initials_and_acronyms': False}),

    # --- Кастомные единицы измерения ---
    # Кастомные единицы (список)
    ('ru', "100 тонн", f"100{CHAR_NBSP}тонн", {'process_units': ['тонн']}),
    # Кастомные единицы (строка)
    ('ru', "50 штук", f"50{CHAR_NBSP}штук", {'process_units': 'штук кг'}),
    # Стандартные единицы должны продолжать работать вместе с кастомными
    ('ru', "100 тонн и 10 км", f"100{CHAR_NBSP}тонн и 10{CHAR_NBSP}км", {'process_units': ['тонн']}),
    # Кастомные единицы не должны мешать другим правилам
    ('ru', "А.С. Пушкин получил 10 бочек селёдки",
           f"А.{CHAR_THIN_SP}С.{CHAR_NBSP}Пушкин получил 10{CHAR_NBSP}бочек селёдки", {'process_units': ['бочек']}),
]


@pytest.mark.parametrize("lang, input_string, expected_output, options", LAYOUT_OPTIONS_TEST_CASES)
def test_layout_processor_with_options(lang, input_string, expected_output, options):
    """Проверяет работу LayoutProcessor с кастомными настройками."""
    processor = LayoutProcessor(langs=lang, **options)
    actual_output = processor.process(input_string)
    assert actual_output == expected_output