# etpgrf/hanging.py
# Модуль для расстановки висячей пунктуации.

import logging
from bs4 import BeautifulSoup, NavigableString, Tag
from .config import (
    HANGING_PUNCTUATION_CHARS,
    HANGING_PUNCTUATION_LEFT_CHARS,
    HANGING_PUNCTUATION_MODE_LEFT,
    HANGING_PUNCTUATION_MODE_RIGHT,
    HANGING_PUNCTUATION_RIGHT_CHARS,
    HANGING_PUNCTUATION_SPACE_CHARS,
    HANGING_PUNCTUATION_SPACE_CLASSES,
    HANGING_PUNCTUATION_SYMBOLS_CLASSES_FLAT,
    HANGING_CANCELLATION_SP,
)

logger = logging.getLogger(__name__)


class HangingPunctuationProcessor:
    """
    Оборачивает символы висячей пунктуации в теги <span> с классами.
    """

    def __init__(self, mode: str | bool | list[str] | None = None):
        """
        :param mode: Режим работы:
                     - None / False: отключено.
                     - 'left': левая висячая пунктуация.
                     - 'right': правая висячая пунктуация.
                     - list[str]: список тегов (например, ['p', 'blockquote']),
                       внутри которых применять висячую пунктуацию в обе стороны.
                     - True эквивалентно 'left'.
        """
        self.mode = mode
        self.target_tags = None
        self.active_chars = set()
        self.space_classes = {}
        self.direction = None
        self.left_chars = HANGING_PUNCTUATION_LEFT_CHARS
        self.right_chars = HANGING_PUNCTUATION_RIGHT_CHARS
        # Сначала определяем, какие режимы и классы активны (левый, правый или оба) и подгружаем символы.

        if isinstance(mode, list):
            self.target_tags = set(t.lower() for t in mode)
            directions = (HANGING_PUNCTUATION_MODE_LEFT, HANGING_PUNCTUATION_MODE_RIGHT)
        else:
            normalized_mode = HANGING_PUNCTUATION_MODE_LEFT if mode is True else mode
            directions = (normalized_mode,) if normalized_mode in (HANGING_PUNCTUATION_MODE_LEFT, HANGING_PUNCTUATION_MODE_RIGHT) else ()
            self.direction = normalized_mode

        for direction in directions:
            self.active_chars.update(HANGING_PUNCTUATION_CHARS.get(direction, frozenset()))
            self.space_classes.update(HANGING_PUNCTUATION_SPACE_CLASSES.get(direction, {}))

        self.char_to_class = {
            char: cls
            for char, cls in HANGING_PUNCTUATION_SYMBOLS_CLASSES_FLAT.items()
            if char in self.active_chars
        }

        logger.debug(f"HangingPunctuationProcessor initialized. Mode: {mode}, Active chars count: {len(self.active_chars)}")

    def process(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Проходит по дереву soup и оборачивает висячие символы в span.
        """
        if not self.active_chars:
            return soup

        # Если задан список целевых тегов, обрабатываем только их содержимое
        if self.target_tags:
            # Находим все теги из списка
            # Используем select для поиска (например: "p, blockquote, h1")
            selector = ", ".join(self.target_tags)
            roots = soup.select(selector)
        else:
            # Иначе обрабатываем весь документ (начиная с корня)
            roots = [soup]

        for root in roots:
            self._process_node_recursive(root, soup)

        return soup

    def _process_node_recursive(self, node, soup):
        """Рекурсивно обходит дерево HTML-узлов.

        :param node: Текущий узел, внутри которого ищем висячие символы.
        :param soup: Корневой объект soup, нужный для создания новых тегов.
        :return: None — модификации происходят "на месте".
        """
        # Работаем с копией списка детей, так как будем менять структуру дерева на лету
        # (replace_with меняет дерево)
        if hasattr(node, 'children'):
            for child in list(node.children):
                if getattr(child, 'parent', None) is None:
                    # Узел уже был заменён/удалён при обработке соседей
                    continue
                if isinstance(child, NavigableString):
                    # Обрабатываем текстовые узлы отдельно согласно выбранному режиму
                    self._process_text_node(child, soup)
                elif isinstance(child, Tag):
                    if self.direction == HANGING_PUNCTUATION_MODE_LEFT:
                        first_left = self._find_first_left_char_in_node(child)
                        if first_left:
                            self._wrap_parent_space_before_child(child, first_left, soup)
                    # Не заходим внутрь тегов, которые мы сами же и создали (или аналогичных),
                    # чтобы избежать рекурсивного ада, хотя классы у нас специфичные.
                    self._process_node_recursive(child, soup)
                    if self.direction == HANGING_PUNCTUATION_MODE_RIGHT:
                        last_right = self._find_last_right_char_in_node(child)
                        if last_right:
                            self._wrap_parent_space_after_child(child, last_right, soup)

    def _process_text_node(self, text_node: NavigableString, soup: BeautifulSoup):
        """Обрабатывает текстовый узел в зависимости от направления висячей пунктуации.

        :param text_node: Текстовый узел BeautifulSoup, содержащий собранный текст.
        :param soup: Объект парсера для создания новых тегов.
        :return: None — текст заменяется на набор узлов/тегов.
        """
        if self.direction == HANGING_PUNCTUATION_MODE_LEFT:
            self._process_text_node_left_mode(text_node, soup)
            return

        if self.direction == HANGING_PUNCTUATION_MODE_RIGHT:
            self._process_text_node_right_mode(text_node, soup)
            return

        text = str(text_node)
        
        # Быстрая проверка: если в тексте вообще нет ни одного нашего символа, выходим
        if not any(char in text for char in self.active_chars):
            return

        # Если символы есть, нам нужно "разобрать" строку.
        new_nodes = []
        current_text_buffer = ""
        text_len = len(text)

        for i, char in enumerate(text):
            if char in self.char_to_class:
                should_hang = False
                
                # Проверяем контекст (пробелы или другие висячие символы вокруг)
                if char in self.left_chars:
                    if (i == 0 or 
                        text[i-1].isspace() or 
                        text[i-1] in self.left_chars):
                        should_hang = True
                elif char in self.right_chars:
                    if (i == text_len - 1 or 
                        text[i+1].isspace() or 
                        text[i+1] in self.right_chars):
                        should_hang = True
                
                if should_hang:
                    if current_text_buffer:
                        new_nodes.append(NavigableString(current_text_buffer))
                        current_text_buffer = ""
                    
                    span = soup.new_tag("span")
                    span['class'] = self.char_to_class[char]
                    span.string = char
                    new_nodes.append(span)
                else:
                    current_text_buffer += char
            else:
                current_text_buffer += char

        if current_text_buffer:
            new_nodes.append(NavigableString(current_text_buffer))

        if new_nodes:
            first_node = new_nodes[0]
            text_node.replace_with(first_node)
            
            current_pos = first_node
            for next_node in new_nodes[1:]:
                current_pos.insert_after(next_node)
                current_pos = next_node

    def _process_text_node_left_mode(self, text_node: NavigableString, soup: BeautifulSoup):
        """Реализует алгоритм обёртки для левого режима висячей пунктуации.

        Пробегает по тексту, захватывая слово и оборачивая его вместе с левой кавычкой,
        добавляя компенсационные пробелы, когда они есть.

        :param text_node: Текстовый узел, где устанавливаются span-ы.
        :param soup: Парсер для создания span-обёрток.
        :return: None — изменяется дерево DOM.
        """
        text = str(text_node)
        if not any(char in self.left_chars for char in text):
            return

        nodes: list[NavigableString | Tag] = []
        text_len = len(text)
        boundary_chars = HANGING_PUNCTUATION_SPACE_CHARS
        cancellation_chars = HANGING_CANCELLATION_SP
        last_index = 0
        i = 0

        while i < text_len:
            char = text[i]
            if char not in self.left_chars:
                # Пропускаем любые символы, которые не участвуют в левом висении
                i += 1
                continue

            prev_char = self._peek_previous_char_before_text_node(text_node, i)
            if prev_char and self._is_word_char(prev_char):
                # Если перед левым символом идёт буква/цифра/подчёркивание — это не висячий символ внутри слова
                i += 1
                continue

            if i > 0 and text[i-1] in cancellation_chars:
                # Если перед символом стоит запрещённый неразрывной пробел — пропускаем
                i += 1
                continue

            comp_bounds = self._locate_left_compensation_bounds(text, i, last_index,
                                                                boundary_chars, cancellation_chars)
            if comp_bounds:
                comp_start, comp_end = comp_bounds
                if comp_start > last_index:
                    nodes.append(NavigableString(text[last_index:comp_start]))
                space_span = soup.new_tag('span')
                space_span['class'] = self.space_classes.get(char, '')
                space_span.string = text[comp_start:comp_end]
                nodes.append(space_span)
                last_index = comp_end
            elif last_index < i:
                # Добавляем буфер текста между последней обёрткой и новой левым кавычкой
                nodes.append(NavigableString(text[last_index:i]))
                last_index = i

            span_start = last_index
            span_end = span_start
            while span_end < text_len and text[span_end] not in boundary_chars:
                span_end += 1
            if span_end == span_start:
                span_end = span_start + 1

            left_span = soup.new_tag('span')
            left_span['class'] = self.char_to_class.get(char, '')
            left_span.string = text[span_start:span_end]
            nodes.append(left_span)
            last_index = span_end
            i = span_end

        if last_index < text_len:
            nodes.append(NavigableString(text[last_index:]))

        if nodes:
            first = nodes[0]
            text_node.replace_with(first)
            current = first
            for part in nodes[1:]:
                current.insert_after(part)
                current = part

    def _locate_left_compensation_bounds(self, text: str, left_idx: int, last_idx: int,
                                          boundary_chars: frozenset[str], cancellation_chars: frozenset[str]) -> tuple[int, int] | None:
        """Находит диапазон (слово + пробел), который нужно обернуть перед левым символом.

        :param text: Строка, из которой извлекаются границы.
        :param left_idx: Индекс левой кавычки.
        :param last_idx: Последний обработанный индекс — не повторяем участки.
        :param boundary_chars: Набор символов, разрешённых для разрывов.
        :param cancellation_chars: Символы, отменяющие висячие привязки.
        :return: Кортеж (start, end) или None, если приращение не нужно.
        """
        if left_idx == 0:
            return None
        prev_idx = left_idx - 1
        prev_char = text[prev_idx]
        if prev_char not in boundary_chars or prev_char in cancellation_chars:
            return None

        # Перемещаемся назад по строке, чтобы найти цепочку пробелов перед словом
        space_end = prev_idx
        while space_end > last_idx and text[space_end - 1] in boundary_chars:
            space_end -= 1

        start = space_end
        while start > last_idx and text[start - 1] not in boundary_chars:
            start -= 1

        return (start, left_idx) if start < left_idx else None

    def _find_first_left_char_in_node(self, node: Tag) -> str | None:
        """Ищет первый символ левого режима во вложенном поддереве.

        :param node: Тег, внутри которого итерируем по потомкам.
        :return: Символ из `left_chars` или None.
        """
        for descendant in node.descendants:
            if isinstance(descendant, NavigableString):
                for char in str(descendant):
                    if char.isspace():
                        continue
                    if char in self.left_chars:
                        return char
                    return None
        return None

    def _wrap_parent_space_before_child(self, child: Tag, first_left_char: str, soup: BeautifulSoup) -> bool:
        """Оборачивает слово + пробел перед дочерним узлом у родителя.

        :param child: Дочерний тег, который начал с висячего символа.
        :param first_left_char: Символ, наложивший необходимость обёртки.
        :param soup: Объект парсера для span-ов.
        :return: True, если обёртка добавлена; False — иначе.
        """
        prev_text_node = self._find_previous_navigable_text(child)
        if not prev_text_node:
            return False

        fragment = self._extract_trailing_compensation_fragment(str(prev_text_node))
        if not fragment:
            return False

        text_start, text_end = fragment
        substring = str(prev_text_node)[text_start:text_end]
        head = str(prev_text_node)[:text_start]
        css_class = self.space_classes.get(first_left_char)
        if not css_class or not substring:
            return False

        span = soup.new_tag('span')
        span['class'] = css_class
        span.string = substring

        new_nodes: list[NavigableString | Tag] = []
        if head:
            new_nodes.append(NavigableString(head))
        new_nodes.append(span)

        self._replace_text_node(prev_text_node, new_nodes)
        return True

    def _extract_trailing_compensation_fragment(self, text: str) -> tuple[int, int] | None:
        """Извлекает диапазон слова с последним пробелом перед дочерним узлом.

        :param text: Текущий текст узла, последний символ которого — потенциальный пробел.
        :return: Кортеж (start, end) или None, если для компенсации нет подходящего фрагмента.
        """
        if not text:
            return None
        boundary_chars = HANGING_PUNCTUATION_SPACE_CHARS
        end = len(text)
        if text[end - 1] not in boundary_chars:
            return None

        start = end
        while start > 0 and text[start - 1] in boundary_chars:
            # Отступаем до конца последовательности пробельных символов
            start -= 1

        word_start = start
        while word_start > 0 and text[word_start - 1] not in boundary_chars:
            # Продолжаем вверх до начала последнего слова перед пробелами
            word_start -= 1

        return (word_start, end) if word_start < end else None

    def _find_previous_navigable_text(self, child: Tag) -> NavigableString | None:
        """Возвращает предыдущий текстовый узел, если он содержит непустой текст."""
        prev = child.previous_sibling
        while prev:
            if isinstance(prev, NavigableString) and prev.strip():
                return prev
            prev = prev.previous_sibling
        return None

    def _replace_text_node(self, old_node: NavigableString, new_nodes: list[NavigableString | Tag]) -> None:
        """Заменяет текстовый узел на последовательность новых узлов."""
        if not new_nodes:
            old_node.extract()
            return
        first = new_nodes[0]
        old_node.replace_with(first)
        current = first
        for node in new_nodes[1:]:
            current.insert_after(node)
            current = node

    def _find_last_right_char_in_node(self, node: Tag) -> str | None:
        """Ищет последний символ правого режима во вложенном поддереве."""
        last_char = None
        for descendant in node.descendants:
            if isinstance(descendant, NavigableString):
                for char in str(descendant):
                    if char in self.right_chars:
                        last_char = char
        return last_char

    def _wrap_parent_space_after_child(self, child: Tag, last_right_char: str, soup: BeautifulSoup) -> bool:
        """Оборачивает пробел после дочернего узла у родителя."""
        next_text_node = self._find_next_navigable_text(child)
        if not next_text_node:
            return False

        fragment = self._extract_leading_compensation_fragment(str(next_text_node), 0, HANGING_PUNCTUATION_SPACE_CHARS)
        if not fragment:
            return False

        text_start, text_end = fragment
        substring = str(next_text_node)[text_start:text_end]
        tail = str(next_text_node)[text_end:]
        css_class = self.space_classes.get(last_right_char)
        if not css_class or not substring:
            return False

        span = soup.new_tag('span')
        span['class'] = css_class
        span.string = substring

        new_nodes: list[NavigableString | Tag] = [span]
        if tail:
            new_nodes.append(NavigableString(tail))

        self._replace_text_node(next_text_node, new_nodes)
        # Если после обёртки остался текстовый хвост, догоним его обработкой правого режима.
        if self.direction == HANGING_PUNCTUATION_MODE_RIGHT and new_nodes and isinstance(new_nodes[-1], NavigableString):
            self._process_text_node(new_nodes[-1], soup)
        return True

    def _extract_leading_compensation_fragment(self, text: str, start_idx: int,
                                               boundary_chars: frozenset[str]) -> tuple[int, int] | None:
        """Извлекает диапазон пробелов, начинающийся с заданного индекса."""
        if start_idx >= len(text) or text[start_idx] not in boundary_chars:
            return None

        end = start_idx
        while end < len(text) and text[end] in boundary_chars:
            end += 1

        return (start_idx, end) if end > start_idx else None

    def _find_next_navigable_text(self, child: Tag) -> NavigableString | None:
        """Возвращает следующий текстовый узел, если он содержит непустой текст."""
        next = child.next_sibling
        while next:
            if isinstance(next, NavigableString) and next.strip():
                return next
            next = next.next_sibling
        return None


    def _process_text_node_right_mode(self, text_node: NavigableString, soup: BeautifulSoup):
        """Аналогичный левому алгоритм, но в правом направлении.

        :param text_node: Текстовый узел, содержащий возможную правую пунктуацию.
        :param soup: Парсер для создания тегов.
        :return: None.
        """
        text = str(text_node)
        if not any(char in self.right_chars for char in text):
            return

        nodes: list[NavigableString | Tag] = []
        text_len = len(text)
        boundary_chars = HANGING_PUNCTUATION_SPACE_CHARS
        cancellation_chars = HANGING_CANCELLATION_SP
        last_index = 0
        i = 0
        right_spans: list[tuple[Tag, str]] = []

        while i < text_len:
            char = text[i]
            if char not in self.right_chars:
                # Пропускаем нецелевые символы
                i += 1
                continue

            if i > 0 and text[i-1] in cancellation_chars:
                # Не трогаем коль символ окружён запретными символами
                i += 1
                continue

            prev_char = self._peek_previous_char_before_text_node(text_node, i)
            if prev_char in cancellation_chars:
                # Учёт запретных символов даже если они находятся в соседнем узле слева от текущей позиции.
                i += 1
                continue

            next_char = self._peek_next_char_after_text_node(text_node, i)
            if next_char in cancellation_chars:
                # Пропускаем висячий символ, если сразу после него идёт запретный символ в любом соседнем узле
                i += 1
                continue

            if self._is_word_char(next_char):
                # Не оборачиваем символы внутри слов/идентификаторов и цифр
                i += 1
                continue

            # Находим диапазон слова, которое должно соединиться с текущей правой пунктуацией.
            comp_bounds = self._locate_right_compensation_bounds(text, i, last_index, boundary_chars)
            if not comp_bounds:
                # Нет слова в текущем узле (граница узла или символ стоит первым) — оборачиваем сам символ
                if i > last_index:
                    nodes.append(NavigableString(text[last_index:i]))

                solo_span = soup.new_tag('span')
                solo_span['class'] = self.char_to_class.get(char, '')
                solo_span.string = char
                nodes.append(solo_span)
                right_spans.append((solo_span, char))
                last_index = i + 1

                boundary_fragment = self._extract_leading_compensation_fragment(text, last_index, boundary_chars)
                if boundary_fragment:
                    space_start, space_end = boundary_fragment
                    space_span = soup.new_tag('span')
                    space_span['class'] = self.space_classes.get(char, '')
                    space_span.string = text[space_start:space_end]
                    nodes.append(space_span)
                    last_index = space_end
                    i = space_end
                else:
                    i = last_index
                continue

            span_start, span_mid, right_idx = comp_bounds
            if span_start > last_index and text[span_start - 1] in self.left_chars:
                # Захватываем прилегающую слева левую пунктуацию вместе со словом
                span_start -= 1

            if span_start > last_index:
                # Вставляем текст между предыдущим фрагментом и текущим словом, чтобы ничего не потерять.
                nodes.append(NavigableString(text[last_index:span_start]))

            right_span = soup.new_tag('span')
            right_span['class'] = self.char_to_class.get(char, '')
            # Объединяем слово перед правым символом и сам символ без промежуточных пробелов
            right_span.string = text[span_start:span_mid] + text[right_idx:right_idx + 1]
            nodes.append(right_span)
            right_spans.append((right_span, char))
            last_index = right_idx + 1

            # После символа оборачиваем пробелы-компенсаторы в отдельные span'ы
            boundary_fragment = self._extract_leading_compensation_fragment(text, last_index, boundary_chars)
            if boundary_fragment:
                space_start, space_end = boundary_fragment
                space_span = soup.new_tag('span')
                space_span['class'] = self.space_classes.get(char, '')
                space_span.string = text[space_start:space_end]
                nodes.append(space_span)
                last_index = space_end
                i = space_end
            else:
                # Продолжаем сканирование сразу после обработанного правого символа.
                i = last_index

        if last_index < text_len:
            nodes.append(NavigableString(text[last_index:]))

        if nodes:
            first = nodes[0]
            text_node.replace_with(first)
            current = first
            for part in nodes[1:]:
                current.insert_after(part)
                current = part
            for span_node, span_char in right_spans:
                self._wrap_parent_space_after_child(span_node, span_char, soup)

    def _peek_next_char_after_text_node(self, text_node: NavigableString, idx: int) -> str | None:
        """Ищет следующий символ текста, переходя через границы узлов."""
        node = text_node
        offset = idx + 1
        while node:
            if isinstance(node, NavigableString):
                text = str(node)
                if offset < len(text):
                    return text[offset]
                offset = 0
            node = node.next_element
        return None

    def _peek_previous_char_before_text_node(self, text_node: NavigableString, idx: int) -> str | None:
        """Ищет предыдущий символ текста перед текущим индексом, переходя между узлами."""
        if idx > 0:
            return str(text_node)[idx - 1]

        node = text_node.previous_element
        while node:
            if isinstance(node, NavigableString):
                text = str(node)
                if text:
                    return text[-1]
            node = node.previous_element
        return None

    def _is_word_char(self, char: str | None) -> bool:
        """Возвращает True, если браузер не может разорвать строку именно по этому символу."""
        return bool(char) and char not in HANGING_PUNCTUATION_SPACE_CHARS

    def _locate_right_compensation_bounds(self, text: str, right_idx: int, last_idx: int,
                                           boundary_chars: frozenset[str]) -> tuple[int, int, int] | None:
        """Находит пределы слова перед правым символом и сам символ без учета пробелов.

        :param text: Строка, из которой извлекаются границы.
        :param right_idx: Индекс правого символа (например, '»').
        :param last_idx: Последний обработанный индекс — чтобы не перекрывать уже взятые фрагменты.
        :param boundary_chars: Набор символов, разрешённых для разделения слов.
        :return: Кортеж (start_of_word, boundary_start, right_idx) или None, если нет подходящего слова.
        """
        if right_idx <= last_idx:
            return None

        prev_idx = right_idx - 1
        # Отбрасываем разделители между словом и символом, чтобы добраться до последнего слова.
        while prev_idx >= last_idx and text[prev_idx] in boundary_chars:
            prev_idx -= 1

        if prev_idx < last_idx:
            return None

        word_end = prev_idx + 1
        word_start = word_end
        # Поднимаемся к началу слова, чтобы взять все символы перед правым знаком.
        stopper = boundary_chars | (self.right_chars - {text[right_idx]})
        while word_start > last_idx and text[word_start - 1] not in stopper:
            word_start -= 1

        # Разрешаем захватить ведущий левый символ, если он стоит вплотную к слову.
        while word_start > last_idx and text[word_start - 1] in self.left_chars:
            word_start -= 1

        if word_start == word_end:
            # Если перед символом нет слова, ничего оборачивать не нужно.
            return None

        return (word_start, word_end, right_idx)
