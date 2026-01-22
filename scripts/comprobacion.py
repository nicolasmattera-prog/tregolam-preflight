# scripts/comprobacion.py
import os
import json
import spacy
from docx import Document
from regex_rules import aplicar_regex_editorial

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

def comprobar_archivo(nombre_archivo):
    # Cargar el modelo español completo en lugar de blank
    try:
        nlp = spacy.load("es_core_news_sm")
    except OSError:
        print("Error: No se encontró el modelo es_core_news_sm")
        print("Por favor ejecuta: python -m spacy download es_core_news_sm")
        return None

    ruta_excepciones = os.path.join(BASE_DIR, "data", "excepciones.json")
    excepciones = {}
    if os.path.exists(ruta_excepciones):
        with open(ruta_excepciones, "r", encoding="utf-8") as f:
            excepciones = json.load(f)

    # Buscar primero en entrada, luego en salida
    ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)
    if not os.path.exists(ruta_lectura):
        ruta_lectura = os.path.join(SALIDA_DIR, nombre_archivo)
    if not os.path.exists(ruta_lectura):
        print(f"Error: No se encontró el archivo {nombre_archivo}")
        return None

    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)

    try:
        doc = Document(ruta_lectura)
        textos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]

        hallazgos = []

        for i, doc_spacy in enumerate(nlp.pipe(textos)):
            pid = f"ID_{i+1}"
            texto = textos[i]
            fijo = aplicar_regex_editorial(texto)

            if texto != fijo:
                hallazgos.append(
                    f"FORMATO | {pid} | {texto[:40]} | {fijo[:40]} | Espacios o signos"
                )

            for token in doc_spacy:
                palabra = token.text.lower()
                if palabra in excepciones:
                    hallazgos.append(
                        f"ORTOGRAFIA | {pid} | {token.text} | {excepciones[palabra]} | Diccionario"
                    )

        with open(ruta_txt, "w", encoding="utf-8") as f:
            if hallazgos:
                for h in hallazgos:
                    partes = [p.strip() for p in h.split("|")]
                    while len(partes) < 5:
                        partes.append("-")
                    f.write(" | ".join(partes[:5]) + "\n")
            else:
                f.write("FORMATO | ID_0 | Sin errores | - | No se detectaron fallos\n")

        return nombre_txt
        
    except Exception as e:
        print(f"Error procesando el archivo: {e}")
        return None
