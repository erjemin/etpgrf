# etpgrf/defaults.py -- Настройки по умолчанию для типографа etpgrf
import logging
from etpgrf.config import LANG_RU, MODE_MIXED

class LoggingDefaults:
    LEVEL = logging.NOTSET
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
    # Можно добавить ещё настройки, если понадобятся:
    # FILE_PATH: str | None = None # Путь к файлу лога, если None - не пишем в файл


class HyphenationDefaults:
    """
    Настройки по умолчанию для Hyphenator etpgrf.
    """
    MAX_UNHYPHENATED_LEN: int = 14
    MIN_TAIL_LEN: int = 4           # Это значение должно быть >= 2 (чтоб не "вылетать" за индекс в английских словах)


class EtpgrfDefaultSettings:
    """
    Общие настройки по умолчанию для всех модулей типографа etpgrf.
    """
    def __init__(self):
        self.LANGS: list[str] | str = LANG_RU
        self.MODE: str = MODE_MIXED
        self.logging_settings = LoggingDefaults()
        self.hyphenation = HyphenationDefaults()
        # self.quotes = EtpgrfQuoteDefaults()

etpgrf_settings = EtpgrfDefaultSettings()