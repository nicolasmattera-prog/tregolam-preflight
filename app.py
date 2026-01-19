#!/usr/bin/env python3
import os
import streamlit as st
import precorreccion

# ---------- RUTAS ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- UI ----------
st.set_page_config(page_title="Preflight Word", layout="centered")
st.title("📄 Preflight de manuscritos Word")

archivo = st.file_uploader(
    "Sube un archivo Word (.docx)",
    type=["docx"]
)

if archivo:
    nombre_original = archivo.name
    ruta_entrada = os.path.join(INPUT_FOLDER, nombre_original)

    # ---------- GUARDAR SIEMPRE EL ORIGINAL ----------
    with open(ruta_entrada, "wb") as f:
        f.write(archivo.getbuffer())

    st.success(f"Archivo cargado: {nombre_original}")

    col1, col2 = st.columns(2)

    # ---------- COMPROBACIÓN ----------
    with col1:
        if st.button("🔍 Comprobar errores"):
            try:
                informe = precorreccion.comprobar_archivo(nombre_original)

                ruta_informe = os.path.join(OUTPUT_FOLDER, informe)
                with open(ruta_informe, "r", encoding="utf-8") as f:
                    contenido = f.read()

                st.text_area("Informe de comprobación", contenido, height=400)

                st.download_button(
                    "⬇️ Descargar informe",
                    contenido,
                    file_name=informe,
                    mime="text/plain"
                )

            except Exception as e:
                st.error("❌ Error durante la comprobación")
                st.exception(e)

    # ---------- CORRECCIÓN ----------
    with col2:
        if st.button("✍️ Corregir manuscrito"):
            try:
                precorreccion.procesar_archivo(nombre_original)

                nombre_corregido = nombre_original.replace(
                    ".docx", "_CORREGIDO.docx"
                )
                ruta_corregido = os.path.join(OUTPUT_FOLDER, nombre_corregido)

                with open(ruta_corregido, "rb") as f:
                    st.download_button(
                        "⬇️ Descargar manuscrito corregido",
                        f,
                        file_name=nombre_corregido,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

            except Exception as e:
                st.error("❌ Error durante la corrección")
                st.exception(e)
