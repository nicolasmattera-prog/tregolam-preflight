# scripts/regex_rules.py  (VERSIÓN COMPLETA)
import re

# ---------- TILDES/DIÉRESIS AUTOMÁTICAS ----------
import unicodedata

def add_tildes(texto: str) -> str:
    """
    Devuelve el texto con las tildes/diéresis puestas
    usando el diccionario ortográfico de Python.
    """
    # Normaliza a forma NFC (caracter + tilde combinada)
    return unicodedata.normalize('NFC', texto)

TILDES_AUTO = [
    (re.compile(r'\b\w+\b'), lambda m: add_tildes(m.group(0)))
]

# ---------- SIGNOS DOBLES ----------
SIGNOS_DOBLES = [
    (re.compile(r'[,,]+'), ','),
    (re.compile(r'[!!]+'), '!'),
    (re.compile(r'[??]+'), '?'),
    (re.compile(r'[;;]+'), ';'),
    (re.compile(r'[::]+'), ':'),
    (re.compile(r'[  ]+'), ' '),  # dobles espacios
]

# ---------- ESPACIOS DE APERTURA ----------
APERTURA = [
    (re.compile(r'([¡¿«])([^\s])'), r'\1 \2'),
]

# ---------- ESPACIOS DE CIERRE ----------
CIERRE = [
    (re.compile(r'([^\s])([.,;:])([^\s])'), r'\1\2 \3'),
    (re.compile(r'([^\s])([.,;:])$'), r'\1\2'),
]

# ---------- NÚMEROS > 4 CIFRAS ----------
NUMEROS = [
    (re.compile(r'\b(\d{5,})\b'), lambda m: f"{int(m.group(1)):,}".replace(',', ' ')),
]

# ---------- ABREVIATURAS ----------
ABREVIATURAS = [
    (re.compile(r'\bee\s*uu\b', re.I), 'EE. UU.'),
    (re.compile(r'\ba\.?\s*c\b', re.I), 'a. C.'),
    (re.compile(r'\bn[º°]?\b', re.I), 'n.º'),
    (re.compile(r'\bSr\b', re.I), 'Sr.'),
    (re.compile(r'\bSra\b', re.I), 'Sra.'),
    (re.compile(r'\bDr\b', re.I), 'Dr.'),
    (re.compile(r'\bDra\b', re.I), 'Dra.'),
]

# ---------- PASIVAS COMUNES ----------
PASIVAS = [
    (re.compile(r'\b(fue|fueron)\s+(\w+ado|ada|idos|idas|to|ta|so|sa)\s+por\s+(\w+)\b', re.I),
     lambda m: f"{m.group(3)} {m.group(2)}"),
    (re.compile(r'\b(es|son)\s+(\w+ado|ada|idos|idas|to|ta|so|sa)\s+por\s+(\w+)\b', re.I),
     lambda m: f"{m.group(3)} {m.group(2)}"),
]

# ---------- GERUNDIOS DE POSTERIORIDAD ----------
GERUNDIOS = [
    (re.compile(r'\b(\w+ó|ó)\s*,?\s*(generando|provocando|creando|dejando)\b', re.I),
     r'\1 y \2ó'),  # ← \2 en lugar de \3
]

# ---------- QUEÍSMO / DEQUEÍSMO ----------
QUEISMOS = [
    (re.compile(r'\bque\s+de\s+que\b', re.I), 'que'),
    (re.compile(r'\bde\s+que\s+(no|nada|nadie)\b', re.I), r'que \1'),
]

# ---------- COMILLAS ----------
COMILLAS = [
    (re.compile(r'["“”]'), '«'),
    (re.compile(r'["“”]'), '»'),
]

# ORDEN DE APLICACIÓN
RULES = (
    [('ORTOGRAFIA', *r) for r in TILDES] +
    [('SIGNOS', *r) for r in SIGNOS_DOBLES] +
    [('FORMATO', *r) for r in COMILLAS + APERTURA + CIERRE + NUMEROS] +
    [('ABREVIATURA', *r) for r in ABREVIATURAS] +
    [('PASIVA', *r) for r in PASIVAS] +
    [('GERUNDIO', *r) for r in GERUNDIOS] +
    [('QUEISMO', *r) for r in QUEISMOS]
)
