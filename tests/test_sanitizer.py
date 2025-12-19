# tests/test_sanitizer.py
# Тестирует модуль SanitizerProcessor.

import pytest
from bs4 import BeautifulSoup
from etpgrf.sanitizer import SanitizerProcessor
from etpgrf.config import SANITIZE_NONE, SANITIZE_ETPGRF, SANITIZE_ALL_HTML


def test_sanitizer_mode_none():
    """
    Проверяет, что в режиме SANITIZE_NONE (по умолчанию) ничего не происходит.
    """
    html_input = '<p><span class="etp-laquo">«</span>Hello<span class="user-class"> world</span>.</p>'
    soup = BeautifulSoup(html_input, 'html.parser')
    
    # Тестируем с mode=None и mode=False
    processor_none = SanitizerProcessor(mode=SANITIZE_NONE)
    processor_false = SanitizerProcessor(mode=False)

    result_soup_none = processor_none.process(soup)
    result_soup_false = processor_false.process(soup)

    assert str(result_soup_none) == html_input
    assert str(result_soup_false) == html_input


def test_sanitizer_mode_all_html():
    """
    Проверяет, что в режиме SANITIZE_ALL_HTML удаляются все теги.
    """
    html_input = '<p>Hello <b>world</b>! <a href="#">Click me</a>.</p>'
    soup = BeautifulSoup(html_input, 'html.parser')
    processor = SanitizerProcessor(mode=SANITIZE_ALL_HTML)

    result_text = processor.process(soup)

    assert result_text == "Hello world! Click me."


ETPGRF_SANITIZE_TEST_CASES = [
    # ID, Описание, Входной HTML, Ожидаемый HTML
    (
        "simple_unwrap", "Простое разворачивание span'а с одним etp-классом",
        '<p><span class="etp-laquo">«</span>Hello</p>',
        '<p>«Hello</p>'
    ),
    (
        "aggressive_unwrap", "Агрессивное разворачивание span'а со смешанными классами",
        '<p>Hello<span class="user-class etp-raquo">»</span></p>',
        '<p>Hello»</p>'
    ),
    (
        "keep_user_span", "Не трогаем span'ы с пользовательскими классами",
        '<p>Hello <span class="user-class">world</span></p>',
        '<p>Hello <span class="user-class">world</span></p>'
    ),
    (
        "keep_user_span", "Не трогаем span'ы с пользовательскими etp-классами",
        '<p>Hello <span class="etp-user-class">world</span></p>',
        '<p>Hello <span class="etp-user-class">world</span></p>'
    ),
    (
        "keep_other_tags", "Не трогаем другие теги",
        '<div><b>Bold</b> and <i>italic</i></div>',
        '<div><b>Bold</b> and <i>italic</i></div>'
    ),
    (
        "complex_case", "Сложный случай с несколькими разными span'ами",
        '<h1><span class="etp-laquo">«</span>Title<span class="etp-raquo">»</span></h1>\n<p>And <span class="note">note</span>.</p>',
        '<h1>«Title»</h1>\n<p>And <span class="note">note</span>.</p>'
    ),
]

@pytest.mark.parametrize("case_id, description, html_input, expected_html", ETPGRF_SANITIZE_TEST_CASES)
def test_sanitizer_mode_etpgrf(case_id, description, html_input, expected_html):
    """
    Проверяет, что в режиме SANITIZE_ETPGRF удаляется только разметка висячей пунктуации.
    """
    soup = BeautifulSoup(html_input, 'html.parser')
    processor = SanitizerProcessor(mode=SANITIZE_ETPGRF)

    result_soup = processor.process(soup)

    assert str(result_soup) == expected_html