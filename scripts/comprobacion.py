import os
import spacy
import re
from docx import Document
from regex_rules import aplicar_regex_editorial

# Cargar el modelo de español (Instalado previamente con python -m spacy download es_core_news_sm)
try:
    nlp = spacy.load("es_core_news_sm")
except:
    # Fallback por si no se ha descargado el modelo
    import os
    os.system("python -m spacy download es_core_news_sm")
    nlp = spacy.load("es_core_news_sm")

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
        hallazgos = []

        for i, p in enumerate(doc.paragraphs):
            texto_original = p.text.strip()
            if len(texto_original) < 5: continue

            # 1. AUDITORÍA TÉCNICA (Tus Regex)
            # Si el texto cambia al aplicar regex, hay un error de formato
            texto_con_regex = aplicar_regex_editorial(texto_original)
            if texto_original != texto_con_regex:
                hallazgos.append(f"FORMATO | ID_{i+1} | {texto_original[:30]}... | Corrección técnica aplicada | Error de espacio/símbolo")

            # 2. AUDITORÍA DE DICCIONARIO (spaCy)
            doc_spacy = nlp(texto_original)
            for token in doc_spacy:
                # Si la palabra no es nombre propio, no es puntuación y no está en el diccionario
                if not token.is_oov: continue # oov = Out of Vocabulary
                if token.is_punct or token.like_num or token.pos_ == "PROPN": continue
                
                hallazgos.append(f"ORTOGRAFIA | ID_{i+1} | {token.text} | Revisar | Palabra no reconocida")

        # Guardar resultados
        with open(ruta_txt, "w", encoding="utf-8") as f:
            if hallazgos:
                f.write("INFORME DE AUDITORÍA LOCAL (Coste $0)\n" + "="*40 + "\n")
                f.write("\n".join(hallazgos))
            else:
                f.write("✅ No se detectaron errores en la auditoría técnica.")

        return nombre_txt

    except Exception as e:
        return f"ERROR: {str(e)}"
