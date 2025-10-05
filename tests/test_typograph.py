# tests/test_typograph.py
# Тестирует основной класс Typographer и его конвейер обработки.

import pytest
from etpgrf import Typographer
from etpgrf.config import CHAR_NBSP, CHAR_THIN_SP

TYPOGRAPHER_HTML_TEST_CASES = [
    # --- Базовая обработка без HTML ---
    ('mnemonic', 'Простой текст с "кавычками".',  f'Простой текст с&nbsp;&laquo;кавычками&raquo;.'),
    ('mixed', 'Простой текст с "кавычками".', f'Простой текст с&nbsp;«кавычками».'),
    ('unicode', 'Простой текст с "кавычками".',  f'Простой текст с{CHAR_NBSP}«кавычками».'),
    # --- Базовая обработка с HTML ---
    ('mnemonic', '<p>Простой параграф с «кавычками».</p>', '<p>Простой параграф с&nbsp;&laquo;кавычками&raquo;.</p>'),
    ('mixed', '<p>Простой параграф с "кавычками".</p>', '<p>Простой параграф с&nbsp;«кавычками».</p>'),
    ('unicode', '<p>Простой параграф с "кавычками".</p>', f'<p>Простой параграф с{CHAR_NBSP}«кавычками».</p>'),
    # --- Рекурсивный обход ---
    ('mnemonic', '<div><p>Текст, а внутри <b>для проверки "жирный"</b> текст.</p></div>',
                 '<div><p>Текст, а&nbsp;внутри <b>для&nbsp;проверки &laquo;жирный&raquo;</b> текст.</p></div>'),
    ('mixed', '<div><p>Текст, а внутри <b>для проверки "жирный"</b> текст.</p></div>',
              '<div><p>Текст, а&nbsp;внутри <b>для&nbsp;проверки «жирный»</b> текст.</p></div>'),
    ('unicode', '<div><p>Текст, а внутри <b>для проверки "жирный"</b> текст.</p></div>',
                f'<div><p>Текст, а{CHAR_NBSP}внутри <b>для{CHAR_NBSP}проверки «жирный»</b> текст.</p></div>'),
    # --- Вложенные теги с предлогом в тексте ---
    ('mnemonic', '<div><p>Текст с предлогом <b>в <i>доме</i></b>.</p></div>',
                 '<div><p>Текст с&nbsp;предлогом <b>в&nbsp;<i>доме</i></b>.</p></div>'),
    ('mixed', '<div><p>Текст с предлогом <b>в <i>доме</i></b>.</p></div>',
              '<div><p>Текст с&nbsp;предлогом <b>в&nbsp;<i>доме</i></b>.</p></div>'),
    ('unicode', '<div><p>Текст с предлогом <b>в <i>доме</i></b>.</p></div>',
                f'<div><p>Текст с{CHAR_NBSP}предлогом <b>в{CHAR_NBSP}<i>доме</i></b>.</p></div>'),
    # --- Обработка соседних текстовых узлов ---
    ('mnemonic', '<p>Союз и <b>слово</b> и еще один союз а <span>текст</span>.</p>',
                 '<p>Союз и&nbsp;<b>слово</b> и&nbsp;еще один союз а&nbsp;<span>текст</span>.</p>'),
    ('mixed', '<p>Союз и <b>слово</b> и еще один союз а <span>текст</span>.</p>',
                '<p>Союз и&nbsp;<b>слово</b> и&nbsp;еще один союз а&nbsp;<span>текст</span>.</p>'),
    ('unicode', '<p>Союз и <b>слово</b> и еще один союз а <span>текст</span>.</p>',
                    f'<p>Союз и{CHAR_NBSP}<b>слово</b> и{CHAR_NBSP}еще один союз а{CHAR_NBSP}<span>текст</span>.</p>'),




    # # --- Проверка "небезопасных" тегов ---
    # (
    #     'Небезопасные теги не должны обрабатываться.',
    #     '<p>Текст "до".</p><script>var text = "не трогать";</script><pre>  - 10</pre><code>"тоже не трогать"</code>',
    #     '<p>Текст «до».</p><script>var text = "не трогать";</script><pre>  - 10</pre><code>"тоже не трогать"</code>'
    # ),
    # # --- Проверка атрибутов ---
    # (
    #     'Атрибуты тегов не должны обрабатываться.',
    #     '<a href="/a-b" title="Текст в кавычках \'внутри\' атрибута">Текст "снаружи"</a>',
    #     '<a href="/a-b" title="Текст в кавычках \'внутри\' атрибута">Текст «снаружи»</a>'
    # ),
    # # --- Комплексный интеграционный тест ---
    # (
    #     'Все правила вместе в HTML.',
    #     '<p>Он сказал: "В 1941-1945 гг. -- было 100 тыс. руб. и т. д."</p>',
    #     f'<p>Он сказал: «В 1941–1945{CHAR_NBSP}гг.{CHAR_NBSP}— было 100{CHAR_NBSP}тыс.{CHAR_THIN_SP}руб. и{CHAR_NBSP}т.{CHAR_THIN_SP}д.»</p>'
    # ),
    # # --- Проверка пустого текста и узлов с пробелами ---
    # (
    #     'Пустые и пробельные узлы.',
    #     '<p>  </p><div>\n\t</div><p>Слово</p>',
    #     '<p>  </p><div>\n\t</div><p>Слово</p>'
    # ),
]


@pytest.mark.parametrize("mode, input_html, expected_html", TYPOGRAPHER_HTML_TEST_CASES)
def test_typographer_html_processing(mode, input_html, expected_html):
    """
    Проверяет полный конвейер Typographer при обработке HTML.
    """
    typo = Typographer(langs='ru', process_html=True, mode=mode)
    actual_html = typo.process(input_html)
    assert actual_html == expected_html


def test_typographer_plain_text_processing():
    """
    Проверяет, что в режиме process_html=False типограф маскирует HTML-теги и обрабатывает весь текст.
    """
    typo = Typographer(langs='ru', process_html=False)
    input_text = '<i>Текст "без" <b>HTML</b>, но с предлогом в доме.</i>'
    expected_text = '&lt;i&gt;Текст «без» &lt;b&gt;HTML&lt;/b&gt;, но&nbsp;с&nbsp;предлогом в&nbsp;доме.&lt;/i&gt;'
    actual_text = typo.process(input_text)
    assert actual_text == expected_text