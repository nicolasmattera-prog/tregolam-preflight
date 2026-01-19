#!/usr/bin/env python3
import os
from docx import Document

# IMPORTAMOS LAS REGLAS YA EXISTENTES (SIN IA)
from precorreccion import (
    limpieza_mecanica,
    correcciones_gramaticales_seguras
)

# ---------- RUTAS ----------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- COMPROBACIÓN ----------
def comprobar_archivo(name):
    ruta_entrada = os.path.join(INPUT_FOLDER, name)
    doc = Document(ruta_entrada)

    informe = [f"AUDITORÍA DE CALIDAD: {name}\n" + "=" * 40 + "\n"]
    avisos = 0

    # --- recoger TODOS los párrafos (texto + tablas) ---
    parrafos = []
    for p in doc.paragraphs:
        parrafos.append(p)
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    parrafos.append(p)

    for i, p in enumerate(parrafos):
        texto = p.text
        if not texto.strip():
            continue

        # Aplicamos reglas, PERO NO GUARDAMOS EL RESULTADO
        texto_limpio = limpieza_mecanica(texto)
        texto_reglas = correcciones_gramaticales_seguras(texto_limpio)

        # Si alguna regla cambiaría algo → aviso
        if texto_reglas != texto:
            avisos += 1
            informe.append(f"📍 PÁRRAFO {i+1}")
            informe.append("MOTIVO: Posible errata mecánica / gramatical objetiva")
            informe.append(f"TEXTO: {texto}")
            informe.append("-" * 20)

    nombre_txt = f"VALIDACION_{name.replace('.docx', '')}.txt"
    ruta_txt = os.path.join(OUTPUT_FOLDER, nombre_txt)

    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(informe))

    return nombre_txt
