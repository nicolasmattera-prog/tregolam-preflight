import streamlit as st
import os
import sys
import pandas as pd

st.set_page_config(page_title="Preflight® - Tregolam", page_icon="🔍", layout="wide")

# CSS para evitar que la pantalla se estire
st.markdown("""
    <style>
    .block-container { max-width: 1000px; padding-top: 2rem; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3em; }
    .header-box { background-color: #1E1E1E; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

base_path = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(base_path, "scripts")
sys.path.append(scripts_path)

import precorreccion
import comprobacion
from regex_rules import RULES

with st.sidebar:
    logo = os.path.join(scripts_path, "isologo tregolma prefligth.png")
    if os.path.exists(logo): st.image(logo, width=180)
    st.divider()
    st.success(f"Motor: {len(RULES)} reglas")
    st.caption("v2.1 - Preflight® - Tregolam Literatura S.L.")

st.markdown('<div class="header-box"><h1>🔍 Panel de Auditoría Ortotipográfica</h1></div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Sube tu manuscrito (.docx)", type="docx")

if uploaded_file:
    # Guardar archivo de entrada
    entrada_path = os.path.join(base_path, "entrada", uploaded_file.name)
    with open(entrada_path, "wb") as f: f.write(uploaded_file.getbuffer())

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Corrección Ortotipográfica")
        if st.button("✨ Ejecutar Corrección"):
            with st.spinner("Procesando..."):
                msg = precorreccion.ejecutar_precorreccion(uploaded_file.name)
                st.success(msg)
                
    with col2:
        st.subheader("Comprobación de erratas")
        if st.button("🤖 Iniciar Auditoría IA"):
            with st.spinner("Analizando con IA..."):
                nombre_inf = comprobacion.comprobar_archivo(uploaded_file.name)
                st.session_state['informe'] = nombre_inf
                st.rerun()

    if 'informe' in st.session_state:
        st.divider()
        st.info(f"Informe listo: {st.session_state['informe']}")
