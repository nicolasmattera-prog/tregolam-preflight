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

def comprobar_archivo(nombre_archivo):
    """
    Esta función es la que llama tu app.py. 
    Cargamos spaCy AQUÍ ADENTRO para que el 'import' inicial no falle.
    """
    try:
        # Intentamos cargar el modelo de español
        # Usamos disable para que sea ultra rápido
        nlp = spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])
    except OSError:
        # Si no está instalado (pasa en el primer arranque), lo bajamos
        os.system("python -m spacy download es_core_news_sm")
        nlp = spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])

    # 1. Cargar excepciones personales
    ruta_excepciones = os.path.join(BASE_DIR, "data", "excepciones.json")
    excepciones = {}
    if os.path.exists(ruta_excepciones):
        try:
            with open(ruta_excepciones, "r", encoding="utf-8") as f:
                excepciones = json.load(f)
        except:
            excepciones = {}

    # 2. Localizar archivo (Entrada o Salida)
    ruta_lectura = os.path.join(SALIDA_DIR, nombre_archivo)
    if not os.path.exists(ruta_lectura):
        ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)

    if not os.path.exists(ruta_lectura):
        return f"ERROR: No se encuentra {nombre_archivo}"

    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)

    # 3. Procesamiento del documento
    try:
        doc = Document(ruta_lectura)
        # Solo párrafos con texto
        textos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]
        hallazgos = []

        # Procesamiento por lotes para no colgar el servidor
        for i, doc_spacy in enumerate(nlp.pipe(textos, batch_size=50)):
            texto_original = textos[i]

            # A. Comprobación de Formato (Regex)
            if texto_original != aplicar_regex_editorial(texto_original):
                # El formato de salida debe ser: CATEGORIA | ID | ORIGINAL | CORRECCION | MOTIVO
                hallazgos.append(f"FORMATO | ID_{i+1} | {texto_original[:30]}... | {aplicar_regex_editorial(texto_original)[:30]}... | Error de espacios o símbolos")

            # B. Comprobación de Ortografía (spaCy + Excepciones)
            for token in doc_spacy:
                palabra_low = token.text.lower()
                
                # Si está en tus excepciones
                if palabra_low in excepciones:
                    hallazgos.append(f"ORTOGRAFIA | ID_{i+1} | {token.text} | {excepciones[palabra_low]} | Diccionario personal")
                    continue
                
                # Si spaCy dice que no existe (is_oov) y no es un nombre propio/número
                if token.is_oov and not (token.is_punct or token.like_num or token.pos_ == "PROPN"):
                    hallazgos.append(f"ORTOGRAFIA | ID_{i+1} | {token.text} | Revisar | Palabra no reconocida")

        # 4. Guardar informe con el formato que tu app.py sabe leer
        with open(ruta_txt, "w", encoding="utf-8") as f:
            if hallazgos:
                f.write("\n".join(hallazgos))
            else:
                f.write("S_OK") # Para que tu app sepa que no hay errores

        return nombre_txt
        
    except Exception as e:
        return f"ERROR CRÍTICO | ID_0 | Error | Error | {str(e)}"
