# scripts/precorreccion.py
import os
import re
import difflib
from docx import Document
from docx.shared import RGBColor
from regex_rules import RULES
from tooltip_helper import add_tooltip
from ortografia import corregir_ortografia

# ---------- CONFIGURACIÓN DE RUTAS ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- FUNCIÓN DE CORRECCIÓN ----------
def corregir_texto(texto: str) -> str:
    for categoria, patron, reemplazo in RULES:
        if callable(reemplazo):
            texto = patron.sub(reemplazo, texto)
        else:
            texto = patron.sub(reemplazo, texto)
    return texto

def aplicar_cambios_quirurgicos(parrafo, original: str, corregido: str):
    if original == corregido:
        return

    for run in parrafo.runs:
        run.text = ""

    run = parrafo.add_run(corregido)
    run.font.name = 'Garamond'
    run.font.color.rgb = RGBColor(0, 0, 180)  # azul

# ---------- FUNCIÓN PRINCIPAL ----------
def ejecutar_precorreccion(name: str) -> str:
    try:
        ruta_archivo = os.path.join(INPUT_FOLDER, name)
        if not os.path.exists(ruta_archivo):
            return f"ERROR: No se encuentra {ruta_archivo}"

        doc = Document(ruta_archivo)
        objetivos = [p for p in doc.paragraphs]
        for t in doc.tables:
            for r in t.rows:
                for c in r.cells:
                    for p in c.paragraphs:
                        objetivos.append(p)

        # Correcciones ortotipográficas
        for p in objetivos:
            original = p.text
            corregido = corregir_texto(original)

            if len(corregido) < 300:
                corregido = corregir_ortografia(corregido)

            aplicar_cambios_quirurgicos(p, original, corregido)
        
        # ---------- FORMATO ----------
        from docx.shared import Cm
        from docx.enum.text import WD_LINE_SPACING, WD_TAB_ALIGNMENT

        # 1. Márgenes 2,5 cm
        for sec in doc.sections:
            sec.top_margin = Cm(2.5)
            sec.bottom_margin = Cm(2.5)
            sec.left_margin = Cm(2.5)
            sec.right_margin = Cm(2.5)

        # 2. Interlineado 1,15
        for p in objetivos:
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            p.paragraph_format.line_spacing = 1.15

        # 3. Sangría primera línea 0,7 cm
        for p in objetivos:
            p.paragraph_format.first_line_indent = Cm(0.7)

        # 4. Tabulador a 0,7 cm (por si se usa)
        for p in objetivos:
            p.paragraph_format.tab_stops.add_tab_stop(Cm(0.7), WD_TAB_ALIGNMENT.LEFT)

        # Guardar
        ruta_salida = os.path.join(OUTPUT_FOLDER, name)
        doc.save(ruta_salida)
        return f"✅ Archivo '{name}' procesado y guardado en salida."
    except Exception as e:
        return f"ERROR en precorrección: {str(e)}"








