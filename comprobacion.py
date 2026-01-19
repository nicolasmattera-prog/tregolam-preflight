import os
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

# Configuración
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def comprobar_archivo(nombre_original):
    # Definición de rutas (Sincronizado con app.py)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(BASE_DIR)
    INPUT_FOLDER = os.path.join(ROOT_DIR, "entrada")
    OUTPUT_FOLDER = os.path.join(ROOT_DIR, "salida")
    
    ruta_input = os.path.join(INPUT_FOLDER, nombre_original)
    
    if not os.path.exists(ruta_input):
        return f"ERROR: No se encuentra el archivo en {ruta_input}"

    # Lectura del Word
    doc = Document(ruta_input)
    informe = [f"AUDITORÍA: {nombre_original}\n" + "="*30]
    
    bloque = []
    for i, p in enumerate(doc.paragraphs):
        texto = p.text.strip()
        if len(texto) < 5:
            continue
        
        bloque.append(f"ID_{i+1}: {texto}")

        # Procesamos cada 10 párrafos para evitar timeouts
        if len(bloque) >= 10:
            res_ia = enviar_a_ia("\n".join(bloque))
            if res_ia:
                informe.append(res_ia)
            bloque = []

    # Resto de párrafos
    if bloque:
        res_ia = enviar_a_ia("\n".join(bloque))
        if res_ia:
            informe.append(res_ia)

    # Guardar Informe
    nombre_txt = f"INFORME_{nombre_original.replace('.docx', '.txt')}"
    ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_txt)
    
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(informe))
        
    return nombre_txt

def enviar_a_ia(texto_bloque):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Analiza errores ortográficos. Formato: ID_X: error -> corrección. Si no hay errores en un ID, ignóralo."},
                {"role": "user", "content": texto_bloque}
            ],
            temperature=0,
            timeout=20
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None
