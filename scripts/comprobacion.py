import os
import json
import sys
import subprocess
from docx import Document
from regex_rules import aplicar_regex_editorial

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

def instalar_y_cargar_nlp():
    import spacy
    try:
        # Intento 1: Carga normal
        return spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])
    except:
        try:
            # Intento 2: Descarga forzada en ejecución
            subprocess.run([sys.executable, "-m", "spacy", "download", "es_core_news_sm"], check=True)
            return spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])
        except:
            return None

def comprobar_archivo(nombre_archivo):
    # Intentar cargar el motor
    nlp = instalar_y_cargar_nlp()
    
    # Cargar excepciones
    ruta_excepciones = os.path.join(BASE_DIR, "data", "excepciones.json")
    excepciones = {}
    if os.path.exists(ruta_excepciones):
        try:
            with open(ruta_excepciones, "r", encoding="utf-8") as f:
                excepciones = json.load(f)
        except: pass

    # Rutas
    ruta_lectura = os.path.join(SALIDA_DIR, nombre_archivo)
    if not os.path.exists(ruta_lectura):
        ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)

    if not os.path.exists(ruta_lectura):
        return f"ERROR: No se encuentra {nombre_archivo}"

    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)

    try:
        doc = Document(ruta_lectura)
        hallazgos = []

        for i, p in enumerate(doc.paragraphs):
            texto = p.text.strip()
            if len(texto) < 5: continue
            
            p_id = f"ID_{i+1}"

            # 1. TEST REGEX (Siempre funciona)
            texto_fixed = aplicar_regex_editorial(texto)
            if texto != texto_fixed:
                hallazgos.append(f"FORMATO | {p_id} | {texto[:30]} | {texto_fixed[:30]} | Espacios o símbolos")

            # 2. TEST LINGÜÍSTICO (Si spaCy cargó)
            if nlp:
                doc_nlp = nlp(texto)
                for token in doc_nlp:
                    palabra = token.text.lower()
                    if palabra in excepciones:
                        hallazgos.append(f"ORTOGRAFIA | {p_id} | {token.text} | {excepciones[palabra]} | Diccionario personal")
                    elif token.is_oov and not (token.is_punct or token.like_num or token.pos_ == "PROPN"):
                        hallazgos.append(f"ORTOGRAFIA | {p_id} | {token.text} | Revisar | No reconocida")
            else:
                # Si no hay spaCy, al menos revisamos las excepciones manualmente
                for pal_exc, corr in excepciones.items():
                    if pal_exc in texto.lower():
                        hallazgos.append(f"ORTOGRAFIA | {p_id} | {pal_exc} | {corr} | Diccionario personal (Manual)")

        # GUARDADO OBLIGATORIO PARA QUE APP.PY VEA ALGO
        with open(ruta_txt, "w", encoding="utf-8") as f:
            if hallazgos:
                f.write("\n".join(hallazgos))
            else:
                f.write("FORMATO | ID_0 | Sin errores | - | No se detectaron fallos")

        return nombre_txt

    except Exception as e:
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(f"FORMATO | ID_0 | ERROR | - | {str(e)}")
        return nombre_txt
