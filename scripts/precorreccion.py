#!/usr/bin/env python3
import os, re, difflib
from docx import Document
from docx.shared import RGBColor
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from dotenv import load_dotenv

# ---------- CONFIGURACIÓN ----------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_MINI = "gpt-4o-mini"
MODEL_FULL = "gpt-4o"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- RESTAURACIÓN DE TUS PROMPTS ULTRA-ESTRICTOS ----------
PROMPT_F1 = """
Eres un CORRECTOR ORTOGRÁFICO Y TIPOGRÁFICO de texto ya existente.  
Tu única tarea es aplicar, SIN EXCEPCIONES, las reglas que se listan a continuación:

1. Diálogos: Raya de apertura (—) pegada al texto. Raya de inciso pegada al texto (—dijo Rubén). Puntuación siempre después de la raya de cierre: —dijo—.
   Ejemplo correcto: —Texto del diálogo— dijo X—. Texto del diálogo.
2. Mayúsculas: Corrige capitalización sin tocar siglas ni acrónimos.
3. Ortografía: Tildes, diéresis, v/b, haches y concordancia simple.
4. Signos: Quita repeticiones (,, !!, ??).
5. VOCATIVO: Coma obligatoria (ej: «Marta, cierra la puerta»).
6. ESPACIOS APERTURA: UN espacio entre la palabra anterior y el signo de apertura (¿, ¡, «).
7. PEGOTES: UN espacio después de punto, coma, etc. Separa «autenticidad.Los» -> «autenticidad. Los».
8. GRAMÁTICA: Corrige "si + habría" por "si + hubiera/hubiese".

RESTRICCIONES: No cambies palabras correctas, no añadas frases, no pongas comentarios.
"""

PROMPT_F2 = """Eres editor literario. Mejora la agilidad verbal:
1. GERUNDIOS DE POSTERIORIDAD: 'terminó, generando' -> 'terminó y generó'.
2. VOZ PASIVA: Cámbiala a activa REORDENANDO la frase.
3. ESTRUCTURAS PESADAS: Mejora el flujo natural (ej: 'no venía' -> 'no habría venido').
4. LIMPIEZA LINGÜÍSTICA: Corrige queísmo/dequeísmo y concordancia de colectivos.

REGLA DE ORO: Respeta escrupulosamente los espacios en cifras y comillas de la fase anterior."""

# ---------- FUNCIONES TÉCNICAS (CON TOKENIZER DE ESPACIOS) ----------

def _tokenize(txt):
    """Devuelve lista de tuplas (palabra, espacios_posteriores)."""
    return re.findall(r'(\S+)([ \t\u00A0\r\n]*)', txt, re.UNICODE)

def limpieza_residuos_chat(texto):
    patrones_basura = [r"^claro, aquí tienes.*?:", r"^aquí está el texto.*?:", r"^he corregido.*?:", r"espero que te sirva.*$"]
    for patron in patrones_basura:
        texto = re.sub(patron, "", texto, flags=re.IGNORECASE | re.MULTILINE)
    return texto.strip().strip('"')

def eliminar_inserciones_largas(original, corregido, max_palabras=3):
    """Bloquea alucinaciones sin romper la tipografía."""
    orig_tok = _tokenize(original)
    corr_tok = _tokenize(corregido)
    
    s = difflib.SequenceMatcher(None, [w for w, _ in orig_tok], [w for w, _ in corr_tok])
    out = []
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'insert' and (j2 - j1) > max_palabras:
            continue # Bloqueamos inserción de más de X palabras (alucinación)
        
        if tag == 'replace' and (j2 - j1) > (i2 - i1) + max_palabras:
            # Si el reemplazo es sospechosamente largo, volvemos al original
            for i in range(i1, i2):
                pal, esp = orig_tok[i]
                out.append(pal + esp)
            continue

        for j in range(j1, j2):
            pal, esp = corr_tok[j]
            out.append(pal + esp)
            
    return ''.join(out)

# ---------- PROCESAMIENTO ----------

def corregir_bloque(texto):
    if not texto.strip(): return texto
    try:
        # FASE 1: Tu corrección ortotipográfica estricta
        res1 = client.chat.completions.create(
            model=MODEL_MINI,
            messages=[{"role": "system", "content": PROMPT_F1}, {"role": "user", "content": texto}],
            temperature=0
        )
        r = limpieza_residuos_chat(res1.choices[0].message.content.strip())
        r = eliminar_inserciones_largas(texto, r, max_palabras=3)

        # FASE 2: Estilo
        t_lower = r.lower()
        if any(re.search(p, t_lower) for p in [r"ando\b", r"endo\b", r"\bfue\b", r"\bfueron\b"]) or len(r.split()) > 15:
            res2 = client.chat.completions.create(
                model=MODEL_MINI,
                messages=[{"role": "system", "content": PROMPT_F2}, {"role": "user", "content": r}],
                temperature=0 
            )
            r2 = limpieza_residuos_chat(res2.choices[0].message.content.strip())
            
            # Margen dinámico para cambios de estilo legítimos
            margen = 5 if re.search(r'\b(fue|fueron|será|serán|es|son)\b.+\bpor\b', r, re.I) else 4
            r2_filtrado = eliminar_inserciones_largas(r, r2, max_palabras=margen)
            
            if 0.75 <= len(r2_filtrado) / (len(r) + 1) <= 1.3:
                r = r2_filtrado
        return r
    except Exception as e:
        print(f"Error: {e}")
        return texto

# ---------- WORD MAPPING ----------

def aplicar_cambios_quirurgicos(parrafo, original, corregido):
    if original.strip() == corregido.strip(): return
    era_cursiva = any(run.italic for run in parrafo.runs)
    for run in parrafo.runs: run.text = ""

    orig_words = [w for w, _ in _tokenize(original)]
    corr_list = _tokenize(corregido)
    corr_words = [w for w, e in corr_list]

    s = difflib.SequenceMatcher(None, orig_words, corr_words)
    
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        segmento = "".join([w + e for w, e in corr_list[j1:j2]])
        if not segmento: continue
        
        run = parrafo.add_run(segmento)
        run.font.name = 'Garamond'
        run.italic = era_cursiva
        
        if j2 == len(corr_list) and not segmento.endswith((' ', '\u00A0')):
            run.text += ' '

        if tag == 'replace': run.font.color.rgb = RGBColor(0, 0, 180)
        elif tag == 'insert': run.font.color.rgb = RGBColor(180, 0, 0)
        else: run.font.color.rgb = RGBColor(0, 0, 0)

def procesar_archivo(name):
    print(f"🚀 Procesando con tus reglas originales: {name}")
    doc = Document(os.path.join(INPUT_FOLDER, name))
    objetivos = [p for p in doc.paragraphs if p.text.strip()]
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    if p.text.strip(): objetivos.append(p)

    textos_orig = [p.text for p in objetivos]
    with ThreadPoolExecutor(max_workers=8) as exe:
        resultados = list(exe.map(corregir_bloque, textos_orig))

    for p, orig, corr in zip(objetivos, textos_orig, resultados):
        aplicar_cambios_quirurgicos(p, orig, corr)

    doc.save(os.path.join(OUTPUT_FOLDER, name))
    print(f"✅ Finalizado con éxito.")

if __name__ == "__main__":
    archivos = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".docx")]
    for a in archivos: procesar_archivo(a)
