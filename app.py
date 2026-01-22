# app.py  (FUNCIONA / ARRANCA / SIN ROMPER STREAMLIT)
import streamlit as st
import os
import pandas as pd

st.set_page_config(page_title="Preflight® - Tregolam", page_icon="🔍", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

os.makedirs(ENTRADA_DIR, exist_ok=True)
os.makedirs(SALIDA_DIR, exist_ok=True)

from scripts.comprobacion import comprobar_archivo
from regex_rules import RULES

st.sidebar.success(f"Motor activo: {len(RULES)} reglas")

uploaded = st.file_uploader("Sube tu manuscrito (.docx)", type="docx")

if uploaded:
    ruta = os.path.join(ENTRADA_DIR, uploaded.name)
    with open(ruta, "wb") as f:
        f.write(uploaded.getbuffer())

    if st.button("Iniciar auditoría"):
        informe = comprobar_archivo(uploaded.name)
        st.session_state["informe"] = informe
        st.success("Auditoría completada")

if "informe" in st.session_state:
    ruta = os.path.join(SALIDA_DIR, st.session_state["informe"])

    datos = []
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            partes = [p.strip() for p in linea.split("|")]
            if len(partes) == 5:
                datos.append({
                    "Categoría": partes[0],
                    "ID": partes[1],
                    "Original": partes[2],
                    "Corrección": partes[3],
                    "Motivo": partes[4],
                })

    df = pd.DataFrame(datos)
    st.dataframe(df, use_container_width=True)

    with open(ruta, "rb") as f:
        st.download_button("Descargar informe", f, file_name=st.session_state["informe"])
