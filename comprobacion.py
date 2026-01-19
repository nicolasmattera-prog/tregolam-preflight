import os
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def comprobar_archivo(nombre_original):
    # Rutas relativas al repositorio
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_FOLDER = os.path.join(os.path.dirname(BASE_DIR), "entrada")
    OUTPUT_FOLDER = os.path.join(os.path.dirname(BASE_DIR), "salida")
    
    ruta_input = os.path.join(INPUT_FOLDER, nombre_original)
    
    if not os.path.exists(ruta_input):
        return f"ERROR: No existe {nombre_original}"

    doc = Document(ruta_input)
    informe = [f"AUDITORÍA DE: {nombre_original}\n" + "="*30]
    
    # Procesamos en bloques para que sea rápido pero no sature
    texto_acumulado = []
    
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if len(t) > 10:
            texto_acumulado.append(f"P{i+1}: {t}")

        # Enviamos cada 15 párrafos para no exceder límites y ser rápidos
        if len(texto_acumulado) >= 15:
            resultado = enviar_a_ia("\n".join(texto_acumulado))
            if resultado:
                informe.append(resultado)
            texto_acumulado = []

    # Enviar lo que quede
    if texto_acumulado:
        resultado = enviar_a_ia("\n".join(texto_acumulado))
        if resultado:
            informe.append(resultado)

    nombre_informe = f"INFORME_{nombre_original.replace('.docx', '.txt')}"
    ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_informe)
    
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(informe))
        
    return nombre_informe

def enviar_a_ia(texto):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un corrector experto. Analiza los párrafos y lista SOLO los errores reales: 'PX: error -> corrección'. Si no hay errores, no escribas nada."},
                {"role": "user", "content": texto}
            ],
            temperature=0,
            timeout=15 # Si en 15 seg no responde, saltamos para no bloquear la app
        )
        return res.choices[0].message.content.strip()
    except:
        return None
