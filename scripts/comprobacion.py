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
    """Descarga e instala el modelo si no existe."""
    modelo = "es_core_news_sm"
    try:
        return spacy.load(modelo, disable=["ner", "parser", "lemmatizer"])
    except OSError:
        import subprocess
        import sys
        subprocess.run([sys.executable, "-m", "spacy", "download", modelo], check=True)
        return spacy.load(modelo, disable=["ner", "parser", "lemmatizer"])

def comprobar_archivo(nombre_archivo):
    nlp = cargar_nlp()

    ruta_lectura = os.path.join(SALIDA_DIR, nombre_archivo)
    if not os.path.exists(ruta_lectura):
        ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)
    
    if not os.path.exists(ruta_lectura):
        return f"ERROR: No se encuentra {nombre_archivo}"

    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)

    try:
        doc = Document(ruta_lectura)
        textos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]
        hallazgos = []

        for i, doc_spacy in enumerate(nlp.pipe(textos, batch_size=50)):
            texto_original = textos[i]
            if texto_original != aplicar_regex_editorial(texto_original):
                hallazgos.append(f"FORMATO | Párrafo {i+1} | Error técnico o de espacios")

            for token in doc_spacy:
                palabra = token.text.lower()
                if token.is_oov and not (token.is_punct or token.like_num or token.pos_ == "PROPN"):
                    hallazgos.append(f"ORTOGRAFIA | Párrafo {i+1} | {token.text} | No reconocida")

        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(f"INFORME DE AUDITORÍA: {len(hallazgos)} avisos encontrados.\n")
            f.write("=" * 50 + "\n\n")
            f.write("\n".join(hallazgos) if hallazgos else "No se detectaron errores.")

        return nombre_txt

    except Exception as e:
        return f"ERROR CRÍTICO: {str(e)}"
