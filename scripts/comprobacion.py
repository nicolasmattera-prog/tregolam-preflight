import os
import json
import re
import spacy
from docx import Document
from regex_rules import aplicar_regex_editorial

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

def cargar_modelo():
    """Carga el modelo completo, no uno en blanco."""
    try:
        # Intentamos cargar el modelo preinstalado
        return spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])
    except OSError:
        # Si no está, intentamos cargarlo como paquete de Python
        try:
            import es_core_news_sm
            return es_core_news_sm.load(disable=["ner", "parser", "lemmatizer"])
        except ImportError:
            # Si nada funciona, error claro
            return None

def comprobar_archivo(nombre_archivo):
    nlp = cargar_modelo()
    if nlp is None:
        return "ERROR: El motor de idioma no está instalado correctamente en el servidor."

    # 1. Cargar excepciones
    ruta_excepciones = os.path.join(BASE_DIR, "data", "excepciones.json")
    excepciones = {}
    if os.path.exists(ruta_excepciones):
        try:
            with open(ruta_excepciones, "r", encoding="utf-8") as f:
                excepciones = json.load(f)
        except:
            excepciones = {}

    # 2. Localizar archivo
    ruta_lectura = os.path.join(SALIDA_DIR, nombre_archivo)
    if not os.path.exists(ruta_lectura):
        ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)

    if not os.path.exists(ruta_lectura):
        return f"ERROR: No se encuentra {nombre_archivo}"

    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)

    # 3. Leer y Procesar
    try:
        doc = Document(ruta_lectura)
        textos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]
        hallazgos = []

        for i, doc_spacy in enumerate(nlp.pipe(textos, batch_size=50)):
            texto_original = textos[i]

            # Auditoría de Formato (Regex)
            if texto_original != aplicar_regex_editorial(texto_original):
                hallazgos.append(f"FORMATO | Párrafo {i+1} | Error técnico o de espacios")

            # Auditoría de Ortografía (Diccionario + Excepciones)
            for token in doc_spacy:
                palabra_low = token.text.lower()
                
                # Prioridad 1: Tu lista
                if palabra_low in excepciones:
                    hallazgos.append(f"ORTOGRAFIA | Párrafo {i+1} | {token.text} | {excepciones[palabra_low]}")
                    continue
                
                # Prioridad 2: Diccionario real (is_oov significa 'fuera de diccionario')
                if token.is_oov and not (token.is_punct or token.like_num or token.pos_ == "PROPN"):
                    hallazgos.append(f"ORTOGRAFIA | Párrafo {i+1} | {token.text} | No reconocida")

        # 4. Guardar informe
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(f"INFORME DE AUDITORÍA: {len(hallazgos)} avisos encontrados.\n")
            f.write("=" * 50 + "\n\n")
            f.write("\n".join(hallazgos) if hallazgos else "No se detectaron errores.")

        return nombre_txt
    except Exception as e:
        return f"ERROR CRÍTICO: {str(e)}"
