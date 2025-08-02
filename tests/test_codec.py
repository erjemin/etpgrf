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
    ("&plus; &minus; &times; &divide; &equals; &ne;", "+ − × ÷ = ≠"),   # Математические символы
    ("&plusmn; &not; &deg; &sup1; &sup2 &sup3;", "± ¬ ° ¹ ² ³"),
    ("&fnof; &percnt; &permil; &pertenk;", "ƒ % ‰ ‱"),
    ("&forall; &comp; &part; &exist; &nexist;", "∀ ∁ ∂ ∃ ∄"),
    ("&empty; &nabla; &isin; &notin; &ni; &notni;", "∅ ∇ ∈ ∉ ∋ ∌"),
    ("&prod; &coprod; &sum; &mnplus; &minusd;", "∏ ∐ ∑ ∓ ∸"),
    ("&plusdo; &setminus; &lowast; &compfn; &radic;", "∔ ∖ ∗ ∘ √"),
    ("&prop; &infin; &ang; &angrt; &angmsd; &mid;", "∝ ∞ ∠ ∟ ∡ ∣"),
    ("&angsph; &nmid; '&parallel; &npar; &and; &or;", "∢ ∤ '∥ ∦ ∧ ∨"),
    ("&cap; &cup; &int; &Int; &iiint; &conint;", "∩ ∪ ∫ ∬ ∭ ∮"),
    ("&Conint; &Cconint; &cwint; &cwconint;", "∯ ∰ ∱ ∲"),
    ("&awconint; &there4; &because; &ratio; &Colon;", "∳ ∴ ∵ ∶ ∷"),
    ("&mDDot; &homtht; &sim; &bsim; &ac; &acd;", "∺ ∻ ∼ ∽ ∾ ∿"),
    ("&wreath; &nsim; &esim; &sime; &nsime; &cong;", "≀ ≁ ≂ ≃ ≄ ≅"),
    ("&asymp; &simne; &ncong; &nap; &approxeq; &apid;", "≈ ≆ ≇ ≉ ≊ ≋"),
    ("&bcong; &asympeq; &bump; &bumpe; &esdot; &eDot;", "≌ ≍ ≎ ≏ ≐ ≑"),
    ("&efDot; &erDot; &colone; &ecolon; &ecir; &cire;", "≒ ≓ ≔ ≕ ≖ ≗"),
    ("&wedgeq; &veeeq; &trie; &equest; &equiv;", "≙ ≚ ≜ ≟ ≡"),
    ("&nequiv; &le; &ge; &lE; &gE; &lnE; &gnE;", "≢ ≤ ≥ ≦ ≧ ≨ ≩"),
    ("&Lt; &Gt; &between; &NotCupCap; &nlt; &ngt;", "≪ ≫ ≬ ≭ ≮ ≯"),
    ("&nle; &nge; &lsim; &gsim; &nlsim; &ngsim;", "≰ ≱ ≲ ≳ ≴ ≵"),
    ("&lg; &gl; &ntlg; &ntgl; &pr; &sc;", "≶ ≷ ≸ ≹ ≺ ≻"),
    ("&prcue; &sccue; &prsim; &scsim; &npr; &nsc;", "≼ ≽ ≾ ≿ ⊀ ⊁"),
    ("&sub; &sup; &nsub; &nsup; &sube; &supe;", "⊂ ⊃ ⊄ ⊅ ⊆ ⊇"),
    ("&nsube; &nsupe; &subne; &supne; &cupdot;", "⊈ ⊉ ⊊ ⊋ ⊍"),
    ("&uplus; &sqsub; &sqsup; &sqsube; &sqsupe;", "⊎ ⊏ ⊐ ⊑ ⊒"),
    ("&sqcap; &sqcup; &oplus; &ominus; &otimes;", "⊓ ⊔ ⊕ ⊖ ⊗"),
    ("&osol; &odot; &ocir; &oast; &odash; &plusb;", "⊘ ⊙ ⊚ ⊛ ⊝ ⊞"),
    ("&minusb; &timesb; &sdotb; &vdash; &dashv; &top;", "⊟ ⊠ ⊡ ⊢ ⊣ ⊤"),
    ("&bot; &models; &vDash; &Vdash; &Vvdash;", "⊥ ⊧ ⊨ ⊩ ⊪"),
    ("&VDash; &nvdash; &nvDash; &nVdash; &nVDash;", "⊫ ⊬ ⊭ ⊮ ⊯"),
    ("&prurel; &vltri; &vrtri; &ltrie; &rtrie;", "⊰ ⊲ ⊳ ⊴ ⊵"),
    ("&origof; &imof; &mumap; &hercon; &intcal;", "⊶ ⊷ ⊸ ⊹ ⊺"),
    ("&veebar; &barvee; &angrtvb; &lrtri; &xwedge;", "⊻ ⊽ ⊾ ⊿ ⋀"),
    ("&xvee; &xcap; &xcup; &diamond; &sdot; &Star;", "⋁ ⋂ ⋃ ⋄ ⋅ ⋆"),
    ("&divonx; &bowtie; &ltimes; &rtimes; &lthree;", "⋇ ⋈ ⋉ ⋊ ⋋"),
    ("&rthree; &bsime; &cuvee; &cuwed; &Sub; &Sup;", "⋌ ⋍ ⋎ ⋏ ⋐ ⋑"),
    ("&Cap; &Cup; &fork; &epar; &ltdot; &gtdot;", "⋒ ⋓ ⋔ ⋕ ⋖ ⋗"),
    ("&Ll; &Gg; &leg; &gel; &cuepr; &cuesc;", "⋘ ⋙ ⋚ ⋛ ⋞ ⋟"),
    ("&nprcue; &nsccue; &nsqsube; &nsqsupe;", "⋠ ⋡ ⋢ ⋣"),
    ("&lnapprox; &gnapprox; &lnsim; &gnsim; &prnsim;", "⪉ ⪊ ⋦ ⋧ ⋨"),
    ("&scnsim; &nltri; &nrtri; &nltrie; &nrtrie;", "⋩ ⋪ ⋫ ⋬ ⋭"),
    ("&vellip; &ctdot; &utdot; &dtdot; &disin;", "⋮ ⋯ ⋰ ⋱ ⋲"),
    ("&isinsv; &isins; &isindot; &notinvc; &notinvb;", "⋳ ⋴ ⋵ ⋶ ⋷"),
    ("&isinE; &nisd; &xnis; &nis; &notnivc;", "⋹ ⋺ ⋻ ⋼ ⋽"),
    ("&notnivb; &barwed; &Barwed; &lceil; &lceil;", "⋾ ⌅ ⌆ ⌈ ⌈"),
    ("&rceil; &lfloor; &rfloor; &lang; &rang;", "⌉ ⌊ ⌋ ⟨ ⟩"),
    ("&copy; &reg; &trade; &copysr; &commat;", "© ® ™ ℗ @"),                    # Другие символы
    ("&Copf; &incare; &gscr; &hamilt; &Hfr; &Hopf;", "ℂ ℅ ℊ ℋ ℌ ℍ"),
    ("&planckh; &planck; &Iscr; &image; &Lscr; &ell;", "ℎ ℏ ℐ ℑ ℒ ℓ"),
    ("&Nopf; &numero; &weierp; &Popf; &Qopf; &Rscr;", "ℕ № ℘ ℙ ℚ ℛ"),
    ("&Ropf; &rx; &Zopf; &mho; &Zfr; &iiota;", "ℝ ℞ ℤ ℧ ℨ ℩"),
    ("&bernou; &Cfr; &escr; &Escr; &Fscr; &Mscr;", "ℬ ℭ ℯ ℰ ℱ ℳ"),
    ("&oscr; &alefsym; &beth; &gimel; &daleth;", "ℴ ℵ ℶ ℷ ℸ"),
    ("&DD; &dd; &ee; &ii; &ffilig; &fflig;", "ⅅ ⅆ ⅇ ⅈ ﬃ ﬀ"),
    ("&filig; &fllig; &starf; &star; &phone;", "ﬁ ﬂ ★ ☆ ☎"),
    ("&female; &male; &spades; &clubs; &hearts; &diams;", "♀ ♂ ♠ ♣ ♥ ♦"),
    ("&loz; &sung; &flat; &natural; &sharp; &check;", "◊ ♪ ♭ ♮ ♯ ✓"),
    ("&cross; &malt; &sext; &VerticalSeparator;", "✗ ✠ ✶ ❘"),
    ("&lbbrk; &rbbrk;", "❲ ❳"),
    ("", ""),
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
