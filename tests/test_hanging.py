# tests/test_hanging.py
# Тесты для модуля висячей пунктуации (HangingPunctuationProcessor).

import pytest
from bs4 import BeautifulSoup
from etpgrf.hanging import HangingPunctuationProcessor
from etpgrf.config import (
    CHAR_RU_QUOT1_OPEN, CHAR_RU_QUOT1_CLOSE,
    CHAR_EN_QUOT1_OPEN, CHAR_EN_QUOT1_CLOSE,
    CHAR_LPAR, CHAR_LSQB, CHAR_LCUB,
    CHAR_RPAR, CHAR_RSQB, CHAR_RCUB,
    CHAR_SHY, CHAR_THIN_SP, CHAR_HAIR_SP,
    CHAR_MED_SP, CHAR_EN_SP, CHAR_EM_SP,
    CHAR_NULL_SP, CHAR_THIN_NBSP, CHAR_NBSP,
    CHAR_ZWNJ, CHAR_PUNT_SP
)

# Вспомогательная функция для создания soup
def make_soup(html_str):
    return BeautifulSoup(html_str, 'html.parser')

# Набор тестовых случаев в формате:
# (режим, входной_html, ожидаемый_html)
HANGING_TEST_CASES = [
    # --- Режим 'left' (только левая висячая пунктуация) ---
    ('left', f'<p>{CHAR_RU_QUOT1_OPEN}Цитата{CHAR_RU_QUOT1_CLOSE}</p>',
             f'<p><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}Цитата{CHAR_RU_QUOT1_CLOSE}</span></p>'),
    ('left', f'<p>{CHAR_RU_QUOT1_OPEN}Цитата{CHAR_RU_QUOT1_CLOSE} вначале текста</p>',
             f'<p><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}Цитата{CHAR_RU_QUOT1_CLOSE}</span> вначале текста</p>'),
    ('left', f'<p>А вот это {CHAR_RU_QUOT1_OPEN}Цитата{CHAR_RU_QUOT1_CLOSE} внутри текста</p>',
             f'<p>А вот <span class="etp-sp-laquo">это </span><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}Цитата{CHAR_RU_QUOT1_CLOSE}</span> внутри текста</p>'),
    ('left', f'<p>А вот это {CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE} внутри текста</p>',
             f'<p>А вот <span class="etp-sp-laquo">это </span><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}Длинная</span> цитата{CHAR_RU_QUOT1_CLOSE} внутри текста</p>'),
    ('left', f'<p>А вот это <b>{CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE}</b> внутри текста</p>',
             f'<p>А вот <span class="etp-sp-laquo">это </span><b><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}Длинная</span> цитата{CHAR_RU_QUOT1_CLOSE}</b> внутри текста</p>'),\
    ('left', f'<p>А вот это <b><i>{CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE}</i></b> внутри текста</p>',
             f'<p>А вот <span class="etp-sp-laquo">это </span><b><i><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}Длинная</span> цитата{CHAR_RU_QUOT1_CLOSE}</i></b> внутри текста</p>'),
    ('left', f'<p>А вот это {CHAR_RU_QUOT1_OPEN}<b>Длинная цитата</b>{CHAR_RU_QUOT1_CLOSE} внутри текста</p>',
             f'<p>А вот <span class="etp-sp-laquo">это </span><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}</span><b>Длинная цитата</b>{CHAR_RU_QUOT1_CLOSE} внутри текста</p>'),
    ('left', f'<p>А вот{CHAR_NBSP}это {CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE} внутри текста</p>',
             f'<p>А <span class="etp-sp-laquo">вот{CHAR_NBSP}это </span><span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}Длинная</span> цитата{CHAR_RU_QUOT1_CLOSE} внутри текста</p>'),
    # Английские кавычки "лапки"
    ('left', f'<p>This is some {CHAR_EN_QUOT1_OPEN}<b>wisdom quote</b>{CHAR_EN_QUOT1_CLOSE} for the test.</p>',
             f'<p>This is <span class="etp-sp-ldquo">some </span><span class="etp-ldquo">{CHAR_EN_QUOT1_OPEN}</span><b>wisdom quote</b>{CHAR_EN_QUOT1_CLOSE} for the test.</p>'),
    # Неразрывные пробелы и символы, отменяющие перенос, не должны оборачиваться, но должны сохраняться в тексте
    ('left', f'<p>Неразрывный пробел перед{CHAR_NBSP}{CHAR_RU_QUOT1_OPEN}Цитатой{CHAR_RU_QUOT1_CLOSE} внутри текста</p>',
             f'<p>Неразрывный пробел перед{CHAR_NBSP}{CHAR_RU_QUOT1_OPEN}Цитатой{CHAR_RU_QUOT1_CLOSE} внутри текста</p>'),
    ('left', f'<p>Неразрывный пробел перед{CHAR_ZWNJ}{CHAR_RU_QUOT1_OPEN}Цитатой{CHAR_RU_QUOT1_CLOSE} внутри текста</p>',
             f'<p>Неразрывный пробел перед{CHAR_ZWNJ}{CHAR_RU_QUOT1_OPEN}Цитатой{CHAR_RU_QUOT1_CLOSE} внутри текста</p>'),
    ('left', f'<p>Неразрывный пробел перед{CHAR_THIN_NBSP}{CHAR_RU_QUOT1_OPEN}Цитатой{CHAR_RU_QUOT1_CLOSE} внутри текста</p>',
             f'<p>Неразрывный пробел перед{CHAR_THIN_NBSP}{CHAR_RU_QUOT1_OPEN}Цитатой{CHAR_RU_QUOT1_CLOSE} внутри текста</p>'),
    # Примеры "круглая скобка"
    ('left', '<p>(Скобки)</p>', '<p><span class="etp-lpar">(Скобки)</span></p>'),
    ('left', '<p>Висячая пунктуация оборачивает (Скобки)</p>',
             '<p>Висячая пунктуация <span class="etp-sp-lpar">оборачивает </span><span class="etp-lpar">(Скобки)</span></p>'),
    ('left', '<p>Висячая пунктуация оборачивает (Круглые скобки) вот так.</p>',
             '<p>Висячая пунктуация <span class="etp-sp-lpar">оборачивает </span><span class="etp-lpar">(Круглые</span> скобки) вот так.</p>'),
    ('left', '<p>Перечисли, (элемент списка)</p>',
             '<p><span class="etp-sp-lpar">Перечисли, </span><span class="etp-lpar">(элемент</span> списка)</p>'),
    # Примеры "квадратная скобка"
    ('left', '<p>[Скобки]</p>', '<p><span class="etp-lsqb">[Скобки]</span></p>'),
    ('left', '<p>Висячая пунктуация оборачивает [Скобки]</p>',
             '<p>Висячая пунктуация <span class="etp-sp-lsqb">оборачивает </span><span class="etp-lsqb">[Скобки]</span></p>'),
    ('left', '<p>Висячая пунктуация оборачивает [Квадратные скобки] вот так.</p>',
             '<p>Висячая пунктуация <span class="etp-sp-lsqb">оборачивает </span><span class="etp-lsqb">[Квадратные</span> скобки] вот так.</p>'),
    # Примеры "фигурная скобка"
    ('left', '<p>{Скобки}</p>', '<p><span class="etp-lcub">{Скобки}</span></p>'),
    ('left', '<p>Висячая пунктуация оборачивает {Скобки}</p>',
             '<p>Висячая пунктуация <span class="etp-sp-lcub">оборачивает </span><span class="etp-lcub">{Скобки}</span></p>'),
    ('left', '<p>Висячая пунктуация оборачивает {Фигурные скобки} вот так.</p>',
             '<p>Висячая пунктуация <span class="etp-sp-lcub">оборачивает </span><span class="etp-lcub">{Фигурные</span> скобки} вот так.</p>'),
    # Обычный текст, в котором нет символов для висячей пунктуации, не должен изменяться
    ('left', '<p>Текст.</p>', '<p>Текст.</p>'),
    ('left', '<p>Пароль `89(fg#_Wfgq0[89`</p>', '<p>Пароль `89(fg#_Wfgq0[89`</p>'),
    # Проверка на альтернативный разрывной символ (не пробел)
    ('left', '<p>Висячая пунктуация оборачивает\t{Скобки}</p>',
             '<p>Висячая пунктуация <span class="etp-sp-lcub">оборачивает\t</span><span class="etp-lcub">{Скобки}</span></p>'),
    ('left', f'<p>Висячая пунктуация оборачивает{CHAR_SHY}{{Скобки}}</p>',
             f'<p>Висячая пунктуация <span class="etp-sp-lcub">оборачивает{CHAR_SHY}</span><span class="etp-lcub">{{Скобки}}</span></p>'),
    ('left', f'<p>Висячая пунктуация оборачивает{CHAR_PUNT_SP}{{Скобки}}</p>',
             f'<p>Висячая пунктуация <span class="etp-sp-lcub">оборачивает{CHAR_PUNT_SP}</span><span class="etp-lcub">{{Скобки}}</span></p>'),
    ('left', f'<p>Висячая пунктуация оборачивает\n{{Скобки}}</p>',
             f'<p>Висячая пунктуация <span class="etp-sp-lcub">оборачивает\n</span><span class="etp-lcub">{{Скобки}}</span></p>'),
    ('left', f'<p>Висячая пунктуация обора{CHAR_SHY}чивает {{Скобки}}</p>',
             f'<p>Висячая пунктуация обора{CHAR_SHY}<span class="etp-sp-lcub">чивает </span><span class="etp-lcub">{{Скобки}}</span></p>'),

    # --- Режим 'right' (только правая пунктуация) ---
    ('right', f'<p>{CHAR_RU_QUOT1_OPEN}Цитата{CHAR_RU_QUOT1_CLOSE}</p>',
              f'<p><span class="etp-raquo">{CHAR_RU_QUOT1_OPEN}Цитата{CHAR_RU_QUOT1_CLOSE}</span></p>'),
    ('right', f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE}</p>',
              f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная <span class="etp-raquo">цитата{CHAR_RU_QUOT1_CLOSE}</span></p>'),
    ('right', f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE} внутри текста</p>',
              f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная <span class="etp-raquo">цитата{CHAR_RU_QUOT1_CLOSE}</span><span class="etp-sp-raquo"> </span>внутри текста</p>'),
    ('right', f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE} внутри текста.</p>',
              f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная <span class="etp-raquo">цитата{CHAR_RU_QUOT1_CLOSE}</span><span class="etp-sp-raquo"> </span>внутри <span class="etp-r-dot">текста.</span></p>'),
    ('right', f'<p>Right {CHAR_EN_QUOT1_OPEN}long quote{CHAR_EN_QUOT1_CLOSE} within the text.</p>',
              f'<p>Right {CHAR_EN_QUOT1_OPEN}long <span class="etp-rdquo">quote{CHAR_EN_QUOT1_CLOSE}</span><span class="etp-sp-rdquo"> </span>within the <span class="etp-r-dot">text.</span></p>'),
    ## С границами узлов
    ('right', f'<p>Right {CHAR_EN_QUOT1_OPEN}<b>long quote</b>{CHAR_EN_QUOT1_CLOSE} within the text.</p>',
              f'<p>Right {CHAR_EN_QUOT1_OPEN}<b>long quote</b><span class="etp-rdquo">{CHAR_EN_QUOT1_CLOSE}</span><span class="etp-sp-rdquo"> </span>within the <span class="etp-r-dot">text.</span></p>'),
    ('right', f'<p>Right <b>{CHAR_EN_QUOT1_OPEN}long quote{CHAR_EN_QUOT1_CLOSE}</b> within the text.</p>',
              f'<p>Right <b>{CHAR_EN_QUOT1_OPEN}long <span class="etp-rdquo">quote{CHAR_EN_QUOT1_CLOSE}</span></b><span class="etp-sp-rdquo"> </span>within the <span class="etp-r-dot">text.</span></p>'),
    # Неразрывные пробелы и символы, отменяющие перенос, не должны оборачиваться, но должны сохраняться в тексте
    ('right', f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE}{CHAR_NBSP}внутри текста 2</p>',
              f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE}{CHAR_NBSP}внутри текста 2</p>'),
    ('right', f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE}{CHAR_ZWNJ}внутри текста 2</p>',
              f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE}{CHAR_ZWNJ}внутри текста 2</p>'),
    ('right', f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE}{CHAR_THIN_NBSP}внутри текста 2</p>',
              f'<p>Правая {CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE}{CHAR_THIN_NBSP}внутри текста 2</p>'),
    ('right', f'<p>Правая <b>{CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE}</b>{CHAR_NBSP}внутри текста 2</p>',
              f'<p>Правая <b>{CHAR_RU_QUOT1_OPEN}Длинная цитата{CHAR_RU_QUOT1_CLOSE}</b>{CHAR_NBSP}внутри текста 2</p>'),
    #('right', '<p>Текст.</p>', '<p>Текст<span class="etp-r-dot">.</span></p>'),
    #('right', '<p>(Скобки)</p>', '<p>(Скобки<span class="etp-rpar">)</span></p>'),
    ('right', '<p>End.</p>', '<p><span class="etp-r-dot">End.</span></p>'),
    # Внутри цифр и текста висячие символы не должны оборачиваться, так как они не являются висячими в этом контексте
    ('right', '<p>3.14</p>', '<p>3.14</p>'),
    ('right', '3.14', '3.14'),
    ('right', '<p>3,14</p>', '<p>3,14</p>'),
    ('right', '<p>Переменная <code>self.right_chars</code></p>', '<p>Переменная <code>self.right_chars</code></p>'),
    ('right', 'Переменная `self.right_chars`', 'Переменная `self.right_chars`'),


    # --- Режим None / False (отключено) ---
    (None, f'<p>{CHAR_RU_QUOT1_OPEN}Текст{CHAR_RU_QUOT1_CLOSE}</p>',
           f'<p>{CHAR_RU_QUOT1_OPEN}Текст{CHAR_RU_QUOT1_CLOSE}</p>'),
    (False, f'<p>{CHAR_RU_QUOT1_OPEN}Текст{CHAR_RU_QUOT1_CLOSE}</p>',
            f'<p>{CHAR_RU_QUOT1_OPEN}Текст{CHAR_RU_QUOT1_CLOSE}</p>'),
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


