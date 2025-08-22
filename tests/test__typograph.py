# tests/test__typograph.py
# Тесты для модуля Typographer. Проверяют отключение модулей обработки текста.

import pytest
from etpgrf.typograph import Typographer
from etpgrf.config import CHAR_SHY, CHAR_NBSP, CHAR_COPY, CHAR_MDASH, CHAR_ARROW_L


def test_typographer_disables_symbols_processor():
    """
    Проверяет, что при symbols=False модуль обработки символов отключается.
    """
    # Arrange
    input_string = "Текст --- с символами (c) и стрелками A --> B."
    typo = Typographer(langs='ru-en', symbols=False)

    # Act
    output_string = typo.process(input_string)

    # Assert
    # 1. Проверяем внутреннее состояние: модуль действительно отключен
    assert typo.symbols is None
    # 2. Проверяем результат: символы НЕ появились в тексте.
    #    Это главная и самая надежная проверка.
    assert CHAR_MDASH not in output_string  # длинное тире
    assert CHAR_COPY not in output_string  # символ копирайта
    assert CHAR_ARROW_L not in output_string  # стрелка


def test_typographer_disables_quotes_processor():
    """
    Проверяет, что при quotes=False модуль обработки кавычек отключается.
    """
    # Arrange
    input_string = 'Текст "в кавычках", который не должен измениться.'
    # Создаем два экземпляра: с None и с False для полной проверки
    typo_false = Typographer(langs='ru', quotes=False)

    # Act
    output_false = typo_false.process(input_string)

    # Assert
    # 1. Проверяем внутреннее состояние: модуль действительно отключен
    assert typo_false.quotes is None

    # 2. Проверяем результат: типографские кавычки НЕ появились в тексте.
    #    Это главная и самая надежная проверка.
    assert '«' not in output_false and '»' not in output_false


def test_typographer_disables_hyphenation():
    """
    Проверяет, что при hyphenation=False модуль переносов отключается.
    """
    # Arrange
    input_string = "Длинноесловодляпроверкипереносов"
    typo = Typographer(langs='ru', hyphenation=False)

    # Act
    output_string = typo.process(input_string)

    # Assert
    # 1. Проверяем внутреннее состояние
    assert typo.hyphenation is None
    # 2. Проверяем результат: в тексте не появилось символов мягкого переноса
    assert CHAR_SHY not in output_string


def test_typographer_disables_unbreakables():
    """
    Проверяет, что при unbreakables=False модуль неразрывных пробелов отключается.
    """
    # Arrange
    input_string = "Он сказал: в дом вошла она."
    typo = Typographer(langs='ru', unbreakables=False)

    # Act
    output_string = typo.process(input_string)

    # Assert
    # 1. Проверяем внутреннее состояние
    assert typo.unbreakables is None
    # 2. Проверяем результат: в тексте не появилось неразрывных пробелов
    assert CHAR_NBSP not in output_string