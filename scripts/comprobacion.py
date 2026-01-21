import os
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

PROMPT_AUDITORIA = """Actúa como un auditor ortotipográfico experto. Tu tarea es clasificar errores en: ORTOGRAFIA, FORMATO o SUGERENCIA.

REGLAS TÉCNICAS:
1. CIFRAS: Espacio de no ruptura en miles (Ej: 20 000). NO puntos ni comas.
2. COMILLAS: Convertir "" o '' en latinas « ». SI YA SON « », NO REPORTAR NADA.
3. RAYAS: Diálogos con raya larga — pegada al texto (Ej: —Hola).
4. SÍMBOLOS: Espacio entre cifra y símbolo (Ej: 10 %).

FORMATO DE RESPUESTA (ESTRICTO - UNA SOLA LÍNEA POR ERROR):
CATEGORIA | ID | ORIGINAL | CORRECCION | MOTIVO
Si no hay errores, responde únicamente: S_OK"""

def comprobar_archivo(nombre_archivo):
    ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)
    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)
    
    # Limpiamos el archivo para empezar de cero
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
    """Limpia la respuesta de la IA de cabeceras y líneas fragmentadas antes de guardar."""
    if not respuesta or "S_OK" in respuesta.upper():
        return

    lineas_validas = []
    # Dividimos por líneas y filtramos morralla
    for linea in respuesta.split("\n"):
        linea = linea.strip()
        # Solo aceptamos líneas con el separador que NO sean la cabecera
        if "|" in linea and "CATEGORIA" not in linea.upper() and "ORIGINAL" not in linea.upper():
            # Limpiamos espacios internos para evitar saltos de línea fantasmas
            lineas_validas.append(" ".join(linea.split()))

    if lineas_validas:
        with open(ruta_dest, "a", encoding="utf-8") as f:
            f.write("\n".join(lineas_validas) + "\n")

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
    except:
        return "S_OK"
