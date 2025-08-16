import logging
import html
try:
    from bs4 import BeautifulSoup, NavigableString
except ImportError:
    BeautifulSoup = None
from etpgrf.comutil import parse_and_validate_mode, parse_and_validate_langs
from etpgrf.hyphenation import Hyphenator
from etpgrf.unbreakables import Unbreakables
from etpgrf.quotes import QuotesProcessor
from etpgrf.codec import decode_to_unicode, encode_from_unicode


# --- Настройки логирования ---
logger = logging.getLogger(__name__)


# --- Основной класс Typographer ---
class Typographer:
    def __init__(self,
                 langs: str | list[str] | tuple[str, ...] | frozenset[str] | None = None,
                 mode: str | None = None,
                 process_html: bool = False,        # Флаг обработки HTML-тегов
                 hyphenation: Hyphenator | bool | None = True,  # Перенос слов и параметры расстановки переносов
                 unbreakables: Unbreakables | bool | None = True, # Правила для предотвращения разрыва коротких слов
                 quotes: QuotesProcessor | bool | None = True,  # Правила для обработки кавычек
                 # ... другие модули правил ...
                 ):

        # A. --- Обработка и валидация параметра langs ---
        self.langs: frozenset[str] = parse_and_validate_langs(langs)
        # B. --- Обработка и валидация параметра mode ---
        self.mode: str = parse_and_validate_mode(mode)
        # C. --- Настройка режима обработки HTML ---
        self.process_html = process_html
        if self.process_html and BeautifulSoup is None:
            logger.warning("Параметр 'process_html=True', но библиотека BeautifulSoup не установлена. "
                           "HTML не будет обработан. Установите ее: `pip install beautifulsoup4`")
            self.process_html = False

        # D. --- Инициализация правила переноса ---
        #    Предпосылка: если вызвали типограф, значит, мы хотим обрабатывать текст и переносы тоже нужно расставлять.
        #    А для специальных случаев, когда переносы не нужны, пусть не ленятся и делают `hyphenation=False`.
        self.hyphenation: Hyphenator | None = None
        if hyphenation is True or hyphenation is None:
            # C1. Создаем новый объект Hyphenator с заданными языками и режимом, а все остальное по умолчанию
            self.hyphenation = Hyphenator(langs=self.langs)
        elif isinstance(hyphenation, Hyphenator):
            # C2. Если hyphenation - это объект Hyphenator, то просто сохраняем его (и используем его langs и mode)
            self.hyphenation = hyphenation

        # E. --- Конфигурация правил неразрывных слов ---
        self.unbreakables: Unbreakables | None = None
        if unbreakables is True or unbreakables is None:
            # D1. Создаем новый объект Unbreakables с заданными языками и режимом, а все остальное по умолчанию
            self.unbreakables = Unbreakables(langs=self.langs)
        elif isinstance(unbreakables, Unbreakables):
            # D2. Если unbreakables - это объект Unbreakables, то просто сохраняем его (и используем его langs и mode)
            self.unbreakables = unbreakables

        # F. --- Конфигурация правил обработки кавычек ---
        self.quotes: QuotesProcessor | None = None
        if quotes is True or quotes is None:
            self.quotes = QuotesProcessor(langs=self.langs)
        elif isinstance(quotes, QuotesProcessor):
            self.quotes = quotes

        # G. --- Конфигурация других правил---

        # Z. --- Логирование инициализации ---
        logger.debug(f"Typographer `__init__`: langs: {self.langs}, mode: {self.mode}, "
                     f"hyphenation: {self.hyphenation is not None}, "
                     f"unbreakables: {self.unbreakables is not None}, "
                     f"quotes: {self.quotes is not None}, "
                     f"process_html: {self.process_html}")


    def _process_text_node(self, text: str) -> str:
        """
        Внутренний конвейер, который работает с чистым текстом.
        """
        # Шаг 1: Декодируем весь входящий текст в канонический Unicode
        # (здесь можно использовать html.unescape, но наш кодек тоже подойдет)
        processed_text = decode_to_unicode(text)
        # processed_text = text  # ВРЕМЕННО: используем текст как есть

        # Шаг 2: Применяем правила к чистому Unicode-тексту
        if self.quotes is not None:
            processed_text = self.quotes.process(processed_text)
        if self.unbreakables is not None:
            processed_text = self.unbreakables.process(processed_text)
        if self.hyphenation is not None:
            processed_text = self.hyphenation.hyp_in_text(processed_text)
        # ... вызовы других активных модулей правил ...

        return processed_text




    # Конвейер для обработки текста
    def process(self, text: str) -> str:
        """
        Обрабатывает текст, применяя все активные правила типографики.
        Поддерживает обработку текста внутри HTML-тегов.
        """
        if not text:
            return ""
        # Если включена обработка HTML и BeautifulSoup доступен
        if self.process_html:
            # Мы передаем 'html.parser', он быстрый и встроенный.
            soup = BeautifulSoup(markup=text, features='html.parser')
            text_nodes = soup.find_all(string=True)
            for node in text_nodes:
                # Пропускаем пустые или состоящие из пробелов узлы и узлы внутри тегов, где не нужно обрабатывать текст
                if not node.string.strip() or node.parent.name in ['style', 'script', 'pre', 'code']:
                    continue
                # К каждому текстовому узлу применяем "внутренний" процессор
                processed_node_text: str = self._process_text_node(node.string)
                # Отладочная печать, чтобы видеть, что происходит
                if node.string != processed_node_text:
                    logger.info(f"Processing node: '{node.string}' -> '{processed_node_text}'")
                # Заменяем узел в дереве на обработанный текст.
                # BeautifulSoup сама позаботится об экранировании, если нужно.
                # Важно: мы не можем просто заменить строку, нужно создать новый объект NavigableString,
                #        чтобы BeautifulSoup правильно обработал символы вроде '<' и '>'.
                #        Однако, replace_with достаточно умен, чтобы справиться с этим.
                node.replace_with(processed_node_text)

            # Получаем измененный HTML. BeautifulSoup по умолчанию выводит без тегов <html><body>
            # если их не было в исходной строке.
            processed = str(soup)
        else:
            # Если HTML-режим выключен
            processed = self._process_text_node(text)
        # Возвращаем
        return encode_from_unicode(processed, self.mode)

