#!/usr/bin/env python3
import os
import streamlit as st
import precorreccion

# ---------- RUTAS (las mismas que precorreccion.py) ----------
INPUT_FOLDER = precorreccion.INPUT_FOLDER
OUTPUT_FOLDER = precorreccion.OUTPUT_FOLDER
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- UI ----------
st.set_page_config(page_title="Tregolam Preflight", layout="centered")
st.title("Tregolam · Preflight Word")

archivo = st.file_uploader("Sube un archivo Word (.docx)", type=["docx"])

if archivo is not None:
    nombre_original = os.path.basename(archivo.name)
    ruta_original = os.path.join(INPUT_FOLDER, nombre_original)

    # Guardar el original en /entrada
    with open(ruta_original, "wb") as f:
        f.write(archivo.getbuffer())

    st.success(f"Archivo cargado: {nombre_original}")

    col1, col2 = st.columns(2)

    # ---------- COMPROBACIÓN ----------
    with col1:
        if st.button("Comprobar"):
            with st.spinner("Analizando el documento…"):
                informe = precorreccion.comprobar_archivo(nombre_original)

            ruta_informe = os.path.join(OUTPUT_FOLDER, informe)
            with open(ruta_informe, "r", encoding="utf-8") as f:
                contenido = f.read()

            st.download_button(
                "Descargar informe",
                contenido,
                file_name=informe,
                mime="text/plain"
            )

    # ---------- CORRECCIÓN ----------
    with col2:
        if st.button("Corregir"):
            with st.spinner("Procesando el manuscrito…"):
                precorreccion.procesar_archivo(nombre_original)

            nombre_corregido = nombre_original.replace(".docx", "_CORREGIDO.docx")
            ruta_corregido = os.path.join(OUTPUT_FOLDER, nombre_corregido)

            with open(ruta_corregido, "rb") as f:
                st.download_button(
                    "Descargar Word corregido",
                    f,
                    file_name=nombre_corregido,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