LEFT_FULL_SYMBOLS = [
    (CHAR_RU_QUOT1_OPEN, CHAR_RU_QUOT1_CLOSE, 'etp-laquo'),
    (CHAR_EN_QUOT1_OPEN, CHAR_EN_QUOT1_CLOSE, 'etp-ldquo'),
    (CHAR_LPAR, CHAR_RPAR, 'etp-lpar'),
    (CHAR_LSQB, CHAR_RSQB, 'etp-lsqb'),
    (CHAR_LCUB, CHAR_RCUB, 'etp-lcub'),
]


@pytest.mark.parametrize("open_char, close_char, cls", LEFT_FULL_SYMBOLS)
def test_hanging_left_mode_wraps_symbol_pairs(open_char, close_char, cls):
    """
    Убедимся, что разные висячие символы полностью оборачиваются в левом режиме.

    open_char: символ, открывающий висячий знак.
    close_char: символ, закрывающий висячий знак.
    cls: CSS класс для обёртки висячих знаков.

    """
    input_html = f'<p>{open_char}Текст{close_char}</p>'
    expected_html = f'<p><span class="{cls}">{open_char}Текст{close_char}</span></p>'
    processor = HangingPunctuationProcessor(mode='left')
    soup = make_soup(input_html)

    processor.process(soup)
    assert str(soup) == expected_html


