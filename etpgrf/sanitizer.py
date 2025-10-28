# etpgrf/sanitizer.py
# Модуль для очистки и нормализации HTML-кода перед типографикой.

import logging
from bs4 import BeautifulSoup, NavigableString
from .config import (SANITIZE_ALL_HTML, SANITIZE_ETPGRF, SANITIZE_NONE,
                     HANGING_PUNCTUATION_CLASSES, PROTECTED_HTML_TAGS)

logger = logging.getLogger(__name__)


class SanitizerProcessor:
    """
    Выполняет очистку HTML-кода в соответствии с заданным режимом.
    """

    def __init__(self, mode: str | bool | None = SANITIZE_NONE):
        """
        :param mode: Режим очистки:
                     - 'etp' (SANITIZE_ETPGRF): удаляет только разметку висячей пунктуации.
                     - 'html' (SANITIZE_ALL_HTML): удаляет все HTML-теги.
                     - None или False: ничего не делает.
        """
        if mode is False:
            mode = SANITIZE_NONE
        self.mode = mode
        self._etp_classes_to_clean = frozenset(HANGING_PUNCTUATION_CLASSES.values())

        logger.debug(f"SanitizerProcessor `__init__`. Mode: {self.mode}")

    def process(self, soup: BeautifulSoup) -> BeautifulSoup | str:
        """
        Применяет правила очистки к `soup`-объекту.

        :param soup: Объект BeautifulSoup для обработки.
        :return: Обработанный объект BeautifulSoup или строка (в режиме 'html').
        """
        if self.mode == SANITIZE_ETPGRF:
            # Находим все span'ы, у которых есть <span> с хотя бы одним из наших классов висячей пунктуации
            spans_to_clean = soup.find_all(
                name='span',
                class_=lambda c: c and any(etp_class in c.split() for etp_class in self._etp_classes_to_clean)
            )

            # "Агрессивная" очистка: просто "разворачиваем" все найденные теги,
            # заменяя их своим содержимым.
            for span in spans_to_clean:
                span.unwrap()

            return soup

        elif self.mode == SANITIZE_ALL_HTML:
            # Возвращаем только текст, удаляя все теги
            # При этом уважаем защищенные теги, не извлекая текст из них.
            text_parts = [
                str(node) for node in soup.descendants
                if isinstance(node, NavigableString) and node.parent.name not in PROTECTED_HTML_TAGS
            ]
            return "".join(text_parts)

        # Если режим не задан, ничего не делаем
        return soup