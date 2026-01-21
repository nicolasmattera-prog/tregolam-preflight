import re
from spellchecker import SpellChecker

spell = SpellChecker(language="es")
WORD_RE = re.compile(r"\b[^\W\d_]+\b", re.UNICODE)

def corregir_ortografia(texto: str) -> str:
    words = WORD_RE.findall(texto)
    if not words:
        return texto

    lower_map = {}
    for w in words:
        wl = w.lower()
        lower_map.setdefault(wl, w)

    unknown = spell.unknown(lower_map.keys())

    def repl(m):
        w = m.group(0)
        wl = w.lower()
        if wl not in unknown:
            return w
        corr = spell.correction(wl) or w
        # respeta mayúscula inicial
        if w[:1].isupper():
            corr = corr[:1].upper() + corr[1:]
        return corr

    return WORD_RE.sub(repl, texto)
