# etpgrf/logging_settings.py
import logging
from etpgrf.defaults import etpgrf_settings             # Импортируем наш объект настроек по умолчанию

# --- Корневой логгер для всей библиотеки etpgrf ---
# Имя логгера "etpgrf" позволит пользователям настраивать
# логирование для всех частей библиотеки.
# Например, logging.getLogger("etpgrf").setLevel(logging.DEBUG)
# или logging.getLogger("etpgrf.hyphenation").setLevel(logging.INFO)
_etpgrf_init_logger = logging.getLogger("etpgrf")


# --- Настройка корневого логгера ---
def setup_library_logging():
    """
    Настраивает корневой логгер для библиотеки etpgrf.
    Эту функцию следует вызывать один раз (например, при импорте
    основного модуля библиотеки или при первом обращении к логгеру).
    """
    # Проверяем инициализацию хандлеров логера, чтобы случайно не добавлять хендлеры многократно
    if not _etpgrf_init_logger.hasHandlers():
        log_level_to_set = logging.WARNING      # Значение по умолчанию
        # самый мощный формат, который мы можем использовать
        log_format_to_set = '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
        # обычно достаточно:
        # log_format_to_set = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'      # Формат по умолчанию

        fin_message: str | None = None
        if hasattr(etpgrf_settings, 'logging_settings'):
            if hasattr(etpgrf_settings.logging_settings, 'LEVEL'):
                log_level_to_set = etpgrf_settings.logging_settings.LEVEL
            if hasattr(etpgrf_settings.logging_settings, 'FORMAT') and etpgrf_settings.logging_settings.FORMAT:
                log_format_to_set = etpgrf_settings.logging_settings.FORMAT
        else:
            # Этого не должно происходить, если defaults.py настроен правильно
            fin_message= "ПРЕДУПРЕЖДЕНИЕ: etpgrf_settings.logging_settings не найдены при начальной настройке логгера."

        _etpgrf_init_logger.setLevel(log_level_to_set)      # Устанавливаем уровень логирования
        console_handler = logging.StreamHandler()           # Создаем хендлер вывода в консоль
        console_handler.setLevel(log_level_to_set)          # Уровень для хендлера тоже
        formatter = logging.Formatter(log_format_to_set)    # Создаем форматтер для вывода
        console_handler.setFormatter(formatter)             # Устанавливаем форматтер для хендлера
        _etpgrf_init_logger.addHandler(console_handler)     # Добавляем хендлер в логгер
        if fin_message is not None:
            # Если есть сообщение об отсутствии настроек в `etpgrf_settings`, выводим его
            _etpgrf_init_logger.warning(fin_message)
        _etpgrf_init_logger.debug(f"Корневой логгер 'etpgrf' инициализирован."
                                  f" Уровень: {logging.getLevelName(_etpgrf_init_logger.getEffectiveLevel())}")


# --- Динамическое изменение уровня логирования ---
def update_etpgrf_log_level_from_settings():
    """
    Обновляет уровень логирования для корневого логгера `etpgrf` и его
    обработчиков, читая значение из `etpgrf_settings.logging_settings.LEVEL`.
    """
    # Проверяем, что настройки логирования и уровень существуют в `defaults.etpgrf_settings`
    if not hasattr(etpgrf_settings, 'logging_settings') or \
       not hasattr(etpgrf_settings.logging_settings, 'LEVEL'):
        _etpgrf_init_logger.warning("Невозможно обновить уровень логгера: `etpgrf_settings.logging_settings.LEVEL`"
                                    " не найден.")
        return

    new_level = etpgrf_settings.logging_settings.LEVEL
    _etpgrf_init_logger.setLevel(new_level)
    for handler in _etpgrf_init_logger.handlers:
        handler.setLevel(new_level)     # Устанавливаем уровень для каждого хендлера

    _etpgrf_init_logger.info(f"Уровень логирования `etpgrf` динамически обновлен на:"
                             f" {logging.getLevelName(_etpgrf_init_logger.getEffectiveLevel())}")


# --- Динамическое изменение формата логирования ---
def update_etpgrf_log_format_from_settings():
    """
    Обновляет формат логирования для обработчиков корневого логгера etpgrf,
    читая значение из etpgrf_settings.logging_settings.FORMAT.
    """
    if not hasattr(etpgrf_settings, 'logging_settings') or \
       not hasattr(etpgrf_settings.logging_settings, 'FORMAT') or \
       not etpgrf_settings.logging_settings.FORMAT:
        _etpgrf_init_logger.warning("Невозможно обновить формат логгера: `etpgrf_settings.logging_settings.FORMAT`"
                                    " не найден или пуст.")
        return

    new_format_string = etpgrf_settings.logging_settings.FORMAT
    new_formatter = logging.Formatter(new_format_string)

    for handler in _etpgrf_init_logger.handlers:
        handler.setFormatter(new_formatter) # Применяем новый форматтер к каждому хендлеру

    _etpgrf_init_logger.info(f"Формат логирования для 'etpgrf' динамически обновлен на: '{new_format_string}'")


# --- Инициализация логгера при первом импорте ---
setup_library_logging()


# --- Предоставление логгеров для модулей ---
def get_logger(name: str) -> logging.Logger:
    """
    Возвращает логгер для указанного имени.
    Обычно используется как logging.getLogger(__name__) в модулях.
    Имя будет дочерним по отношению к "etpgrf", например, "etpgrf.hyphenation".
    """
    # Убедимся, что имя логгера начинается с "etpgrf." для правильной иерархии,
    # если только это не сам корневой логгер.
    if not name.startswith("etpgrf") and name != "etpgrf":
         # Это может быть __name__ из модуля верхнего уровня, использующего библиотеку. В этом случае мы не хотим
         # делать его дочерним от "etpgrf" насильно. Просто вернем логгер с именем...
         # Либо можно настроить, что все логгеры, получаемые через эту функцию, должны быть частью иерархии "etpgrf"...
         # Для простоты оставим так:
         pass       # logging_settings = logging.getLogger(name)
    # Более правильный подход для модулей ВНУТРИ библиотеки etpgrf: они должны вызывать `logging.getLogger(__name__)`
    # напрямую. Тогда эта функция `get_logger()` может быть и не нужна, если модули ничего не делают кроме:
    #   import logging
    #   logging_settings = logging.getLogger(__name__)
    #
    # Однако, если нужно централизованно получать логгеры, можно сделать, чтобы `get_logger()` всегда возвращал
    # дочерний логгер:
    #   if not name.startswith("etpgrf."):
    #        name = f"etpgrf.{name}"
    return logging.getLogger(name)

