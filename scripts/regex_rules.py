# scripts/regex_rules.py
import re

# ======================================================
# REGLAS QUE SÍ CORRIGEN (SEGURAS)
# ======================================================

# ---------- ESPACIOS Y SIGNOS ----------
SIGNOS_DOBLES = [
    (re.compile(r'[ ]{2,}'), ' '),
    (re.compile(r',+'), ','),
    (re.compile(r'!+'), '!'),
    (re.compile(r'\?+'), '?'),
    (re.compile(r';+'), ';'),
    (re.compile(r':+'), ':'),
]

# ---------- ESPACIOS DE APERTURA ----------
APERTURA = [
    (re.compile(r'([¡¿«])([^\s])'), r'\1 \2'),
]

# ---------- ESPACIOS DE CIERRE ----------
CIERRE = [
    (re.compile(r'([^\s])([.,;:])([^\s])'), r'\1\2 \3'),
    (re.compile(r'\s+([.,;:])'), r'\1'),
]

# ---------- NÚMEROS ----------
NUMEROS = [
    (re.compile(r'\b(\d{5,})\b'),
     lambda m: f"{int(m.group(1)):,}".replace(',', ' ')),
]

# ---------- ABREVIATURAS (LISTA CERRADA) ----------
ABREVIATURAS = [
    (re.compile(r'\bee\s*uu\b', re.I), 'EE. UU.'),
    (re.compile(r'\ba\.?\s*c\b', re.I), 'a. C.'),
    (re.compile(r'\bn[º°]?\b', re.I), 'n.º'),
    (re.compile(r'\bSr\b', re.I), 'Sr.'),
    (re.compile(r'\bSra\b', re.I), 'Sra.'),
    (re.compile(r'\bDr\b', re.I), 'Dr.'),
    (re.compile(r'\bDra\b', re.I), 'Dra.'),
]

# ---------- COMILLAS (POR PARES, NO PISAN) ----------
COMILLAS = [
    (re.compile(r'“([^”]+)”'), r'«\1»'),
    (re.compile(r'"([^"]+)"'), r'«\1»'),
]

# ======================================================
# REGLAS QUE SOLO SE DETECTAN (NO SE CORRIGEN)
# (se usarán luego con tooltips)
# ======================================================

DETECTAR_PASIVAS = [
    re.compile(r'\b(fue|fueron|es|son)\s+\w+(ado|ada|idos|idas)\s+por\b', re.I)
]

DETECTAR_GERUNDIOS = [
    re.compile(r',\s*(generando|provocando|causando|dejando)\b', re.I)
]

DETECTAR_QUEISMOS = [
    re.compile(r'\bque\s+de\s+que\b', re.I),
    re.compile(r'\bde\s+que\s+(no|nada|nadie)\b', re.I),
]

# ======================================================
# ORDEN DE APLICACIÓN (SOLO LO SEGURO)
# ======================================================

RULES = (
    [('SIGNOS', *r) for r in SIGNOS_DOBLES] +
    [('COMILLAS', *r) for r in COMILLAS] +
    [('APERTURA', *r) for r in APERTURA] +
    [('CIERRE', *r) for r in CIERRE] +
    [('NUMEROS', *r) for r in NUMEROS] +
    [('ABREVIATURA', *r) for r in ABREVIATURAS]
)
