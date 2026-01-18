import streamlit as st
import os
import time
from docx import Document
# Importamos la función de tu otro archivo
from precorreccion import corregir_bloque 

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋", layout="wide")

# Inyección de CSS para diseño tecnológico
st.markdown("""
    <style>
    /* Fondo y tipografía */
    .stApp {
        background: radial-gradient(circle at top right, #001f3f, #050505);
        color: #ffffff;
    }
    
    /* Contenedores con efecto cristal */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
    }

    /* Botón CORREGIR (Degradado Azul) */
    .stButton > button {
        border-radius: 10px;
        height: 60px;
        font-weight: bold;
        font-size: 18px;
        transition: 0.3s;
    }
    
    /* Botón específico de ejecución */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00AEEF, #0054A6) !important;
        border: none !important;
        color: white !important;
    }

    /* Consola de Proceso */
    .console-box {
        background-color: #000000;
        color: #00ffcc;
        padding: 15px;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        border: 1px solid #00AEEF;
        min-height: 150px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("isologo tregolma prefligth.png")
    st.markdown("### Configuración")
    genero = st.selectbox("Tipo de texto", ["Texto General", "Novela", "Ensayo"])
    st.divider()
    st.caption("Versión 1.0.0 - IA Correctora")

# --- CUERPO PRINCIPAL ---
st.title("🐋 Tregolam Preflight")
st.write("Herramienta profesional de corrección ortotipográfica.")

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    uploaded_file = st.file_uploader("Arrastra aquí tu archivo .docx", type=["docx"])
    
    st.subheader("📦 Estado del Proceso")
    progreso = st.progress(0)
    consola = st.empty()
    consola.markdown('<div class="console-box">Esperando documento...</div>', unsafe_allow_html=True)

with col2:
    st.subheader("⚙️ Acciones")
    if st.button("🚀 INICIAR CORRECCIÓN"):
        if uploaded_file:
            consola.markdown('<div class="console-box">Analizando documento...<br>Iniciando motor GPT-4o...</div>', unsafe_allow_html=True)
            # Aquí iría la llamada a tu lógica de procesamiento
            # procesar_archivo(uploaded_file.name) 
            st.success("¡Documento procesado!")
        else:
            st.error("Por favor, sube un archivo primero.")
            
    st.button("📄 GENERAR INFORME")
    st.button("🔍 COMPROBACIÓN (BETA)")
    
    st.divider()
    st.button("📥 DESCARGAR", disabled=not uploaded_file)
    st.button("🛑 DETENER", type="primary", key="detener")
