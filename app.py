import os
import streamlit as st
import sys

# AÑADIR SCRIPTS AL PATH PARA QUE STREAMLIT LOS VEA
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "scripts"))

import comprobacion
import precorreccion

# CONFIGURACIÓN DE RUTAS
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

st.set_page_config(page_title="Tregolam · Preflight Word", layout="centered")
st.title("Tregolam · Preflight Word")

archivo = st.file_uploader("Sube un archivo Word (.docx)", type=["docx"])

if archivo:
    nombre_original = archivo.name
    ruta_original = os.path.join(INPUT_FOLDER, nombre_original)

    with open(ruta_original, "wb") as f:
        f.write(archivo.getbuffer())

    st.success(f"Archivo listo: {nombre_original}")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Comprobar"):
            with st.spinner("Analizando..."):
                # PASAMOS LA RUTA COMPLETA PARA EVITAR DUDAS
                informe_nombre = comprobacion.comprobar_archivo(ruta_original)
                
                if "ERROR" in informe_nombre:
                    st.error(informe_nombre)
                else:
                    ruta_informe = os.path.join(OUTPUT_FOLDER, informe_nombre)
                    if os.path.exists(ruta_informe):
                        with open(ruta_informe, "r", encoding="utf-8") as f:
                            st.download_button("Descargar informe", f.read(), file_name=informe_nombre)

    with col2:
        if st.button("Corregir"):
            with st.spinner("Corrigiendo..."):
                precorreccion.procesar_archivo(nombre_original)
                # (Asegúrate de que precorreccion use OUTPUT_FOLDER para guardar)
                st.info("Proceso de corrección finalizado.")
