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
spell = SpellChecker(language='es')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- REGLAS MECÁNICAS (COSTE 0) ----------
REGLAS_TIPOGRAFICAS = [
    ("Doble espacio", r'  +'),
    ("Hora mal espaciada", r'\b\d{1,2}:\s+\d{2}\b'),
    ("Puntuación pegada", r'([.,;:!])([a-zA-ZáéíóúÁÉÍÓÚ])'),
    ("Espacio antes de signo", r'\s+([,.:;?])'),
    ("Comillas no latinas", r'[“”"]'),
]

def auditar_ortografia_ia(texto):
    """
    Solo envía el párrafo si hay dudas y pide una lista mínima de errores.
    """
    prompt_auditor = (
        "Actúa como un auditor ortográfico. Analiza el texto y devuelve "
        "ÚNICAMENTE una lista de errores en formato: 'error -> corrección'. "
        "Si no hay errores, responde solo 'OK'. No reescribas el párrafo."
    )
    
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini", # El más barato y rápido
            messages=[
                {"role": "system", "content": prompt_auditor},
                {"role": "user", "content": texto}
            ],
            temperature=0
        )
        respuesta = res.choices[0].message.content.strip()
        return None if respuesta.upper() == "OK" else respuesta
    except Exception as e:
        return f"Error API: {e}"

def comprobar_archivo(name):
    ruta_entrada = os.path.join(INPUT_FOLDER, name)
    doc = Document(ruta_entrada)
    informe = [f"INFORME DE AUDITORÍA: {name}\n" + "="*40 + "\n"]
    
    for i, p in enumerate(doc.paragraphs):
        texto = p.text.strip()
        if not texto: continue

        errores_parrafo = []

        # 1. Filtro Regex (Mecánico)
        for nombre, patron in REGLAS_TIPOGRAFICAS:
            if re.search(patron, p.text):
                errores_parrafo.append(f"[TIPOGRAFÍA] {nombre}")

        # 2. Filtro Diccionario Local (Ortografía base)
        # Limpiamos el texto de signos para chequear palabras
        palabras = re.findall(r'\b\w+\b', texto.lower())
        desconocidas = spell.unknown(palabras)

        # 3. Solo si hay palabras sospechosas, consultamos a la IA
        if desconocidas:
            resultado_ia = auditar_ortografia_ia(texto)
            if resultado_ia:
                errores_parrafo.append(f"[ORTOGRAFÍA] {resultado_ia}")

        if errores_parrafo:
            informe.append(f"📍 PÁRRAFO {i+1}:")
            informe.append(f"   \"{texto[:100]}...\"")
            for err in errores_parrafo:
                informe.append(f"   - {err}")
            informe.append("-" * 20)

    # Guardar informe final
    nombre_informe = f"INFORME_{name.replace('.docx', '.txt')}"
    with open(os.path.join(OUTPUT_FOLDER, nombre_informe), "w", encoding="utf-8") as f:
        f.write("\n".join(informe))
    return nombre_informe

if __name__ == "__main__":
    for f in os.listdir(INPUT_FOLDER):
        if f.endswith(".docx"):
            print(f"Auditando: {f}...")
            rep = comprobar_archivo(f)
            print(f"✅ Informe listo: {rep}")
