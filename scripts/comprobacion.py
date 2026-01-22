import os
import spacy
import json
import re
from docx import Document
from regex_rules import aplicar_regex_editorial

# Carga robusta del modelo para Streamlit Cloud
try:
    # Intentamos cargarlo por su nombre de paquete completo
    nlp = spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])
except OSError:
    # Si falla, intentamos forzar la carga desde el nombre técnico del link
    try:
        import es_core_news_sm
        nlp = es_core_news_sm.load(disable=["ner", "parser", "lemmatizer"])
    except ImportError:
        # Si sigue fallando, lo descargamos en caliente (último recurso)
        os.system("python -m spacy download es_core_news_sm")
        nlp = spacy.load("es_core_news_sm", disable=["ner", "parser", "lemmatizer"])
