# app.py
import os
import sys
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

os.makedirs(ENTRADA_DIR, exist_ok=True)
os.makedirs(SALIDA_DIR, exist_ok=True)

if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

# Configurar página PRIMERO
st.set_page_config(page_title="Preflight® - Tregolam", page_icon="🔍", layout="wide")

# Luego verificar el modelo
try:
    import spacy
    spacy.load("es_core_news_sm")
    modelo_disponible = True
except:
    modelo_disponible = False
    st.warning("⚠️ Modelo de español no disponible. Usando tokenizador básico.")

import comprobacion
import precorreccion
from regex_rules import RULES

st.markdown("""
<style>
.block-container { max-width: 1100px; padding-top: 2rem; }
.stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; }
.header-box { background:#1E1E1E; padding:25px; border-radius:12px; color:#fff; text-align:center; margin-bottom:2rem; }
</style>
""", unsafe_allow_html=True)

if "informe" not in st.session_state:
    st.session_state.informe = None
if "procesado" not in st.session_state:
    st.session_state.procesado = False

with st.sidebar:
    st.success(f"✅ Motor: {len(RULES)} reglas")
    st.caption("v2.1 - Preflight® - Tregolam Literatura S.L.")

st.markdown('<div class="header-box"><h1>🔍 Panel de Auditoría Editorial</h1></div>', unsafe_allow_html=True)

uploaded = st.file_uploader("Sube tu manuscrito (.docx)", type="docx")

if uploaded:
    ruta_entrada = os.path.join(ENTRADA_DIR, uploaded.name)
    with open(ruta_entrada, "wb") as f:
        f.write(uploaded.getbuffer())

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Corrección Ortotipográfica")
        if st.button("✨ Ejecutar corrección"):
            precorreccion.procesar_archivo(uploaded.name)
            st.success("Corrección completada")

    with col2:
        st.subheader("Comprobación de erratas")
        if st.button("🤖 Iniciar Auditoría IA"):
            st.session_state.informe = comprobacion.comprobar_archivo(uploaded.name)
            st.session_state.procesado = True
            st.success("Auditoría completada")

if st.session_state.procesado and st.session_state.informe:
    ruta_informe = os.path.join(SALIDA_DIR, st.session_state.informe)

    if os.path.exists(ruta_informe):
        datos = []
        with open(ruta_informe, "r", encoding="utf-8") as f:
            for linea in f:
                partes = [p.strip() for p in linea.split("|")]
                if len(partes) >= 5:
                    datos.append({
                        "Categoría": partes[0],
                        "ID": partes[1],
                        "Original": partes[2],
                        "Corrección": partes[3],
                        "Motivo": partes[4],
                    })

        st.divider()
        st.subheader("📋 Resultados del Análisis")

        if datos:
            df = pd.DataFrame(datos)
            t1, t2, t3 = st.tabs(["🔴 Ortografía", "🟡 Formato", "🟢 Sugerencias"])

            with t1:
                st.dataframe(df[df["Categoría"].str.contains("ORTOGRAFIA", na=False)],
                             use_container_width=True, hide_index=True)
            with t2:
                st.dataframe(df[df["Categoría"].str.contains("FORMATO", na=False)],
                             use_container_width=True, hide_index=True)
            with t3:
                st.dataframe(df[df["Categoría"].str.contains("SUGERENCIA", na=False)],
                             use_container_width=True, hide_index=True)
        else:
            st.warning("El informe se generó sin filas estructuradas.")

        with open(ruta_informe, "rb") as f:
            st.download_button(
                "📥 Descargar informe (.txt)",
                data=f,
                file_name=st.session_state.informe
            )
