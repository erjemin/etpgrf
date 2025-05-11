from etpgrf.comutil import parce_and_validate_mode, parse_and_validate_langs
from etpgrf.hyphenation import Hyphenator
import copy


# --- Основной класс Typographer ---
class Typographer:
    def __init__(self,
                 langs: str | list[str] | tuple[str, ...] | frozenset[str] | None = None,
                 mode: str | None = None,
                 hyphenation_rule: Hyphenator | None = None,  # Перенос слов и параметры расстановки переносов
                 # glue_prepositions_rule: GluePrepositionsRule | None = None, # Для других правил
                 # ... другие модули правил ...
                 ):

        # --- Обработка и валидация параметра langs ---
        self.langs: frozenset[str] = parse_and_validate_langs(langs)

        # --- Обработка и валидация параметра mode ---
        self.mode: str = parce_and_validate_mode(mode)

        # Сохраняем переданные модули правил
        if hyphenation_rule is not None:
            # 1. Создаем поверхностную копию объекта hyphenation_rule.
            self.hyphenation_rule = copy.copy(hyphenation_rule)
            # 2. Наследуем режим типографа, если он не задан в hyphenation_rule.
            if self.hyphenation_rule.mode is None:
                self.hyphenation_rule.mode = self.mode
            # 2. Наследуем языки от типографа, если они не заданы в hyphenation_rule.
            if self.hyphenation_rule.langs is None:
                self.hyphenation_rule.langs = self.langs
        else:
            self.hyphenation_rule = hyphenation_rule


    # Конвейер для обработки текста
    def process(self, text: str) -> str:
        processed_text = text
        if self.hyphenation_rule:
            # Обработчик переносов (Hyphenator) активен. Обрабатываем текст...
            processed_text = self.hyphenation_rule.hyp_in_text(processed_text)

        # if self.glue_prepositions_rule:
        #     processed_text = self.glue_prepositions_rule.hyp_in_text(processed_text, non_breaking_space_char=self._get_nbsp())

        # ... вызовы других активных модулей правил ...
        return processed_text

    # def _get_nbsp(self): # Пример получения неразрывного пробела
    #     return "\u00A0" if self.mode in UTF else "&nbsp;"

