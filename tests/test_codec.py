# tests/test_codec.py
import pytest
from etpgrf import codec

# Вообще, проверять кодирование HTML-мнемоников в Unicode не обязательно, так как это внутренняя библиотека html,
# но так как мнемоники были собраны из разных сторонников, полезно проверить какие из них работают, а какие нет...
# Это способствует тому, что обратное преобразование из Unicode в HTML-мнемоники будет работать корректно.
STRINGS_FOR_DECODE = [
    # Тестовые строки для декодирования html-метаккода в uft-8
    ("", ""),                                   # Пустая строка
    ("Hello world!", "Hello world!"),           # Строка
    ("Привет типограф!", "Привет типограф!"),   # Строка русского текста
    ("&lt; &gt; &amp; &quot;", "< > & \""),     # Самый простой набор HTML-мнемоников
    ("&shy;", "\u00AD"),                        # Мягкий перенос
    ("&nbsp;&ensp;&emsp;&thinsp;&zwj;&zwnj;", "\u00A0\u2002\u2003\u2009\u200D\u200C"), # Набор пробелов и невидимых символов
    ("&ndash; &mdash; &hyphen; &horbar;", "– — ‐ ―"),  # Набор тире и дефисов
    ("&dollar; &cent; &pound; &curren; &yen; &euro; &#8381;", "$ ¢ £ ¤ ¥ € ₽"),  # Валютные символы
    # Набор из html.entities.name2codepoint
    ("&AElig; &Aacute; &Acirc; &Agrave; &Alpha; &Aring; &Atilde; &Auml; &Auml;", "Æ Á Â À Α Å Ã Ä Ä"),
    ("&Beta; &Ccedil; &Chi; &Dagger; &Delta; &ETH; &Eacute; &Ecirc; &Egrave;", "Β Ç Χ ‡ Δ Ð É Ê È"),
    ("&Epsilon; &Eta; &Euml; &Gamma; &Iacute; &Icirc; &Igrave; &Iota; &Iuml;", "Ε Η Ë Γ Í Î Ì Ι Ï"),
    ("&Kappa; &Lambda; &Mu; &Ntilde; &Nu; &OElig; &Oacute; &Ocirc; &Ograve; &Ouml;", "Κ Λ Μ Ñ Ν Œ Ó Ô Ò Ö"),
    ("&Omega; &Omicron; &Oslash; &Otilde; &Phi; &Pi; &Prime; &Psi; &Rho; &Scaron;", "Ω Ο Ø Õ Φ Π ″ Ψ Ρ Š"),
    ("&Sigma; &THORN; &Tau; &Theta; &Uacute; &Ucirc; &Ugrave; &Upsilon; &Uuml;", "Σ Þ Τ Θ Ú Û Ù Υ Ü"),
    ("&Xi; &Yacute; &Yuml; &Zeta; &aacute; &acirc; &acute; &aelig; &agrave;", "Ξ Ý Ÿ Ζ á â ´ æ à"),
    ("&alefsym; &alpha; &amp; &and; &ang; &apos; &aring; &asymp; &atilde; &auml;", "ℵ α & ∧ ∠ ' å ≈ ã ä"),
    ("&bdquo; &beta; &brvbar; &bull; &cap; &ccedil; &cedil; &cent; &chi; &circ;", "„ β ¦ • ∩ ç ¸ ¢ χ ˆ"),
    ("&clubs; &cong; &copy; &crarr; &cup; &curren; &dArr; &dagger; &darr; &deg;", "♣ ≅ © ↵ ∪ ¤ ⇓ † ↓ °"),
    ("&delta; &diams; &divide; &eacute; &ecirc; &egrave; &empty; &emsp; &ensp;", "δ ♦ ÷ é ê è ∅ \u2003 \u2002"),
    ("&epsilon; &equiv; &eta; &eth; &euml; &euro; &exist; &fnof; &forall; &frac12;", "ε ≡ η ð ë € ∃ ƒ ∀ ½"),
    ("&frac14; &frac34; &frasl; &gamma; &ge; &gt; &hArr; &harr; &hearts; &hellip;", "¼ ¾ ⁄ γ ≥ > ⇔ ↔ ♥ …"),
    ("&iacute; &icirc; &iexcl; &igrave; &image; &infin; &int; &iota; &iquest; &isin;", "í î ¡ ì ℑ ∞ ∫ ι ¿ ∈"),
    ("&iuml; &kappa; &lArr; &lambda; &lang; &laquo; &larr; &lceil; &ldquo; &le;", "ï κ ⇐ λ ⟨ « ← ⌈ “ ≤"),
    ("&lfloor; &lowast; &loz; &lrm; &lsaquo; &lsquo; &lt; &macr; &mdash; &micro;", "⌊ ∗ ◊ \u200e ‹ ‘ < ¯ — µ"),
    ("&middot; &minus; &mu; &nabla; &nbsp; &ndash; &ne; &ni; &not; &notin;", "· − μ ∇ \u00A0 – ≠ ∋ ¬ ∉"),
    ("&nsub; &ntilde; &nu; &oacute; &ocirc; &oelig; &ograve; &oline; &omega;", "⊄ ñ ν ó ô œ ò ‾ ω"),
    ("&omicron; &oplus; &or; &ordf; &ordm; &oslash; &otilde; &otimes; &ouml;", "ο ⊕ ∨ ª º ø õ ⊗ ö"),
    ("&para; &part; &permil; &perp; &phi; &pi; &piv; &plusmn; &pound; &prime; &prod;", "¶ ∂ ‰ ⊥ φ π ϖ ± £ ′ ∏"),
    ("&prop; &psi; &quot; &rArr; &radic; &rang; &raquo; &rarr; &rceil; &rdquo;", "∝ ψ \" ⇒ √ ⟩ » → ⌉ ”"),
    ("&real; &reg; &rfloor; &rho; &rlm; &rsaquo; &rsquo; &sbquo; &scaron;", "ℜ ® ⌋ ρ \u200f › ’ ‚ š"),
    ("&sdot; &sect; &shy; &sigma; &sigmaf; &sim; &spades; &sub; &sube; &sum;", "⋅ § \u00AD σ ς ∼ ♠ ⊂ ⊆ ∑"),
    ("&sup; &sup1; &sup2; &sup3; &supe; &szlig; &tau; &there4; &theta; &thetasym;", "⊃ ¹ ² ³ ⊇ ß τ ∴ θ ϑ"),
    ("&thinsp; &thorn; &tilde; &times; &trade; &uArr; &uacute; &uarr; &ucirc;", "\u2009 þ ˜ × ™ ⇑ ú ↑ û"),
    ("&ugrave; &uml; &upsih; &upsilon; &uuml; &weierp; &xi; &yacute; &yen; &yuml;", "ù ¨ ϒ υ ü ℘ ξ ý ¥ ÿ"),
    ("&zeta; &zwj; &zwnj; &plus; &equals; &percnt;", "ζ \u200D \u200C + = %"),
    # Набор из html.entities.html5
    ("", ""),
    ("", ""),

]

