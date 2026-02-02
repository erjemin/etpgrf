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
from etpgrf.config import PROTECTED_HTML_TAGS, CHAR_PLACEHOLDER, CHAR_NODE_SEPARATOR


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

    def _hide_protected_tags(self, soup) -> list:
        """
        Находит все защищенные теги, заменяет их на плейсхолдеры и возвращает список сохраненных тегов.
        """
        protected_tags = []
        if not PROTECTED_HTML_TAGS:
            return protected_tags

        # Формируем селектор для поиска
        selector = ", ".join(PROTECTED_HTML_TAGS)
        
        # Находим все теги. Важно: find_all возвращает их в порядке появления в документе.
        # Но если мы будем заменять их на лету, структура может измениться.
        # Поэтому лучше собрать список, а потом заменить.
        tags_to_replace = soup.select(selector)
        
        for tag in tags_to_replace:
            # Сохраняем тег (он будет удален из дерева при replace_with, но объект останется в памяти)
            protected_tags.append(tag)
            # Заменяем на текстовый узел с плейсхолдером
            tag.replace_with(NavigableString(CHAR_PLACEHOLDER))
            
        return protected_tags

    def _restore_protected_tags(self, soup, protected_tags: list):
        """
        Восстанавливает защищенные теги на места плейсхолдеров.
        """
        if not protected_tags:
            return

        # Ищем все текстовые узлы, содержащие плейсхолдер
        # Используем список, так как будем менять дерево
        text_nodes_with_placeholder = [
            node for node in soup.descendants 
            if isinstance(node, NavigableString) and CHAR_PLACEHOLDER in node
        ]

        tag_index = 0
        for node in text_nodes_with_placeholder:
            text = str(node)
            # Если в узле есть плейсхолдеры, нам нужно его разбить
            if CHAR_PLACEHOLDER in text:
                parts = text.split(CHAR_PLACEHOLDER)
                
                # Создаем список новых узлов для замены
                new_nodes = []
                for i, part in enumerate(parts):
                    # Добавляем текст (если он не пустой)
                    if part:
                        new_nodes.append(NavigableString(part))
                    
                    # Если это не последняя часть, значит, здесь был плейсхолдер.
                    # Вставляем тег.
                    if i < len(parts) - 1:
                        if tag_index < len(protected_tags):
                            new_nodes.append(protected_tags[tag_index])
                            tag_index += 1
                        else:
                            logger.warning("Mismatch in protected tags count during restoration.")
                
                # Заменяем исходный узел на новые
                if new_nodes:
                    first_node = new_nodes[0]
                    node.replace_with(first_node)
                    current_pos = first_node
                    for next_node in new_nodes[1:]:
                        current_pos.insert_after(next_node)
                        current_pos = next_node
                else:
                    # Если узел состоял только из плейсхолдера и мы его заменили на тег,
                    # то new_nodes может быть пустым (если тег был один и текст пустой).
                    # Но split('') дает [''], так что parts не пустой.
                    # Логика выше должна работать.
                    pass

    def process(self, text: str) -> str:
        """
        Обрабатывает текст, применяя все активные правила типографики.
        Поддерживает обработку текста внутри HTML-тегов.
        """
        if not text:
            return ""
        # Если включена обработка HTML и BeautifulSoup доступен
        if self.process_html:
            # --- ЭТАП 1: Анализ структуры ---
            # Проверяем, есть ли в начале текста теги <html> или <body>.
            # Если есть - значит, это полноценный документ, и мы должны вернуть его целиком.
            # Если нет - значит, это фрагмент, и мы должны вернуть только содержимое body.
            is_full_document = bool(regex.search(r'^\s*<(?:!DOCTYPE|html|body)', text, regex.IGNORECASE))

            # --- ЭТАП 2: Парсинг и Санитизация ---
            try:
                soup = BeautifulSoup(text, 'lxml')
            except Exception:
                soup = BeautifulSoup(text, 'html.parser')

            if self.sanitizer:
                result = self.sanitizer.process(soup)
                # Если режим SANITIZE_ALL_HTML, то результат - это строка (чистый текст)
                if isinstance(result, str):
                    # Переключаемся на обработку обычного текста
                    text = result
                    # ВАЖНО: Мы выходим из ветки process_html и идем в ветку else,
                    # но так как мы внутри if, нам нужно явно вызвать логику для текста.
                    # Проще всего рекурсивно вызвать process с выключенным process_html,
                    # но чтобы не менять состояние объекта, просто выполним логику "else" блока здесь.
                    # Или, еще проще: присвоим text = result и пойдем в блок else? Нет, мы уже внутри if.
                    
                    # Решение: Выполняем логику обработки простого текста прямо здесь
                    return self._process_plain_text(text)
                
                # Если результат - soup, продолжаем работу с ним
                soup = result

            # --- ЭТАП 2.5: Скрытие защищенных тегов ---
            # Заменяем <code>, <script> и т.д. на плейсхолдеры, чтобы они не мешали обработке
            # и не ломали карту длин.
            protected_tags = self._hide_protected_tags(soup)

            # --- ЭТАП 3: Подготовка (токен-стрим) ---
            # 3.1. Создаем "токен-стрим" из текстовых узлов.
            # Теперь здесь только обычный текст и плейсхолдеры.
            text_nodes = [node for node in soup.descendants
                          if isinstance(node, NavigableString)
                          # and node.strip()
                          and node.parent.name not in PROTECTED_HTML_TAGS] # PROTECTED уже скрыты, но на всякий случай
            # 3.2. Создаем "супер-строку" с маркерами границ
            super_string = ""
            # lengths_map больше не нужен, так как мы используем разделители
            
            for node in text_nodes:
                # ВАЖНО: Используем node.string (Unicode), а не str(node) (HTML-encoded).
                # str(node) может вернуть экранированные символы (например, &lt; вместо <),
                # что увеличит длину строки и приведет к рассинхронизации карты длин (смещению текста).
                node_text = node.string or ""
                # Добавляем текст и разделитель
                super_string += node_text + CHAR_NODE_SEPARATOR

            # --- ЭТАП 4: Контекстная обработка ---
            processed_super_string = super_string
            # Применяем правила, которым нужен полный контекст (вся супер-строка контекста, очищенная от html).
            # Важно, чтобы эти правила не меняли длину строки!!!! Иначе карта длин слетит и восстановление не получится.
            if self.quotes:
                processed_super_string = self.quotes.process(processed_super_string)
            if self.unbreakables:
                processed_super_string = self.unbreakables.process(processed_super_string)

            # --- ЭТАП 5: Восстановление структуры ---
            # Разбиваем строку по разделителям.
            # split вернет список, где последний элемент будет пустым (из-за разделителя в конце).
            # Поэтому берем все элементы, кроме последнего.
            # Но если строка пустая, split вернет [''], и мы возьмем [].
            # Если строка 'a\uFFFF', split -> ['a', '']. Берем ['a'].
            parts = processed_super_string.split(CHAR_NODE_SEPARATOR)
            
            # Проверка на целостность: количество частей должно совпадать с количеством узлов.
            # split всегда возвращает хотя бы один элемент. Если super_string пустая, parts=[''].
            # Если super_string не пустая, parts будет иметь длину N+1 (где N - число разделителей).
            # Нам нужны первые N частей.
            
            if len(parts) > len(text_nodes):
                 parts = parts[:len(text_nodes)]
            
            # Если вдруг частей меньше (кто-то удалил разделитель), это проблема.
            # Но \uFFFF - Non-character, его сложно удалить случайно.
            
            for i, node in enumerate(text_nodes):
                if i < len(parts):
                    new_text_part = parts[i]
                    # Заменяем содержимое узла.
                    # Важно: если new_text_part содержит CHAR_PLACEHOLDER, он останется как есть
                    # и будет обработан на этапе 5.5.
                    node.replace_with(new_text_part)

            # --- ЭТАП 5.5: Восстановление защищенных тегов ---
            self._restore_protected_tags(soup, protected_tags)

            # --- ЭТАП 6: Локальная обработка (второй проход) ---
            # Теперь, когда структура восстановлена (включая защищенные теги),
            # запускаем рекурсивный обход.
            # Важно: _walk_tree пропускает PROTECTED_HTML_TAGS, так что содержимое
            # восстановленных тегов не будет обработано повторно.
            self._walk_tree(soup)

            # --- ЭТАП 7: Висячая пунктуация ---
            # Применяем после всех текстовых преобразований, но перед финальной сборкой
            if self.hanging:
                self.hanging.process(soup)

            # --- ЭТАП 8: Финальная сборка ---
            if is_full_document:
                # Если на входе был полноценный документ, возвращаем все дерево
                processed_html = str(soup)
            else:
                # Если на входе был фрагмент, возвращаем только содержимое body.
                # decode_contents() возвращает строку с содержимым тега (без самого тега).
                # Если body нет (что странно для BS), возвращаем str(soup).
                if soup.body:
                    processed_html = soup.body.decode_contents()
                else:
                    processed_html = str(soup)

            # Удаляем плейсхолдеры и разделители, если они вдруг просочились
            processed_html = processed_html.replace(CHAR_PLACEHOLDER, '').replace(CHAR_NODE_SEPARATOR, '')

            # BeautifulSoup по умолчанию экранирует амперсанды (& -> &amp;), которые мы сгенерировали
            # в _process_text_node. Возвращаем их обратно.
            return processed_html.replace('&amp;', '&')
        else:
            return self._process_plain_text(text)

    def _process_plain_text(self, text: str) -> str:
        """
        Логика обработки обычного текста (вынесена из process для переиспользования).
        """
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
