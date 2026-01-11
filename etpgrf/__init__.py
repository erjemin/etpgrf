"""
etpgrf - библиотека для экранной типографики текста с поддержкой HTML.

Основные возможности:
- Автоматическая расстановка переносов
- Неразрывные пробелы для союзов и предлогов
- Корректные кавычки в зависимости от языка
- Висячая пунктуация
- Очистка и обработка HTML
"""
__version__ = "0.1.3"
__author__ = "Sergei Erjemin"
__email__ = "erjemin@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2025 Sergei Erjemin"

import etpgrf.defaults
import etpgrf.logger

from etpgrf.hyphenation import Hyphenator
from etpgrf.layout import LayoutProcessor
from etpgrf.quotes import QuotesProcessor
from etpgrf.sanitizer import SanitizerProcessor
from etpgrf.symbols import SymbolsProcessor
from etpgrf.typograph import Typographer
from etpgrf.unbreakables import Unbreakables
