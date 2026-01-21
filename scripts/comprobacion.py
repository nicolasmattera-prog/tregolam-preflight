import os
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

# PROMPT MEJORADO: Clasificación estricta y fin de falsos positivos
PROMPT_AUDITORIA = """Actúa como un auditor ortotipográfico implacable. Solo reporta errores reales.

CLASIFICACIÓN ESTRICTA:
- ORTOGRAFIA: Solo para errores de escritura, acentos, concordancia o mayúsculas.
- FORMATO: Rayas de diálogo, espacios, puntos finales, cifras.
- SUGERENCIA: Estilo, cambios de palabras (ej. subjuntivos), léxico. 

REGLAS DE ORO (PROHIBICIONES):
1. COMILLAS: Si el texto original YA TIENE comillas latinas « », es CORRECTO. NO lo reportes. Es un error grave reportar comillas que ya son latinas.
2. SIN CAMBIO: Si no vas a proponer un cambio real en el texto, no reportes nada.
3. ESTILO: Cualquier mejora de redacción que no sea una falta de ortografía DEBE ser CATEGORIA: SUGERENCIA.

FORMATO: CATEGORIA | ID | ORIGINAL | CORRECCION | MOTIVO"""

def comprobar_archivo(nombre_archivo):
    ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)
    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)
    
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write("")

    try:
        doc = Document(ruta_lectura)
        parrafos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]
        bloque = []

        for i, texto in enumerate(parrafos):
            bloque.append(f"ID_{i+1}: {texto}")
            if len(bloque) >= 8:
                respuesta = llamar_ia("\n".join(bloque))
                procesar_y_guardar(respuesta, ruta_txt)
                bloque = []

        if bloque:
            respuesta = llamar_ia("\n".join(bloque))
            procesar_y_guardar(respuesta, ruta_txt)
        return nombre_txt
    except Exception as e:
        return f"ERROR: {str(e)}"

def procesar_y_guardar(respuesta, ruta_dest):
    if not respuesta or "S_OK" in respuesta.upper():
        return
    lineas_ia = respuesta.split("\n")
    lineas_limpias = []
    for linea in lineas_ia:
        linea = linea.strip()
        if linea.count("|") == 4:
            partes = [p.strip() for p in linea.split("|")]
            # Filtrado extra: si la IA reporta algo como igual, lo descartamos aquí también
            if "CATEGORIA" not in partes[0].upper() and partes[2] != partes[3]:
                lineas_limpias.append(" | ".join(partes))
    if lineas_limpias:
        with open(ruta_dest, "a", encoding="utf-8") as f:
            f.write("\n".join(lineas_limpias) + "\n")

def llamar_ia(texto_bloque):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT_AUDITORIA},
                {"role": "user", "content": texto_bloque}
            ],
            temperature=0 # Temperatura 0 para máxima precisión
        )
        return res.choices[0].message.content.strip()
    except:
        return "S_OK"
