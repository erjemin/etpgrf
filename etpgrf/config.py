# etpgrf/conf.py
# Настройки по умолчанию и "источник правды" для типографа etpgrf
from html import entities

# === КОНФИГУРАЦИИ ===
# Режимы "отдачи" результатов обработки
MODE_UNICODE = "unicode"
MODE_MNEMONIC = "mnemonic"
MODE_MIXED = "mixed"

# Языки, поддерживаемые библиотекой
LANG_RU = 'ru'  # Русский
LANG_RU_OLD = 'ruold'  # Русская дореволюционная орфография
LANG_EN = 'en'  # Английский
SUPPORTED_LANGS = frozenset([LANG_RU, LANG_RU_OLD, LANG_EN])
DEFAULT_LANGS = (LANG_RU, LANG_EN)  # Языки по умолчанию

# === ИСТОЧНИК ПРАВДЫ ===
# --- Базовые алфавиты: Эти константы используются как для правил переноса, так и для правил кодирования ---

# Русский алфавит
RU_VOWELS_UPPER = frozenset(['А', 'О', 'И', 'Е', 'Ё', 'Э', 'Ы', 'У', 'Ю', 'Я'])
RU_CONSONANTS_UPPER = frozenset(['Б', 'В', 'Г', 'Д', 'Ж', 'З', 'К', 'Л', 'М', 'Н', 'П', 'Р', 'С', 'Т', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ'])
RU_J_SOUND_UPPER = frozenset(['Й'])
RU_SIGNS_UPPER = frozenset(['Ь', 'Ъ'])
RU_ALPHABET_UPPER = RU_VOWELS_UPPER | RU_CONSONANTS_UPPER | RU_J_SOUND_UPPER | RU_SIGNS_UPPER
RU_ALPHABET_LOWER = frozenset([char.lower() for char in RU_ALPHABET_UPPER])
RU_ALPHABET_FULL = RU_ALPHABET_UPPER | RU_ALPHABET_LOWER

# Английский алфавит
EN_VOWELS_UPPER = frozenset(['A', 'E', 'I', 'O', 'U', 'Æ', 'Œ'])
EN_CONSONANTS_UPPER = frozenset(['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z'])
EN_ALPHABET_UPPER = EN_VOWELS_UPPER | EN_CONSONANTS_UPPER
EN_ALPHABET_LOWER = frozenset([char.lower() for char in EN_ALPHABET_UPPER])
EN_ALPHABET_FULL = EN_ALPHABET_UPPER | EN_ALPHABET_LOWER

# --- Специальные символы ---
CHAR_NBSP = '\u00a0'      # Неразрывный пробел (&nbsp;)
CHAR_SHY = '\u00ad'       # Мягкий перенос (&shy;)
CHAR_THIN_SP = '\u2009'   # Тонкий пробел (шпация, &thinsp;)
CHAR_NDASH = '\u2013'     # Cреднее тире (– / &ndash;)
CHAR_MDASH = '\u2014'     # Длинное тире (—  / &mdash;)
CHAR_HELLIP = '\u2026'    # Многоточие (… / &hellip;)
CHAR_RU_QUOT1_OPEN = '«'  # Русские кавычки открывающие (« / &laquo;)
CHAR_RU_QUOT1_CLOSE = '»'
CHAR_RU_QUOT2_OPEN = '„'
CHAR_RU_QUOT2_CLOSE = '“'
CHAR_EN_QUOT1_OPEN = '“'
CHAR_EN_QUOT1_CLOSE = '”'
CHAR_EN_QUOT2_OPEN = '‘'
CHAR_EN_QUOT2_CLOSE = '’'
CHAR_COPY = '\u00a9'  # Символ авторского права / © / &copy;
CHAR_REG = '\u00ae'   # Зарегистрированная торговая марка / ® / &reg;
CHAR_COPYP = '\u2117' # Знак звуковой записи / ℗ / &copyp;
CHAR_TRADE = '\u2122' # Знак торговой марки / ™ / &trade;
CHAR_ARROW_LR_DOUBLE = '\u21d4' # Двойная двунаправленная стрелка / ⇔ / &hArr;
CHAR_ARROW_L_DOUBLE = '\u21d0'  # Двойная стрелка влево / ⇐ / &lArr;
CHAR_ARROW_R_DOUBLE = '\u21d2'  # Двойная стрелка вправо / ⇒ / &rArr;
CHAR_AP = '\u2248'         # Приблизительно равно / ≈ / &ap;
CHAR_ARROW_L = '\u27f5'    # Стрелка влево / ← / &larr;
CHAR_ARROW_R = '\u27f6'    # Стрелка вправо / → / &rarr;
CHAR_ARROW_LR = '\u27f7'   # Длинная двунаправленная стрелка ↔ / &harr;
CHAR_ARROW_L_LONG_DOUBLE = '\u27f8'  # Длинная двойная стрелка влево
CHAR_ARROW_R_LONG_DOUBLE = '\u27f9'  # Длинная двойная стрелка вправо
CHAR_ARROW_LR_LONG_DOUBLE = '\u27fa' # Длинная двойная двунаправленная стрелка
CHAR_MIDDOT = '\u00b7'    # Средняя точка (· иногда используется как знак умножения) / &middot;
CHAR_UNIT_SEPARATOR = '\u25F0' # Символ временный разделитель для составных единиц (◰), чтобы не уходить
                               # в "мертвый" цикл при замене на тонкий пробел. Можно взять любой редкий символом.


# === КОНСТАНТЫ ПСЕВДОГРАФИКИ ===
# Для простых замен "строка -> символ" используем список кортежей.
# Порядок важен: более длинные последовательности должны идти раньше более коротких, которые
#                могут быть их частью (например, '<---' до '---', а та, в свою очередь, до '--').
STR_TO_SYMBOL_REPLACEMENTS = [
    # 5-символьные последовательности
    ('<===>', CHAR_ARROW_LR_LONG_DOUBLE),  # Длинная двойная двунаправленная стрелка
    # 4-символьные последовательности
    ('<===', CHAR_ARROW_L_LONG_DOUBLE),  # Длинная двойная стрелка влево
    ('===>', CHAR_ARROW_R_LONG_DOUBLE),  # Длинная двойная стрелка вправо
    ('<==>', CHAR_ARROW_LR_DOUBLE),  # Двойная двунаправленная стрелка
    ('(tm)', CHAR_TRADE), ('(TM)', CHAR_TRADE), # Знак торговой марки (нижний и верхний регистр)
    ('<-->', CHAR_ARROW_LR),  # Длинная двунаправленная стрелка
    # 3-символьные последовательности
    ('<--', CHAR_ARROW_L),  # Стрелка влево
    ('-->', CHAR_ARROW_R),  # Стрелка вправо
    ('==>', CHAR_ARROW_R_DOUBLE),  # Двойная стрелка вправо
    ('<==', CHAR_ARROW_L_DOUBLE),  # Двойная стрелка влево
    ('---', CHAR_MDASH), # Длинное тире
    ('...', CHAR_HELLIP),  # Многоточие
    ('(c)', CHAR_COPY), ('(C)', CHAR_COPY), # Знак авторского права (нижний и верхний регистр)
    ('(r)', CHAR_REG), ('(R)', CHAR_REG), # Знак зарегистрированной торговой марки (нижний и верхний регистр)
    ('(p)', CHAR_COPYP), ('(P)', CHAR_COPYP), # Знак права на звукозапись (нижний и верхний регистр)
    # 2-символьные последовательности
    ('--', CHAR_NDASH), # Среднее тире (дефисные соединения и диапазоны)
    ('~=', CHAR_AP),  # Приблизительно равно (≈)
]


# === КОНСТАНТЫ ДЛЯ КОДИРОВАНИЯ HTML-МНЕМНОИКОВ ===
# --- ЧЕРНЫЙ СПИСОК: Символы, которые НИКОГДА не нужно кодировать в мнемоники ---
NEVER_ENCODE_CHARS = (frozenset(['!', '#', '%', '(', ')', '*', ',', '.', '/', ':', ';', '=', '?', '@',
                                 '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~', '\n', '\t', '\r'])
                      | RU_ALPHABET_FULL | EN_ALPHABET_FULL)

# 2. БЕЛЫЙ СПИСОК (ДЛЯ БЕЗОПАСНОСТИ):
#    Символы, которые ВСЕГДА должны превращаться в мнемоники в "безопасных" режимах вывода. Сюда добавлены символы,
#    которые не видны, на глаз и не отличимы друг от друга в обычном тексте, или очень специфичные
SAFE_MODE_CHARS_TO_MNEMONIC = frozenset([
    '<', '>', '&', '"', '\'',
    CHAR_SHY,  # Мягкий перенос (Soft Hyphen) -- &shy;
    CHAR_NBSP, # Неразрывный пробел (Non-Breaking Space) -- &nbsp;
    '\u2002',  # Полужирный пробел (En Space) -- &ensp;
    '\u2003',  # Широкий пробел (Em Space) -- &emsp;
    '\u2007',  # Цифровой пробел -- &numsp;
    '\u2008',  # Пунктуационный пробел -- &puncsp;
    CHAR_THIN_SP,  # Межсимвольный пробел, тонкий пробел, шпация -- &thinsp;'
    '\u200A',  # Толщина волоса (Hair Space) -- &hairsp;
    '\u200B',  # Негативный пробел (Negative Space) -- &NegativeThinSpace;
    '\u200C',  # Нулевая ширина (без объединения) (Zero Width Non-Joiner) -- &zwj;
    '\u200D',  # Нулевая ширина (с объединением) (Zero Width Joiner) -- &zwnj;
    '\u200E',  # Изменить направление текста на слева-направо (Left-to-Right Mark /LRE) -- &lrm;
    '\u200F',  # Изменить направление текста направо-налево (Right-to-Left Mark /RLM) -- &rlm;
    '\u2010',  # Дефис (Hyphen) -- &dash;
    '\u205F',  # Средний пробел (Medium Mathematical Space) -- &MediumSpace;
    '\u2060',  # &NoBreak;
    '\u2062',  # &InvisibleTimes; -- для семантической разметки математических выражений
    '\u2063',  # &InvisibleComma; -- для семантической разметки математических выражений
    ])

# 3. СПИСОК ДЛЯ ЧИСЛОВОГО КОДИРОВАНИЯ: Символы без стандартного имени.
ALWAYS_ENCODE_TO_NUMERIC_CHARS = frozenset([
    '\u058F',  # Знак армянского драма (֏)
    '\u20B4',  # Знак украинской гривны (₴)
    '\u20B8',  # Знак казахстанского тенге (₸)
    '\u20B9',  # Знак индийской рупии (₹)
    '\u20BA',  # Знак турецкой лиры (₺)
    '\u20BB',  # Знак итальянской лиры (₻)
    '\u20BC',  # Знак азербайджанского маната
    '\u20BD',  # Знак русского рубля (₽)
    '\u20BE',  # Знак грузинский лари (₾)
    '\u20BF',  # Знак биткоина (₿)
])

# 4. СЛОВАРЬ ПРИОРИТЕТОВ: Кастомные и/или предпочитаемые мнемоники.
#    Некоторые utf-символы имеют несколько мнемоник, а значит для таких символов преобразование
#    в из utf во html-мнемоники может иметь несколько вариантов. Словарь приоритетов задает предпочтительное
#    преобразование. Эти правила применяются в последнюю очередь и имеют наивысший приоритет,
#    гарантируя предсказуемый результат для символов с несколькими именами.
#
#    Также можно использовать для создания исключений из "черного списка" NEVER_ENCODE_CHARS.
CUSTOM_ENCODE_MAP = {
    # '\u2010': '&hyphen;',  # Для \u2010 всегда предпочитаем &hyphen;, а не &dash;
    # # Исключения для букв, которые есть в алфавитах, но должны кодироваться (для обеспечения консистентности):
    # # 'Æ': '&AElig;',
    # # 'Œ': '&OElig;',
    # # 'æ': '&aelig;',
    # # 'œ': '&oelig;',
    # '\u002a': '&ast;',		# * / &ast; / &midast;
    # '\u005b': '&lsqb;',       # [ / &lsqb; / &lbrack;
    # '\u005d': '&rsqb;',       # ] / &rsqb; / &rbrack;
    # '\u005f': '&lowbar;',     # _ / &lowbar; / &UnderBar;
    # '\u007b': '&lcub;',       # { / &lcub; / &lbrace;
    # '\u007d': '&rcub;',       # } / &rcub; / &rbrace;
    # '\u007c': '&vert;',       # | / &vert; / &verbar; / &VerticalLine;
    CHAR_NBSP: '&nbsp;',      #   / &nbsp; / &NonBreakingSpace;
    CHAR_REG: '&reg;',  # ® / &reg; / &REG; / &circledR;
    CHAR_COPY: '&copy;',  # © / &copy; / &COPY;
    '\u0022': '&quot;',         # " / &quot; / &QUOT;
    '\u0026': '&amp;',          # & / &amp; / &AMP;
    '\u003e': '&gt;',           # > / &gt; / &GT;
    '\u003c': '&lt;',           # < / &lt; / &LT;
    CHAR_MIDDOT: '&middot;',    # · / &middot; / &centerdot; / &CenterDot;
    '\u0060': '&grave;',        # ` / &grave; / &DiacriticalGrave;
    '\u00a8': '&die;',          # ¨ / &die; / &Dot; / &uml; / &DoubleDot;
    '\u00b1': '&pm;',           # ± / &pm; / &PlusMinus;
    '\u00bd': '&half;',         # ½ / &frac12; / &half;
    '\u00af': '&macr;',         # ¯ / &macr; / &strns;
    '\u201a': '&sbquo;',        # ‚ / &sbquo; / &lsquor;
    '\u223e': '&ac;',		    # ∾ / &ac; / &mstpos;
    '\u2207': '&Del;',		    # ∇ / &Del; / &nabla;
    '\u2061': '&af;',		    #   / &af; / &ApplyFunction;
    '\u2221': '&angmsd;',		# ∡ / &angmsd; / &measuredangle;
    CHAR_AP: '&ap;',		    # ≈ / &ap; / &thkap; / &approx; / &TildeTilde; / &thickapprox;
    '\u224a': '&ape;',		    # ≊ / &ape; / &approxeq;
    '\u2254': '&Assign;',		# ≔ / &Assign; / &colone; / &coloneq;
    '\u224d': '&CupCap;',		# ≍ / &CupCap; / &asympeq;
    '\u2233': '&awconint;',		# ∳ / &awconint; / &CounterClockwiseContourIntegral;
    '\u224c': '&bcong;',		# ≌ / &bcong; / &backcong;
    '\u03f6': '&bepsi;',		# ϶ / &bepsi; / &backepsilon;
    '\u2035': '&bprime;',		# ‵ / &bprime; / &backprime;
    '\u223d': '&bsim;',	    	# ∽ / &bsim; / &backsim;
    '\u22cd': '&bsime;',		# ⋍ / &bsime; / &backsimeq;
    '\u2216': '&setmn;',		# ∖ / &setmn; / &ssetmn; / &setminus; / &Backslash; / &smallsetminus;
    '\u2306': '&Barwed;',		# ⌆ / &Barwed; / &doublebarwedge;
    '\u2305': '&barwed;',		# ⌅ / &barwed; / &barwedge;
    '\u23b5': '&bbrk;',		    # ⎵ / &bbrk; / &UnderBracket;
    '\u2235': '&becaus;',		# ∵ / &becaus; / &because; / &Because;
    '\u212c': '&Bscr;',		    # ℬ / &Bscr; / &bernou; / &Bernoullis;
    '\u2264': '&le;',		    # ≤ / &le; / &leq;
    '\u226c': '&twixt;',		# ≬ / &twixt; / &between;
    '\u22c2': '&xcap;',		    # ⋂ / &xcap; / &bigcap; / &Intersection;
    '\u25ef': '&xcirc;',		# ◯ / &xcirc; / &bigcirc;
    '\u22c3': '&xcup;',		    # ⋃ / &xcup; / &Union; / &bigcup;
    '\u2a00': '&xodot;',		# ⨀ / &xodot; / &bigodot;
    '\u2a01': '&xoplus;',		# ⨁ / &xoplus; / &bigoplus;
    '\u2a02': '&xotime;',		# ⨂ / &xotime; / &bigotimes;
    '\u2a06': '&xsqcup;',		# ⨆ / &xsqcup; / &bigsqcup;
    '\u2605': '&starf;',		# ★ / &starf; / &bigstar;
    '\u25bd': '&xdtri;',		# ▽ / &xdtri; / &bigtriangledown;
    '\u25b3': '&xutri;',		# △ / &xutri; / &bigtriangleup;
    '\u2a04': '&xuplus;',		# ⨄ / &xuplus; / &biguplus;
    '\u22c1': '&Vee;',		    # ⋁ / &Vee; / &xvee; / &bigvee;
    '\u22c0': '&Wedge;',		# ⋀ / &Wedge; / &xwedge; / $bigwedge;
    '\u2227': '&and;',		    # ∧ / &and; / &wedge;
    '\u290d': '&rbarr;',		# ⤍ / &rbarr; / &bkarow;
    '\u29eb': '&lozf;',		    # ⧫ / &lozf; / &blacklozenge;
    '\u25ca': '&loz;',		    # ◊ / &loz; / &lozenge
    '\u25aa': '&squf;',		    # ▪ / &squf; / &squarf; / &blacksquare; / &FilledVerySmallSquare;
    '\u25b4': '&utrif;',		# ▴ / &utrif; / &blacktriangle;
    '\u25be': '&dtrif;',		# ▾ / &dtrif; / &blacktriangledown;
    '\u25c2': '&ltrif;',		# ◂ / &ltrif; / &blacktriangleleft;
    '\u25b8': '&rtrif;',		# ▸ / &rtrif; / &blacktriangleright;
    '\u22a5': '&bot;',		    # ⊥ / &bot; / &UpTee; / &bottom; / &perp;
    '\u2500': '&boxh;',		    # ─ / &boxh; / &HorizontalLine;
    '\u229f': '&minusb;',		# ⊟ / &minusb; / &boxminus;
    '\u229e': '&plusb;',		# ⊞ / &plusb; / &boxplus;
    '\u22a0': '&timesb;',		# ⊠ / &timesb; / &boxtimes;
    '\u02d8': '&breve;',		# ˘ / &breve; / &Breve;
    '\u224e': '&bump;',		    # ≎ / &bump; / &Bumpeq; / &HumpDownHump;
    '\u224f': '&bumpe;',		# ≏ / &bumpe; / &bumpeq; / &HumpEqual;
    '\u2145': '&DD;',		    # ⅅ / &DD; / &CapitalDifferentialD;
    '\u02c7': '&caron;',		# ˇ / &Hacek; / &caron;
    '\u212d': '&Cfr;',		    # ℭ / &Cfr; / &Cayleys;
    '\u2713': '&check;',		# ✓ / &check; / &checkmark;
    '\u2257': '&cire;',		    # ≗ / &cire; / &circeq;
    '\u21ba': '&olarr;',		# ↺ / &olarr; / &circlearrowleft;
    '\u21bb': '&orarr;',		# ↻ / &orarr; / &circlearrowright;
    '\u229b': '&oast;',		    # ⊛ / &oast; / &circledast;
    '\u229a': '&ocir;',		    # ⊚ / &ocir; / &circledcirc;
    '\u229d': '&odash;',		# ⊝ / &odash; / &circleddash;
    '\u2299': '&odot;',		    # ⊙ / &odot; / &CircleDot;
    '\u2200': '&forall;',		# ∀ / &forall; / &ForAll;
    '\u24c8': '&oS;',		    # Ⓢ / &oS; / &circledS;
    '\u2296': '&ominus;',		# ⊖ / &ominus; / &CircleMinus;
    '\u2232': '&cwconint;',		# ∲ / &cwconint; / &ClockwiseContourIntegral;
    '\u201d': '&rdquo;',		# ” /  &rdquo; / &rdquor; / &CloseCurlyDoubleQuote;
    '\u2019': '&rsquo;',		# ’ / &rsquo; / &rsquor; / &CloseCurlyQuote;
    '\u2237': '&Colon;',		# ∷ / &Colon; / &Proportion;
    '\u2201': '&comp;',		    # ∁ / &comp; / &complement;
    '\u2218': '&compfn;',		# ∘ / &compfn; / &SmallCircle;
    '\u2102': '&Copf;',		    # ℂ / &Copf; / &complexes;
    '\u222f': '&Conint;',		# ∯ / &Conint; / &DoubleContourIntegral;
    '\u222e': '&oint;',		    # ∮ / &oint; / &conint; / &ContourIntegral;
    '\u2210': '&coprod;',		# ∐ / &coprod; / &Coproduct;
    '\u22de': '&cuepr;',		# ⋞ / &cuepr; / &curlyeqprec;
    '\u22df': '&cuesc;',		# ⋟ / &cuesc; / &curlyeqsucc;
    '\u21b6': '&cularr;',		# ↶ / &cularr; / &curvearrowleft;
    '\u21b7': '&curarr;',		# ↷ / &curarr; / &curvearrowright;
    '\u22ce': '&cuvee;',		# ⋎ / &cuvee; / &curlyvee;
    '\u22cf': '&cuwed;',		# ⋏ / &cuwed; / &curlywedge;
    '\u2010': '&dash;',		    # ‐ / &dash; / &hyphen;
    '\u2ae4': '&Dashv;',		# ⫤ / &Dashv; / &DoubleLeftTee;
    '\u22a3': '&dashv;',		# ⊣ / &dashv; / &LeftTee;
    '\u290f': '&rBarr;',		# ⤏ / &rBarr; / &dbkarow;
    '\u02dd': '&dblac;',		# ˝ / &dblac; / &DiacriticalDoubleAcute;
    '\u2146': '&dd;',		    # ⅆ / &dd; / &DifferentialD;
    '\u21ca': '&ddarr;',		# ⇊ / &ddarr; / &downdownarrows;
    '\u2a77': '&eDDot;',		# ⩷ / &eDDot; / &ddotseq;
    '\u21c3': '&dharl;',		# ⇃ / &dharl; / &LeftDownVector; / &downharpoonleft;
    '\u21c2': '&dharr;',		# ⇂ / &dharr; / &RightDownVector; / &downharpoonright;
    '\u02d9': '&dot;',		    # ˙ / &dot; / &DiacriticalDot;
    '\u222b': '&int;',		    # ∫ / &int; / &Integral;
    '\u22c4': '&diam;',		    # ⋄ / &diam; / &diamond; / &Diamond;
    '\u03b5': '&epsi;',		    # ε / &epsi; / &epsilon;
    '\u03dd': '&gammad;',		# ϝ / &gammad; / &digamma;
    '\u22c7': '&divonx;',		# ⋇ / &divonx; / &divideontimes;
    '\u231e': '&dlcorn;',		# ⌞ / &dlcorn; / &llcorner;
    '\u2250': '&esdot;',		# ≐ / &esdot; / &doteq; / &DotEqual;
    '\u2251': '&eDot;',		    # ≑ / &eDot; / &doteqdot;
    '\u2238': '&minusd;',		# ∸ / &minusd; / &dotminus;
    '\u2214': '&plusdo;',		# ∔ / &plusdo; / &dotplus;
    '\u22a1': '&sdotb;',		# ⊡ / &sdotb; / &dotsquare;
    '\u21d3': '&dArr;',		    # ⇓ / &dArr; / &Downarrow; / &DoubleDownArrow;
    CHAR_ARROW_R_DOUBLE: '&rArr;',  # ⇒ / &rArr; / &Implies; / &Rightarrow; / &DoubleRightArrow;
    CHAR_ARROW_L_DOUBLE: '&lArr;',   # ⇐ / &lArr; / &Leftarrow; / &DoubleLeftArrow;
    CHAR_ARROW_LR_DOUBLE: '&iff;',   # ⇔ / &iff; / &hArr; / &Leftrightarrow; / &DoubleLeftRightArrow;
    CHAR_ARROW_L_LONG_DOUBLE: '&xlArr;',		# ⟸ / &xlArr; / &Longleftarrow; / &DoubleLongLeftArrow;
    CHAR_ARROW_R_LONG_DOUBLE: '&xrArr;',  # ⟹ / &xrArr; / &Longrightarrow; / &DoubleLongRightArrow;
    CHAR_ARROW_LR_LONG_DOUBLE: '&xhArr;',		# ⟺ / &xhArr; / &Longleftrightarrow; / &DoubleLongLeftRightArrow;
    '\u22a8': '&vDash;',		# ⊨ / &vDash; / &DoubleRightTee;
    '\u21d1': '&uArr;',		    # ⇑ / &uArr; / &Uparrow; / &DoubleUpArrow;
    '\u2202': '&part;',         # ∂ / &part; / &PartialD;
    '\u21d5': '&vArr;',		    # ⇕ / &vArr; / &Updownarrow; / &DoubleUpDownArrow;
    '\u2225': '&par;',		    # ∥ / &par; / &spar; / &parallel; / &shortparallel; / &DoubleVerticalBar;
    '\u2193': '&darr;',	   	    # ↓ / &darr; / &downarrow; / &DownArrow; / &ShortDownArrow;
    '\u21f5': '&duarr;',		# ⇵ / &duarr; / &DownArrowUpArrow;
    '\u21bd': '&lhard;',		# ↽ / &lhard; /&DownLeftVector; / &leftharpoondown;
    '\u21c1': '&rhard;',		# ⇁ / &rhard; / &DownRightVector; / &rightharpoondown;
    '\u22a4': '&top;',		    # ⊤ / &top; / &DownTee;
    '\u21a7': '&mapstodown;',	# ↧ / &mapstodown; / &DownTeeArrow;
    '\u2910': '&RBarr;',		# ⤐ / &RBarr; / &drbkarow;
    '\u231f': '&drcorn;',		# ⌟ / &drcorn; / &lrcorner;
    '\u25bf': '&dtri;',		    # ▿ / &dtri; / &triangledown;
    '\u296f': '&duhar;',		# ⥯ / &duhar; / &ReverseUpEquilibrium;
    '\u2256': '&ecir;',		    # ≖ / &ecir; / &eqcirc;
    '\u2255': '&ecolon;',		# ≕ / &ecolon; / &eqcolon;
    '\u2147': '&ee;',		    # ⅇ / &ee; / &exponentiale; / &ExponentialE;
    '\u2252': '&efDot;',		# ≒ / &efDot; / &fallingdotseq;
    '\u2a96': '&egs;',		    # ⪖ / &egs; / &eqslantgtr;
    '\u2208': '&in;',		    # ∈ / &in; / &isin; / &isinv; / &Element;
    '\u2a95': '&els;',		    # ⪕ / &els; / &eqslantless;
    '\u2205': '&empty;',		# ∅ / &empty; / &emptyv; / &emptyset; / &varnothing;
    '\u03f5': '&epsiv;',		# ϵ / &epsiv; / &varepsilon; / &straightepsilon;
    '\u2242': '&esim;',		    # ≂ / &esim; / &eqsim; / &EqualTilde;
    '\u225f': '&equest;',		# ≟ / &equest; / &questeq;
    '\u21cc': '&rlhar;',		# ⇌ / &rlhar; / &Equilibrium; / &rightleftharpoons;
    '\u2253': '&erDot;',		# ≓ / &erDot; / &risingdotseq;
    '\u2130': '&Escr;',		    # ℰ / &Escr; / &expectation;
    '\u22d4': '&fork;',		    # ⋔ / &fork; / &pitchfork;
    '\u2131': '&Fscr;',		    # ℱ / &Fscr; / &Fouriertrf;
    '\u2322': '&frown;',		# ⌢ / &frown; / &sfrown;
    '\u2a86': '&gap;',		    # ⪆ / &gap; / &gtrapprox;
    '\u2267': '&gE;',		    # ≧ / &gE; / &geqq; / &GreaterFullEqual;
    '\u2a8c': '&gEl;',	  	    # ⪌ / &gEl; / &gtreqqless;
    '\u22db': '&gel;',		    # ⋛ / &gel; / &gtreqless; / &GreaterEqualLess;
    '\u2265': '&ge;',		    # ≥ / &ge; / &geq; / &GreaterEqual;
    '\u2a7e': '&ges;',		    # ⩾ / &ges; / &geqslant; / &GreaterSlantEqual;
    '\u22d9': '&Gg;',		    # ⋙ / &Gg; / &ggg;
    '\u226b': '&gg;',		    # ≫ / &gg ;/ &Gt; / &NestedGreaterGreater;
    '\u2277': '&gl;',		    # ≷ / &gl; / &gtrless; / &GreaterLess;
    '\u2a8a': '&gnap;',		    # ⪊ / &gnap; / &gnapprox;
    '\u2269': '&gnE;',		    # ≩ / &gnE; / &gneqq;
    '\u2260': '&ne;',		    # ≠ / &ne; / &NotEqual;
    '\u2a88': '&gne;',		    # ⪈ / &gne; / &gneq;
    '\u2273': '&gsim;',		    # ≳ / &gsim; / &gtrsim; / &GreaterTilde;
    '\u22d7': '&gtdot;',		# ⋗ / &gtdot; / &gtrdot;
    '\u200a': '&hairsp;',		#   / &hairsp; / &VeryThinSpace;
    '\u210b': '&Hscr;',		    # ℋ / &Hscr; / &hamilt; / &HilbertSpace;
    '\u21ad': '&harrw;',		# ↭ / &harrw; / &leftrightsquigarrow;
    '\u210f': '&hbar;',		    # ℏ / &hbar; / &planck; / &hslash; / &plankv;
    '\u210c': '&Hfr;',		    # ℌ / &Hfr; / &Poincareplane;
    '\u2925': '&searhk;',		# ⤥ / &searhk; / &hksearow;
    '\u2926': '&swarhk;',		# ⤦ / &swarhk; / &hkswarow;
    '\u21a9': '&larrhk;',		# ↩ / &larrhk; / &hookleftarrow;
    '\u21aa': '&rarrhk;',		# ↪ / &rarrhk; / &hookrightarrow;
    '\u210d': '&Hopf;',		    # ℍ / &Hopf; / &quaternions;
    '\u2063': '&ic;',		    # ⁣ / &ic; / &InvisibleComma;
    '\u2111': '&Im;',		    # ℑ / &Im; / &Ifr; / &image; / &imagpart;
    '\u2148': '&ii;',		    # ⅈ / &ii; / &ImaginaryI;
    '\u2a0c': '&qint;',		    # ⨌ / &qint; / &iiiint;
    '\u222d': '&tint;',		    # ∭ / &tint; / &iiint;
    '\u2110': '&Iscr;',		    # ℐ / &Iscr; / &imagline;
    '\u0131': '&imath;',		# ı / &imath; / &inodot;
    '\u22ba': '&intcal;',		# ⊺ / &intcal; / &intercal;
    '\u2124': '&Zopf;',		    # ℤ / &Zopf; / &integers;
    '\u2a3c': '&iprod;',		# ⨼ / &iprod; / &intprod;
    '\u2062': '&it;',		    # ⁢ / &it; / &InvisibleTimes;
    '\u03f0': '&kappav;',		# ϰ / &kappav; / &varkappa;
    '\u21da': '&lAarr;',		# ⇚ / &lAarr; / &Lleftarrow;
    '\u2112': '&Lscr;',		    # ℒ / &Lscr; / &lagran; / &Laplacetrf;
    '\u27e8': '&lang;',		    # ⟨ / &lang; / &langle; / &LeftAngleBracket;
    '\u2a85': '&lap;',		    # ⪅ / &lap; / &lessapprox;
    '\u219e': '&Larr;',		    # ↞ / &Larr; / &twoheadleftarrow;
    '\u21e4': '&larrb;',		# ⇤ / &larrb; / &LeftArrowBar;
    '\u21ab': '&larrlp;',		# ↫ / &larrlp; / &looparrowleft;
    '\u21a2': '&larrtl;',		# ↢ / &larrtl; / &leftarrowtail;
    '\u2266': '&lE;',		    # ≦ / &lE; / &leqq; / &LessFullEqual;
    '\u2190': '&larr;',		    # ← / &larr; / &slarr; / &LeftArrow; / &leftarrow; / &ShortLeftArrow;
    '\u21c6': '&lrarr;',		# ⇆ / &lrarr; / &leftrightarrows; / &LeftArrowRightArrow;
    '\u27e6': '&lobrk;',		# ⟦ / &lobrk; / &LeftDoubleBracket;
    '\u21bc': '&lharu;',		# ↼ / &lharu; / &LeftVector; / &leftharpoonup;
    '\u21c7': '&llarr;',		# ⇇ / &llarr; / &leftleftarrows;
    '\u2194': '&harr;',		    # ↔ / &harr; / &leftrightarrow; / &LeftRightArrow;
    '\u21cb': '&lrhar;',		# ⇋ / &lrhar; / &leftrightharpoons; / &ReverseEquilibrium;
    '\u21a4': '&mapstoleft;',	# ↤ / &mapstoleft; / &LeftTeeArrow;
    '\u22cb': '&lthree;',		# ⋋ / &lthree; / &leftthreetimes;
    '\u22b2': '&vltri;',		# ⊲ / &vltri; / &LeftTriangle; / &vartriangleleft;
    '\u22b4': '&ltrie;',		# ⊴ / &ltrie; / &trianglelefteq; / &LeftTriangleEqual;
    '\u21bf': '&uharl;',		# ↿ / &uharl; / &LeftUpVector; / &upharpoonleft;
    '\u2308': '&lceil;',        # ⌈ / &lceil; / &LeftCeiling;
    '\u230a': '&lfloor;',       # ⌊ / &lfloor; / &LeftFloor;
    '\u2a8b': '&lEg;',		    # ⪋ / &lEg; / &lesseqqgtr;
    '\u22da': '&leg;',		    # ⋚ / &leg; / &lesseqgtr; / &LessEqualGreater;
    '\u2a7d': '&les;',		    # ⩽ / &les; / &leqslant; / &LessSlantEqual;
    '\u22d6': '&ltdot;',		# ⋖ / &ltdot; / &lessdot;
    '\u2276': '&lg;',		    # ≶ / &lg; / &lessgtr; / &LessGreater;
    '\u2272': '&lsim;',		    # ≲ / &lsim; / &lesssim; / &LessTilde;
    '\u226a': '&ll;',		    # ≪ / &ll; / &Lt; / &NestedLessLess;
    '\u23b0': '&lmoust;',		# ⎰ / &lmoust; / &lmoustache;
    '\u2a89': '&lnap;',		    # ⪉ / &lnap; / &lnapprox;
    '\u2268': '&lnE;',		    # ≨ / &lnE; / &lneqq;
    '\u2a87': '&lne;',		    # ⪇ / &lne; / &lneq;
    CHAR_ARROW_L: '&xlarr;',		# ⟵ / &xlarr; / &longleftarrow; / &LongLeftArrow;
    CHAR_ARROW_R: '&xrarr;',  # ⟶ / &xrarr; / &LongRightArrow; / &longrightarrow;
    CHAR_ARROW_LR: '&xharr;',		# ⟷ / &xharr; / &longleftrightarrow; / &LongLeftRightArrow;
    '\u27fc': '&xmap;',		    # ⟼ / &xmap; / &longmapsto;
    '\u21ac': '&rarrlp;',		# ↬ / &rarrlp; / &looparrowright;
    '\u201e': '&bdquo;',		# „ / &bdquo; / &ldquor;
    '\u2199': '&swarr;',		# ↙ / &swarr; / &swarrow; / &LowerLeftArrow;
    '\u2198': '&searr;',		# ↘ / &searr; / &searrow; / &LowerRightArrow;
    '\u21b0': '&lsh;',		    # ↰ / &Lsh; / &lsh;
    '\u25c3': '&ltri;',		    # ◃ / &ltri; / &triangleleft;
    '\u2720': '&malt;',		    # ✠ / &malt; / &maltese;
    '\u21a6': '&map;',		    # ↦ / &map; / &mapsto; / &RightTeeArrow;
    '\u21a5': '&mapstoup;',		# ↥ / &mapstoup; / &UpTeeArrow;
    '\u2133': '&Mscr;',		    # ℳ / &Mscr; / &phmmat; / &Mellintrf;
    '\u2223': '&mid;',		    # ∣ / &mid; / &smid; / &shortmid; / &VerticalBar;
    '\u2213': '&mp;',		    # ∓ / &mp; / &mnplus; / &MinusPlus;
    CHAR_HELLIP: '&mldr;',	    # … / &mldr; / &hellip;
    '\u22b8': '&mumap;',		# ⊸ / &mumap; / &multimap;
    '\u2249': '&nap;',		    # ≉ / &nap; / &napprox; / &NotTildeTilde;
    '\u266e': '&natur;',		# ♮ / &natur; / &natural;
    '\u2115': '&Nopf;',		    # ℕ / &Nopf; / &naturals;
    '\u2247': '&ncong;',		# ≇ / &ncong; / &NotTildeFullEqual;
    '\u2197': '&nearr;',		# ↗ / &nearr; / &nearrow; / &UpperRightArrow;
    '\u200b': '&ZeroWidthSpace;',		#   / &ZeroWidthSpace; / &NegativeThinSpace; / &NegativeMediumSpace;
                                        # &NegativeThickSpace; / &NegativeVeryThinSpace;
    '\u2262': '&nequiv;',		# ≢ / &nequiv; / &NotCongruent;
    '\u2928': '&toea;',		    # ⤨ / &toea; / &nesear;
    '\u2203': '&exist;',		# ∃ / &exist; / &Exists;
    '\u2204': '&nexist;',		# ∄ / &nexist; / &nexists; / &NotExists;
    '\u2271': '&nge;',		    # ≱ / &nge; / &ngeq; / &NotGreaterEqual;
    '\u2275': '&ngsim;',		# ≵ / &ngsim; / &NotGreaterTilde;
    '\u226f': '&ngt;',		    # ≯ / &ngt; / &ngtr; / &NotGreater;
    '\u21ce': '&nhArr;',		# ⇎ / &nhArr; / &nLeftrightarrow;
    '\u21ae': '&nharr;',		# ↮ / &nharr; / &nleftrightarrow;
    '\u220b': '&ni;',		    # ∋ / &ni; / &niv; / &SuchThat; / &ReverseElement;
    '\u21cd': '&nlArr;',		# ⇍ / &nlArr; / &nLeftarrow;
    '\u219a': '&nlarr;',		# ↚ / &nlarr; / &nleftarrow;
    '\u2270': '&nle;',		    # ≰ / &nle; / &nleq; / &NotLessEqual;
    '\u226e': '&nlt;',		    # ≮ / &nlt; / &nless; / &NotLess;
    '\u2274': '&nlsim;',		# ≴ / &nlsim; / &NotLessTilde;
    '\u22ea': '&nltri;',		# ⋪ / &nltri; / &ntriangleleft; / &NotLeftTriangle;
    '\u22ec': '&nltrie;',		# ⋬ / &nltrie; / &ntrianglelefteq; / &NotLeftTriangleEqual;
    '\u2224': '&nmid;',		    # ∤ / &nmid; / &nsmid; / &nshortmid; / &NotVerticalBar;
    '\u2226': '&npar;',		    # ∦ / &npar; / &nspar; / &nparallel; / &nshortparallel; / &NotDoubleVerticalBar;
    '\u2209': '&notin;',		# ∉ / &notin; / &notinva; / &NotElement;
    '\u2279': '&ntgl;',		    # ≹ / &ntgl; / &NotGreaterLess;
    '\u2278': '&ntlg;',		    # ≸ / &ntlg; / &NotLessGreater;
    '\u220c': '&notni;',		# ∌ / &notni; / &notniva; / &NotReverseElement;
    '\u2280': '&npr;',		    # ⊀ / &npr; / &nprec; / &NotPrecedes;
    '\u22e0': '&nprcue;',		# ⋠ / &nprcue; / &NotPrecedesSlantEqual;
    '\u22eb': '&nrtri;',		# ⋫ / &nrtri; / &ntriangleright; / &NotRightTriangle;
    '\u22ed': '&nrtrie;',		# ⋭ / &nrtrie; / &ntrianglerighteq; / &NotRightTriangleEqual;
    '\u22e2': '&nsqsube;',		# ⋢ / &nsqsube; / &NotSquareSubsetEqual;
    '\u22e3': '&nsqsupe;',		# ⋣ / &nsqsupe; / &NotSquareSupersetEqual;
    '\u2288': '&nsube;',		# ⊈ / &nsube; / &nsubseteq; / &NotSubsetEqual;
    '\u2281': '&nsc;',		    # ⊁ / &nsc; / &nsucc; / &NotSucceeds;
    '\u22e1': '&nsccue;',		# ⋡ / &nsccue; / &NotSucceedsSlantEqual;
    '\u2289': '&nsupe;',		# ⊉ / &nsupe; / &nsupseteq; / &NotSupersetEqual;
    '\u2241': '&nsim;',		    # ≁ / &nsim; / &NotTilde;
    '\u2244': '&nsime;',		# ≄ / &nsime; / &nsimeq; / &NotTildeEqual;
    '\u21cf': '&nrArr;',		# ⇏ / &nrArr; / &nRightarrow;
    '\u219b': '&nrarr;',		# ↛ / &nrarr; / &nrightarrow;
    '\u2196': '&nwarr;',		# ↖ / &nwarr; / &nwarrow; / &UpperLeftArrow;
    '\u2134': '&oscr;',		    # ℴ / &oscr; / &order; / &orderof;
    '\u203e': '&oline;',		#  ̄ / &oline; / &OverBar;
    '\u23b4': '&tbrk;',		    # ⎴ / &tbrk; / &OverBracket;
    '\u03d6': '&piv;',          # ϖ / &piv; / &varpi;
    '\u03d5': '&phiv;',		    # ϕ / &phiv; / &varphi; / &straightphi;
    '\u2665': '&hearts;',		# ♥ / &hearts; / &heartsuit; /
    '\u2119': '&Popf;',		    # ℙ / &Popf; / &primes;
    '\u227a': '&pr;',		    # ≺ / &pr; / &prec; / &Precedes;
    '\u2ab7': '&prap;',		    # ⪷ / &prap; / &precapprox;
    '\u227c': '&prcue;',		# ≼ / &prcue; / &preccurlyeq; / &PrecedesSlantEqual;
    '\u2aaf': '&pre;',		    # ⪯ / &pre; / &preceq; / &PrecedesEqual;
    '\u227e': '&prsim;',		# ≾ / &prsim; / &precsim; / &PrecedesTilde;
    '\u2ab9': '&prnap;',		# ⪹ / &prnap; / &precnapprox;
    '\u2ab5': '&prnE;',		    # ⪵ / &prnE; / &precneqq;
    '\u22e8': '&prnsim;',		# ⋨ / &prnsim; / &precnsim;
    '\u220f': '&prod;',         # ∏ / &prod; / &Product;
    '\u221d': '&prop;',		    # ∝ / &prop; / &vprop; / &propto; / &varpropto; / &Proportional;
    '\u211a': '&Qopf;',		    # ℚ / &Qopf; / &rationals;
    '\u21db': '&rAarr;',		# ⇛ / &rAarr; / &Rrightarrow;
    '\u27e9': '&rang;',		    # ⟩ / &rang; / &rangle; / &RightAngleBracket;
    '\u21a0': '&Rarr;',		    # ↠ / &Rarr; / &twoheadrightarrow;
    '\u21e5': '&rarrb;',		# ⇥ / &rarrb; / &RightArrowBar;
    '\u21a3': '&rarrtl;',		# ↣ / &rarrtl; / &rightarrowtail;
    '\u2309': '&rceil;',        # ⌉ / &rceil; / &RightCeiling;
    '\u219d': '&rarrw;',		# ↝ / &rarrw; / &rightsquigarrow;
    '\u03a9': '&ohm;',          # Ω / &ohm; / &Omega;
    '\u211c': '&Re;',		    # ℜ / &real; / &Re; / &Rfr; / &realpart;
    '\u211b': '&Rscr;',		    # ℛ / &Rscr; / &realine;
    '\u211d': '&Ropf;',		    # ℝ / &Ropf; / &reals;
    '\u21c0': '&rharu;',		# ⇀ / &rharu; / &RightVector; / &rightharpoonup;
    '\u03f1': '&rhov;',		    # ϱ / &rhov; / &varrho;
    '\u2192': '&rarr;',		    # → / &rarr; / &srarr; / &rightarrow; / &RightArrow; / &ShortRightArrow;
    '\u21c4': '&rlarr;',		# ⇄ / &rlarr; / &rightleftarrows; / &RightArrowLeftArrow;
    '\u27e7': '&robrk;',		# ⟧ / &robrk; / &RightDoubleBracket;
    '\u230b': '&rfloor;',       # ⌋ / &rfloor; / &RightFloor;
    '\u21c9': '&rrarr;',		# ⇉ / &rrarr; / &rightrightarrows;
    '\u22a2': '&vdash;',		# ⊢ / &vdash; / &RightTee;
    '\u22cc': '&rthree;',		# ⋌ / &rthree; / &rightthreetimes;
    '\u22b3': '&vrtri;',		# ⊳ / &vrtri; / &RightTriangle; / &vartriangleright;
    '\u22b5': '&rtrie;',		# ⊵ / &rtrie; / &trianglerighteq; / &RightTriangleEqual;
    '\u21be': '&uharr;',		# ↾ / &uharr; / &RightUpVector; / &upharpoonright;
    '\u23b1': '&rmoust;',		# ⎱ / &rmoust; / &rmoustache;
    '\u201c': '&ldquo;',        # “ / &ldquo; / &OpenCurlyDoubleQuote;
    '\u2018': '&lsquo;',        # ‘ / &lsquo; / &OpenCurlyQuote;
    '\u21b1': '&rsh;',		    # ↱ / &rsh; / &Rsh;
    '\u25b9': '&rtri;',		    # ▹ / &rtri; / &triangleright;
    '\u227b': '&sc;',		    # ≻ / &sc; / &succ; / &Succeeds;
    '\u2ab8': '&scap;',		    # ⪸ / &scap; / &succapprox;
    '\u227d': '&sccue;',		# ≽ / &sccue; / &succcurlyeq; / &SucceedsSlantEqual;
    '\u2ab0': '&sce;',		    # ⪰ / &sce; / &succeq; / &SucceedsEqual;
    '\u2aba': '&scnap;',		# ⪺ / &scnap; / &succnapprox;
    '\u2ab6': '&scnE;',		    # ⪶ / &scnE; / &succneqq;
    '\u22e9': '&scnsim;',		# ⋩ / &scnsim; / &succnsim;
    '\u227f': '&scsim;',		# ≿ / &scsim; / &succsim; / &SucceedsTilde;
    '\u2929': '&tosa;',		    # ⤩ / &tosa; / &seswar;
    '\u03c2': '&sigmaf;',		# ς / &sigmaf; / &sigmav; / &varsigma;
    '\u2243': '&sime;',		    # ≃ / &sime; / &simeq; / &TildeEqual;
    '\u2323': '&smile;',		# ⌣ / &smile; / &ssmile;
    '\u2660': '&spades;',		# ♠ / &spades; / &spadesuit; /
    '\u2293': '&sqcap;',		# ⊓ / &sqcap; / &SquareIntersection;
    '\u2294': '&sqcup;',		# ⊔ / &sqcup; / &SquareUnion;
    '\u221a': '&Sqrt;',		    # √ / &Sqrt; / &radic;
    '\u228f': '&sqsub;',		# ⊏ / &sqsub; / &sqsubset; / &SquareSubset;
    '\u2291': '&sqsube;',		# ⊑ / &sqsube; / &sqsubseteq; / &SquareSubsetEqual;
    '\u2290': '&sqsup;',		# ⊐ / &sqsup; / &sqsupset; / &SquareSuperset;
    '\u2292': '&sqsupe;',		# ⊒ / &sqsupe; / &sqsupseteq; / &SquareSupersetEqual;
    '\u25a1': '&squ;',		    # □ / &squ; / &Square; / &square;
    '\u22c6': '&Star;',		    # ⋆ / &Star; / &sstarf;
    '\u22d0': '&Sub;',		    # ⋐ / &Sub; / &Subset;
    '\u2282': '&sub;',		    # ⊂ / &sub; / &subset;
    '\u2ac5': '&subE;',		    # ⫅ / &subE; / &subseteqq;
    '\u2acb': '&subnE;',		# ⫋ / &subnE; / &subsetneqq;
    '\u228a': '&subne;',		# ⊊ / &subne; / &subsetneq;
    '\u2286': '&sube;',		    # ⊆ / &sube; / &subseteq; / &SubsetEqual;
    '\u2211': '&sum;',		    # ∑ / &sum; / &Sum;
    '\u22d1': '&Sup;',		    # ⋑ / &Sup; / &Supset;
    '\u2ac6': '&supE;',		    # ⫆ / &supE; / &supseteqq;
    '\u2283': '&sup;',		    # ⊃ / &sup; / &supset; / &Superset;
    '\u2287': '&supe;', 		# ⊇ / &supe; / &supseteq; / &SupersetEqual;
    '\u2acc': '&supnE;',		# ⫌ / &supnE; / &supsetneqq;
    '\u228b': '&supne;',		# ⊋ / &supne; / &supsetneq;
    '\u223c': '&sim;',          # ∼ / &sim; / &Tilde; / &thksim; / &thicksim;
    '\u2245': '&cong;',         # ≅ / &cong; / &TildeFullEqual;
    '\u20db': '&tdot;',		    # ⃛ / &tdot; / &TripleDot;
    '\u2234': '&there4;',		# ∴ / &there4; / &Therefore; / &therefore;
    '\u03d1': '&thetav;',		# ϑ / &thetav; / &vartheta; / &thetasym;
    CHAR_TRADE: '&trade;',		# ™ / &trade; / &TRADE;
    '\u25b5': '&utri;',		    # ▵ / &utri; / &triangle;
    '\u225c': '&trie;',		    # ≜ / &trie; / &triangleq;
    '\u21c5': '&udarr;',		# ⇅ / &udarr; / &UpArrowDownArrow;
    '\u296e': '&udhar;',		# ⥮ / &udhar; / &UpEquilibrium;
    '\u231c': '&ulcorn;',		# ⌜ / &ulcorn; / &ulcorner;
    '\u03d2': '&Upsi;',         # ϒ / &Upsi; / &upsih;
    '\u03c5': '&upsi;',		    # υ / &upsi; / &upsilon;
    '\u228e': '&uplus;',		# ⊎ / &uplus; / &UnionPlus;
    '\u2195': '&varr;',		    # ↕ / &varr; / &updownarrow; / &UpDownArrow;
    '\u2191': '&uarr;',         # ↑ / &uarr; / &uparrow; / &UpArrow; / &ShortUpArrow;
    '\u21c8': '&uuarr;',		# ⇈ / &uuarr; / &upuparrows;
    '\u231d': '&urcorn;',		# ⌝ / &urcorn; / &urcorner;
    '\u2016': '&Vert;',		    # ‖ / &Vert; / &Verbar;
    '\u2228': '&or;',		    # ∨ / &or; / &vee;
    CHAR_THIN_SP: '&thinsp;',	#   / &thinsp; / &ThinSpace;
    '\u2240': '&wr;',		    # ≀ / &wr; / &wreath; / &VerticalTilde;
    '\u2128': '&Zfr;',		    # ℨ / &Zfr; / &zeetrf;
    '\u2118': '&wp;',           # ℘ / &wp; / &weierp;
}

# === Динамическая генерация карт преобразования ===

def _build_translation_maps() -> dict[str, str]:
    """
    Создает карту для кодирования на лету, используя все доступные источники
    из html.entities и строгий порядок приоритетов для обеспечения
    предсказуемого и детерминированного результата.
    """
    # ШАГ 1: Создаем ЕДИНУЮ и ПОЛНУЮ карту {каноническое_имя: числовой_код}.
    # Это решает проблему разных форматов и дубликатов с точкой с запятой.
    unified_name2codepoint = {}

    # Сначала обрабатываем большой исторический словарь.
    for name, codepoint in entities.name2codepoint.items():
        # Нормализуем имя СРАЗУ, убирая опциональную точку с запятой (в html.entities предусмотрено, что иногда
        # символ `;` не ставится всякими неаккуратными верстальщиками и парсерами).
        canonical_name = name.rstrip(';')
        unified_name2codepoint[canonical_name] = codepoint
    # Затем обновляем его современным стандартом html5.
    # Это гарантирует, что если мнемоника есть в обоих, будет использована версия из html5.
    for name, char in entities.html5.items():
        # НОВОЕ: Проверяем, что значение является ОДИНОЧНЫМ символом.
        # Наш кодек, основанный на str.translate, не может обрабатывать
        # мнемоники, которые соответствуют строкам из нескольких символов
        # (например, символ + вариативный селектор). Мы их игнорируем.
        if len(char) != 1:
            continue
        # Нормализуем имя СРАЗУ.
        canonical_name = name.rstrip(';')
        unified_name2codepoint[canonical_name] = ord(char)

    # Теперь у нас есть полный и консистентный словарь unified_name2codepoint.
    # На его основе строим нашу карту для кодирования.
    encode_map = {}

    # ШАГ 2: Высший приоритет. Загружаем наши кастомные правила.
    encode_map.update(CUSTOM_ENCODE_MAP)

    # ШАГ 3: Следующий приоритет. Добавляем числовое кодирование.
    for char in ALWAYS_ENCODE_TO_NUMERIC_CHARS:
        if char not in encode_map:
            encode_map[char] = f'&#{ord(char)};'

    # ШАГ 4: Низший приоритет. Заполняем все остальное из нашей
    # объединенной и нормализованной карты unified_name2codepoint.
    for name, codepoint in unified_name2codepoint.items():
        char = chr(codepoint)
        if char not in encode_map and char not in NEVER_ENCODE_CHARS:
            # Теперь 'name' - это уже каноническое имя без ';',
            # поэтому дополнительная нормализация не нужна. Код стал проще!
            encode_map[char] = f'&{name};'

    return encode_map


# Создаем карту один раз при импорте модуля.
ENCODE_MAP = _build_translation_maps()

# --- Публичный API модуля ---
def get_encode_map():
    """Возвращает готовую карту для кодирования."""
    return ENCODE_MAP


# === КОНСТАНТЫ ДЛЯ ЕДИНИЦ ИЗМЕРЕНИЯ ===
# ТОЛЬКО АТОМАРНЫЕ единицы измерения: 'г', 'м', 'с', 'км', 'кв', 'куб', 'ч' и так далее.
# Никаких сложных и составных, типа: 'кв.м.', 'км/ч' или "до н.э." ...
# Пост-позиционные (можно ставить точку после, но не обязательно) (км, г., с.)
DEFAULT_POST_UNITS = [
    # Русские
    # --- Время и эпохи ---
    'гг', 'г.', 'в.', 'вв', 'н', 'э', 'сек', 'с.', 'мин', 'ч',
    # --- Масса и объём ---
    'кг', 'мг', 'ц', 'т', 'л', 'мл',
    # --- Размеры ---
    'кв', 'куб', 'мм', 'см', 'м', 'км', 'сот', 'га', 'м²', 'м³',
    # --- Финансы и количество ---
    'руб', 'коп', 'тыс', 'млн', 'млрд', 'трлн', 'трлрд', 'шт', 'об', 'ящ', 'уп', 'кор', 'пар', 'комп',
    # --- Издательское дело ---
    'пп', 'стр', 'рис', 'гр', 'табл', 'гл', 'п', 'пт', 'гл', 'том', 'т.', 'кн', 'илл', 'ред', 'изд', 'пер',
    # --- Физические и технические ---
    'дБ', 'Вт', 'кВт', 'МВт', 'ГВт', 'А', 'В', 'Ом', 'Па', 'кПа', 'МПа', 'Бар', 'кБар', 'Гц', 'кГц', 'МГц', 'ГГц',
    'рад', 'К', '°C', '°F', '%', 'мкм', 'нм', 'А°', 'эВ', 'Дж', 'кДж', 'МДж', 'пкФ', 'нФ', 'мкФ', 'мФ', 'Ф',
    'Гн', 'мГн', 'мкГн', 'Тл', 'Гс', 'эрг', 'бод', 'бит', 'байт', 'Кб', 'Мб', 'Гб', 'Тб', 'Пб', 'Эб', 'кал', 'ккал',
    # Английские
    # --- Издательское дело ---
    'pp', 'p', 'para', 'sect', 'fig', 'vol', 'ed', 'rev', 'dpi',
    # --- Имперские и американские единицы ---
    'in', 'ft', 'yd', 'mi', 'oz', 'lb', 'st', 'pt', 'qt', 'gal', 'mph', 'rpm', 'hp', 'psi', 'cal',
]
# Пред-позиционные (№ 5, $ 10)
DEFAULT_PRE_UNITS = ['№', '$', '€', '£', '₽', '#', '§', '¤', '₴', '₿', '₺', '₦', '₩', '₪', '₫', '₲', '₡', '₵',
                     'ГОСТ', 'ТУ', 'ИСО', 'DIN', 'ASTM', 'EN', 'IEC', 'IEEE'] # технические стандарты перед числом работают как единицы измерения

# Операторы, которые могут стоять между единицами измерения (км/ч)
# Сложение и вычитание здесь намеренно отсутствуют.
UNIT_MATH_OPERATORS = ['/', '*', '×', CHAR_MIDDOT, '÷']

# === КОНСТАНТЫ ДЛЯ ФИНАЛЬНЫХ СОКРАЩЕНИЙ ===
# Эти сокращения (обычно в конце фразы) будут "склеены" тонкой шпацией, а перед ними будет поставлен неразрывный пробел.
# Важно, чтобы многосложные сокращения (типа "и т. д.") были в списке с разделителем пробелом (иначе мы не сможем их найти).
ABBR_COMMON_FINAL = [
     # 'т. д.', 'т. п.', 'др.', 'пр.',
     # УБРАНЫ из-за неоднозначности: др. -- "другой", "доктор", "драм" / пр. -- "прочие", "профессор", "проект", "проезд" ...
    'т. д.', 'т. п.',
]

ABBR_COMMON_PREPOSITION = [
    'т. е.', 'т. к.', 'т. о.', 'т. ч.',
    'и. о.', 'ио', 'вр. и. о.', 'врио',
    'тов.', 'г-н.', 'г-жа.', 'им.',
    'д. о. с.', 'д. о. н.', 'д. м. н.', 'к. т. д.', 'к. т. п.',
    'АО', 'ООО', 'ЗАО', 'ПАО', 'НКО', 'ОАО', 'ФГУП', 'НИИ', 'ПБОЮЛ', 'ИП',
]