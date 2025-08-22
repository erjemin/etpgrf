# tests/test_hyphenation.py
import pytest
from etpgrf import Hyphenator
from etpgrf.config import CHAR_SHY

# --- Тестовые данные для русского языка ---
# Формат: (входное_слово, ожидаемый_результат_с_переносами)
# Используем {CHAR_SHY} - это Unicode-представление мягкого переноса (&shy;)
RUSSIAN_HYPHENATION_CASES = [
    ("дом", "дом"),  # Сочень короткое (короче max_unhyphenated_len) не должно меняться
    ("проверка", f"про{CHAR_SHY}верка"),
    ("тестирование", f"тести{CHAR_SHY}рова{CHAR_SHY}ние"),
    ("благотворительностью", f"бла{CHAR_SHY}готво{CHAR_SHY}ритель{CHAR_SHY}ностью"), # Слово с переносом на мягкий знак
    ("фотоаппаратура", f"фотоап{CHAR_SHY}пара{CHAR_SHY}тура"), # проверка слова со сдвоенной согласной
    ("программирование", f"про{CHAR_SHY}грам{CHAR_SHY}миро{CHAR_SHY}вание"),  # слова со сдвоенной согласной
    ("сверхзвуковой", f"сверх{CHAR_SHY}зву{CHAR_SHY}ковой"),
    ("автомобиль", f"авто{CHAR_SHY}мобиль"),
    ("интернационализация", f"инте{CHAR_SHY}рнаци{CHAR_SHY}онали{CHAR_SHY}зация"),
    ("электронный", f"элек{CHAR_SHY}трон{CHAR_SHY}ный"),
    ("информационный", f"инфо{CHAR_SHY}рма{CHAR_SHY}цион{CHAR_SHY}ный"),
    ("автоматизация", f"автома{CHAR_SHY}тиза{CHAR_SHY}ция"),
    ("многоклеточный", f"мно{CHAR_SHY}гокле{CHAR_SHY}точный"),
    ("многофункциональный", f"мно{CHAR_SHY}гофун{CHAR_SHY}кцио{CHAR_SHY}наль{CHAR_SHY}ный"),
    ("непрерывность", f"непре{CHAR_SHY}рывно{CHAR_SHY}сть"),
    ("сверхпроводимость", f"сверх{CHAR_SHY}прово{CHAR_SHY}димо{CHAR_SHY}сть"),
    ("многообразие", f"мно{CHAR_SHY}гоо{CHAR_SHY}бра{CHAR_SHY}зие"),
    ("противоречивость", f"про{CHAR_SHY}тиво{CHAR_SHY}речи{CHAR_SHY}вость"),
    ("непревзойденный", f"непре{CHAR_SHY}взой{CHAR_SHY}ден{CHAR_SHY}ный"),
    ("многослойный", f"мно{CHAR_SHY}гослой{CHAR_SHY}ный"),
    ("суперкомпьютер", f"супе{CHAR_SHY}рко{CHAR_SHY}мпью{CHAR_SHY}тер"), # Неправильный перенос (нужен словарь "приставок/корней/суффиксов")
    ("сверхчувствительный", f"свер{CHAR_SHY}хчув{CHAR_SHY}стви{CHAR_SHY}тель{CHAR_SHY}ный"),  # Неправильный перенос
    ("гиперподъездной", f"гипе{CHAR_SHY}рпо{CHAR_SHY}дъез{CHAR_SHY}дной"),  # Неправильный перенос
]


@pytest.mark.parametrize("input_word, expected_output", RUSSIAN_HYPHENATION_CASES)
def test_russian_word_hyphenation(input_word, expected_output):
    """
    Проверяет ПОВЕДЕНИЕ: правильная расстановка переносов в отдельных русских словах.
    """
    # Arrange (подготовка)
    hyphenator_ru = Hyphenator(langs='ru', max_unhyphenated_len=5, min_tail_len=3)
    # Act (действие) - тестируем самый "атомарный" метод
    actual_output = hyphenator_ru.hyp_in_word(input_word)
    # Assert (проверка)
    assert actual_output == expected_output


ENGLISH_HYPHENATION_CASES = [
    ("color", "color"),  # Короткое слово, не должно меняться
    ("throughout", "throughout"),  # Длинное слово, но из-за икс-графа "ough" не будет переноситься
    ("ambrella", f"amb{CHAR_SHY}rella"),
    ("unbelievable", f"unbel{CHAR_SHY}iev{CHAR_SHY}able"),  # Проверка переноса перед суффиксом "able"
    ("acknowledgment", f"ack{CHAR_SHY}now{CHAR_SHY}ledg{CHAR_SHY}ment"),  # Проверка переноса перед суффиксом "ment"
    ("friendship", f"frien{CHAR_SHY}dship"),  # Проверка переноса перед суффиксом "ship"
    ("thoughtful", f"though{CHAR_SHY}tful"),  #
    ("psychology", f"psy{CHAR_SHY}cho{CHAR_SHY}logy"),  # Проверка переноса после "psy"
    ("extraordinary", f"ext{CHAR_SHY}raor{CHAR_SHY}din{CHAR_SHY}ary"),  # Проверка сложного слова
    ("unbreakable", f"unb{CHAR_SHY}rea{CHAR_SHY}kable"),  # Проверка переноса перед "able"
    ("acknowledgement", f"ack{CHAR_SHY}now{CHAR_SHY}ledge{CHAR_SHY}ment"),  # Проверка икс-графа "dge"
    ("misunderstanding", f"mis{CHAR_SHY}under{CHAR_SHY}stan{CHAR_SHY}ding"),  # Проверка сложного слова
    ("floccinaucinihilipilification", f"floc{CHAR_SHY}cin{CHAR_SHY}auc{CHAR_SHY}inih{CHAR_SHY}ili{CHAR_SHY}pili{CHAR_SHY}fica{CHAR_SHY}tion"),
]

@pytest.mark.parametrize("input_word, expected_output", ENGLISH_HYPHENATION_CASES)
def test_english_word_hyphenation(input_word, expected_output):
    """
    Проверяет ПОВЕДЕНИЕ: правильная расстановка переносов в отдельных английских словах.
    """
    # Arrange (подготовка)
    hyphenator_en = Hyphenator(langs='en', max_unhyphenated_len=5, min_tail_len=3)
    # Act (действие) - тестируем самый "атомарный" метод
    actual_output = hyphenator_en.hyp_in_word(input_word)
    # Assert (проверка)
    assert actual_output == expected_output

