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
    ("&plus; &minus; &times; &divide; &equals; &ne;", "+ − × ÷ = ≠"),            # Математические символы
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
    ("&excl; &num; &percnt; &lpar; &rpar; &ast;", "! # % ( ) *"),               # Знаки препинания
    ("&comma; &period; &sol; &colon; &semi;", ", . / : ;"),
    ("&quest; &lbrack; &bsol; &rbrack; &Hat; &lowbar;", "? [ \\ ] ^ _"),
    ("&grave; &lbrace; &vert; &rbrace; &tilde;", "` { | } ˜"),
    ("&circ; &lrm; &rlm; &iexcl; &brvbar; &sect;", "ˆ \u200e \u200f ¡ ¦ §"),
    ("&uml; &ordf; &not; &macr; &acute; &micro; &bprime;", "¨ ª ¬ ¯ ´ µ ‵"),
    ("&para; &middot; &cedil; &ordm; &iquest; &Vert;", "¶ · ¸ º ¿ ‖"),
    ("&dagger; &Dagger; &bull; &nldr; &hellip;", "† ‡ • ‥ …"),
    ("&permil; &pertenk; &prime; &Prime; &tprime;", "‰ ‱ ′ ″ ‴"),
    ("&oline; &caret; &hybull; &frasl; &bsemi; &qprime;", "‾ ⁁ ⁃ ⁄ ⁏ ⁗"),
    ("&frac12; &frac13; &frac14; &frac15; &frac16;", "½ ⅓ ¼ ⅕ ⅙"),              # Дробные символы и знаки
    ("&frac18; &frac23; &frac25; &frac34; &frac35;", "⅛ ⅔ ⅖ ¾ ⅗"),
    ("&frac38; &frac45; &frac56; &frac58; &frac78;", "⅜ ⅘ ⅚ ⅝ ⅞"),
    ("&Alpha; &Beta; &Gamma; &Delta; &Epsilon; &Zeta;", "Α Β Γ Δ Ε Ζ"),        # Греческие символы
    ("&Eta; &Theta; &Iota; &Kappa; &Lambda; &Mu;", "Η Θ Ι Κ Λ Μ"),
    ("&Nu; &Xi; &Omicron; &Pi; &Rho; &Sigma; &Tau;", "Ν Ξ Ο Π Ρ Σ Τ"),
    ("&Upsilon; &Phi; &Chi; &Psi; &Omega; &alpha;", "Υ Φ Χ Ψ Ω α"),
    ("&beta; &gamma; &delta; &epsilon; &zeta; &eta;", "β γ δ ε ζ η"),
    ("&theta; &iota; &kappa; &lambda; &mu; &nu;", "θ ι κ λ μ ν"),
    ("&xi; &omicron; &pi; &rho; &sigmaf; &tau;", "ξ ο π ρ ς τ"),
    ("&upsilon; &phi; &chi; &psi; &omega;", "υ φ χ ψ ω"),
    ("&thetasym; &upsih; &piv;", "ϑ ϒ ϖ"),
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
