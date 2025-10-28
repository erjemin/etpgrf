"""
etpgrf - библиотека для экранной типографики текста с поддержкой HTML.

Основные возможности:
- Автоматическая расстановка переносов
- Неразрывные пробелы для союзов и предлогов
- Корректные кавычки в зависимости от языка
- Висячая пунктуация
- Очистка и обработка HTML
"""
__version__ = "0.1.0"

import etpgrf.defaults
import etpgrf.logger

from etpgrf.hyphenation import Hyphenator
from etpgrf.layout import LayoutProcessor
from etpgrf.quotes import QuotesProcessor
from etpgrf.sanitizer import SanitizerProcessor
from etpgrf.symbols import SymbolsProcessor
from etpgrf.typograph import Typographer
from etpgrf.unbreakables import Unbreakables
