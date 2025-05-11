from etpgrf.config import DEFAULT_LANGS, SUPPORTED_LANGS
import os
import regex
# Общие функции для типографа etpgrf

def parse_and_validate_langs(
    langs_input: str | list[str] | tuple[str, ...] | frozenset[str] | None = None,
) -> frozenset[str]:
    """
    Обрабатывает и валидирует входной параметр языков.
    Если langs_input не предоставлен (None), используются языки по умолчанию
    (сначала из переменной окружения ETPGRF_DEFAULT_LANGS, затем внутренний дефолт).

    :param langs_input: Язык(и) для обработки. Может быть строкой (например, "ru+en"),
                        списком, кортежем или frozenset.
    :return: Frozenset валидированных кодов языков в нижнем регистре.
    :raises TypeError: Если langs_input имеет неожиданный тип.
    :raises ValueError: Если langs_input пуст после обработки или содержит неподдерживаемые коды.
    """
    _langs_input = langs_input

    if _langs_input is None:
        # Если langs_input не предоставлен явно, будем выкручиваться и искать в разных местах
        # 1. Попытка получить языки из переменной окружения системы
        env_default_langs = os.environ.get('ETPGRF_DEFAULT_LANGS')
        if env_default_langs:
            # Нашли язык для библиотеки в переменных окружения
            _langs_input = env_default_langs
            # print(f"Using ETPGRF_DEFAULT_LANGS from environment: {env_default_langs}") # Для отладки
        else:
            # Если в переменной окружения нет, используем то что есть в конфиге `etpgrf/config.py`
            _langs_input = DEFAULT_LANGS
            # print(f"Using library internal default langs: {DEFAULT_LANGS}") # Для отладки

    if isinstance(_langs_input, str):
        # Разделяем строку по любым небуквенным символам, приводим к нижнему регистру
        # и фильтруем пустые строки
        parsed_lang_codes_list = [lang.lower() for lang in regex.split(r'[^a-zA-Z]+', _langs_input) if lang]
    elif isinstance(_langs_input, (list, tuple, frozenset)): # frozenset тоже итерируемый
        # Приводим к строке, нижнему регистру и проверяем, что строка не пустая
        parsed_lang_codes_list = [str(lang).lower() for lang in _langs_input if str(lang).strip()]
    else:
        raise TypeError(
            f"etpgrf: параметр 'langs' должен быть строкой, списком, кортежем или frozenset. Получен: {type(_langs_input)}"
        )

    if not parsed_lang_codes_list:
        raise ValueError(
            "etpgrf: параметр 'langs' не может быть пустым или приводить к пустому списку языков после обработки."
        )

    validated_langs_set = set()
    for code in parsed_lang_codes_list:
        if code not in SUPPORTED_LANGS:
            raise ValueError(
                f"etpgrf: код языка '{code}' не поддерживается. Поддерживаемые языки: {list(SUPPORTED_LANGS)}"
            )
        validated_langs_set.add(code)

    # Эта проверка на случай, если parsed_lang_codes_list был не пуст, но все коды оказались невалидными
    # (хотя предыдущее исключение должно было сработать раньше для каждого невалидного кода).
    if not validated_langs_set:
        raise ValueError("etpgrf: не предоставлено ни одного валидного кода языка.")

    return frozenset(validated_langs_set)