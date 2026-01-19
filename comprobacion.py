#!/usr/bin/env python3
import os
import re
from docx import Document
from spellchecker import SpellChecker
from openai import OpenAI
from dotenv import load_dotenv

# ---------- CONFIGURACIÓN ----------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Cargamos el diccionario en español
spell = SpellChecker(language='es')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def limpiar_palabra(palabra):
    """Elimina signos de puntuación pegados a la palabra para no engañar al corrector."""
    return re.sub(r'[^\wáéíóúÁÉÍÓÚñÑ]', '', palabra)

def auditar_con_ia(texto):
    """Consulta a la IA solo si hay dudas reales, pidiendo el formato solicitado."""
    prompt = (
        "Actúa como un auditor de textos. Tu tarea es encontrar errores ortográficos o gramaticales. "
        "Si encuentras errores, lístalos así: 'Error -> Corrección'. "
        "Si el texto es correcto, responde solo 'OK'. "
        "No des explicaciones, solo la lista o la palabra OK."
    )
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": texto}
            ],
            temperature=0
        )
        respuesta = res.choices[0].message.content.strip()
        return None if respuesta.upper() == "OK" else respuesta
    except:
        return None

def comprobar_archivo(name):
    ruta_entrada = os.path.join(INPUT_FOLDER, name)
    doc = Document(ruta_entrada)
    informe = [f"INFORME DE AUDITORÍA: {name}\n" + "="*40 + "\n"]
    
    for i, p in enumerate(doc.paragraphs):
        texto = p.text.strip()
        if not texto or len(texto) < 2: continue

        # 1. REGLAS MECÁNICAS (Regex) - Coste 0
        errores_mecanicos = []
        if "  " in texto:
            errores_mecanicos.append("Doble espacio detectado")
        if re.search(r'[.,;!?:»])(?=[a-zA-Záéíóú])', texto):
            errores_mecanicos.append("Falta espacio tras signo de puntuación")

        # 2. FILTRO DE DICCIONARIO (Mejorado)
        # Separamos por espacios y limpiamos cada palabra de signos
        palabras_sucias = texto.split()
        palabras_limpias = [limpiar_palabra(w) for w in palabras_sucias if limpiar_palabra(w)]
        
        # Solo palabras que no son números y tienen longitud > 1
        palabras_a_revisar = [w for w in palabras_limpias if not w.isdigit()]
        desconocidas = spell.unknown(palabras_a_revisar)

        # 3. LLAMADA A IA (Solo si hay sospechas)
        hallazgos_ia = None
        if desconocidas or errores_mecanicos:
            hallazgos_ia = auditar_con_ia(texto)

        # 4. CONSTRUCCIÓN DEL INFORME
        if errores_mecanicos or hallazgos_ia:
            informe.append(f"📍 PÁRRAFO {i+1}")
            informe.append(f"TEXTO: {texto}")
            for err in errores_mecanicos:
                informe.append(f"   - [MECÁNICO]: {err}")
            if hallazgos_ia:
                informe.append(f"   - [CORRECCIÓN]: {hallazgos_ia}")
            informe.append("-" * 30)

    # Guardado
    with open(os.path.join(OUTPUT_FOLDER, f"AUDITORIA_{name}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(informe))

if __name__ == "__main__":
    for f in os.listdir(INPUT_FOLDER):
        if f.endswith(".docx"):
            print(f"Analizando: {f}")
            comprobar_archivo(f)
