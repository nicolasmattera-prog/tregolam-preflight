import os
import re
from docx import Document
from spellchecker import SpellChecker
from openai import OpenAI
from dotenv import load_dotenv

# Configuración básica
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
spell = SpellChecker(language='es')

# RUTAS SIMPLIFICADAS: Todo relativo a este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Subimos un nivel si estamos en la carpeta 'scripts'
ROOT_DIR = os.path.dirname(BASE_DIR) 
INPUT_FOLDER = os.path.join(ROOT_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(ROOT_DIR, "salida")

# Crear carpetas si no existen para evitar errores de "Ruta no encontrada"
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def auditar_bloque(bloque):
    """Envía un grupo de párrafos para ganar velocidad sin perder precisión."""
    texto_para_ia = "\n".join([f"ID_{i}: {t}" for i, t in bloque])
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un corrector ortográfico. REGLA: Si hay error, responde 'ID_X: error -> corrección'. Si no hay, no digas nada de ese ID. NO REESCRIBAS EL TEXTO."},
                {"role": "user", "content": texto_para_ia}
            ],
            temperature=0
        )
        return res.choices[0].message.content.strip()
    except:
        return ""

def procesar():
    archivos = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".docx")]
    if not archivos:
        print("No hay archivos en la carpeta 'entrada'.")
        return

    for nombre_fichero in archivos:
        print(f"--- Iniciando: {nombre_fichero} ---")
        doc = Document(os.path.join(INPUT_FOLDER, nombre_fichero))
        pendientes_ia = []
        informe = [f"AUDITORÍA: {nombre_fichero}\n" + "="*30]

        for i, p in enumerate(doc.paragraphs):
            texto = p.text.strip()
            if len(texto) < 4: continue

            # Filtro 1: Doble espacio (Gratis/Rápido)
            if "  " in texto:
                informe.append(f"Párrafo {i+1}: [FORMATO] Doble espacio detectado.")

            # Filtro 2: Diccionario (Gratis/Rápido)
            palabras = re.findall(r'\b\w+\b', texto.lower())
            if spell.unknown(palabras):
                pendientes_ia.append((i+1, texto))

        # Procesar con IA en bloques de 10 (Más seguro que 15 para evitar cortes)
        for j in range(0, len(pendientes_ia), 10):
            bloque = pendientes_ia[j:j+10]
            respuesta = auditar_bloque(bloque)
            if respuesta:
                informe.append(f"\nSugerencias detectadas:\n{respuesta}")

        # Guardar resultado
        ruta_txt = os.path.join(OUTPUT_FOLDER, f"RESULTADO_{nombre_fichero}.txt")
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(informe))
        print(f"--- Finalizado: {ruta_txt} ---")

if __name__ == "__main__":
    procesar()
