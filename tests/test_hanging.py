# tests/test_hanging.py
# Тесты для модуля висячей пунктуации (HangingPunctuationProcessor).

import pytest
from bs4 import BeautifulSoup
from etpgrf.hanging import HangingPunctuationProcessor
from etpgrf.config import (
    CHAR_RU_QUOT1_OPEN, CHAR_RU_QUOT1_CLOSE,
    CHAR_EN_QUOT1_OPEN, CHAR_EN_QUOT1_CLOSE
)

# Вспомогательная функция для создания soup
def make_soup(html_str):
    return BeautifulSoup(html_str, 'html.parser')

# Набор тестовых случаев в формате:
# (режим, входной_html, ожидаемый_html)
HANGING_TEST_CASES = [
    # --- Режим 'left' (только левая пунктуация) ---
    ('left', f'<p>{CHAR_RU_QUOT1_OPEN}Цитата{CHAR_RU_QUOT1_CLOSE}</p>',
             f'<p><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}</span>Цитата{CHAR_RU_QUOT1_CLOSE}</p>'),
    ('left', f'<p>(Скобки)</p>',
             f'<p><span class="etp-lpar">(</span>Скобки)</p>'),
    # Правая пунктуация игнорируется
    ('left', f'<p>Текст.</p>', f'<p>Текст.</p>'),

    # --- Режим 'right' (только правая пунктуация) ---
    ('right', f'<p>{CHAR_RU_QUOT1_OPEN}Цитата{CHAR_RU_QUOT1_CLOSE}</p>',
              f'<p>{CHAR_RU_QUOT1_OPEN}Цитата<span class="etp-raquo">{CHAR_RU_QUOT1_CLOSE}</span></p>'),
    ('right', f'<p>Текст.</p>',
              f'<p>Текст<span class="etp-r-dot">.</span></p>'),
    # Левая пунктуация игнорируется
    ('right', f'<p>(Скобки)</p>', f'<p>(Скобки<span class="etp-rpar">)</span></p>'),

    # --- Режим 'both' (и левая, и правая) ---
    ('both', f'<p>{CHAR_RU_QUOT1_OPEN}Цитата{CHAR_RU_QUOT1_CLOSE}</p>',
             f'<p><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}</span>Цитата<span class="etp-raquo">{CHAR_RU_QUOT1_CLOSE}</span></p>'),
    ('both', f'<p>Текст.</p>',
             f'<p>Текст<span class="etp-r-dot">.</span></p>'),
    # Последовательность символов (точка + кавычка)
    ('both', f'<p>Текст.{CHAR_RU_QUOT1_CLOSE}</p>',
             f'<p>Текст<span class="etp-r-dot">.</span><span class="etp-raquo">{CHAR_RU_QUOT1_CLOSE}</span></p>'),
    # Вложенные теги
    ('both', f'<p><b>{CHAR_RU_QUOT1_OPEN}Жирный{CHAR_RU_QUOT1_CLOSE}</b></p>',
             f'<p><b><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}</span>Жирный<span class="etp-raquo">{CHAR_RU_QUOT1_CLOSE}</span></b></p>'),
    # Смешанный контент
    ('both', f'<p>{CHAR_RU_QUOT1_OPEN}Начало <i>курсив</i> конец.{CHAR_RU_QUOT1_CLOSE}</p>',
             f'<p><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}</span>Начало <i>курсив</i> конец<span class="etp-r-dot">.</span><span class="etp-raquo">{CHAR_RU_QUOT1_CLOSE}</span></p>'),

    # --- Режим None / False (отключено) ---
    (None, f'<p>{CHAR_RU_QUOT1_OPEN}Текст{CHAR_RU_QUOT1_CLOSE}</p>',
           f'<p>{CHAR_RU_QUOT1_OPEN}Текст{CHAR_RU_QUOT1_CLOSE}</p>'),
    (False, f'<p>{CHAR_RU_QUOT1_OPEN}Текст{CHAR_RU_QUOT1_CLOSE}</p>',
            f'<p>{CHAR_RU_QUOT1_OPEN}Текст{CHAR_RU_QUOT1_CLOSE}</p>'),

    # --- Отсутствие висячих символов ---
    ('both', '<p>Простой текст без спецсимволов!</p>', '<p>Простой текст без спецсимволов!</p>'),

    # --- Проверка контекста (пробелы) ---
    # 1. Левая кавычка внутри слова (не должна висеть)
    ('both', f'<p>func{CHAR_RU_QUOT1_OPEN}arg{CHAR_RU_QUOT1_CLOSE}</p>',
             f'<p>func{CHAR_RU_QUOT1_OPEN}arg<span class="etp-raquo">{CHAR_RU_QUOT1_CLOSE}</span></p>'), # Правая висит, т.к. конец узла
    # 2. Правая кавычка внутри слова (не должна висеть)
    ('both', f'<p>1{CHAR_RU_QUOT1_CLOSE}2</p>',
             f'<p>1{CHAR_RU_QUOT1_CLOSE}2</p>'),
    # 3. Левая кавычка после пробела (должна висеть)
    ('both', f'<p>func {CHAR_RU_QUOT1_OPEN}arg</p>',
             f'<p>func <span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}</span>arg</p>'),
    # 4. Правая кавычка перед пробелом (должна висеть)
    ('both', f'<p>arg{CHAR_RU_QUOT1_CLOSE} next</p>',
             f'<p>arg<span class="etp-raquo">{CHAR_RU_QUOT1_CLOSE}</span> next</p>'),
    # 5. Точка внутри числа (не должна висеть)
    ('both', '<p>3.14</p>', '<p>3.14</p>'),
    # 6. Точка в конце предложения (должна висеть)
    ('both', '<p>End.</p>', '<p>End<span class="etp-r-dot">.</span></p>'),
]


@pytest.mark.parametrize("mode, input_html, expected_html", HANGING_TEST_CASES)
def test_hanging_punctuation_processor(mode, input_html, expected_html):
    """
    Проверяет работу HangingPunctuationProcessor в различных режимах.
    """
    # Arrange
    processor = HangingPunctuationProcessor(mode=mode)
    soup = make_soup(input_html)

    # Act
    processor.process(soup)
    actual_html = str(soup)

    # Assert
    assert actual_html == expected_html


def test_hanging_punctuation_target_tags():
    """
    Отдельный тест для проверки работы со списком целевых тегов.
    """
    mode = ['blockquote', 'h1']
    input_html = (f'<div>{CHAR_RU_QUOT1_OPEN}Игнор{CHAR_RU_QUOT1_CLOSE}</div>'
                  f'<blockquote>{CHAR_RU_QUOT1_OPEN}Обработка{CHAR_RU_QUOT1_CLOSE}</blockquote>'
                  f'<h1>{CHAR_RU_QUOT1_OPEN}Заголовок{CHAR_RU_QUOT1_CLOSE}</h1>')
    
    expected_html = (f'<div>{CHAR_RU_QUOT1_OPEN}Игнор{CHAR_RU_QUOT1_CLOSE}</div>'
                     f'<blockquote><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}</span>Обработка<span class="etp-raquo">{CHAR_RU_QUOT1_CLOSE}</span></blockquote>'
                     f'<h1><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}</span>Заголовок<span class="etp-raquo">{CHAR_RU_QUOT1_CLOSE}</span></h1>')

    processor = HangingPunctuationProcessor(mode=mode)
    soup = make_soup(input_html)
    
    processor.process(soup)
    
    assert str(soup) == expected_html
