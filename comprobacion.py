import os
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

# Cargamos entorno
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def comprobar_archivo(nombre_original):
    # Rutas relativas al servidor
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(BASE_DIR)
    INPUT_FOLDER = os.path.join(ROOT_DIR, "entrada")
    OUTPUT_FOLDER = os.path.join(ROOT_DIR, "salida")
    
    ruta_input = os.path.join(INPUT_FOLDER, nombre_original)
    
    # Verificación de existencia
    if not os.path.exists(ruta_input):
        return f"Error: No se encuentra el archivo {nombre_original}"

    doc = Document(ruta_input)
    informe = [f"AUDITORÍA: {nombre_original}\n" + "="*30]
    
    # Procesamos en bloques para evitar cortes de conexión
    bloque_actual = []
    
    for i, p in enumerate(doc.paragraphs):
        texto = p.text.strip()
        if len(texto) < 5: 
            continue
        
        bloque_actual.append(f"ID_{i+1}: {texto}")

        # Enviamos a la IA cada 10 párrafos (ideal para 6 páginas)
        if len(bloque_actual) >= 10:
            resultado = enviar_a_ia("\n".join(bloque_actual))
            if resultado:
                informe.append(resultado)
            bloque_actual = []

    # Procesar párrafos restantes
    if bloque_actual:
        resultado = enviar_a_ia("\n".join(bloque_actual))
        if resultado:
            informe.append(resultado)

    # Guardado final
    nombre_txt = f"INFORME_{nombre_original.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(OUTPUT_FOLDER, nombre_txt)
    
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(informe))
        
    return nombre_txt

def enviar_a_ia(texto):
    try:
        # Timeout de 20 segundos para no bloquear el spinner de Streamlit
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Corrector ortográfico técnico. Formato: 'ID_X: error -> corrección'. Si no hay errores en un ID, no lo menciones."},
                {"role": "user", "content": texto}
            ],
            temperature=0,
            timeout=20
        )
        return res.choices[0].message.content.strip()
    except Exception:
        # Si falla la conexión, devolvemos aviso para que el proceso no se pare
        return "[Error de conexión en este bloque]"
