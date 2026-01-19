import os
import sys
import streamlit as st

# 1. ESTO ARREGLA LA IMPORTACIÓN:
# Como app.py está fuera y tus scripts dentro de /scripts, 
# añadimos la carpeta al path para que Python los encuentre.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(BASE_DIR, "scripts")
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

import comprobacion
import precorreccion

# 2. CONFIGURACIÓN DE RUTAS (Raíz)
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

st.set_page_config(page_title="Tregolam · Preflight", layout="centered")
st.title("Tregolam · Preflight Word")

archivo = st.file_uploader("Sube un archivo .docx", type=["docx"])

if archivo is not None:
    nombre_original = archivo.name
    ruta_original = os.path.join(INPUT_FOLDER, nombre_original)

    with open(ruta_original, "wb") as f:
        f.write(archivo.getbuffer())

    st.success(f"Archivo cargado: {nombre_original}")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Comprobar"):
            with st.spinner("Analizando..."):
                # Llamamos a la función de scripts/comprobacion.py
                informe = comprobacion.comprobar_archivo(nombre_original)
                
                ruta_informe = os.path.join(OUTPUT_FOLDER, informe)
                if os.path.exists(ruta_informe):
                    with open(ruta_informe, "r", encoding="utf-8") as f:
                        st.download_button("Descargar Informe", f.read(), file_name=informe)

    with col2:
        if st.button("Corregir"):
            with st.spinner("Corrigiendo..."):
                # Llamamos a la función de scripts/precorreccion.py
                precorreccion.procesar_archivo(nombre_original)
                
                nombre_corregido = nombre_original.replace(".docx", "_CORREGIDO.docx")
                ruta_corregido = os.path.join(OUTPUT_FOLDER, nombre_corregido)
                
                if os.path.exists(ruta_corregido):
                    with open(ruta_corregido, "rb") as f:
                        st.download_button("Descargar Word Corregido", f, file_name=nombre_corregido)
