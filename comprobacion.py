import os
import re
from docx import Document
from spellchecker import SpellChecker
from openai import OpenAI
from dotenv import load_dotenv

# Configuración de servicios
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
spell = SpellChecker(language='es')

# Localización de carpetas (Sincronizado con tu app.py)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

def auditar_bloque(bloque):
    """Lógica de IA para auditar varios párrafos a la vez."""
    texto_peticion = "\n".join([f"ID_{i}: {t}" for i, t in bloque])
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un auditor ortográfico. Si hay error, responde 'ID_X: error -> corrección'. Si no hay error en un ID, ignóralo. No des explicaciones."},
                {"role": "user", "content": texto_peticion}
            ],
            temperature=0
        )
        return res.choices[0].message.content.strip()
    except:
        return ""

def comprobar_archivo(nombre_original):
    """ESTA ES LA FUNCIÓN QUE LLAMA TU APP.PY"""
    ruta_input = os.path.join(INPUT_FOLDER, nombre_original)
    doc = Document(ruta_input)
    
    informe = [f"INFORME DE AUDITORÍA: {nombre_original}\n" + "="*30]
    pendientes_ia = []

    # 1. Análisis rápido (Regex + Diccionario)
    for i, p in enumerate(doc.paragraphs):
        texto = p.text.strip()
        if len(texto) < 5: continue

        # Errores mecánicos
        if "  " in texto:
            informe.append(f"Párrafo {i+1}: [FORMATO] Doble espacio detectado.")

        # Dudas ortográficas
        palabras = re.findall(r'\b\w+\b', texto.lower())
        if spell.unknown(palabras):
            pendientes_ia.append((i+1, texto))

    # 2. Consulta agrupada a la IA (Batching)
    for j in range(0, len(pendientes_ia), 10):
        bloque = pendientes_ia[j:j+10]
        respuesta_ia = auditar_bloque(bloque)
        if respuesta_ia:
            informe.append(f"\nSugerencias (Párrafos {bloque[0][0]} a {bloque[-1][0]}):\n{respuesta_ia}")

    # 3. Guardar y devolver nombre para el botón de descarga
    nombre_informe = f"INFORME_{nombre_original.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(OUTPUT_FOLDER, nombre_informe)
    
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(informe))
        
    return nombre_informe # IMPORTANTE: app.py espera este string
