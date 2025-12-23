# etpgrf/hanging.py
# Модуль для расстановки висячей пунктуации.

import logging
from bs4 import BeautifulSoup, NavigableString, Tag
from .config import (
    HANGING_PUNCTUATION_LEFT_CHARS,
    HANGING_PUNCTUATION_RIGHT_CHARS,
    HANGING_PUNCTUATION_CLASSES
)

logger = logging.getLogger(__name__)


class HangingPunctuationProcessor:
    """
    Оборачивает символы висячей пунктуации в специальные теги <span> с классами.
    """

    def __init__(self, mode: str | bool | list[str] | None = None):
        """
        :param mode: Режим работы:
                     - None / False: отключено.
                     - 'left': только левая пунктуация.
                     - 'right': только правая пунктуация.
                     - 'both' / True: и левая, и правая.
                     - list[str]: список тегов (например, ['p', 'blockquote']),
                       внутри которых применять 'both'.
        """
        self.mode = mode
        self.target_tags = None
        self.active_chars = set()

        # Определяем, какие символы будем обрабатывать
        if isinstance(mode, list):
            self.target_tags = set(t.lower() for t in mode)
            # Если передан список тегов, включаем полный режим ('both') внутри них
            self.active_chars.update(HANGING_PUNCTUATION_LEFT_CHARS)
            self.active_chars.update(HANGING_PUNCTUATION_RIGHT_CHARS)
        elif mode == 'left':
            self.active_chars.update(HANGING_PUNCTUATION_LEFT_CHARS)
        elif mode == 'right':
            self.active_chars.update(HANGING_PUNCTUATION_RIGHT_CHARS)
        elif mode == 'both' or mode is True:
            self.active_chars.update(HANGING_PUNCTUATION_LEFT_CHARS)
            self.active_chars.update(HANGING_PUNCTUATION_RIGHT_CHARS)
        
        # Предварительно фильтруем карту классов, оставляя только активные символы
        self.char_to_class = {
            char: cls 
            for char, cls in HANGING_PUNCTUATION_CLASSES.items()
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
        """
        Рекурсивно обходит узлы. Если находит NavigableString с нужными символами,
        разбивает его и вставляет span'ы.
        """
        # Работаем с копией списка детей, так как будем менять структуру дерева на лету
        # (replace_with меняет дерево)
        if hasattr(node, 'children'):
            for child in list(node.children):
                if isinstance(child, NavigableString):
                    self._process_text_node(child, soup)
                elif isinstance(child, Tag):
                    # Не заходим внутрь тегов, которые мы сами же и создали (или аналогичных),
                    # чтобы избежать рекурсивного ада, хотя классы у нас специфичные.
                    self._process_node_recursive(child, soup)

    def _process_text_node(self, text_node: NavigableString, soup: BeautifulSoup):
        """
        Анализирует текстовый узел. Если в нем есть символы для висячей пунктуации,
        заменяет узел на фрагмент (список узлов), где эти символы обернуты в span.
        """
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
                if char in HANGING_PUNCTUATION_LEFT_CHARS:
                    # Левая пунктуация:
                    # 1. Начало узла
                    # 2. Перед ней пробел
                    # 3. Перед ней другой левый висячий символ (например, "((text")
                    if (i == 0 or 
                        text[i-1].isspace() or 
                        text[i-1] in HANGING_PUNCTUATION_LEFT_CHARS):
                        should_hang = True
                elif char in HANGING_PUNCTUATION_RIGHT_CHARS:
                    # Правая пунктуация:
                    # 1. Конец узла
                    # 2. После нее пробел
                    # 3. После нее другой правый висячий символ (например, "text.»")
                    if (i == text_len - 1 or 
                        text[i+1].isspace() or 
                        text[i+1] in HANGING_PUNCTUATION_RIGHT_CHARS):
                        should_hang = True
                
                if should_hang:
                    # 1. Сбрасываем накопленный буфер текста (если есть)
                    if current_text_buffer:
                        new_nodes.append(NavigableString(current_text_buffer))
                        current_text_buffer = ""
                    
                    # 2. Создаем span для висячего символа
                    span = soup.new_tag("span")
                    span['class'] = self.char_to_class[char]
                    span.string = char
                    new_nodes.append(span)
                else:
                    # Если контекст не подходит, оставляем символ как обычный текст
                    current_text_buffer += char
            else:
                # Просто накапливаем символ
                current_text_buffer += char

        # Добавляем остаток буфера
        if current_text_buffer:
            new_nodes.append(NavigableString(current_text_buffer))

        # Заменяем исходный текстовый узел на набор новых узлов.
        if new_nodes:
            first_node = new_nodes[0]
            text_node.replace_with(first_node)
            
            # Остальные вставляем последовательно после первого
            current_pos = first_node
            for next_node in new_nodes[1:]:
                current_pos.insert_after(next_node)
                current_pos = next_node
