#!/usr/bin/env python3
import os, re, difflib, sys
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

# ---------- CONFIGURACIÓN DE RUTAS ABSOLUTAS ----------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Localizamos la raíz del proyecto subiendo un nivel desde 'scripts/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

# Asegurar que existan las carpetas en la raíz
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

MODEL_MINI = "gpt-4o-mini"
MODEL_FULL = "gpt-4o"

# ---------- PROMPTS ULTRA-ESTRICTOS ----------
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
11. ESPACIOS DE APERTURA: Siempre un espacio antes de ¿, ¡, o «.
12. ESPACIOS DE CIERRE: Siempre un espacio después de . , ; :
13. GRAMÁTICA: Corrige "si + habría" por "si + hubiera/hubiese".

RESTRICCIONES: No cambies estilo, no añadas comentarios, no borres frases.
"""

PROMPT_F2 = """Eres editor literario. Tu única función es mejorar la agilidad verbal:
1. GERUNDIOS DE POSTERIORIDAD: 'terminó, generando' -> 'terminó y generó'.
2. VOZ PASIVA: Cámbiala a activa.
3. ESTRUCTURAS PESADAS: Mejora el flujo natural.
4. LIMPIEZA LINGÜÍSTICA: Corrige queísmo/dequeísmo."""

# ---------- FUNCIONES DE LIMPIEZA Y SEGURIDAD ----------
def limpieza_residuos_chat(texto):
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
    t = texto.lower()
    gatillos = [r"ando\b", r"endo\b", r"\bfue\b", r"\bfueron\b", r"\bser\b", r"\bsido\b", r"\bestar\b"]
    if any(re.search(p, t) for p in gatillos): return True
    if len(t.split()) > 15: return True
    return False

def es_alucinacion(res):
    blacklist = ["frase está correcta", "no hay cambios", "no necesita", "sin comentarios"]
    return any(f in res.lower() for f in blacklist)

# ---------- NÚCLEO DE PROCESAMIENTO ----------
def corregir_bloque(texto):
    if len(texto.strip()) < 3: return texto
    try:
        # FASE 1: Ortografía (Temperatura 0 para evitar estocasticidad)
        res1 = client.chat.completions.create(
            model=MODEL_MINI,
            messages=[{"role": "system", "content": PROMPT_F1}, {"role": "user", "content": texto}],
            temperature=0
        )
        log_tokens(MODEL_MINI, res1.usage, "F1_Orto")
        r = limpieza_residuos_chat(res1.choices[0].message.content.strip())

        # CONTROL DE INTEGRIDAD
        if es_alucinacion(r) or len(r) < len(texto) * 0.98:
            res_full = client.chat.completions.create(
                model=MODEL_FULL,
                messages=[{"role": "system", "content": PROMPT_F1}, {"role": "user", "content": texto}],
                temperature=0
            )
            r = limpieza_residuos_chat(res_full.choices[0].message.content.strip())

        # FASE 2: Estilo
        if necesita_fase_2(r):
            res2 = client.chat.completions.create(
                model=MODEL_MINI,
                messages=[{"role": "system", "content": PROMPT_F2}, {"role": "user", "content": r}],
                temperature=0 
            )
            r2 = limpieza_residuos_chat(res2.choices[0].message.content.strip())
            if not es_alucinacion(r2) and (len(r) * 0.85 <= len(r2) <= len(r) * 1.2):
                r = r2
        return r
    except Exception as e:
        return texto

def aplicar_cambios_quirurgicos(parrafo, original, corregido):
    if original == corregido: return
    era_cursiva = any(run.italic for run in parrafo.runs)
    for run in parrafo.runs: run.text = ""
    s = difflib.SequenceMatcher(None, original.split(), corregido.split())
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        palabras = corregido.split()[j1:j2]
        if not palabras: continue
        texto_segmento = " ".join(palabras) + " "
        run = parrafo.add_run(texto_segmento)
        run.font.name = 'Garamond'
        run.italic = era_cursiva
        if tag in ('replace', 'insert'):
            run.font.color.rgb = RGBColor(0, 0, 180) # Azul para cambios
        else:
            run.font.color.rgb = RGBColor(0, 0, 0)

# ---------- FUNCIÓN LLAMADA DESDE APP.PY ----------
def ejecutar_precorreccion(name):
    """
    Función principal para la precorrección. 
    Usa rutas absolutas para garantizar compatibilidad con Streamlit Cloud.
    """
    try:
        ruta_archivo = os.path.join(INPUT_FOLDER, name)
        if not os.path.exists(ruta_archivo):
            return f"ERROR: No se encuentra {ruta_archivo}"

        doc = Document(ruta_archivo)
        objetivos = [p for p in doc.paragraphs]
        for t in doc.tables:
            for r in t.rows:
                for c in r.cells:
                    for p in c.paragraphs: objetivos.append(p)

        textos_orig = [p.text for p in objetivos]
        
        with ThreadPoolExecutor(max_workers=8) as exe:
            resultados = list(exe.map(corregir_bloque, textos_orig))

        for p, orig, corr in zip(objetivos, textos_orig, resultados):
            aplicar_cambios_quirurgicos(p, orig, corr)

        ruta_salida = os.path.join(OUTPUT_FOLDER, name)
        doc.save(ruta_salida)
        return f"✅ Archivo '{name}' procesado y guardado en salida."
    
    except Exception as e:
        return f"ERROR en precorreccion: {str(e)}"

if __name__ == "__main__":
    # Para pruebas locales por consola
    archivos = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".docx")]
    for a in archivos:
        print(ejecutar_precorreccion(a))
