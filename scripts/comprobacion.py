import os
import sys
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv
from regex_rules import aplicar_regex_editorial

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

PROMPT_AUDITORIA = """Actúa como un auditor ortotipográfico implacable. Solo reporta errores reales.
FORMATO: CATEGORIA | ID | ORIGINAL | CORRECCION | MOTIVO
REGLAS:
1. Si el texto original ya tiene comillas latinas « », es CORRECTO.
2. No reportes nada si no hay un cambio real."""

def comprobar_archivo(nombre_archivo):
    ruta_lectura = os.path.join(SALIDA_DIR, nombre_archivo)
    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)
    
    with open(ruta_txt, "w", encoding="utf-8") as f: f.write("")

    try:
        doc = Document(ruta_lectura)
        parrafos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]
        bloque = []
        for i, texto in enumerate(parrafos):
            bloque.append(f"ID_{i+1}: {texto}")
            if len(bloque) >= 10:
                res = llamar_ia("\n".join(bloque))
                procesar_y_guardar(res, ruta_txt)
                bloque = []
        if bloque:
            res = llamar_ia("\n".join(bloque))
            procesar_y_guardar(res, ruta_txt)
        return nombre_txt
    except Exception as e: return f"ERROR: {str(e)}"

def procesar_y_guardar(respuesta, ruta_dest):
    if not respuesta or "S_OK" in respuesta.upper(): return
    lineas_limpias = []
    for linea in respuesta.split("\n"):
        partes = [p.strip() for p in linea.split("|")]
        if len(partes) == 5:
            orig, corr = partes[2], partes[3]
            # FILTRO: ¿La regex ya soluciona lo que dice la IA?
            if aplicar_regex_editorial(orig) == aplicar_regex_editorial(corr): continue
            # FILTRO: No permitir que la IA rompa caracteres especiales
            if any(c in orig for c in ('«', '»', '\u00A0', '\u202f')) and not any(c in corr for c in ('«', '»', '\u00A0', '\u202f')): continue
            
            if orig != corr: lineas_limpias.append(" | ".join(partes))
    if lineas_limpias:
        with open(ruta_dest, "a", encoding="utf-8") as f: f.write("\n".join(lineas_limpias) + "\n")

def llamar_ia(texto):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": PROMPT_AUDITORIA}, {"role": "user", "content": texto}],
            temperature=0
        )
        return res.choices[0].message.content.strip()
    except: return "S_OK"
