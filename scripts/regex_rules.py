import re

# Configuración: True para [corchetes], False para «latinas»
flag_corchetes = False  

# ---------- 1. LIMPIEZA Y UNIFICACIÓN (PUNTO 4) ----------
LIMPIEZA_Y_UNIFICACION = [
    # Punto 4: 1200 kilos -> 1200 kg (antes de procesar números)
    (re.compile(r'\b(\d+)\s*kilos\b', re.I), r'\1 kg'),
    (re.compile(r'\(corregido\)', re.I), ''),
    (re.compile(r'Nota:.*$', re.MULTILINE | re.I), ''),
]

# ---------- 2. MONEDA Y MILLARES (PUNTO 1) ----------
NUMEROS_Y_MONEDA = [
    # Punto 1: 14750 eur -> 14 750 € (Millares con moneda forzados)
    # Soporta 14750, 14.750 o 14,750 y lo unifica a 14 750 €
    (re.compile(r'(\d{1,3})[,.]?(\d{3})\s*(?:euros?|eur|€)\b', re.I), r'\1 \2 €'),
    
    # Millares generales (para que 25000 unidades -> 25 000 unidades)
    (re.compile(r'(\d{2,3})[,.](\d{3})'), r'\1 \2'),
    
    # Punto EXTRA: 2, 5 h -> 2,5 h (Elimina espacio en decimales)
    (re.compile(r'(\d+),\s+(\d+)'), r'\1,\2'),
]

# ---------- 3. COMILLAS (PUNTO 5: EL CAZADOR TOTAL) ----------
# Captura cualquier tipo de comilla y la unifica
COMILLAS = [
    (re.compile(r'[„“”"‘’\']([^„“”"‘’\']+)[„“”"‘’\']'), r'[\1]' if flag_corchetes else r'«\1»'),
]

# ---------- 6. DEFENSA FINAL (CON FILTRO TÉCNICO) ----------
DEFENSA_FINAL = [
    # 1. Quita espacios dobles y limpia espacios antes de puntuación
    (re.compile(r'\s+([,.;:!?])'), r'\1'),
    
    # 2. ESPACIO DESPUÉS DE PUNTUACIÓN (Solo si NO es contexto numérico)
    # Esta regla dice: "Pon espacio tras :,.;!? SOLO si no hay números pegados"
    (re.compile(r'(?<!\d)([:;,.!?»])(?!\d)'), r'\1 '),
    (re.compile(r'([:;,.!?»])(?![ \d]|$)'), r'\1 '),

    # 3. REGLA ESPECÍFICA PARA HORAS (Escudo extra)
    # Si la IA o una regla anterior metió "14: 00", esto lo vuelve a pegar
    (re.compile(r'(\d{1,2}):\s+(\d{2})'), r'\1:\2'),
    
    # 4. REGLA ESPECÍFICA PARA DECIMALES (Escudo extra)
    # Si quedó "17, 50", esto lo vuelve a pegar como "17,50"
    (re.compile(r'(\d+),\s+(\d+)'), r'\1,\2'),
]

# ---------- 5. RAYAS ----------
RAYAS = [
    (re.compile(r'(?<!—)—(?!=—)'), '—'),
    (re.compile(r'—([.!?])'), r'\1'),
    (re.compile(r'([^—]*?[.!?])—([.!?])'), r'\1\2'),
]

# ---------- 6. DEFENSA FINAL (PUNTO 3) ----------
DEFENSA_FINAL = [
    # Punto 3: EE. UU.a -> EE. UU. a
    (re.compile(r'(EE\. UU\.)(?!\s)([a-záéíóú])', re.I), r'\1 \2'),
    
    # Limpieza de espacios dobles y puntuación pegada
    (re.compile(r'\s+([,.;:!?])'), r'\1'),
    (re.compile(r'([,.;:!?»])([a-zA-ZáéíóúÁÉÍÓÚñÑ0-9])'), r'\1 \2'),
]

# ---------- ENSAMBLADO ----------
RULES = (
    [('LIMPIEZA', *r) for r in LIMPIEZA_Y_UNIFICACION] +
    [('MONEDA', *r) for r in NUMEROS_Y_MONEDA] +
    [('COMILLAS', *r) for r in COMILLAS] +
    [('TECNICO', *r) for r in TECNICO] +
    [('RAYAS', *r) for r in RAYAS] +
    [('DEFENSA', *r) for r in DEFENSA_FINAL]
)
def aplicar_regex_editorial(texto):
    """
    Aplica todas las reglas editoriales al texto y devuelve
    el texto normalizado.
    """
    if not texto:
        return ""

    resultado = texto
    for _, patron, reemplazo in RULES:
        resultado = patron.sub(reemplazo, resultado)

    return resultado
