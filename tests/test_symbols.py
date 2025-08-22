# tests/test_symbols.py
# Тестирует модуль SymbolsProcessor. Проверяет обработку псевдографики в тексте (тире, стрелки, спецсимволы).

import pytest
from etpgrf.symbols import SymbolsProcessor
from etpgrf.config import (
    CHAR_NDASH, CHAR_MDASH, CHAR_HELLIP, CHAR_COPY, CHAR_REG, CHAR_COPYP,
    CHAR_TRADE, CHAR_AP, CHAR_ARROW_L, CHAR_ARROW_R, CHAR_ARROW_LR,
    CHAR_ARROW_L_DOUBLE, CHAR_ARROW_R_DOUBLE, CHAR_ARROW_LR_DOUBLE,
    CHAR_ARROW_L_LONG_DOUBLE, CHAR_ARROW_R_LONG_DOUBLE, CHAR_ARROW_LR_LONG_DOUBLE,
)

SYMBOLS_TEST_CASES = [
    # 1. --- Простые замены из STR_TO_SYMBOL_REPLACEMENTS ---
    # Тире и многоточие
    ("Текст --- текст", f"Текст {CHAR_MDASH} текст"),
    ("Текст---текст", f"Текст{CHAR_MDASH}текст"),
    ("Текст -- текст", f"Текст {CHAR_NDASH} текст"),
    ("Текст--текст", f"Текст{CHAR_NDASH}текст"),
    ("Текст...", f"Текст{CHAR_HELLIP}"),

    # Спецсимволы
    ("(c) 2025 Компания правообладатель", f"{CHAR_COPY} 2025 Компания правообладатель"),
    ("(C) 2025 Компания правообладатель", f"{CHAR_COPY} 2025 Компания правообладатель"),
    ("Товар(r)", f"Товар{CHAR_REG}"),
    ("Товар(R)", f"Товар{CHAR_REG}"),
    ("(p) 2025 Звукозапись", f"{CHAR_COPYP} 2025 Звукозапись"),
    ("(P) 2025 Звукозапись", f"{CHAR_COPYP} 2025 Звукозапись"),
    ("Продукт(tm)", f"Продукт{CHAR_TRADE}"),
    ("Продукт(TM)", f"Продукт{CHAR_TRADE}"),


    # Стрелки
    ("A <--> B", f"A {CHAR_ARROW_LR} B"),
    ("A <-- B", f"A {CHAR_ARROW_L} B"),
    ("A --> B", f"A {CHAR_ARROW_R} B"),
    ("A <==> B", f"A {CHAR_ARROW_LR_DOUBLE} B"),
    ("A <== B", f"A {CHAR_ARROW_L_DOUBLE} B"),
    ("A ==> B", f"A {CHAR_ARROW_R_DOUBLE} B"),
    ("A <===> B", f"A {CHAR_ARROW_LR_LONG_DOUBLE} B"),
    ("A <=== B", f"A {CHAR_ARROW_L_LONG_DOUBLE} B"),
    ("A ===> B", f"A {CHAR_ARROW_R_LONG_DOUBLE} B"),

    # Математические
    ("a ~= b", f"a {CHAR_AP} b"),

    # 2. --- Диапазоны чисел (обработка дефиса после простых замен) ---
    ("1941-1945 гг.", f"1941{CHAR_NDASH}1945 гг."),
    ("страницы 10-12", f"страницы 10{CHAR_NDASH}12"),
    ("I-V век", f"I{CHAR_NDASH}V век"),
    ("ix-vi до н.э.", f"ix{CHAR_NDASH}vi до н.э."),

    # 3. --- Комбинированные и пограничные случаи ---
    # Сначала сработает простая замена '---' -> '—', потом диапазон '1-5' -> '1–5'
    ("1-5 --- это диапазон (c)", f"1{CHAR_NDASH}5 {CHAR_MDASH} это диапазон {CHAR_COPY}"),
    # Простая замена '--' -> '–' не должна мешать диапазону '1-5'
    ("1-5 -- это диапазон", f"1{CHAR_NDASH}5 {CHAR_NDASH} это диапазон"),
    ("-10 -- -5 -- это диапазон", f"-10 {CHAR_NDASH} -5 – это диапазон"),
    # Проверка порядка: '---' должно замениться до '--'
    ("A---B--C", f"A{CHAR_MDASH}B{CHAR_NDASH}C"),
    # Проверка, что замена не жадная и заменяет все вхождения
    ("далее...", f"далее{CHAR_HELLIP}"),
    ("...и...и...", f"{CHAR_HELLIP}и{CHAR_HELLIP}и{CHAR_HELLIP}"),
    ("A-->B-->C", f"A{CHAR_ARROW_R}B{CHAR_ARROW_R}C"),
    ("A<--B<--C", f"A{CHAR_ARROW_L}B{CHAR_ARROW_L}C"),
    ("A<-->B<-->C", f"A{CHAR_ARROW_LR}B{CHAR_ARROW_LR}C"),
    ("A<==>B<==>C", f"A{CHAR_ARROW_LR_DOUBLE}B{CHAR_ARROW_LR_DOUBLE}C"),
    ("A<===>B<===>C", f"A{CHAR_ARROW_LR_LONG_DOUBLE}B{CHAR_ARROW_LR_LONG_DOUBLE}C"),
    # Очень длинные, комбинированные стрелки
    ("A <----> B", f"A {CHAR_ARROW_L}{CHAR_ARROW_R} B"),
    ("A <======> B", f"A {CHAR_ARROW_L_LONG_DOUBLE}{CHAR_ARROW_R_LONG_DOUBLE} B"),
]


@pytest.mark.parametrize("input_string, expected_output", SYMBOLS_TEST_CASES)
def test_symbols_processor(input_string, expected_output):
    processor = SymbolsProcessor()
    actual_output = processor.process(input_string)
    assert actual_output == expected_output