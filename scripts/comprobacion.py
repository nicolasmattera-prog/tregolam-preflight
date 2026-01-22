import os
import json
import spacy
import streamlit as st
from docx import Document
from regex_rules import aplicar_regex_editorial

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

@st.cache_resource
def cargar_nlp():
    try:
        return spacy.load(
            "es_core_news_sm",
            disable=["ner", "parser", "lemmatizer"]
        )
    except Exception:
        return spacy.blank("es")

def comprobar_archivo(nombre_archivo):
    nlp = cargar_nlp()

    ruta_excepciones = os.path.join(BASE_DIR, "data", "excepciones.json")
    excepciones = {}
    if os.path.exists(ruta_excepciones):
        try:
            with open(ruta_excepciones, "r", encoding="utf-8") as f:
                excepciones = json.load(f)
        except:
            excepciones = {}

    ruta_lectura = os.path.join(SALIDA_DIR, nombre_archivo)
    if not os.path.exists(ruta_lectura):
        ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)

    if not os.path.exists(ruta_lectura):
        return f"ERROR: No se encuentra {nombre_archivo}"

    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)

    doc = Document(ruta_lectura)
    textos_parrafos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]
    hallazgos = []

    for i, doc_spacy in enumerate(nlp.pipe(textos_parrafos, batch_size=50)):
        texto_original = textos_parrafos[i]

        if texto_original != aplicar_regex_editorial(texto_original):
            hallazgos.append(f"FORMATO | Párrafo {i+1} | Error técnico o de espacios")

        for token in doc_spacy:
            palabra_low = token.text.lower()

            if palabra_low in excepciones:
                hallazgos.append(
                    f"ORTOGRAFIA | Párrafo {i+1} | {token.text} | {excepciones[palabra_low]}"
                )
                continue

            if token.is_oov and not (
                token.is_punct or token.like_num
            ):
                hallazgos.append(
                    f"ORTOGRAFIA | Párrafo {i+1} | {token.text} | No reconocida"
                )

    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(f"INFORME DE AUDITORÍA: {len(hallazgos)} avisos encontrados.\n")
        f.write("=" * 50 + "\n\n")
        f.write("\n".join(hallazgos) if hallazgos else "No se detectaron errores.")

    return nombre_txt
