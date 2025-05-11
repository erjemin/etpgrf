from etpgrf.config import DEFAULT_MODE, DEFAULT_LANGS
from etpgrf.comutil import parce_and_validate_mode, parse_and_validate_langs
from etpgrf.hyphenation import Hyphenator


# --- Основной класс Typographer ---
class Typographer:
    def __init__(self,
                 langs: str | list[str] | tuple[str, ...] | frozenset[str] = DEFAULT_LANGS,
                 mode: str = DEFAULT_MODE,
                 hyphenation_rule: Hyphenator | None = None,  # Перенос слов и параметры расстановки переносов
                 # glue_prepositions_rule: GluePrepositionsRule | None = None, # Для других правил
                 # ... другие модули правил ...
                 ):

        # --- Обработка и валидация параметра langs ---
        self.langs: frozenset[str] = parse_and_validate_langs(langs)

        # --- Обработка и валидация параметра mode ---
        self.mode: str = parce_and_validate_mode(mode)

        # Сохраняем переданные модули правил
        self.hyphenation_rule = hyphenation_rule

    # Конвейер для обработки текста
    def process(self, text: str) -> str:
        processed_text = text
        if self.hyphenation_rule:
            # Передаем активные языки и символ переноса, если модуль Hyphenator
            # не получает их в своем __init__ напрямую от пользователя,
            # а конструируется с настройками по умолчанию, а потом конфигурируется.
            # В нашем примере Hyphenator уже получает их в __init__.
            processed_text = self.hyphenation_rule.hyp_in_text(processed_text)

        # if self.glue_prepositions_rule:
        #     processed_text = self.glue_prepositions_rule.hyp_in_text(processed_text, non_breaking_space_char=self._get_nbsp())

        # ... вызовы других активных модулей правил ...
        return processed_text

    # def _get_nbsp(self): # Пример получения неразрывного пробела
    #     return "\u00A0" if self.mode in UTF else "&nbsp;"

