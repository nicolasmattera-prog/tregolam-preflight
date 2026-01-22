import os
import json
import re
import spacy
from docx import Document
from regex_rules import aplicar_regex_editorial

# Directorios de trabajo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

def comprobar_archivo(nombre_archivo):
    """
    Función principal de auditoría. 
    Carga el modelo de lenguaje de forma interna para evitar errores de despliegue.
    """
    
    # 1. CARGA INTERNA (Lazy Load) para evitar OSError al importar
    try:
        # Intentamos cargar el modelo de español
        nlp = spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])
    except OSError:
        # Si falla (común en el primer arranque de Streamlit), lo descargamos forzosamente
        os.system("python -m spacy download es_core_news_sm")
        nlp = spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])

    # 2. CARGA DE EXCEPCIONES (data/excepciones.json)
    ruta_excepciones = os.path.join(BASE_DIR, "data", "excepciones.json")
    excepciones = {}
    if os.path.exists(ruta_excepciones):
        try:
            with open(ruta_excepciones, "r", encoding="utf-8") as f:
                excepciones = json.load(f)
        except:
            excepciones = {}

    # 3. LOCALIZACIÓN DEL ARCHIVO
    ruta_lectura = os.path.join(SALIDA_DIR, nombre_archivo)
    if not os.path.exists(ruta_lectura):
        ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)
    
    if not os.path.exists(ruta_lectura):
        return f"ERROR: No se encuentra {nombre_archivo}"

    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)

    try:
        doc = Document(ruta_lectura)
        textos_parrafos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]
        hallazgos = []

        # 4. PROCESAMIENTO POR LOTES (NLP.PIPE)
        # Usamos nlp.pipe para máxima velocidad en archivos grandes
        for i, doc_spacy in enumerate(nlp.pipe(textos_parrafos, batch_size=50)):
            texto_original = textos_parrafos[i]
            
            # A. Auditoría de Formato (Regex)
            if texto_original != aplicar_regex_editorial(texto_original):
                hallazgos.append(f"FORMATO | Párrafo {i+1} | Error técnico o de espacios")

            # B. Auditoría Lingüística (Excepciones + Diccionario)
            for token in doc_spacy:
                palabra_low = token.text.lower()
                
                # Prioridad 1: Tu lista de excepciones
                if palabra_low in excepciones:
                    hallazgos.append(f"ORTOGRAFIA | Párrafo {i+1} | {token.text} | {excepciones[palabra_low]}")
                    continue

                # Prioridad 2: Diccionario de spaCy (Fuera de vocabulario)
                if token.is_oov and not (token.is_punct or token.like_num or token.pos_ == "PROPN"):
                    hallazgos.append(f"ORTOGRAFIA | Párrafo {i+1} | {token.text} | No reconocida")

        # 5. GENERACIÓN DEL INFORME
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(f"INFORME DE AUDITORÍA: {len(hallazgos)} avisos encontrados.\n")
            f.write("="*50 + "\n\n")
            if hallazgos:
                f.write("\n".join(hallazgos))
            else:
                f.write("No se detectaron errores en esta revisión.")

        return nombre_txt

    except Exception as e:
        return f"ERROR CRÍTICO: {str(e)}"
