import os
import re
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# El filtro de "Librería" para ahorrar tokens
def tiene_error_potencial(texto):
    patrones = [r'\d%', r'\d°C', r'\d{5,}', r'[“”"]', r'[sS]i [aA]bría', r'\.\w', r' ,', r'  ']
    return any(re.search(p, texto) for p in patrones)

PROMPT_AUDITORIA = """Eres un AUDITOR TÉCNICO. Reporta errores de cifras, comillas latinas, espacios y gramática (si habría). 
FORMATO: ID_X: "error" -> "corrección" (Motivo). Si no hay errores, responde: SIN_ERRORES."""

def comprobar_archivo(ruta_completa):
    # Definir carpetas
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    try:
        # 1. Cargar documento
        doc = Document(ruta_completa)
        nombre_base = os.path.basename(ruta_completa)
        informe = [f"AUDITORÍA: {nombre_base}\n" + "="*30]
        
        bloque = []
        for i, p in enumerate(doc.paragraphs):
            t = p.text.strip()
            # Filtro: solo enviamos a la IA si hay sospecha
            if len(t) > 5 and tiene_error_potencial(t):
                bloque.append(f"ID_{i+1}: {t}")
            
            if len(bloque) >= 10:
                res = llamar_ia("\n".join(bloque))
                if res and "SIN_ERRORES" not in res:
                    informe.append(res)
                bloque = []
        
        if bloque:
            res = llamar_ia("\n".join(bloque))
            if res and "SIN_ERRORES" not in res:
                informe.append(res)

        if len(informe) <= 1:
            informe.append("No se detectaron errores técnicos.")

        # 2. Guardar resultado
        nombre_txt = f"INFORME_{nombre_base.replace('.docx', '.txt')}"
        ruta_txt = os.path.join(OUTPUT_FOLDER, nombre_txt)
        
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(informe))
            
        return nombre_txt # Retorna solo el nombre para que app.py construya la ruta

    except Exception as e:
        # Si falla, creamos un archivo de error para que no se bloquee la interfaz
        return f"Error: {str(e)}"

def llamar_ia(texto):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": PROMPT_AUDITORIA},
                      {"role": "user", "content": texto}],
            temperature=0, timeout=15
        )
        return res.choices[0].message.content.strip()
    except:
        return "SIN_ERRORES"