SPACE_VARIANTS = [
    ' ', CHAR_SHY, CHAR_THIN_SP, CHAR_HAIR_SP,
    CHAR_MED_SP, CHAR_EN_SP, CHAR_EM_SP, CHAR_NULL_SP,
]


@pytest.mark.parametrize("space", SPACE_VARIANTS)
def test_hanging_left_mode_compensates_different_spaces(space):
    """Проверяем компенсацию для разных типов разрывных пробелов."""
    text = f'<p>Проба{space}{CHAR_RU_QUOT1_OPEN}Текст{CHAR_RU_QUOT1_CLOSE}</p>'
    expected_html = (f'<p><span class="etp-sp-laquo">Проба{space}</span>'
                     f'<span class="etp-laquo">{CHAR_RU_QUOT1_OPEN}Текст{CHAR_RU_QUOT1_CLOSE}</span></p>')

    processor = HangingPunctuationProcessor(mode='left')
    soup = make_soup(text)

    processor.process(soup)
    assert str(soup) == expected_html


@pytest.mark.parametrize("separator", [CHAR_NBSP, CHAR_THIN_NBSP, CHAR_ZWNJ])
def test_hanging_left_mode_honors_cancellation(separator):
    """Символы, отменяющие перенос, остаются без обёрток."""
    input_html = f'<p>Неразрывный{separator}{CHAR_RU_QUOT1_OPEN}Текст{CHAR_RU_QUOT1_CLOSE}</p>'
    processor = HangingPunctuationProcessor(mode='left')
    soup = make_soup(input_html)

    processor.process(soup)
    assert str(soup) == input_html
