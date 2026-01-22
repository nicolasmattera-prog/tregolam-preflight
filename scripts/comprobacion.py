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
    from regex_rules import aplicar_regex_editorial
except ImportError:
    from regex_rules import aplicar_regex_editorial

# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

# -------------------------------------------------
# NORMALIZACIÓN Y BLINDAJES
# -------------------------------------------------
def texto_limpio(texto):
    if not texto:
        return ""
    return aplicar_regex_editorial(texto)

def contiene_caracteres_especiales(texto):
    especiales = ('„', '“', '”', '«', '»', '\u00A0', '\u202f')
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
    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)

    open(ruta_txt, "w", encoding="utf-8").close()

    contador_categorias = Counter()

    try:
        doc = Document(ruta_lectura)
        parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        bloque = []
        for i, texto in enumerate(parrafos):
            bloque.append(f"ID_{i+1}: {texto}")

            if len(bloque) >= 10:
                respuesta = llamar_ia("\n".join(bloque))
                procesar_y_guardar(respuesta, ruta_txt, contador_categorias)
                bloque = []

        if bloque:
            respuesta = llamar_ia("\n".join(bloque))
            procesar_y_guardar(respuesta, ruta_txt, contador_categorias)

        # -------- RESUMEN FINAL (UNA SOLA VEZ) --------
        if contador_categorias:
            with open(ruta_txt, "a", encoding="utf-8") as f:
                f.write("\n\nRESUMEN GENERAL\n")
                f.write("----------------\n")
                total = sum(contador_categorias.values())
                f.write(f"TOTAL ERRORES: {total}\n")
                for cat, cant in contador_categorias.items():
                    f.write(f"{cat}: {cant}\n")

        return nombre_txt

    except Exception as e:
        return f"ERROR_ARCHIVO | {str(e)}"

# -------------------------------------------------
# PROCESAMIENTO SEGURO DEL JSON IA
# -------------------------------------------------
def procesar_y_guardar(respuesta, ruta_dest, contador):
    if not respuesta:
        return

    if respuesta.startswith("ERROR_IA"):
        with open(ruta_dest, "a", encoding="utf-8") as f:
            f.write(respuesta + "\n")
        return

    try:
        data = json.loads(respuesta)
    except json.JSONDecodeError:
        with open(ruta_dest, "a", encoding="utf-8") as f:
            f.write("ERROR_JSON | Respuesta no válida\n")
        return

    if data.get("estado") != "ERRORES":
        return

    lineas_validas = []

    for item in data.get("resultados", []):
        categoria = item.get("categoria", "").strip()
        original = item.get("original", "").strip()
        correccion = item.get("correccion", "").strip()
        motivo = item.get("motivo", "").strip()
        id_txt = item.get("id", "").strip()

        if not all([categoria, original, correccion, motivo, id_txt]):
            continue

        # Comparación real tras normalización
        if texto_limpio(original) == texto_limpio(correccion):
            continue

        # Blindaje de caracteres editoriales
        if contiene_caracteres_especiales(original) and not contiene_caracteres_especiales(correccion):
            continue

        if original != correccion:
            linea = f"{categoria} | {id_txt} | {original} | {correccion} | {motivo}"
            lineas_validas.append(linea)
            contador[categoria] += 1

    if lineas_validas:
        with open(ruta_dest, "a", encoding="utf-8") as f:
            f.write("\n".join(lineas_validas) + "\n")

# -------------------------------------------------
# LLAMADA IA SEGURA
# -------------------------------------------------
def llamar_ia(texto_bloque):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT_AUDITORIA},
                {"role": "user", "content": texto_bloque}
            ],
            temperature=0
        )
        return res.choices[0].message.content.strip()

    except Exception as e:
        return f"ERROR_IA | {str(e)}"

