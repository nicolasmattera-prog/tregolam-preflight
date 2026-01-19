#!/usr/bin/env python3
import os
import re
from docx import Document

# ---------- RUTAS ----------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- NORMALIZACIÓN PARA AUDITORÍA ----------
def normalizar_para_auditoria(texto):
    if not texto:
        return ""
    t = texto
    t = re.sub(r'\s+', ' ', t)
    t = t.strip()
    return t

# ---------- REGLAS OBJETIVAS ----------
REGLAS = [
    ("Hora mal espaciada", re.compile(r'\b\d{1,2}:\s+\d{2}\b')),
    ("Doble espacio", re.compile(r'  +')),
    ("Puntuación duplicada", re.compile(r'([.,;:!?])\1+')),
    ("Signo pegado", re.compile(r'[a-zA-ZáéíóúÁÉÍÓÚ][¿¡]')),
    ("Espacio antes de coma/punto", re.compile(r'\s+[,.]')),
    ("Comillas no latinas", re.compile(r'[“”"]')),
]

# ---------- COMPROBACIÓN ----------
def comprobar_archivo(name):
    ruta_entrada = os.path.join(INPUT_FOLDER, name)
    doc = Document(ruta_entrada)

    informe = [f"AUDITORÍA DE CALIDAD: {name}\n" + "=" * 40 + "\n"]
    avisos = 0

    for i, p in enumerate(doc.paragraphs):
        texto = p.text
        if not texto.strip():
            continue

        texto_norm = normalizar_para_auditoria(texto)

        for motivo, patron in REGLAS:
            if patron.search(texto_norm):
                avisos += 1
                informe.append(f"📍 PÁRRAFO {i+1}")
                informe.append(f"MOTIVO: {motivo}")
                informe.append(f"TEXTO: {texto}")
                informe.append("-" * 20)
                break  # un aviso por párrafo, suficiente

    nombre_txt = f"VALIDACION_{name.replace('.docx', '')}.txt"
    ruta_txt = os.path.join(OUTPUT_FOLDER, nombre_txt)

    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(informe))

    return nombre_txt

