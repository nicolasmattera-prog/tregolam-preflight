import os
import spacy
import re
from docx import Document
from regex_rules import aplicar_regex_editorial

# Carga del modelo (una sola vez)
try:
    nlp = spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])
except:
    import os
    os.system("python -m spacy download es_core_news_sm")
    nlp = spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

def comprobar_archivo(nombre_archivo):
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

        # Procesamiento por lotes (rápido y eficiente)
        for i, doc_spacy in enumerate(nlp.pipe(textos_parrafos, batch_size=50)):
            texto_original = textos_parrafos[i]
            
            # 1. Regex Editorial
            texto_con_regex = aplicar_regex_editorial(texto_original)
            if texto_original != texto_con_regex:
                hallazgos.append(f"FORMATO | Párrafo {i+1} | Error técnico/espacios")

            # 2. Diccionario + spaCy
            for token in doc_spacy:
                palabra_low = token.text.lower()
                if token.is_oov and not (token.is_punct or token.like_num or token.pos_ == "PROPN"):
                    hallazgos.append(f"ORTOGRAFIA | Párrafo {i+1} | {token.text} | No reconocida")

        # Escritura final
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(f"AUDITORÍA FINALIZADA: {len(hallazgos)} avisos encontrados.\n\n")
            f.write("\n".join(hallazgos))

        return nombre_txt

    except Exception as e:
        return f"ERROR CRÍTICO: {str(e)}"
