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
    Función de auditoría compatible con app.py.
    Carga el modelo internamente para evitar fallos de importación en el arranque.
    """
    # 1. CARGA DEL MOTOR (Dentro de la función para no bloquear app.py)
    try:
        # Intentamos cargar el modelo instalado vía requirements.txt
        nlp = spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])
    except OSError:
        # Fallback por si el servidor no lo registró a tiempo
        os.system("python -m spacy download es_core_news_sm")
        nlp = spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])

    # 2. CARGA DE EXCEPCIONES
    ruta_excepciones = os.path.join(BASE_DIR, "data", "excepciones.json")
    excepciones = {}
    if os.path.exists(ruta_excepciones):
        try:
            with open(ruta_excepciones, "r", encoding="utf-8") as f:
                excepciones = json.load(f)
        except:
            excepciones = {}

    # 3. LOCALIZAR ARCHIVO
    ruta_lectura = os.path.join(SALIDA_DIR, nombre_archivo)
    if not os.path.exists(ruta_lectura):
        ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)

    if not os.path.exists(ruta_lectura):
        return f"ERROR: No se encuentra {nombre_archivo}"

    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)

    # 4. PROCESAMIENTO
    try:
        doc = Document(ruta_lectura)
        textos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]
        hallazgos = []

        # Usamos nlp.pipe para procesar los párrafos de forma masiva
        for i, doc_spacy in enumerate(nlp.pipe(textos, batch_size=50)):
            texto_original = textos[i]
            parrafo_id = f"ID_{i+1}"

            # --- A. COMPROBACIÓN DE FORMATO (Regex) ---
            texto_corregido = aplicar_regex_editorial(texto_original)
            if texto_original != texto_corregido:
                # Formato: CATEGORIA | ID | ORIGINAL | CORRECCION | MOTIVO
                hallazgos.append(
                    f"FORMATO | {parrafo_id} | {texto_original[:40]}... | {texto_corregido[:40]}... | Error de espaciado o símbolos"
                )

            # --- B. COMPROBACIÓN DE ORTOGRAFÍA (Diccionario + Excepciones) ---
            for token in doc_spacy:
                palabra_low = token.text.lower()
                
                # Prioridad 1: Diccionario de excepciones personal
                if palabra_low in excepciones:
                    hallazgos.append(
                        f"ORTOGRAFIA | {parrafo_id} | {token.text} | {excepciones[palabra_low]} | Detectado por diccionario personal"
                    )
                    continue
                
                # Prioridad 2: Detección de errores (is_oov = Out of Vocabulary)
                # Filtramos puntuación, números y nombres propios para evitar falsos positivos
                if token.is_oov and not (token.is_punct or token.like_num or token.pos_ == "PROPN"):
                    hallazgos.append(
                        f"ORTOGRAFIA | {parrafo_id} | {token.text} | Revisar | Palabra no reconocida por el motor"
                    )

        # 5. GUARDAR INFORME (Formato compatible con los filtros de app.py)
        with open(ruta_txt, "w", encoding="utf-8") as f:
            if hallazgos:
                f.write("\n".join(hallazgos))
            else:
                f.write("OK | ID_0 | Todo | Correcto | No se detectaron errores")

        return nombre_txt

    except Exception as e:
        return f"ERROR | ID_0 | Sistema | Fallo | {str(e)}"
