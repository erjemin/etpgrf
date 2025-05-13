# etpgrf/defaults.py -- Настройки по умолчанию для типографа etpgrf
from etpgrf.config import LANG_RU, MODE_MIXED

class HyphenationDefaults:
    """
    Настройки по умолчанию для Hyphenator etpgrf.
    """
    MAX_UNHYPHENATED_LEN: int = 14
    MIN_TAIL_LEN: int = 3


class EtpgrfDefaultSettings:
    """
    Общие настройки по умолчанию для всех модулей типографа etpgrf.
    """
    def __init__(self):
        self.LANGS: list[str] | str = LANG_RU
        self.MODE: str = MODE_MIXED
        self.hyphenation = HyphenationDefaults()
        # self.quotes = EtpgrfQuoteDefaults()

etpgrf_settings = EtpgrfDefaultSettings()