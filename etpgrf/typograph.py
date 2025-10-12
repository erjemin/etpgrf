# etpgrf/typograph.py
# Основной класс Typographer, который объединяет все модули правил и предоставляет единый интерфейс.
# Поддерживает обработку текста внутри HTML-тегов с помощью BeautifulSoup.
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
from etpgrf.layout import LayoutProcessor
from etpgrf.symbols import SymbolsProcessor
from etpgrf.codec import decode_to_unicode, encode_from_unicode
from etpgrf.config import PROTECTED_HTML_TAGS


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

        # I. --- Конфигурация других правил---

        # Z. --- Логирование инициализации ---
        logger.debug(f"Typographer `__init__`: langs: {self.langs}, mode: {self.mode}, "
                     f"hyphenation: {self.hyphenation is not None}, "
                     f"unbreakables: {self.unbreakables is not None}, "
                     f"quotes: {self.quotes is not None}, "
                     f"layout: {self.layout is not None}, "
                     f"symbols: {self.symbols is not None}, "
                     f"process_html: {self.process_html}")


    def _process_text_node(self, text: str) -> str:
        """
        Внутренний конвейер, который работает с чистым текстом.
        """
        # Шаг 1: Декодируем весь входящий текст в канонический Unicode
        # (здесь можно использовать html.unescape, но наш кодек тоже подойдет)
        processed_text = decode_to_unicode(text)
        # processed_text = text  # ВРЕМЕННО: используем текст как есть

        # Шаг 2: Применяем правила к чистому Unicode-тексту (только правила на уровне ноды)
        if self.symbols is not None:
            processed_text = self.symbols.process(processed_text)
        if self.layout is not None:
            processed_text = self.layout.process(processed_text)
        if self.hyphenation is not None:
            processed_text = self.hyphenation.hyp_in_text(processed_text)
        # ... вызовы других активных модулей правил ...

        # Финальный шаг: кодируем результат в соответствии с выбранным режимом
        return encode_from_unicode(processed_text, self.mode)

    def _walk_tree(self, node):
        """
        Рекурсивно обходит DOM-дерево, находя и обрабатывая все текстовые узлы.
        """
        # Список "детей" узла, который мы будем изменять.
        # Копируем в список, так как будем изменять его во время итерации.
        for child in list(node.children):
            if isinstance(child, NavigableString):
                # Если это текстовый узел, обрабатываем его
                # Пропускаем пустые или состоящие из пробелов узлы
                if not child.string.strip():
                    continue

                processed_node_text = self._process_text_node(child.string)
                child.replace_with((processed_node_text))
            elif child.name not in PROTECTED_HTML_TAGS:
                # Если это "обычный" html-тег, рекурсивно заходим в него
                self._walk_tree(child)

    def process(self, text: str) -> str:
        """
        Обрабатывает текст, применяя все активные правила типографики.
        Поддерживает обработку текста внутри HTML-тегов.
        """
        if not text:
            return ""
        # Если включена обработка HTML и BeautifulSoup доступен
        if self.process_html:
            # --- ЭТАП 1: Токенизация и "умная склейка" ---
            try:
                soup = BeautifulSoup(text, 'lxml')
            except Exception:
                soup = BeautifulSoup(text, 'html.parser')
            # 1.1. Создаем "токен-стрим" из текстовых узлов, которые мы будем обрабатывать.
            # soup.descendants возвращает все дочерние узлы (теги и текст) в порядке их следования.
            text_nodes = [node for node in soup.descendants
                          if isinstance(node, NavigableString)
                          # and node.strip()
                          and node.parent.name not in PROTECTED_HTML_TAGS]
            # 1.2. Создаем "супер-строку" и "карту длин"
            super_string = ""
            lengths_map = []
            for node in text_nodes:
                super_string += str(node)
                lengths_map.append(len(str(node)))

            # --- ЭТАП 2: Контекстная обработка (ПОКА ЧТО ПРОПУСКАЕМ) ---
            processed_super_string = super_string
            # Применяем правила, которым нужен полный контекст (вся супер-строка контекста, очищенная от html).
            # Важно, чтобы эти правила не меняли длину строки!!!! Иначе карта длин слетит и восстановление не получится.
            if self.quotes:
                processed_super_string = self.quotes.process(processed_super_string)
            if self.unbreakables:
                processed_super_string = self.unbreakables.process(processed_super_string)

            # --- ЭТАП 3: "Восстановление" ---
            current_pos = 0
            for i, node in enumerate(text_nodes):
                length = lengths_map[i]
                new_text_part = processed_super_string[current_pos : current_pos + length]
                node.replace_with(new_text_part) # Заменяем содержимое узла на месте
                current_pos += length

            # --- ЭТАП 4: Локальная обработка (второй проход) ---
            # Теперь, когда структура восстановлена, запускаем наш старый рекурсивный обход,
            # который применит все остальные правила к каждому текстовому узлу.
            self._walk_tree(soup)

            # --- ЭТАП 5: Финальная сборка ---
            processed_html = str(soup)
            # BeautifulSoup по умолчанию экранирует амперсанды (& -> &amp;), которые мы сгенерировали
            # в _process_text_node. Возвращаем их обратно.
            return processed_html.replace('&amp;', '&')
        else:
            # Если HTML-режим выключен, используем полный конвейер для простого текста.
             # Шаг 0: Нормализация
             processed_text = decode_to_unicode(text)
             # Шаг 1: Применяем все правила последовательно
             if self.quotes:
                 processed_text = self.quotes.process(processed_text)
             if self.unbreakables:
                 processed_text = self.unbreakables.process(processed_text)
             if self.symbols:
                 processed_text = self.symbols.process(processed_text)
             if self.layout:
                 processed_text = self.layout.process(processed_text)
             if self.hyphenation:
                 processed_text = self.hyphenation.hyp_in_text(processed_text)
             # Шаг 2: Финальное кодирование
             return encode_from_unicode(processed_text, self.mode)

