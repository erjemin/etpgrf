"""
Typography - библиотека для экранной типографики текста с поддержкой HTML.

Основные возможности:
- Автоматическая расстановка переносов
- Неразрывные пробелы для союзов и предлогов
- Корректные кавычки в зависимости от языка
- Висячая пунктуация
- Очистка и обработка HTML
"""
__version__ = "0.1.0"

from etpgrf.typograph import Typographer
from etpgrf.hyphenation import Hyphenator
import etpgrf.config