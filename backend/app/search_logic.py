import re
import difflib
from typing import Optional, Tuple, List

COMMON_MODELS = [
    "cobalt", "jentra", "spark", "nexia", "lacetti", "malibu", "gentra",
    "matiz", "damas", "tracker", "captiva", "onix", "epica",
]

TRANSLIT_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "j", "з": "z",
    "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sh",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    "қ": "q", "ғ": "g", "ў": "o", "ҳ": "h", "і": "i",
}

SYNONYM_RULES = [
    (r"\b(фара|fara|far|headlight|lamp|lampa)\b", "fara"),
    (r"\b(old\s*fara|old\s*far|old\s*headlight|стар(ый|ая)\s*фара)\b", "old fara"),
    (r"\b(orqa\s*fara|rear\s*light|tail\s*light|задн(яя|ий)\s*фара)\b", "orqa fara"),
    (r"\b(амортизатор|amortizator|amort|mortizator|стойка)\b", "amortizator"),
    (r"\b(шина|tire|tyre)\b", "shina"),
    (r"\b(диск|disk|wheel)\b", "disk"),
]


def normalize_query(q: str) -> str:
    q = (q or "").lower().strip()
    q = re.sub(r"\s+", " ", q)
    return q


def translit_ru_to_lat(text: str) -> str:
    return "".join(TRANSLIT_MAP.get(ch, ch) for ch in (text or "").lower())


def canonicalize_synonyms(q: str) -> str:
    q = (q or "").lower()
    for pattern, repl in SYNONYM_RULES:
        q = re.sub(pattern, repl, q)
    return re.sub(r"\s+", " ", q).strip()


def build_query_variants(raw_q: str) -> List[str]:
    v = []
    a = normalize_query(raw_q)
    b = canonicalize_synonyms(a)
    c = normalize_query(translit_ru_to_lat(a))
    d = canonicalize_synonyms(c)
    for x in (a, b, c, d):
        if x and x not in v:
            v.append(x)
    return v[:4]


def guess_model_token(token: str) -> Optional[str]:
    token = (token or "").lower().strip()
    if not token:
        return None
    if token in COMMON_MODELS:
        return token
    matches = difflib.get_close_matches(token, COMMON_MODELS, n=1, cutoff=0.70)
    return matches[0] if matches else None


def detect_model_anywhere(nq: str) -> Tuple[Optional[str], str, float]:
    tokens = [t for t in nq.split(" ") if t]
    if not tokens:
        return None, nq, 0.0

    best_model = None
    best_conf = 0.0
    best_idx = None

    for i, tok in enumerate(tokens):
        m = guess_model_token(tok)
        if m:
            conf = 1.0 if tok == m else 0.85
            if conf > best_conf:
                best_model = m
                best_conf = conf
                best_idx = i

    if not best_model:
        return None, nq, 0.0

    remaining = " ".join(t for j, t in enumerate(tokens) if j != best_idx).strip()
    return best_model, remaining, best_conf
