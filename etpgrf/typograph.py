# etpgrf/typograph.py
# Основной класс Typographer, который объединяет все модули правил и предоставляет единый интерфейс.
# Поддерживает обработку текста внутри HTML-тегов с помощью BeautifulSoup.
import logging
import html
import regex # Для проверки наличия корневых тегов
try:
    from bs4 import BeautifulSoup, NavigableString
except ImportError:
    BeautifulSoup = None
from etpgrf.comutil import parse_and_validate_mode, parse_and_validate_langs
from etpgrf.hyphenation import Hyphenator
from etpgrf.unbreakables import Unbreakables
from etpgrf.quotes import QuotesProcessor
from etpgrf.layout import LayoutProcessor
from etpgrf.symbols import SymbolsProcessor
from etpgrf.sanitizer import SanitizerProcessor
from etpgrf.hanging import HangingPunctuationProcessor
from etpgrf.codec import decode_to_unicode, encode_from_unicode
from etpgrf.config import PROTECTED_HTML_TAGS, CHAR_PLACEHOLDER, CHAR_NODE_SEPARATOR, CHAR_AMP_PLACEHOLDER


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
                 layout: LayoutProcessor | bool | None = True,  # Правила для тире и спецсимволов
                 symbols: SymbolsProcessor | bool | None = True, # Правила для псевдографики
                 sanitizer: SanitizerProcessor | str | bool | None = None, # Правила очистки
                 hanging_punctuation: str | bool | list[str] | None = None, # Висячая пунктуация
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

        # D. --- Конфигурация правил для псевдографики ---
        self.symbols: SymbolsProcessor | None = None
        if symbols is True or symbols is None:
            self.symbols = SymbolsProcessor()
        elif isinstance(symbols, SymbolsProcessor):
            self.symbols = symbols

        # E. --- Инициализация правила переноса ---
        #    Предпосылка: если вызвали типограф, значит, мы хотим обрабатывать текст и переносы тоже нужно расставлять.
        #    А для специальных случаев, когда переносы не нужны, пусть не ленятся и делают `hyphenation=False`.
        self.hyphenation: Hyphenator | None = None
        if hyphenation is True or hyphenation is None:
            # C1. Создаем новый объект Hyphenator с заданными языками и режимом, а все остальное по умолчанию
            self.hyphenation = Hyphenator(langs=self.langs)
        elif isinstance(hyphenation, Hyphenator):
            # C2. Если hyphenation - это объект Hyphenator, то просто сохраняем его (и используем его langs и mode)
            self.hyphenation = hyphenation

        # F. --- Конфигурация правил неразрывных слов ---
        self.unbreakables: Unbreakables | None = None
        if unbreakables is True or unbreakables is None:
            # D1. Создаем новый объект Unbreakables с заданными языками и режимом, а все остальное по умолчанию
            self.unbreakables = Unbreakables(langs=self.langs)
        elif isinstance(unbreakables, Unbreakables):
            # D2. Если unbreakables - это объект Unbreakables, то просто сохраняем его (и используем его langs и mode)
            self.unbreakables = unbreakables

        # G. --- Конфигурация правил обработки кавычек ---
        self.quotes: QuotesProcessor | None = None
        if quotes is True or quotes is None:
            self.quotes = QuotesProcessor(langs=self.langs)
        elif isinstance(quotes, QuotesProcessor):
            self.quotes = quotes

        # H. --- Конфигурация правил для тире и спецсимволов ---
        self.layout: LayoutProcessor | None = None
        if layout is True or layout is None:
            self.layout = LayoutProcessor(langs=self.langs)
        elif isinstance(layout, LayoutProcessor):
            self.layout = layout

        # I. --- Конфигурация санитайзера ---
        self.sanitizer: SanitizerProcessor | None = None
        if isinstance(sanitizer, SanitizerProcessor):
            self.sanitizer = sanitizer
        elif sanitizer: # Если передана строка режима или True
             self.sanitizer = SanitizerProcessor(mode=sanitizer)

        # J. --- Конфигурация висячей пунктуации ---
        self.hanging: HangingPunctuationProcessor | None = None
        if hanging_punctuation:
            self.hanging = HangingPunctuationProcessor(mode=hanging_punctuation)

        # Z. --- Логирование инициализации ---
        logger.debug(f"Typographer `__init__`: langs: {self.langs}, mode: {self.mode}, "
                     f"hyphenation: {self.hyphenation is not None}, "
                     f"unbreakables: {self.unbreakables is not None}, "
                     f"quotes: {self.quotes is not None}, "
                     f"layout: {self.layout is not None}, "
                     f"symbols: {self.symbols is not None}, "
                     f"sanitizer: {self.sanitizer is not None}, "
                     f"hanging: {self.hanging is not None}, "
                     f"process_html: {self.process_html}")


    def _hide_protected_tags(self, soup) -> list:
        """
        Находит все защищенные теги, заменяет их на плейсхолдеры и возвращает список сохраненных тегов.
        """
        protected_tags = []
        if not PROTECTED_HTML_TAGS:
            return protected_tags

        selector = ", ".join(PROTECTED_HTML_TAGS)
        tags_to_replace = soup.select(selector)
        
        for tag in tags_to_replace:
            protected_tags.append(tag)
            tag.replace_with(NavigableString(CHAR_PLACEHOLDER))
            
        return protected_tags

    def _restore_protected_tags(self, soup, protected_tags: list):
        """
        Восстанавливает защищенные теги на места плейсхолдеров.
        """
        if not protected_tags:
            return

        text_nodes_with_placeholder = [
            node for node in soup.descendants 
            if isinstance(node, NavigableString) and CHAR_PLACEHOLDER in node
        ]

        tag_index = 0
        for node in text_nodes_with_placeholder:
            text = str(node)
            if CHAR_PLACEHOLDER in text:
                parts = text.split(CHAR_PLACEHOLDER)
                
                new_nodes = []
                for i, part in enumerate(parts):
                    if part:
                        new_nodes.append(NavigableString(part))
                    
                    if i < len(parts) - 1:
                        if tag_index < len(protected_tags):
                            new_nodes.append(protected_tags[tag_index])
                            tag_index += 1
                        else:
                            logger.warning("Mismatch in protected tags count during restoration.")
                
                if new_nodes:
                    first_node = new_nodes[0]
                    node.replace_with(first_node)
                    current_pos = first_node
                    for next_node in new_nodes[1:]:
                        current_pos.insert_after(next_node)
                        current_pos = next_node

    def process(self, text: str) -> str:
        """
        Обрабатывает текст, применяя все активные правила типографики.
        Поддерживает обработку текста внутри HTML-тегов.
        """
        if not text:
            return ""
            
        text = text.replace('&amp;', CHAR_AMP_PLACEHOLDER)

        if self.process_html:
            is_full_document = bool(regex.search(r'^\s*<(?:!DOCTYPE|html|body)', text, regex.IGNORECASE))

            try:
                soup = BeautifulSoup(text, 'lxml')
            except Exception:
                soup = BeautifulSoup(text, 'html.parser')

            if self.sanitizer:
                result = self.sanitizer.process(soup)
                if isinstance(result, str):
                    return self._process_plain_text(result).replace(CHAR_AMP_PLACEHOLDER, '&amp;')
                soup = result

            protected_tags = self._hide_protected_tags(soup)

            text_nodes = [node for node in soup.descendants if isinstance(node, NavigableString)]
            
            super_string = ""
            for node in text_nodes:
                node_text = node.string or ""
                super_string += node_text + CHAR_NODE_SEPARATOR

            processed_super_string = self._process_plain_text(super_string)

            parts = processed_super_string.split(CHAR_NODE_SEPARATOR)
            
            if len(parts) > len(text_nodes):
                 parts = parts[:len(text_nodes)]
            
            for i, node in enumerate(text_nodes):
                if i < len(parts):
                    new_text_part = parts[i]
                    node.replace_with(new_text_part)

            self._restore_protected_tags(soup, protected_tags)

            if self.hanging:
                self.hanging.process(soup)

            if is_full_document:
                processed_html = str(soup)
            else:
                if soup.body:
                    processed_html = soup.body.decode_contents()
                else:
                    processed_html = str(soup)
            
            processed_html = processed_html.replace('&amp;', '&')
            return processed_html.replace(CHAR_AMP_PLACEHOLDER, '&amp;')
        else:
            processed_text = self._process_plain_text(text)
            return processed_text.replace(CHAR_AMP_PLACEHOLDER, '&amp;')

    def _process_plain_text(self, text: str) -> str:
        """
        Логика обработки обычного текста (вынесена из process для переиспользования).
        """
        processed_text = decode_to_unicode(text)
        
        if self.symbols:
            processed_text = self.symbols.process(processed_text)
        if self.quotes:
            processed_text = self.quotes.process(processed_text)
        if self.unbreakables:
            processed_text = self.unbreakables.process(processed_text)
        if self.layout:
            processed_text = self.layout.process(processed_text)
        if self.hyphenation:
            processed_text = self.hyphenation.hyp_in_text(processed_text)

        return encode_from_unicode(processed_text, self.mode)
