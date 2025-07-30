# tests/test_hyphenation.py
import pytest
from etpgrf import Hyphenator
from tests.test_unbreakables import ENGLISH_PREPOSITIONS_TO_TEST

# --- Тестовые данные для русского языка ---
# Формат: (входное_слово, ожидаемый_результат_с_переносами)
# Используем \u00AD - это Unicode-представление мягкого переноса (&shy;)
RUSSIAN_HYPHENATION_CASES = [
    ("дом", "дом"),  # Сочень короткое (короче max_unhyphenated_len) не должно меняться
    ("проверка", "про\u00ADверка"),
    ("тестирование", "тести\u00ADрова\u00ADние"),
    ("благотворительностью", "бла\u00ADготво\u00ADритель\u00ADностью"), # Слово с переносом на мягкий знак
    ("фотоаппаратура", "фотоап\u00ADпара\u00ADтура"), # проверка слова со сдвоенной согласной
    ("программирование", "про\u00ADграм\u00ADмиро\u00ADвание"),  # слова со сдвоенной согласной
    ("сверхзвуковой", "сверх\u00ADзву\u00ADковой"),
    ("автомобиль", "авто\u00ADмобиль"),
    ("интернационализация", "инте\u00ADрнаци\u00ADонали\u00ADзация"),
    ("электронный", "элек\u00ADтрон\u00ADный"),
    ("информационный", "инфо\u00ADрма\u00ADцион\u00ADный"),
    ("автоматизация", "автома\u00ADтиза\u00ADция"),
    ("многоклеточный", "мно\u00ADгокле\u00ADточный"),
    ("многофункциональный", "мно\u00ADгофун\u00ADкцио\u00ADналь\u00ADный"),
    ("непрерывность", "непре\u00ADрывно\u00ADсть"),
    ("сверхпроводимость", "сверх\u00ADпрово\u00ADдимо\u00ADсть"),
    ("многообразие", "мно\u00ADгоо\u00ADбра\u00ADзие"),
    ("противоречивость", "про\u00ADтиво\u00ADречи\u00ADвость"),
    ("непревзойденный", "непре\u00ADвзой\u00ADден\u00ADный"),
    ("многослойный", "мно\u00ADгослой\u00ADный"),
    ("суперкомпьютер", "супе\u00ADрко\u00ADмпью\u00ADтер"), # Неправильный перенос (нужен словарь "приставок/корней/суффиксов")
    ("сверхчувствительный", "свер\u00ADхчув\u00ADстви\u00ADтель\u00ADный"),  # Неправильный перенос
    ("гиперподъездной", "гипе\u00ADрпо\u00ADдъез\u00ADдной"),  # Неправильный перенос
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
    ("ambrella", "amb\u00ADrella"),
    ("unbelievable", "unbel\u00ADiev\u00ADable"),  # Проверка переноса перед суффиксом "able"
    ("acknowledgment", "ack\u00ADnow\u00ADledg\u00ADment"),  # Проверка переноса перед суффиксом "ment"
    ("friendship", "frien\u00ADdship"),  # Проверка переноса перед суффиксом "ship"
    ("thoughtful", "though\u00ADtful"),  #
    ("psychology", "psy\u00ADcho\u00ADlogy"),  # Проверка переноса после "psy"
    ("extraordinary", "ext\u00ADraor\u00ADdin\u00ADary"),  # Проверка сложного слова
    ("unbreakable", "unb\u00ADrea\u00ADkable"),  # Проверка переноса перед "able"
    ("acknowledgement", "ack\u00ADnow\u00ADledge\u00ADment"),  # Проверка икс-графа "dge"
    ("misunderstanding", "mis\u00ADunder\u00ADstan\u00ADding"),  # Проверка сложного слова
    ("floccinaucinihilipilification", "floc\u00ADcin\u00ADauc\u00ADinih\u00ADili\u00ADpili\u00ADfica\u00ADtion"),
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

