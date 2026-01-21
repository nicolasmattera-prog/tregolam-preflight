#!/usr/bin/env python3
import os, re, difflib
from docx import Document
from docx.shared import RGBColor
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from dotenv import load_dotenv

# Intentar importar el monitor de tokens
try:
    from token_monitor import log_tokens
except ImportError:
    def log_tokens(model, usage, tag): pass

# ---------- CONFIGURACIÓN ----------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_MINI = "gpt-4o-mini"
MODEL_FULL = "gpt-4o"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- PROMPTS ULTRA-ESTRICTOS (MODO MOTOR) ----------
PROMPT_F1 = """
Eres un CORRECTOR ORTOGRÁFICO Y TIPOGRÁFICO de texto ya existente.  
Tu única tarea es aplicar, SIN EXCEPCIONES, las reglas que se listan a continuación. Nada de lo que no se mencione está permitido.

1. Números: 4 cifras seguidas (4000). 5 o más cifras: espacio cada 3 (20 000). Años: juntos (2026). Porcentajes: espacio antes del % (20 %).
2. Unidades y símbolos: Espacio entre cantidad y símbolo (12 kg, 45 °C, 60 %). Sin plural en símbolos (kg, %, cm).
3. Abreviaturas: EE. UU., a. C., n.º, D.ª, Sr.
4. Diálogos y citas: Raya de apertura (—) pegada al texto. Raya de inciso pegada al texto (—dijo Rubén). Puntuación siempre después de la raya de cierre: —dijo—. / «eso».
5. Comillas: Sustituye CUALQUIER tipo de comilla doble (ya sean rectas " ", curvas de apertura “ o curvas de cierre ”) por comillas latinas « » siempre.
7. Mayúsculas: Corrige capitalización sin tocar siglas ni acrónimos.
8. Ortografía y gramática básica: Tildes, diéresis, v/b, haches y concordancia simple (género/número).
9. Signos de puntuación: Quita repeticiones (,, !!, ??).
10. VOCATIVO: Coma obligatoria para separar el vocativo (ej: «Marta, cierra la puerta», «Hoy, amigos, celebramos»).

11. REGLA DE ESPACIOS DE APERTURA (OBLIGATORIA): 
    - Siempre debe haber UN espacio entre la palabra anterior y el signo de apertura.
    - Ejemplo correcto: «palabra ¿», «palabra ¡», «palabra «».
    - NUNCA pegues el signo de apertura a la palabra que le precede.

12. REGLA DE ESPACIOS DE CIERRE y PEGOTES:
    - Siempre debe haber UN espacio después de punto, coma, punto y coma y dos puntos.
    - Si dos frases están pegadas por un punto (ej: «autenticidad.Los»), separa OBLIGATORIAMENTE con un espacio: «autenticidad. Los».
    - Nunca pegues una palabra inmediatamente después de un signo de puntuación de cierre.
13. GRAMÁTICA: Corrige el uso de "si + habría" por "si + hubiera/hubiese"

RESTRICCIONES ABSOLUTAS:
- No cambies ni una palabra que esté bien escrita.
- No añadas, suprimas ni reordenes frases.
- No introduzcas comentarios, explicaciones ni ejemplos.
- No uses asteriscos ni otros marcadores.
- No generes párrafos nuevos ni líneas en blanco extra.
- No corrijas estilo, solo errores ortográficos/tipográficos.
"""

# ---------- FASE 2: EDITOR DE ESTILO (AÑADIDO POSTERIOR) ----------
PROMPT_F2 = """Eres editor literario. Tu única función es mejorar la agilidad verbal:
1. GERUNDIOS DE POSTERIORIDAD: 'terminó, generando' -> 'terminó y generó'.
2. VOZ PASIVA: Cámbiala a activa REORDENANDO la frase (Ejemplo: 'Los datos fueron analizados por el equipo' -> 'El equipo analizó los datos').
3. ESTRUCTURAS PESADAS: Mejora el flujo natural de la frase y tiempos verbales (ej: 'no venía' -> 'no habría venido').
4. LIMPIEZA LINGÜÍSTICA: Corrige queísmo/dequeísmo y concordancia de colectivos (ej: 'la mayoría decidió' en lugar de 'decidieron').

REGLA DE ORO: Respeta escrupulosamente los espacios en cifras (20 000, 36,6 °C), símbolos y comillas « » de la fase anterior."""

# ---------- FUNCIONES DE LIMPIEZA Y SEGURIDAD ----------
def limpieza_residuos_chat(texto):
    """Elimina cualquier intento de la IA de hablar o explicar lo que hizo."""
    patrones_basura = [
        r"^claro, aquí tienes.*?:", 
        r"^aquí está el texto.*?:",
        r"^he corregido.*?:",
        r"^revisión de estilo.*?:",
        r"¡dímelo!$",
        r"espero que te sirva.*$",
        r"^según tu solicitud.*?:",
        r"^frases de prueba.*?:",
    ]
    for patron in patrones_basura:
        texto = re.sub(patron, "", texto, flags=re.IGNORECASE | re.MULTILINE)
    return texto.strip().strip('"')

