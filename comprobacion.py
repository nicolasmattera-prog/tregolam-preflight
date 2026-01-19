import os
import re
from docx import Document
from spellchecker import SpellChecker
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
spell = SpellChecker(language='es')

def comprobar_archivo(nombre_original):
    # Definición de rutas absolutas para evitar bloqueos
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_FOLDER = os.path.join(os.path.dirname(BASE_DIR), "entrada")
    OUTPUT_FOLDER = os.path.join(os.path.dirname(BASE_DIR), "salida")
    
    ruta_input = os.path.join(INPUT_FOLDER, nombre_original)
    doc = Document(ruta_input)
    
    informe = [f"AUDITORÍA: {nombre_original}\n" + "="*30]
    
    # Procesamiento directo
    for i, p in enumerate(doc.paragraphs):
        texto = p.text.strip()
        if len(texto) < 5: continue

        # Solo enviamos a la IA si el diccionario local detecta algo raro
        palabras = re.findall(r'\b\w+\b', texto.lower())
        if spell.unknown(palabras):
            try:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Corrector ortográfico. Formato: error -> corrección. Si no hay error, responde OK."},
                        {"role": "user", "content": texto}
                    ],
                    timeout=10, # Evita que se quede girando para siempre
                    temperature=0
                )
                sugerencia = res.choices[0].message.content.strip()
                if "OK" not in sugerencia.upper():
                    informe.append(f"Párrafo {i+1}: {sugerencia}")
            except:
                continue

    nombre_informe = f"INFORME_{nombre_original.replace('.docx', '.txt')}"
    ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_informe)
    
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(informe))
        
    return nombre_informe
