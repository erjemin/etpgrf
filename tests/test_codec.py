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
    ("&apos; &laquo; &raquo;", "' « »"),   # Апостроф и ёлочки
    ("&ldquo; &rdquo; &bdquo;", "“ ” „"),  # Двойные кавычки
    ("&lsquo; &rsquo; &sbquo;", "‘ ’ ‚"),  # Одиночные кавычки
    ("&lsaquo; &rsaquo;", "‹ ›"),  # Французские угловые кавычки
    ("&dollar; &cent; &pound; &curren; &yen; &euro; &#8381;", "$ ¢ £ ¤ ¥ € ₽"),  # Валютные символы
    ("&plus; &minus; &times; &divide; &equals; &ne;", "+ − × ÷ = ≠"),   # Математические символы 01
    ("&plusmn; &not; &deg; &sup1; &sup2 &sup3;", "± ¬ ° ¹ ² ³"),        # Математические символы 02
    ("&fnof; &percnt; &permil; &pertenk;", "ƒ % ‰ ‱"),                  # Математические символы 03
    ("&forall; &comp; &part; &exist; &nexist;", "∀ ∁ ∂ ∃ ∄"),           # Математические символы 04
    ("&empty; &nabla; &isin; &notin; &ni; &notni;", "∅ ∇ ∈ ∉ ∋ ∌"),     # Математические символы 05
    ("&prod; &coprod; &sum; &mnplus; &minusd;", "∏ ∐ ∑ ∓ ∸"),           # Математические символы 06
    ("&plusdo; &setminus; &lowast; &compfn; &radic;", "∔ ∖ ∗ ∘ √"),     # Математические символы 07
    ("&prop; &infin; &ang; &angrt; &angmsd; &mid;", "∝ ∞ ∠ ∟ ∡ ∣"),     # Математические символы 08
    ("&angsph; &nmid; '&parallel; &npar; &and; &or;", "∢ ∤ '∥ ∦ ∧ ∨"),  # Математические символы 09
    ("&cap; &cup; &int; &Int; &iiint; &conint;", "∩ ∪ ∫ ∬ ∭ ∮"),        # Математические символы 10
    ("&Conint; &Cconint; &cwint; &cwconint;", "∯ ∰ ∱ ∲"),              # Математические символы 11
    ("&awconint; &there4; &because; &ratio; &Colon;", "∳ ∴ ∵ ∶ ∷"),     # Математические символы 12
    ("&mDDot; &homtht; &sim; &bsim; &ac; &acd;", "∺ ∻ ∼ ∽ ∾ ∿"),        # Математические символы 13
    ("&wreath; &nsim; &esim; &sime; &nsime; &cong;", "≀ ≁ ≂ ≃ ≄ ≅"),    # Математические символы 14
    ("&asymp; &simne; &ncong; &nap; &approxeq; &apid;", "≈ ≆ ≇ ≉ ≊ ≋"), # Математические символы 15
    ("&bcong; &asympeq; &bump; &bumpe; &esdot; &eDot;", "≌ ≍ ≎ ≏ ≐ ≑"), # Математические символы 16
    ("&efDot; &erDot; &colone; &ecolon; &ecir; &cire;", "≒ ≓ ≔ ≕ ≖ ≗"), # Математические символы 17
    ("&wedgeq; &veeeq; &trie; &equest; &equiv;", "≙ ≚ ≜ ≟ ≡"),          # Математические символы 18
    ("&nequiv; &le; &ge; &lE; &gE; &lnE; &gnE;", "≢ ≤ ≥ ≦ ≧ ≨ ≩"),      # Математические символы 19
    ("&Lt; &Gt; &between; &NotCupCap; &nlt; &ngt;", "≪ ≫ ≬ ≭ ≮ ≯"),     # Математические символы 20
    ("&nle; &nge; &lsim; &gsim; &nlsim; &ngsim;", "≰ ≱ ≲ ≳ ≴ ≵"),       # Математические символы 21
    ("&lg; &gl; &ntlg; &ntgl; &pr; &sc;", "≶ ≷ ≸ ≹ ≺ ≻"),               # Математические символы 22
    ("&prcue; &sccue; &prsim; &scsim; &npr; &nsc;", "≼ ≽ ≾ ≿ ⊀ ⊁"),     # Математические символы 23
    ("&sub; &sup; &nsub; &nsup; &sube; &supe;", "⊂ ⊃ ⊄ ⊅ ⊆ ⊇"),         # Математические символы 24
    ("&nsube; &nsupe; &subne; &supne; &cupdot;", "⊈ ⊉ ⊊ ⊋ ⊍"),          # Математические символы 25
    ("&uplus; &sqsub; &sqsup; &sqsube; &sqsupe;", "⊎ ⊏ ⊐ ⊑ ⊒"),         # Математические символы 26
    ("&sqcap; &sqcup; &oplus; &ominus; &otimes;", "⊓ ⊔ ⊕ ⊖ ⊗"),         # Математические символы 27
    ("&osol; &odot; &ocir; &oast; &odash; &plusb;", "⊘ ⊙ ⊚ ⊛ ⊝ ⊞"),     # Математические символы 28
    ("&minusb; &timesb; &sdotb; &vdash; &dashv; &top;", "⊟ ⊠ ⊡ ⊢ ⊣ ⊤"), # Математические символы 29
    ("&bot; &models; &vDash; &Vdash; &Vvdash;", "⊥ ⊧ ⊨ ⊩ ⊪"),           # Математические символы 30
    ("&VDash; &nvdash; &nvDash; &nVdash; &nVDash;", "⊫ ⊬ ⊭ ⊮ ⊯"),     # Математические символы 31
    ("&prurel; &vltri; &vrtri; &ltrie; &rtrie;", "⊰ ⊲ ⊳ ⊴ ⊵"),         # Математические символы 32
    ("&origof; &imof; &mumap; &hercon; &intcal;", "⊶ ⊷ ⊸ ⊹ ⊺"),        # Математические символы 33
    ("&veebar; &barvee; &angrtvb; &lrtri; &xwedge;", "⊻ ⊽ ⊾ ⊿ ⋀"),     # Математические символы 34
    ("&xvee; &xcap; &xcup; &diamond; &sdot; &Star;", "⋁ ⋂ ⋃ ⋄ ⋅ ⋆"),    # Математические символы 35
    ("&divonx; &bowtie; &ltimes; &rtimes; &lthree;", "⋇ ⋈ ⋉ ⋊ ⋋"),      # Математические символы 36
    ("&rthree; &bsime; &cuvee; &cuwed; &Sub; &Sup;", "⋌ ⋍ ⋎ ⋏ ⋐ ⋑"),    # Математические символы 37
    ("&Cap; &Cup; &fork; &epar; &ltdot; &gtdot;", "⋒ ⋓ ⋔ ⋕ ⋖ ⋗"),       # Математические символы 38
    ("&Ll; &Gg; &leg; &gel; &cuepr; &cuesc;", "⋘ ⋙ ⋚ ⋛ ⋞ ⋟"),          # Математические символы 39
    ("&nprcue; &nsccue; &nsqsube; &nsqsupe;", "⋠ ⋡ ⋢ ⋣"),              # Математические символы 40
    ("&lnapprox; &gnapprox; &lnsim; &gnsim; &prnsim;", "⪉ ⪊ ⋦ ⋧ ⋨"),    # Математические символы 41
    ("&scnsim; &nltri; &nrtri; &nltrie; &nrtrie;", "⋩ ⋪ ⋫ ⋬ ⋭"),      # Математические символы 42
    ("&vellip; &ctdot; &utdot; &dtdot; &disin;", "⋮ ⋯ ⋰ ⋱ ⋲"),         # Математические символы 43
    ("&isinsv; &isins; &isindot; &notinvc; &notinvb;", "⋳ ⋴ ⋵ ⋶ ⋷"),   # Математические символы 44
    ("&isinE; &nisd; &xnis; &nis; &notnivc;", "⋹ ⋺ ⋻ ⋼ ⋽"),            # Математические символы 45
    ("&notnivb; &barwed; &Barwed; &lceil; &lceil;", "⋾ ⌅ ⌆ ⌈ ⌈"),
    ("&rceil; &lfloor; &rfloor; &lang; &rang;", "⌉ ⌊ ⌋ ⟨ ⟩"),
    ("", ""),
    ("", ""),


    ("&copy; &reg; &trade;", "\u00A9 \u00AE \u2122"),  # Символы авторского права, зарегистрированной торговой марки и товарного знака
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