def necesita_fase_2(texto):
    """Detecta si el párrafo tiene potencial para contener vicios de estilo."""
    t = texto.lower()
    # Gatillos: gerundios y formas de pasiva
    gatillos = [r"ando\b", r"endo\b", r"\bfue\b", r"\bfueron\b", r"\bser\b", r"\bsido\b", r"\bestar\b"]
    if any(re.search(p, t) for p in gatillos): return True
    if len(t.split()) > 15: return True
    return False

def es_alucinacion(res):
    blacklist = ["frase está correcta", "no hay cambios", "no necesita", "sin comentarios"]
    return any(f in res.lower() for f in blacklist)

def eliminar_inserciones_largas(original, corregido, max_palabras=3):
    orig = original.split()
    corr = corregido.split()

    s = difflib.SequenceMatcher(None, orig, corr)
    resultado = []

    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'insert':
            bloque = corr[j1:j2]
            if len(bloque) <= max_palabras:
                resultado.extend(bloque)
            # si supera el límite → se elimina
        else:
            resultado.extend(corr[j1:j2])

    return " ".join(resultado)


# ---------- NÚCLEO DE PROCESAMIENTO ----------
def corregir_bloque(texto):
    if len(texto.strip()) < 3: return texto
    
    try:
        # FASE 1: Ortografía (Mini)
        res1 = client.chat.completions.create(
            model=MODEL_MINI,
            messages=[{"role": "system", "content": PROMPT_F1}, {"role": "user", "content": texto}],
            temperature=0
        )
        log_tokens(MODEL_MINI, res1.usage, "F1_Orto")
        r = limpieza_residuos_chat(res1.choices[0].message.content.strip())

        # CONTROL DE INTEGRIDAD (Si el Mini borra mucho, saltamos al Full)
        if es_alucinacion(r) or len(r) < len(texto) * 0.98:
            res_full = client.chat.completions.create(
                model=MODEL_FULL,
                messages=[{"role": "system", "content": PROMPT_F1}, {"role": "user", "content": texto}],
                temperature=0
            )
            log_tokens(MODEL_FULL, res_full.usage, "FALLBACK_FULL")
            r = limpieza_residuos_chat(res_full.choices[0].message.content.strip())

        # FASE 2: Estilo Agresivo
        if necesita_fase_2(r):
            res2 = client.chat.completions.create(
                model=MODEL_MINI,
                messages=[{"role": "system", "content": PROMPT_F2}, {"role": "user", "content": r}],
                temperature=0 
            )
            log_tokens(MODEL_MINI, res2.usage, "F2_Estilo_Agresivo")
            r2 = limpieza_residuos_chat(res2.choices[0].message.content.strip())
            
            # Margen del 85% para permitir el ahorro de palabras de la voz activa
            if not es_alucinacion(r2) and (len(r) * 0.85 <= len(r2) <= len(r) * 1.2):
                r = r2

        return r
    except Exception as e:
        print(f"Error procesando bloque: {e}")
        return texto

def aplicar_cambios_quirurgicos(parrafo, original, corregido):
    if original == corregido:
        return

    era_cursiva = any(run.italic for run in parrafo.runs)
    for run in parrafo.runs:
        run.text = ""

    s = difflib.SequenceMatcher(None, original.split(), corregido.split())

    for tag, i1, i2, j1, j2 in s.get_opcodes():
        palabras = corregido.split()[j1:j2]
        if not palabras:
            continue

        texto_segmento = " ".join(palabras) + " "
        run = parrafo.add_run(texto_segmento)
        run.font.name = 'Garamond'
        run.italic = era_cursiva

        if tag == 'replace':
            run.font.color.rgb = RGBColor(0, 0, 180)      # azul → corrección
        elif tag == 'insert':
            run.font.color.rgb = RGBColor(180, 0, 0)      # rojo → añadido
        else:
            run.font.color.rgb = RGBColor(0, 0, 0)        # negro → igual

# ---------- PROCESO PRINCIPAL ----------
def procesar_archivo(name):
    print(f"🚀 Iniciando Preflight Profesional: {name}")
    doc = Document(os.path.join(INPUT_FOLDER, name))
    
    # Recopilar todos los párrafos (incluyendo tablas)
    objetivos = [p for p in doc.paragraphs]
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs: objetivos.append(p)

    textos_orig = [p.text for p in objetivos]
    
    # Procesamiento paralelo para máxima velocidad real (8 hilos)
    with ThreadPoolExecutor(max_workers=8) as exe:
        resultados = list(exe.map(corregir_bloque, textos_orig))

    # Aplicar resultados al documento
    for p, orig, corr in zip(objetivos, textos_orig, resultados):
        aplicar_cambios_quirurgicos(p, orig, corr)

    doc.save(os.path.join(OUTPUT_FOLDER, name))
    print(f"✅ Preflight completado para {name}. Revisa la carpeta 'salida'.")

if __name__ == "__main__":
    archivos = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".docx")]
    if not archivos:
        print("❌ No se encontraron archivos .docx en la carpeta 'entrada'.")
    else:
        for a in archivos:
            procesar_archivo(a)
