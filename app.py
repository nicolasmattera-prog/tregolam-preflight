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
st.title("🔍 Preflight de manuscritos Word")

archivo = st.file_uploader(
    "Sube un archivo Word (.docx)",
    type=["docx"]
)

if archivo:
    st.success(f"Archivo cargado: {archivo.name}")

    if st.button("Comprobar"):
        # ---------- GUARDAR ARCHIVO ----------
        ruta = os.path.join(INPUT_FOLDER, archivo.name)
        with open(ruta, "wb") as f:
            f.write(archivo.getbuffer())

        st.info("Archivo guardado. Iniciando comprobación...")

        # ---------- PROCESO ----------
        try:
            informe = precorreccion.comprobar_archivo(archivo.name)
            st.success("✅ Comprobación finalizada")

            ruta_informe = os.path.join(OUTPUT_FOLDER, informe)
            with open(ruta_informe, "r", encoding="utf-8") as f:
                st.text_area(
                    "Informe de errores",
                    f.read(),
                    height=400
                )

        except Exception as e:
            st.error("❌ Error durante la comprobación")
            st.exception(e)
