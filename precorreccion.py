import os
import openai
from docx import Document
import streamlit as st

def corregir_bloque(archivo_entrada):
    # 1. Configurar la clave de OpenAI
    if "OPENAI_API_KEY" in st.secrets:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
    else:
        raise Exception("Falta la API KEY en los Secrets de Streamlit")

    # 2. Cargar el documento
    doc = Document(archivo_entrada)
    
    # --- AQUÍ VA TU LÓGICA DE IA ---
    # Este bucle recorre el Word. Aquí puedes añadir tus llamadas a OpenAI.
    for p in doc.paragraphs:
        if len(p.text.strip()) > 0:
            pass # Tu lógica aquí
    
    # 3. Guardar el resultado con nombre fijo
    nombre_salida = "resultado_final.docx"
    doc.save(nombre_salida)
    
    return nombre_salida