@pytest.mark.parametrize("input_string, expected_output", STRINGS_FOR_DECODE)
def test_html_mnemo_to_utf(input_string, expected_output):
    """
    Проверяет ПОВЕДЕНИЕ: декодирование HTML-мнемоников в Unicode-строки.
    """
    # Act (действие) - тестируем
    actual_output = codec.decode_to_unicode(input_string)
    # Assert (проверка)
    assert actual_output == expected_output


STRINGS_FOR_ENCODE = [
    # Тестовые строки для декодирования html-метаккода в uft-8
    ("", ""),                                   # Пустая строка
    ("Hello world!", "Hello world!"),           # Строка
    ("Привет типограф!", "Привет типограф!"),   # Строка русского текста
    ("< > & \"", "&lt; &gt; &amp; &quot;"),     # Самый простой набор HTML-мнемоников
    ("\u00AD", "&shy;"),                        # Мягкий перенос
    ("\u00A0\u2002\u2003\u2009\u200D\u200C", "&nbsp;&ensp;&emsp;&thinsp;&zwj;&zwnj;"), # Набор пробелов и невидимых символов
    ("– — ‐ ―", "&ndash; &mdash; &hyphen; &horbar;"),  # Набор тире и дефисов
    ("$ ¢ £ ¤ ¥ € ₽", "&dollar; &cent; &pound; &curren; &yen; &euro; &#8381;"),  # Валютные символы
    # Набор из html.entities.name2codepoint
    ("Æ Á Â À Α Å Ã Ä Ä", "Æ &Aacute; &Acirc; &Agrave; &Alpha; &Aring; &Atilde; &Auml; &Auml;"),
    ("Β Ç Χ ‡ Δ Ð É Ê È", "&Beta; &Ccedil; &Chi; &Dagger; &Delta; &ETH; &Eacute; &Ecirc; &Egrave;"),
    ("Ε Η Ë Γ Í Î Ì Ι Ï", "&Epsilon; &Eta; &Euml; &Gamma; &Iacute; &Icirc; &Igrave; &Iota; &Iuml;"),
    ("Κ Λ Μ Ñ Ν Œ Ó Ô Ò Ö", "&Kappa; &Lambda; &Mu; &Ntilde; &Nu; Œ &Oacute; &Ocirc; &Ograve; &Ouml;"),
    ("Ω Ο Ø Õ Φ Π ″ Ψ Ρ Š", "&Omega; &Omicron; &Oslash; &Otilde; &Phi; &Pi; &Prime; &Psi; &Rho; &Scaron;"),
    ("Σ Þ Τ Θ Ú Û Ù Υ Ü", "&Sigma; &THORN; &Tau; &Theta; &Uacute; &Ucirc; &Ugrave; &Upsilon; &Uuml;"),
    ("Ξ Ý Ÿ Ζ á â ´ æ à", "&Xi; &Yacute; &Yuml; &Zeta; &aacute; &acirc; &acute; æ &agrave;"),
    ("ℵ α & ∧ ∠ ' å ≈ ã ä", "&alefsym; &alpha; &amp; &and; &ang; &apos; &aring; &asymp; &atilde; &auml;"),
    ("„ β ¦ • ∩ ç ¸ ¢ χ ˆ", "&bdquo; &beta; &brvbar; &bull; &cap; &ccedil; &cedil; &cent; &chi; &circ;"),
    ("♣ ≅ © ↵ ∪ ¤ ⇓ † ↓ °", "&clubs; &cong; &copy; &crarr; &cup; &curren; &dArr; &dagger; &darr; &deg;"),
    ("δ ♦ ÷ é ê è ∅ \u2003 \u2002", "&delta; &diams; &divide; &eacute; &ecirc; &egrave; &empty; &emsp; &ensp;"),
    ("ε ≡ η ð ë € ∃ ƒ ∀ ½", "&epsilon; &equiv; &eta; &eth; &euml; &euro; &exist; &fnof; &forall; &frac12;"),
    ("¼ ¾ ⁄ γ ≥ > ⇔ ↔ ♥ …", "&frac14; &frac34; &frasl; &gamma; &ge; &gt; &hArr; &harr; &hearts; &hellip;"),
    ("í î ¡ ì ℑ ∞ ∫ ι ¿ ∈", "&iacute; &icirc; &iexcl; &igrave; &image; &infin; &int; &iota; &iquest; &isin;"),
    ("ï κ ⇐ λ ⟨ « ← ⌈ “ ≤", "&iuml; &kappa; &lArr; &lambda; &lang; &laquo; &larr; &lceil; &ldquo; &le;"),
    ("⌊ ∗ ◊ \u200e ‹ ‘ < ¯ — µ", "&lfloor; &lowast; &loz; &lrm; &lsaquo; &lsquo; &lt; &macr; &mdash; &micro;"),
    ("· − μ ∇ \u00A0 – ≠ ∋ ¬ ∉", "&middot; &minus; &mu; &nabla; &nbsp; &ndash; &ne; &ni; &not; &notin;"),
    ("⊄ ñ ν ó ô œ ò ‾ ω", "&nsub; &ntilde; &nu; &oacute; &ocirc; œ &ograve; &oline; &omega;"),
    ("ο ⊕ ∨ ª º ø õ ⊗ ö", "&omicron; &oplus; &or; &ordf; &ordm; &oslash; &otilde; &otimes; &ouml;"),
    ("¶ ∂ ‰ ⊥ φ π ϖ ± £ ′ ∏", "&para; &part; &permil; &perp; &phi; &pi; &piv; &plusmn; &pound; &prime; &prod;"),
    ("∝ ψ \" ⇒ √ ⟩ » → ⌉ ”", "&prop; &psi; &quot; &rArr; &radic; &rang; &raquo; &rarr; &rceil; &rdquo;"),
    ("ℜ ® ⌋ ρ \u200f › ’ ‚ š", "&real; &reg; &rfloor; &rho; &rlm; &rsaquo; &rsquo; &sbquo; &scaron;"),
    ("⋅ § \u00AD σ ς ∼ ♠ ⊂ ⊆ ∑", "&sdot; &sect; &shy; &sigma; &sigmaf; &sim; &spades; &sub; &sube; &sum;"),
    ("⊃ ¹ ² ³ ⊇ ß τ ∴ θ ϑ", "&sup; &sup1; &sup2; &sup3; &supe; &szlig; &tau; &there4; &theta; &thetasym;"),
    ("\u2009 þ ˜ × ™ ⇑ ú ↑ û", "&thinsp; &thorn; &tilde; &times; &trade; &uArr; &uacute; &uarr; &ucirc;"),
    ("ù ¨ ϒ υ ü ℘ ξ ý ¥ ÿ", "&ugrave; &uml; &upsih; &upsilon; &uuml; &weierp; &xi; &yacute; &yen; &yuml;"),
    ("ζ \u200D \u200C + = %", "&zeta; &zwj; &zwnj; &plus; = %"),
    # Набор из html.entities.html5
]

@pytest.mark.parametrize("input_string, expected_output", STRINGS_FOR_ENCODE)
def test_utf_to_html_mnemo(input_string, expected_output):
    """
    Проверяет ПОВЕДЕНИЕ: кодирование Unicode-строк в HTML-мнемоники.
    """
    # Act (действие) - тестируем
    actual_output = codec.encode_from_unicode(input_string, mode="mnemonic")
    # Assert (проверка)
    assert actual_output == expected_output