import os
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

# 1. Carga de configuración
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def comprobar_archivo(nombre_original):
    # 2. Rutas (Ajustadas a la estructura de tu repo)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Si app.py está en la raíz y este en /src o similar, ajustamos:
    ROOT_DIR = os.path.dirname(BASE_DIR) 
    INPUT_FOLDER = os.path.join(ROOT_DIR, "entrada")
    OUTPUT_FOLDER = os.path.join(ROOT_DIR, "salida")
    
    ruta_input = os.path.join(INPUT_FOLDER, nombre_original)
    
    if not os.path.exists(ruta_input):
        return f"Error: No se encuentra el archivo {nombre_original}"

    # 3. Lectura del documento
    doc = Document(ruta_input)
    informe = [f"AUDITORÍA: {nombre_original}\n" + "="*30]
    
    bloque_texto = []
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if len(t) > 5:
            bloque_texto.append(f"ID_{i+1}: {t}")

        # Enviamos a la IA en grupos de 10 párrafos
        if len(bloque_texto) >= 10:
            resultado = enviar_a_ia("\n".join(bloque_texto))
            if resultado:
                informe.append(resultado)
            bloque_texto = []

    # 4. Procesar el resto
    if bloque_texto:
        resultado = enviar_a_ia("\n".join(bloque_texto))
        if resultado:
            informe.append(resultado)

    # 5. Guardado del informe TXT
    nombre_txt = f"INFORME_{nombre_original.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(OUTPUT_FOLDER, nombre_txt)
    
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(informe))
        
    return nombre_txt

def enviar_a_ia(texto):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Corrector ortográfico. Formato: ID_X: error -> corrección. Si no hay error, no escribas nada."},
                {"role": "user", "content": texto}
            ],
            temperature=0,
            timeout=20
        )
        return res.choices[0].message.content.strip()
    except Exception:
        return None
