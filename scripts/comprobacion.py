import os
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

PROMPT_AUDITORIA = """Actúa como un auditor ortotipográfico. Clasifica errores en: ORTOGRAFIA, FORMATO o SUGERENCIA.

REGLAS:
1. CIFRAS: Espacio de no ruptura en miles (20 000).
2. COMILLAS: Convertir "" en latinas « ».
3. RAYAS: Diálogos con raya larga —pegada al texto.
4. SIMBOLOS: Espacio entre cifra y símbolo (10 %).

FORMATO DE SALIDA (ESTRICTO, UNA LINEA POR ERROR):
CATEGORIA | ID | ORIGINAL | CORRECCION | MOTIVO
Si no hay errores, responde: S_OK"""

def comprobar_archivo(nombre_archivo):
    ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)
    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)
    
    # Limpiar archivo previo
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
                if respuesta and "S_OK" not in respuesta.upper():
                    with open(ruta_txt, "a", encoding="utf-8") as f:
                        # Limpiamos saltos de línea extra para que no se rompa el formato
                        limpio = "\n".join([line.strip() for line in respuesta.split("\n") if "|" in line])
                        if limpio:
                            f.write(limpio + "\n")
                bloque = []

        if bloque:
            respuesta = llamar_ia("\n".join(bloque))
            if respuesta and "S_OK" not in respuesta.upper():
                with open(ruta_txt, "a", encoding="utf-8") as f:
                    limpio = "\n".join([line.strip() for line in respuesta.split("\n") if "|" in line])
                    if limpio:
                        f.write(limpio + "\n")

        return nombre_txt
    except Exception as e:
        return f"ERROR: {str(e)}"

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
