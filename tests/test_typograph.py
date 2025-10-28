# tests/test_typograph.py
# Тестирует основной класс Typographer и его конвейер обработки.

import pytest
from etpgrf import Typographer
from etpgrf.config import CHAR_NBSP, CHAR_THIN_SP, CHAR_NDASH, CHAR_MDASH

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

    # --- Проверка тегов <style>, <script>, <pre>, <code>, <kbd<, <samp> и <math> ---
    ('mixed', '<p>Текст "до".</p><pre>  - 10</pre><code>"тоже не трогать"</code>',
              '<p>Текст «до».</p><pre>  - 10</pre><code>"тоже не трогать"</code>'),
    ('mixed', '<p>Текст "до".</p><style>body { font-family: "Arial"; }</style>',
              '<p>Текст «до».</p><style>body { font-family: "Arial"; }</style>'),
    ('mixed', '<p>Текст "до".</p><script>var text = "не трогать";</script>',
                '<p>Текст «до».</p><script>var text = "не трогать";</script>'),
    ('mixed', '<p>Текст "до".</p><kbd>Ctrl + C</kbd>',
              '<p>Текст «до».</p><kbd>Ctrl + C</kbd>'),
    ('mixed', '<p>Текст "до".</p><samp>Sample "text"</samp>',
              '<p>Текст «до».</p><samp>Sample "text"</samp>'),
    ('mixed', '<p>Текст "до".</p><math><mi>x</mi><mo>=</mo><mn>5</mn></math>',
              '<p>Текст «до».</p><math><mi>x</mi><mo>=</mo><mn>5</mn></math>'),

    # --- Проверка тегов с атрибутами ---
    ('mixed', '<a href="/a-b" title="Текст в кавычках \'внутри\' атрибута">Текст "снаружи"</a>',
              '<a href="/a-b" title="Текст в кавычках \'внутри\' атрибута">Текст «снаружи»</a>'),
    ('mixed', '<a href="/a-b" title=\'Текст в кавычках \"внутри\" атрибута\'>Текст "снаружи"</a>',
              '<a href="/a-b" title=\'Текст в кавычках \"внутри\" атрибута\'>Текст «снаружи»</a>'),
    ('mixed', '<a href="/a-b" title="Текст в кавычках &laquo;внутри&raquo; атрибута">Текст "снаружи"</a>',
              '<a href="/a-b" title="Текст в кавычках «внутри» атрибута">Текст «снаружи»</a>'),
    ('mnemonic', '<a href="/a-b" title="Текст в кавычках &laquo;внутри&raquo; атрибута">Текст "снаружи"</a>',
                 '<a href="/a-b" title="Текст в кавычках «внутри» атрибута">Текст &laquo;снаружи&raquo;</a>'),

    # --- Комплексный интеграционный тест ---
    ('mnemonic', '<p>Он сказал: "В 1941-1945 гг. -- было 100 тыс. руб. и т. д."</p>',
                 '<p>Он&nbsp;сказал: &laquo;В&nbsp;1941&ndash;1945&nbsp;гг.&nbsp;&ndash; было 100&nbsp;тыс.&thinsp;руб.'
                 ' и&nbsp;т.&thinsp;д.&raquo;</p>'),
    ('mixed', '<p>Он сказал: "В 1941-1945 гг. -- было 100 тыс. руб. и т. д."</p>',
              '<p>Он&nbsp;сказал: «В&nbsp;1941–1945&nbsp;гг.&nbsp;– было 100&nbsp;тыс.&thinsp;руб.'
              ' и&nbsp;т.&thinsp;д.»</p>'),
    ('unicode', '<p>Он сказал: "В 1941-1945 гг. -- было 100 тыс. руб. и т. д."</p>',
                f'<p>Он{CHAR_NBSP}сказал: «В{CHAR_NBSP}1941{CHAR_NDASH}1945{CHAR_NBSP}гг.{CHAR_NBSP}{CHAR_NDASH} было'
                f' 100{CHAR_NBSP}тыс.{CHAR_THIN_SP}руб. и{CHAR_NBSP}т.{CHAR_THIN_SP}д.»</p>'),
    # --- Теги внутри кавычек ---
    ('mnemonic', '<p>"<u>Почему</u>", "<u>зачем</u>" и "<u>кому это выгодно</u>" -- вопросы требующие ответа.</p>',
                 '<p>&laquo;<u>Почему</u>&raquo;, &laquo;<u>зачем</u>&raquo; и&nbsp;&laquo;<u>кому это выгодно</u>'
                 '&raquo;&nbsp;&ndash; вопросы требующие ответа.</p>'),
    ('mixed', '<p>"<u>Почему</u>", "<u>зачем</u>" и "<u>кому это выгодно</u>" -- вопросы требующие ответа.</p>',
                '<p>«<u>Почему</u>», «<u>зачем</u>» и&nbsp;«<u>кому это выгодно</u>»&nbsp;– вопросы требующие ответа.</p>'),
    ('unicode', '<p>"<u>Почему</u>", "<u>зачем</u>" и "<u>кому это выгодно</u>" -- вопросы требующие ответа.</p>',
                f'<p>«<u>Почему</u>», «<u>зачем</u>» и{CHAR_NBSP}«<u>кому это выгодно</u>»{CHAR_NBSP}{CHAR_NDASH} вопросы требующие ответа.</p>'),

    # --- Проверка пустого текста и узлов с пробелами ---
    ('mnemonic', '<p>  </p><div>\n\t</div><p>Слово</p>', '<p> </p><div>\n</div><p>Слово</p>'),
    ('mixed', '<p>  </p><div>\n\t</div><p>Слово</p>', '<p> </p><div>\n</div><p>Слово</p>'),
    ('unicode', '<p>  </p><div>\n\t</div><p>Слово</p>', '<p> </p><div>\n</div><p>Слово</p>'),

    # --- Самозакрывающиеся теги и теги с атрибутами ---
    #     ВАЖНО: 1. Порядок атрибутов в типографированном тексте может быть произвольным
    #            2. Любое число пробельных символов внутри "пустых" тегов будут редуцированы до одного пробела или
    #               перевода строки.
    #            3. Самозакрывающиеся теги будут приведены к единому виду с косой чертой в конце. Типа <br/>
    #            4. Все это "проделки" связаны с использованием библиотеки BeautifulSoup для парсинга HTML,
    #               так что может произойти и другой "улучшайзинг".
    ('mnemonic', '<p>Текст с картинкой <img src="image.jpg" alt="image" /> и текстом.</p>',
                 '<p>Текст с&nbsp;картинкой <img alt="image" src="image.jpg"/> и&nbsp;текстом.</p>'),
    ('mnemonic', '<p>Текст с <code>&lt;br&gt;</code><br>А это новая строка.</p>',
                 '<p>Текст с&nbsp;<code>&lt;br&gt;</code><br/>А&nbsp;это новая строка.</p>'),
    ('mixed', '<p>Текст с картинкой <img src="image.jpg" alt="image" /> и текстом.</p>',
              '<p>Текст с&nbsp;картинкой <img alt="image" src="image.jpg"/> и&nbsp;текстом.</p>'),
    ('mixed', '<p>Текст с <code>&lt;br&gt;</code><br>А это новая строка.</p>',
              '<p>Текст с&nbsp;<code>&lt;br&gt;</code><br/>А&nbsp;это новая строка.</p>'),
    ('unicode', '<p>Текст с картинкой <img src="image.jpg" alt="image" /> и текстом.</p>',
                f'<p>Текст с{CHAR_NBSP}картинкой <img alt="image" src="image.jpg"/> и{CHAR_NBSP}текстом.</p>'),
    ('unicode', '<p>Текст с <code>&lt;br&gt;</code><br>А это новая строка.</p>',
                f'<p>Текст с{CHAR_NBSP}<code>&lt;br&gt;</code><br/>А{CHAR_NBSP}это новая строка.</p>'),
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