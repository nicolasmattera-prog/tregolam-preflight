import re

# Configuración: True para [corchetes], False para «latinas»
flag_corchetes = False  

# ---------- 1. LIMPIEZA Y UNIFICACIÓN ----------
LIMPIEZA_Y_UNIFICACION = [
    (re.compile(r'\b(\d+)\s*kilos\b', re.I), r'\1 kg'),
    (re.compile(r'\(corregido\)', re.I), ''),
    (re.compile(r'Nota:.*$', re.MULTILINE | re.I), ''),
]

# ---------- 2. MONEDA Y MILLARES ----------
NUMEROS_Y_MONEDA = [
    (re.compile(r'(\d{1,3})[,.]?(\d{3})\s*(?:euros?|eur|€)\b', re.I), r'\1 \2 €'),
    (re.compile(r'(\d{2,3})[,.](\d{3})'), r'\1 \2'),
    (re.compile(r'(\d+),\s+(\d+)'), r'\1,\2'),
]

# ---------- 3. COMILLAS ----------
COMILLAS = [
    (re.compile(r'[„“”"‘’\']([^„“”"‘’\']+)[„“”"‘’\']'), r'[\1]' if flag_corchetes else r'«\1»'),
]

# ---------- 4. TÉCNICO ----------
TECNICO = [
    (re.compile(r'\bn\.º(?!\s)(\d+)', re.I), r'n.º \1'),
    (re.compile(r'(\d)(kg|g|cm|mm|m|km|°C|°F|%|h|min|s)\b'), r'\1 \2'),
]

# ---------- 5. RAYAS ----------
RAYAS = [
    (re.compile(r'(?<!—)—(?!=—)'), '—'),
    (re.compile(r'—([.!?])'), r'\1'),
    (re.compile(r'([^—]*?[.!?])—([.!?])'), r'\1\2'),
]

# ---------- 6. DEFENSA FINAL ----------
DEFENSA_FINAL = [
    (re.compile(r'(EE\. UU\.)(?!\s)([a-záéíóú])', re.I), r'\1 \2'),
    (re.compile(r'\s+([,.;:!?])'), r'\1'),
    (re.compile(r'([,.;:!?»])([a-zA-ZáéíóúÁÉÍÓÚñÑ0-9])'), r'\1 \2'),
]

RULES = (
    [('LIMPIEZA', *r) for r in LIMPIEZA_Y_UNIFICACION] +
    [('MONEDA', *r) for r in NUMEROS_Y_MONEDA] +
    [('COMILLAS', *r) for r in COMILLAS] +
    [('TECNICO', *r) for r in TECNICO] +
    [('RAYAS', *r) for r in RAYAS] +
    [('DEFENSA', *r) for r in DEFENSA_FINAL]
)

def aplicar_regex_editorial(texto):
    if not texto: return ""
    res = texto
    for _, patron, reemplazo in RULES:
        res = patron.sub(reemplazo, res)
    return res
