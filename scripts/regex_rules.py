import re

# ---------- CONFIGURACIÓN ----------
flag_corchetes = False  

# ---------- 1. LIMPIEZA ----------
LIMPIEZA_Y_UNIFICACION = [
    ('ID', re.compile(r'\b(\d+)\s*kilos\b', re.I), r'\1 kg'),
    ('ID', re.compile(r'\(corregido\)', re.I), ''),
    ('ID', re.compile(r'Nota:.*$', re.MULTILINE | re.I), ''),
]

# ---------- 2. DIÁLOGOS Y RAYAS (CORREGIDO) ----------
RAYAS_Y_DIALOGOS = [
    # 1. EVITA que las rayas suban a línea anterior (sin salto)
    ('ID', re.compile(r'([^\n])\s*—'), r'\1\n—'),
    
    # 2. Fuerza raya larga
    ('ID', re.compile(r'(?<!—)—(?!=—)'), '—'),
    
    # 3. Quita punto después de ? o ! en diálogos
    ('ID', re.compile(r'([\?\!])\s*\.'), r'\1'),
    
    # 4. EVITA espacio ANTES de cierre de comilla
    ('ID', re.compile(r'\s+([»"])'), r'\1'),
    
    # 5. EVITA espacio DESPUÉS de apertura de comilla
    ('ID', re.compile(r'([«"])\s+'), r'\1'),
    
    # 6. Comillas mal formadas (apertura con espacio o carácter raro)
    ('ID', re.compile(r'[«"]\s*([a-záéíóú])'), r'«\1'),  # Normaliza apertura
    ('ID', re.compile(r'([a-záéíóú])\s*[»"]'), r'\1»'),  # Normaliza cierre
]

# ---------- 3. COMILLAS Y ESPACIOS (REFORZADO) ----------
COMILLAS_ESTILO = [
    # Conversión a latinas
    ('ID', re.compile(r'["“](.*?)["”]'), r'[\1]' if flag_corchetes else r'«\1»'),
    
    # Elimina espacios extremos en comillas
    ('ID', re.compile(r'«\s+'), r'«'),
    ('ID', re.compile(r'\s+»'), r'»'),
    
    # Corrige comillas pegadas sin espacio
    ('ID', re.compile(r'([a-záéíóú])([«"])'), r'\1 \2'),  # palabra« -> palabra «
    ('ID', re.compile(r'([»"])([a-záéíóú])'), r'\1 \2'),  # »palabra -> » palabra
]

# ---------- 4. UNIDADES Y HORAS (CON CORRECCIÓN DE ABREVIATURAS) ----------
TECNICO_Y_HORAS = [
    ('ID', re.compile(r'\bn\.º(?!\s)(\d+)', re.I), r'n.º \1'),
    ('ID', re.compile(r'(\d)\s*(kg|g|cm|mm|m|km|°C|°F|%|h|min|s)\b'), r'\1 \2'),
    
    # EVITA espacio después de "a. m." o "p. m."
    ('ID', re.compile(r'([ap]\.\s*m\.)\s+,', re.I), r'\1,'),  # "a. m. ," -> "a. m.,"
    ('ID', re.compile(r'([ap]\.\s*m\.)\s+\)'), r'\1)'),       # "a. m. )" -> "a. m.)"
]

# ---------- 5. DEFENSA PUNTUACIÓN (MEJORADA) ----------
DEFENSA_PUNTUACION = [
    # Quita espacios ANTES de signos
    ('ID', re.compile(r'\s+([,.;:!?»"])'), r'\1'),
    
    # Pega signo a comilla de cierre
    ('ID', re.compile(r'[»"]\s+([.,])'), r'»\1'),
    
    # EVITA doble espacio después de signo
    ('ID', re.compile(r'([,.;:!?»])(?!\d|$)\s+'), r'\1 '),
    
    # Limpieza final de espacios dobles
    ('ID', re.compile(r' +'), ' '),
]

# ---------- ENSAMBLADO ----------
RULES = (
    LIMPIEZA_Y_UNIFICACION +
    RAYAS_Y_DIALOGOS +
    COMILLAS_ESTILO +
    TECNICO_Y_HORAS +
    DEFENSA_PUNTUACION
)

def aplicar_regex_editorial(texto):
    if not texto:
        return ""
    
    texto = texto.replace('\xa0', ' ').replace('\u202f', ' ')

    for _, patron, reemplazo in RULES:
        try:
            texto = patron.sub(reemplazo, texto)
        except Exception:
            continue

    return texto.strip()
