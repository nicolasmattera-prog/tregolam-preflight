import os
import sys
import json
from collections import Counter
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

# -------------------------------------------------
# IMPORTACIÓN DEL MOTOR DE REGLAS FÍSICAS
# -------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from regex_rules1 import aplicar_regex_editorial
except ImportError:
    from regex_rules import aplicar_regex_editorial

# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

# -------------------------------------------------
# BLINDAJES EDITORIALES
# -------------------------------------------------
def texto_limpio(texto):
    if not texto:
        return ""
    return aplicar_regex_editorial(texto)

def contiene_caracteres_especiales(texto):
    especiales = ('«', '»', '„', '“', '”', '\u00A0', '\u202f')
    return any(c in texto for c in especiales)

# -------------------------------------------------
# PROMPT IA (JSON ESTRICTO)
# -------------------------------------------------
PROMPT_AUDITORIA = """
Actúa como un auditor editorial profesional.

Devuelve EXCLUSIVAMENTE un JSON válido con esta estructura:

{
  "estado": "OK" | "ERRORES",
  "resultados": [
    {
      "categoria": "ORTOGRAFIA" | "FORMATO" | "SUGERENCIA",
      "id": "ID_x",
      "original": "texto original exacto",
      "correccion": "texto corregido",
      "motivo": "explicación breve"
    }
  ]
}

REGLAS:
- No inventes errores.
- Si no hay cambios reales, devuelve estado "OK" y resultados [].
- No modifiques comillas latinas ni espacios de no ruptura.
- No devuelvas texto fuera del JSON.
"""

# -------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------
def comprobar_archivo(nombre_archivo):
    ruta_lectura = os.path.join(SALIDA_DIR, nombre_archivo)
    if not os.path.exists(ruta_lectura):
        ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)

    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)

    open(ruta_txt, "w", encoding="utf-8").close()

    contador = Counter()

    try:
        doc = Document(ruta_lectura)
        parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        bloque = []
        for i, texto in enumerate(parrafos):
            bloque.append(f"ID_{i+1}: {texto}")

            if len(bloque) >= 10:
                respuesta = llamar_ia("\n".join(bloque))
                procesar_respuesta(respuesta, ruta_txt, contador)
                bloque = []

        if bloque:
            respuesta = llamar_ia("\n".join(bloque))
            procesar_respuesta(respuesta, ruta_txt, contador)

        # -------- RESUMEN FINAL --------
        if contador:
            with open(ruta_txt, "a", encoding="utf-8") as f:
                f.write("\n\nRESUMEN GENERAL\n")
                f.write("----------------\n")
                f.write(f"TOTAL ERRORES: {sum(contador.values())}\n")
                for cat, num in contador.items():
                    f.write(f"{c
