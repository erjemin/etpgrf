# tests/test_unbreakables.py
import pytest
from etpgrf import Unbreakables
from etpgrf.config import CHAR_NBSP, CHAR_THIN_SP


# Список русских слов, которые должны "приклеиваться" к следующему слову.
RUSSIAN_PREPOSITIONS_TO_TEST = [
    # Предлоги (только короткие... длинные, типа `ввиду`, `ввиду` и т.п., могут быть "висячими")
    'в', 'без', 'до', 'из', 'к', 'на', 'по', 'о', 'от', 'перед', 'при', 'через', 'с', 'у', 'за', 'над',
    'об', 'под', 'про', 'для', 'ко', 'со', 'без', 'то', 'во', 'из-за', 'из-под', 'как'
    # Союзы (без сложных, тип `как будто`, `как если бы`, `за то` и т.п.)
    'и', 'а', 'но', 'да', 'как',
    # Частицы
    'не', 'ни',
    # Местоимения
    'я', 'ты', 'он', 'мы', 'вы', 'им', 'их', 'ей', 'ею',
    # Устаревшие или специфичные
    'сей', 'сия', 'сие',
]

@pytest.mark.parametrize("word", RUSSIAN_PREPOSITIONS_TO_TEST)
def test_russian_prepositions_are_unbreakable(word):
    """
    Проверяет ПОВЕДЕНИЕ: короткие слова "приклеиваются" к следующему. Для русского языка. Параметризованный тест
    """
    # Arrange (подготовка)
    unbreakables_ru = Unbreakables(langs='ru')
    input_text = f"Проверка {word} тестирование."
    expected_text = f"Проверка {word}{CHAR_NBSP}тестирование."
    # Act (действие, которое выполняем)
    actual_text = unbreakables_ru.process(input_text)
    # Assert (утверждение, что результат соответствует ожиданиям)
    assert actual_text == expected_text


# Список английских слов, которые должны "приклеиваться" к следующему слову.
ENGLISH_PREPOSITIONS_TO_TEST = [
    'a', 'an', 'as', 'at', 'by', 'in', 'is', 'it', 'of', 'on', 'or', 'so', 'to', 'if',
    'for', 'from', 'into', 'that', 'then', 'they', 'this', 'was', 'were', 'what', 'when', 'with',
    'not', 'but', 'which', 'the'
]

@pytest.mark.parametrize("word", ENGLISH_PREPOSITIONS_TO_TEST)
def test_english_prepositions_are_unbreakable(word):
    """
    Проверяет ПОВЕДЕНИЕ: короткие слова "приклеиваются" к следующему. Для английского языка. Параметризованный тест
    """
    # Arrange (подготовка)
    unbreakables_en = Unbreakables(langs='en')
    input_text = f"Training {word} test."
    expected_text = f"Training {word}{CHAR_NBSP}test."
    # Act (действие, которое выполняем)
    actual_text = unbreakables_en.process(input_text)
    # Assert (утверждение, что результат соответствует ожиданиям)
    assert actual_text == expected_text


# Смешанный тест для русского и английского языков
def test_mix_prepositions_are_unbreakable():
    """
    Проверяет ПОВЕДЕНИЕ: короткие слова "приклеиваются" к следующему. Для смешанного русско-английского текста.
    """
    # Arrange (подготовка)
    unbreakables_mix = Unbreakables(langs='ru+en')
    input_text = f"Для the Guardian он написал блестящую статью."
    expected_text = f"Для{CHAR_NBSP}the{CHAR_NBSP}Guardian он{CHAR_NBSP}написал блестящую статью."
    # Act (действие, которое выполняем)
    actual_text = unbreakables_mix.process(input_text)
    # Assert (утверждение, что результат соответствует ожиданиям)
    assert actual_text == expected_text


# Список русских постпозитивных частиц, которые должны "приклеиваться" к предыдущему слову.
RUSSIAN_POSTPOSITIVE_PARTICLES_TO_TEST = [
    'ли', 'ль', 'же', 'ж', 'бы', 'б'
]

@pytest.mark.parametrize("word", RUSSIAN_POSTPOSITIVE_PARTICLES_TO_TEST)
def test_russian_postpositive_particle(word):
    """
    Проверяет ПОВЕДЕНИЕ: русские постпозитивные частицы "приклеиваются" к предыдущему слову.
    """
    # Arrange
    unbreakables_ru = Unbreakables(langs='ru')
    input_text = f"Отчего {word} не поспать?"
    expected_text = f"Отчего{CHAR_NBSP}{word} не{CHAR_NBSP}поспать?"
    # Act
    actual_text = unbreakables_ru.process(input_text)
    # Assert
    assert actual_text == expected_text


# Тесты для проверки особых случаев в Unbreakables
UNBREAKABLES_SPECIAL_TEST_CASES = [
    ('ru', "до н.э.", f"до{CHAR_NBSP}н.э."),
]


@pytest.mark.parametrize("lang, input_string, expected_output", UNBREAKABLES_SPECIAL_TEST_CASES)
def test_layout_processor_with_options(lang, input_string, expected_output):
    """Проверяет работу Unbreakables с особыми случаями. """
    processor = Unbreakables(langs=lang)
    actual_output = processor.process(input_string)
    assert actual_output == expected_output
