# etpgrf/comutil.py
# Общие функции для типографа etpgrf
from etpgrf.config import MODE_UNICODE, MODE_MNEMONIC, MODE_MIXED, SUPPORTED_LANGS, DEFAULT_LANGS
from etpgrf.defaults import etpgrf_settings
import os
import regex
import logging

# --- Настройки логирования ---
logger = logging.getLogger(__name__)


def parse_and_validate_mode(
    mode_input: str | None = None,
) -> str:
    """
    Обрабатывает и валидирует входной параметр mode.
    Если mode_input не предоставлен (None), используется режим по умолчанию.

    :param mode_input: Режим обработки текста. Может быть 'unicode', 'mnemonic' или 'mixed'.
    :return: Валидированный режим в нижнем регистре.
    :raises TypeError: Если mode_input имеет неожиданный тип.
    :raises ValueError: Если mode_input пуст после обработки или содержит неподдерживаемый режим.
    """
    if mode_input is None:
        # Если mode_input не предоставлен явно, используем режим по умолчанию
        _mode_input = etpgrf_settings.MODE
    else:
        _mode_input = str(mode_input).lower()

    if _mode_input not in {MODE_UNICODE, MODE_MNEMONIC, MODE_MIXED}:
        raise ValueError(
            f"etpgrf: режим '{_mode_input}' не поддерживается. Поддерживаемые режимы: {MODE_UNICODE}, {MODE_MNEMONIC}, {MODE_MIXED}"
        )

    return _mode_input


def parse_and_validate_langs(
    langs: str | list[str] | tuple[str, ...] | frozenset[str] | None = None,
) -> list[str]:
    """
    Обрабатывает и валидирует входной параметр языков.
    Если langs_input не предоставлен (None), используются языки по умолчанию
    (сначала из переменной окружения ETPGRF_DEFAULT_LANGS, затем внутренний дефолт).

    :param langs: Язык(и) для обработки. Может быть строкой (например, "ru+en"), списком, кортежем или frozenset.
    :return: Frozenset валидированных кодов языков в нижнем регистре.
    :raises TypeError: Если langs_input имеет неожиданный тип.
    :raises ValueError: Если langs_input пуст после обработки или содержит неподдерживаемые коды.
    """
    _langs = langs

    if _langs is None:
        # Если langs не предоставлен явно, будем выкручиваться и искать в разных местах
        # 1. Попытка получить языки из переменной окружения системы
        env_default_langs = os.environ.get('ETPGRF_DEFAULT_LANGS')
        if env_default_langs:
            # Нашли язык для библиотеки в переменных окружения
            _langs = env_default_langs
        else:
            # Если в переменной окружения нет, используем то, что есть в конфиге `etpgrf/config.py`
            _langs = DEFAULT_LANGS

    if isinstance(_langs, str):
        # Разделяем строку по любым небуквенным символам, приводим к нижнему регистру
        # и фильтруем пустые строки
        parsed_lang_codes_list = [lang.lower() for lang in regex.split(r'[^a-zA-Z]+', _langs) if lang]
    elif isinstance(_langs, (list, tuple, frozenset)): # frozenset тоже итерируемый
        # Приводим к строке, нижнему регистру и проверяем, что строка не пустая
        parsed_lang_codes_list = [str(lang).lower() for lang in _langs if str(lang).strip()]
    else:
        raise TypeError(
            f"etpgrf: параметр 'langs' должен быть строкой, списком, кортежем или frozenset. Получен: {type(_langs)}"
        )

    if not parsed_lang_codes_list:
        raise ValueError(
            "etpgrf: параметр 'langs' не может быть пустым или приводить к пустому списку языков после обработки."
        )

    # Валидируем языки, сохраняя порядок и удаляя дубликаты
    validated_langs = []
    seen_langs = set()
    for code in parsed_lang_codes_list:
        if code not in SUPPORTED_LANGS:
            raise ValueError(
                f"etpgrf: код языка '{code}' не поддерживается. Поддерживаемые языки: {list(SUPPORTED_LANGS)}"
            )
        if code not in seen_langs:
            validated_langs.append(code)
            seen_langs.add(code)

    if not validated_langs:
        raise ValueError("etpgrf: не предоставлено ни одного валидного кода языка.")

    return validated_langs


def is_inside_unbreakable_segment(
    word_segment: str,
    split_index: int,
    unbreakable_set: frozenset[str] | list[str] | set[str],
) -> bool:
    """
    Проверяет, находится ли позиция разбиения внутри неразрывного сегмента.

    :param word_segment: -- Сегмент слова, в котором мы ищем позицию разбиения.
    :param split_index: -- Индекс (позиция внутри сегмента), по которому мы хотим проверить разбиение.
    :param unbreakable_set: -- Набор неразрывных сегментов (например: диграфы, триграфы, акронимы...).
    :return:
    """
    segment_len = len(word_segment)
    # Проверяем, что позиция разбиения не выходит за границы сегмента
    if not (0 < split_index < segment_len):
        return False
    # Пер образуем все в верхний регистр, чтобы сравнения строк работали
    word_segment_upper = word_segment.upper()
    # unbreakable_set_upper = (unit.upper() for unit in unbreakable_set)        # <-- С помощью генератора

    # Отсортируем unbreakable_set по длине лексем (чем короче, тем больше шансов на "ранний выход")
    # и заодно превратим в list
    sorted_units = sorted(unbreakable_set, key=len)
    # sorted_units = sorted(unbreakable_set_upper, key=len)
    for unbreakable in sorted_units:
        unit_len = len(unbreakable)
        if unit_len < 2:
            continue
        # Спорно, что преобразование в верхний регистр эффективнее делать тут, но благодаря возможному
        # "раннему выходу" это может быть быстрее с помощью генератора (см. выше комментарии)
        unbreakable_upper = unbreakable.upper()
        for offset in range(1, unit_len):
            position_start_in_segment = split_index - offset
            position_end_in_segment = position_start_in_segment + unit_len
            # Убедимся, что предполагаемое положение 'unit' не выходит за границы word_segment
            if position_start_in_segment >= 0 and position_end_in_segment <= segment_len and \
                    word_segment_upper[position_start_in_segment:position_end_in_segment] == unbreakable_upper:
                # Нашли 'unbreakable', и split_index находится внутри него.
                return True
    return False
