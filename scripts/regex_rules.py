# scripts/regex_rules.py
import re

# Utilidad para reemplazar sin tocar mayúsculas iniciales
def preserve_case(original: str, new: str) -> str:
    if original[0].isupper():
        return new.capitalize()
    return new

# ----------
# TILDES Y DIÉRESIS
# ----------
TILDES = [
    (re.compile(r'\bhabia\b', re.I), 'había'),
    (re.compile(r'\bestan\b', re.I), 'están'),
    (re.compile(r'\bbiol6gic', re.I), 'biológic'),  # ej. biológicos
    (re.compile(r'\bpsicol6gic', re.I), 'psicológic'),
    (re.compile(r'\bconexi6n\b', re.I), 'conexión'),
]

# ----------
# COMILLAS
# ----------
COMILLAS = [
    (re.compile(r'["“”]'), '«'),
    (re.compile(r'["“”]'), '»'),
]

# ----------
# ESPACIOS DE APERTURA
# ----------
APERTURA = [
    (re.compile(r'([¡¿«])([^\s])'), r'\1 \2'),
]

# ----------
# ESPACIOS DE CIERRE
# ----------
CIERRE = [
    (re.compile(r'([^\s])([.,;:])([^\s])'), r'\1\2 \3'),
]

# ----------
# NÚMEROS > 4 CIFRAS
# ----------
NUMEROS = [
    (re.compile(r'\b(\d{5,})\b'), lambda m: f"{int(m.group(1)):,}".replace(',', ' ')),
]

# ----------
# ABREVIATURAS
# ----------
ABREVIATURAS = [
    (re.compile(r'\bee\s*uu\b', re.I), 'EE. UU.'),
    (re.compile(r'\ba\.?\s*c\b', re.I), 'a. C.'),
    (re.compile(r'\bn[º°]?\b', re.I), 'n.º'),
]

# ----------
# SIGNOS DOBLES
# ----------
SIGNOS_DOBLES = [
    (re.compile(r'[,,]+'), ','),
    (re.compile(r'[!!]+'), '!'),
    (re.compile(r'[??]+'), '?'),
]

# ----------
# PASIVAS COMUNES (starter-kit)
# ----------
PASIVAS = [
    (re.compile(r'\b(fue|fueron)\s+(\w+ado|ada|idos|idas|to|ta|so|sa)\s+por\s+(\w+)\b', re.I),
     lambda m: f"{m.group(3)} {m.group(2)}"),
    (re.compile(r'\b(es|son)\s+(\w+ado|ada|idos|idas|to|ta|so|sa)\s+por\s+(\w+)\b', re.I),
     lambda m: f"{m.group(3)} {m.group(2)}"),
]

# ----------
# GERUNDIOS DE POSTERIORIDAD
# ----------
GERUNDIOS = [
    (re.compile(r'\b(\w+ó|ó)\s*,?\s*(generando|provocando|creando|dejando)\b', re.I),
     r'\1 y \3ó'),
]

# ----------
# QUEÍSMO / DEQUEÍSMO
# ----------
QUEISMOS = [
    (re.compile(r'\bque\s+de\s+que\b', re.I), 'que'),
    (re.compile(r'\bde\s+que\s+(no|nada|nadie)\b', re.I), r'que \1'),
]

# ORDEN DE APLICACIÓN
RULES = (
    [('ORTOGRAFIA', *r) for r in TILDES] +
    [('FORMATO', *r) for r in COMILLAS + APERTURA + CIERRE + NUMEROS] +
    [('ABREVIATURA', *r) for r in ABREVIATURAS] +
    [('SIGNOS', *r) for r in SIGNOS_DOBLES] +
    [('PASIVA', *r) for r in PASIVAS] +
    [('GERUNDIO', *r) for r in GERUNDIOS] +
    [('QUEISMO', *r) for r in QUEISMOS]
)
