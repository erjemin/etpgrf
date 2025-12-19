# etpgrf/sanitizer.py
# Модуль для очистки и нормализации HTML-кода перед типографикой.

import logging
from bs4 import BeautifulSoup
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
        
        # Оптимизация: заранее готовим CSS-селектор для поиска висячей пунктуации
        if self.mode == SANITIZE_ETPGRF:
            # Собираем уникальные классы
            unique_classes = sorted(list(frozenset(HANGING_PUNCTUATION_CLASSES.values())))
            # Формируем селектор вида: span.class1, span.class2, ...
            # Это позволяет использовать нативный парсер (lxml) для поиска, что намного быстрее python-лямбд.
            self._etp_selector = ", ".join(f"span.{cls}" for cls in unique_classes)
        else:
            self._etp_selector = None

        logger.debug(f"SanitizerProcessor `__init__`. Mode: {self.mode}")

    def process(self, soup: BeautifulSoup) -> BeautifulSoup | str:
        """
        Применяет правила очистки к `soup`-объекту.

        :param soup: Объект BeautifulSoup для обработки.
        :return: Обработанный объект BeautifulSoup или строка (в режиме 'html').
        """
        if self.mode == SANITIZE_ETPGRF:
            if not self._etp_selector:
                return soup

            # Используем CSS-селектор для быстрого поиска всех нужных элементов
            spans_to_clean = soup.select(self._etp_selector)

            # "Агрессивная" очистка: просто "разворачиваем" все найденные теги,
            # заменяя их своим содержимым.
            for span in spans_to_clean:
                span.unwrap()

            return soup

        elif self.mode == SANITIZE_ALL_HTML:
            # Оптимизированный подход:
            # 1. Удаляем защищенные теги (script, style и т.д.) вместе с содержимым.
            #    Используем select для поиска, так как это обычно быстрее.
            if PROTECTED_HTML_TAGS:
                # Формируем селектор: script, style, pre, ...
                protected_selector = ", ".join(PROTECTED_HTML_TAGS)
                for tag in soup.select(protected_selector):
                    tag.decompose() # Полное удаление тега из дерева

            # 2. Извлекаем чистый текст из оставшегося дерева.
            #    get_text() работает на уровне C (в lxml) и намного быстрее ручного обхода.
            return soup.get_text()

        # Если режим не задан, ничего не делаем
        return soup
