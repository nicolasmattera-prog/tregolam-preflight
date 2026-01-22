import os
import json
import spacy
from docx import Document
from regex_rules import aplicar_regex_editorial

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

nlp = spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])

def comprobar_archivo(nombre_archivo):
    ruta = os.path.join(ENTRADA_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return None

    excepciones = {}
    ruta_exc = os.path.join(BASE_DIR, "data", "excepciones.json")
    if os.path.exists(ruta_exc):
        with open(ruta_exc, "r", encoding="utf-8") as f:
            excepciones = json.load(f)

    doc = Document(ruta)
    textos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]

    salida = os.path.join(
        SALIDA_DIR,
        f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    )

    hallazgos = []

    for i, d in enumerate(nlp.pipe(textos)):
        pid = f"ID_{i+1}"
        original = textos[i]
        fijo = aplicar_regex_editorial(original)

        if original != fijo:
            hallazgos.append(
                f"FORMATO | {pid} | {original[:40]} | {fijo[:40]} | Espacios o signos"
            )

        for t in d:
            w = t.text.lower()
            if w in excepciones:
                hallazgos.append(
                    f"ORTOGRAFIA | {pid} | {t.text} | {excepciones[w]} | Diccionario"
                )

    with open(salida, "w", encoding="utf-8") as f:
        if hallazgos:
            for h in hallazgos:
                f.write(h + "\n")
        else:
            f.write("FORMATO | ID_0 | Sin errores | - | OK\n")

    return os.path.basename(salida)
