import os
import re
from hunspell import HunSpell

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_DIR = os.path.join(BASE_DIR, "dicts")

h = HunSpell(
    os.path.join(DICT_DIR, "es_ES.dic"),
    os.path.join(DICT_DIR, "es_ES.aff"),
)

WORD_RE = re.compile(r"\b[^\W\d_]+\b", re.UNICODE)

def corregir_ortografia(texto: str) -> str:
    def repl(m):
        w = m.group(0)
        if h.spell(w):
            return w
        sugerencias = h.suggest(w)
        return sugerencias[0] if sugerencias else w

    return WORD_RE.sub(repl, texto)
