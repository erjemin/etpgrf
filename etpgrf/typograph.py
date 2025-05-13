from etpgrf.comutil import parse_and_validate_mode, parse_and_validate_langs

from etpgrf.hyphenation import Hyphenator


# --- Основной класс Typographer ---
class Typographer:
    def __init__(self,
                 langs: str | list[str] | tuple[str, ...] | frozenset[str] | None = None,
                 mode: str | None = None,
                 hyphenation: Hyphenator | bool | None = True,  # Перенос слов и параметры расстановки переносов
                 # glue_prepositions_rule: GluePrepositionsRule | None = None, # Для других правил
                 # ... другие модули правил ...
                 ):

        # A. --- Обработка и валидация параметра langs ---
        self.langs: frozenset[str] = parse_and_validate_langs(langs)
        # B. --- Обработка и валидация параметра mode ---
        self.mode: str = parse_and_validate_mode(mode)
        print("Typographer: langs:", self.langs, "// mode:", self.mode)  # Для отладки
        # C. --- Инициализация правила переноса ---
        #    Предпосылка: если вызвали типограф, значит, мы хотим обрабатывать текст и переносы тоже нужно расставлять.
        #    А для специальных случаев, когда переносы не нужны, пусть не ленятся и делают `hyphenation=False`.
        self.hyphenation: Hyphenator | None = None
        if hyphenation is True or hyphenation is None:
            # 1. Создаем новый объект Hyphenator с заданными языками и режимом, а все остальное по умолчанию
            self.hyphenation = Hyphenator(langs=self.langs, mode=self.mode)
        elif isinstance(hyphenation, Hyphenator):
            # 2. Если hyphenation - это объект Hyphenator, то просто сохраняем его (и используем его langs и mode)
            self.hyphenation = hyphenation
        elif hyphenation is False:
            # 3. Если hyphenation - False, то правило переноса выключено.
            self.hyphenation = None
        else:
            # 4. Если hyphenation что-то неведомое, то игнорируем его и правило переноса выключено
            self.hyphenation = None
        # D. --- Конфигурация других правил---


    # Конвейер для обработки текста
    def process(self, text: str) -> str:
        processed_text = text
        if self.hyphenation is not None:
            # Обработчик переносов (Hyphenator) активен. Обрабатываем текст...
            processed_text = self.hyphenation.hyp_in_text(processed_text)

        # if self.glue_prepositions_rule:
        #     processed_text = self.glue_prepositions_rule.hyp_in_text(processed_text, non_breaking_space_char=self._get_nbsp())

        # ... вызовы других активных модулей правил ...
        return processed_text

    # def _get_nbsp(self): # Пример получения неразрывного пробела
    #     return "\u00A0" if self.mode in UTF else "&nbsp;"

