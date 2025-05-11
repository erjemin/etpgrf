from etpgrf.config import UTF, MNEMO_CODE
from etpgrf.comutil import parse_and_validate_langs
from etpgrf.hyphenation import Hyphenator


# --- Основной класс Typographer ---
class Typographer:
    def __init__(self,
                 langs: str | list[str] | tuple[str, ...] | frozenset[str] = 'ru',
                 code_out: str = 'mnemo',
                 hyphenation_rule: Hyphenator | None = None,  # Перенос слов и параметры расстановки переносов
                 # glue_prepositions_rule: GluePrepositionsRule | None = None, # Для других правил
                 # ... другие модули правил ...
                 ):

        # --- Обработка и валидация параметра langs ---
        self.langs: frozenset[str] = parse_and_validate_langs(langs)

        # --- Обработка и валидация параметра code_out ---
        if code_out not in MNEMO_CODE | UTF:
            raise ValueError(f"etpgrf: code_out '{code_out}' is not supported. Supported codes: {MNEMO_CODE | UTF}")

        # Сохраняем переданные модули правил
        self.hyphenation_rule = hyphenation_rule

        # TODO: вынести все соответствия UTF ⇄ MNEMO_CODE в отдельный класс
        # self.hyphen_char = "­" if code_out in UTF else "&shy;" # Мягкий перенос по умолчанию

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
    #     return "\u00A0" if self.code_out in UTF else "&nbsp;"

