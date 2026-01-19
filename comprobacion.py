import os
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

# 1. Configuración limpia
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def comprobar_archivo(nombre_original):
    # 2. Rutas absolutas directas
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
    
    # Asegurar que las carpetas existen para evitar errores de arranque
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    ruta_input = os.path.join(INPUT_FOLDER, nombre_original)
    
    if not os.path.exists(ruta_input):
        return f"ERROR: No se encuentra {nombre_original}"

    # 3. Procesamiento
    doc = Document(ruta_input)
    informe = [f"AUDITORÍA: {nombre_original}\n" + "="*30]
    
    bloque = []
    for i, p in enumerate(doc.paragraphs):
        texto = p.text.strip()
        if len(texto) < 5: continue
        
        bloque.append(f"ID_{i+1}: {texto}")

        if len(bloque) >= 10:
            res_ia = enviar_a_ia("\n".join(bloque))
            if res_ia:
                informe.append(res_ia)
            bloque = []

    if bloque:
        res_ia = enviar_a_ia("\n".join(bloque))
        if res_ia:
            informe.append(res_ia)

    # 4. Salida
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
                {"role": "system", "content": "Corrector ortográfico. Formato: ID_X: error -> corrección. Si no hay errores, no respondas nada."},
                {"role": "user", "content": texto_bloque}
            ],
            temperature=0,
            timeout=15
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None
