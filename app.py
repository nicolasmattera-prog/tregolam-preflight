import streamlit as st
import os

# --- INTENTO DE IMPORTACIÓN SEGURA ---
try:
    from precorreccion import corregir_bloque
    logic_ready = True
except ImportError:
    logic_ready = False

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋", layout="wide")

# (Aquí va el bloque de CSS que te pasé antes para el diseño oscuro)
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #001f3f, #050505); color: white; }
    .stButton > button { background: linear-gradient(90deg, #00AEEF, #0054A6) !important; color: white !important; border: none !important; border-radius: 10px; height: 50px; }
    .console-box { background-color: #000; color: #00ffcc; padding: 15px; border-radius: 10px; border: 1px solid #00AEEF; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.title("🐋 Tregolam Preflight")

if not logic_ready:
    st.error("⚠️ Error de conexión: No se encuentra el archivo 'precorreccion.py' en GitHub o hay un error en su código.")
    st.stop()

# --- EL RESTO DE TU INTERFAZ ---
col1, col2 = st.columns([2, 1])

with col1:
    archivo = st.file_uploader("Sube tu Word", type=["docx"])
    st.markdown('<div class="console-box">Sistema listo. Esperando archivo...</div>', unsafe_allow_html=True)

with col2:
    if st.button("🚀 INICIAR CORRECCIÓN"):
        if archivo:
            st.info("Procesando... por favor espera.")
            # Aquí llamas a tu función: corregir_bloque()
        else:
            st.warning("Primero sube un archivo.")
