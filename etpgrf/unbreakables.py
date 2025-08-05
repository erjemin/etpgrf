# etpgrf/unbreakables.py
# Модуль для предотвращения "висячих" предлогов, союзов и других коротких слов в начале строки.
# Он "приклеивает" такие слова к последующему слову с помощью неразрывного пробела.
# Кстати в русском тексте союзы составляют 7,61%


import regex
import logging
import html
from etpgrf.config import LANG_RU, LANG_RU_OLD, LANG_EN  # , KEY_NBSP, ALL_ENTITIES
from etpgrf.comutil import parse_and_validate_langs
from etpgrf.defaults import etpgrf_settings

# --- Наборы коротких слов для разных языков ---
# Используем frozenset для скорости и неизменяемости.
# Слова в нижнем регистре для удобства сравнения.

_RU_UNBREAKABLE_WORDS = frozenset([
    # Предлоги (только короткие... длинные, типа `ввиду`, `ввиду` и т.п., могут быть "висячими")
    'в', 'без', 'до', 'из', 'к', 'на', 'по', 'о', 'от', 'перед', 'при', 'через', 'с', 'у', 'за', 'над',
    'об', 'под', 'про', 'для', 'ко', 'со', 'без', 'то', 'во', 'из-за', 'из-под', 'как'
    # Союзы (без сложных, тип `как будто`, `как если бы`, `за то` и т.п.)
    'и', 'а', 'но', 'да', 'как',
    # Частицы
    'не', 'ни',
    # Местоимения
    'я', 'ты', 'он', 'мы', 'вы', 'им', 'их', 'ей', 'ею',
    # Устаревшие или специфичные
    'сей', 'сия', 'сие',
])

# Постпозитивные частицы, которые приклеиваются к ПРЕДЫДУЩЕМУ слову
_RU_POSTPOSITIVE_PARTICLES = frozenset([
    'ли', 'ль', 'же', 'ж', 'бы', 'б'
])

# Для дореформенной орфографии можно добавить специфичные слова, если нужно
_RU_OLD_UNBREAKABLE_WORDS = _RU_UNBREAKABLE_WORDS | frozenset([
    'і', 'безъ', 'черезъ', 'въ', 'изъ', 'къ', 'отъ', 'съ', 'надъ', 'подъ', 'объ', 'какъ',
    'сiя', 'сiе', 'сiй', 'онъ', 'тъ',
])

# Постпозитивные частицы, которые приклеиваются к ПРЕДЫДУЩЕМУ слову
_RU_OLD_POSTPOSITIVE_PARTICLES = frozenset([
    'жъ', 'бъ'
])

_EN_UNBREAKABLE_WORDS = frozenset([
    # 1-2 letter words
    'a', 'an', 'as', 'at', 'by', 'in', 'is', 'it', 'of', 'on', 'or', 'so', 'to', 'if',
    # 3-4 letter words
    'for', 'from', 'into', 'that', 'then', 'they', 'this', 'was', 'were', 'what', 'when', 'with',
    'not', 'but', 'which', 'the'
])

# --- Настройки логирования ---
logger = logging.getLogger(__name__)


# --- Класс Unbreakables (обработка неразрывных конструкций) ---
class Unbreakables:
    """
    Правила обработки коротких слов (предлогов, союзов, частиц и местоимений) для предотвращения их отрыва
    от последующих слов.
    """

    def __init__(self, langs: str | list[str] | tuple[str, ...] | frozenset[str] | None = None):
        self.langs = parse_and_validate_langs(langs)

        # Получаем символ неразрывного пробела напрямую из стандартной библиотеки
        self._nbsp_char = chr(html.entities.name2codepoint['nbsp']) # <--- ИЗМЕНИТЬ

        # --- 1. Собираем наборы слов для обработки ---
        pre_words = set()
        post_words = set()
        # Собираем слова которые должны быть приклеены
        if LANG_RU in self.langs:
            pre_words.update(_RU_UNBREAKABLE_WORDS)
            post_words.update(_RU_POSTPOSITIVE_PARTICLES)
        if LANG_RU_OLD in self.langs:
            pre_words.update(_RU_OLD_UNBREAKABLE_WORDS)
            post_words.update(_RU_OLD_POSTPOSITIVE_PARTICLES)
        if LANG_EN in self.langs:
            pre_words.update(_EN_UNBREAKABLE_WORDS)

        # Собираем единый набор слов с пост-позиционными словами (не отрываются от предыдущих слов)
        # Убедимся, что пост-позиционные слова не обрабатываются дважды
        pre_words -= post_words

        # --- 2. Компиляция паттернов с оптимизацией ---
        self._pre_pattern = None
        if pre_words:
            # Оптимизация: сортируем слова по длине от большего к меньшему
            sorted_words = sorted(list(pre_words), key=len, reverse=True)
            # Паттерн для слов, ПОСЛЕ которых нужен nbsp. regex.escape для безопасности.
            self._pre_pattern = regex.compile(r"(?i)\b(" + "|".join(map(regex.escape, sorted_words)) + r")\b\s+")

        self._post_pattern = None
        if post_words:
            # Оптимизация: сортируем слова по длине от большего к меньшему
            sorted_particles = sorted(list(post_words), key=len, reverse=True)
            # Паттерн для слов, ПЕРЕД которыми нужен nbsp.
            self._post_pattern = regex.compile(r"(?i)(\s)\b(" + "|".join(map(regex.escape, sorted_particles)) + r")\b")

        logger.debug(f"Unbreakables `__init__`. Langs: {self.langs}, "
                      f"Pre-words: {len(pre_words)}, Post-words: {len(post_words)}")


    def process(self, text: str) -> str:
        """
        Заменяет обычные пробелы вокруг коротких слов на неразрывные.
        """
        if not text:
            return text
        processed_text = text

        # 1. Обработка слов, ПОСЛЕ которых нужен неразрывный пробел ("в дом" -> "в&nbsp;дом")
        if self._pre_pattern:
            processed_text = self._pre_pattern.sub(r"\g<1>" + self._nbsp_char, processed_text)

        # 2. Обработка частиц, ПЕРЕД которыми нужен неразрывный пробел ("сказал бы" -> "сказал&nbsp;бы")
        if self._post_pattern:
            # \g<1> - это пробел, \g<2> - это частица
            processed_text = self._post_pattern.sub(self._nbsp_char + r"\g<2>", processed_text)

        return processed_text
