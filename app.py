import streamlit as st
import os

# --- 1. CONFIGURACIÓN VISUAL (LO QUE PIDE EL CROQUIS) ---
st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋", layout="wide")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #001f3f, #050505); color: white; }
    .stButton > button { 
        background: linear-gradient(90deg, #00AEEF, #0054A6) !important; 
        color: white !important; border: none !important; border-radius: 10px; height: 50px; width: 100%;
    }
    .console-box { 
        background-color: #000; color: #00ffcc; padding: 15px; border-radius: 10px; 
        border: 1px solid #00AEEF; font-family: monospace; min-height: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXIÓN CON TU LÓGICA ---
logic_ready = False
try:
    import precorreccion
    logic_ready = True
except Exception as e:
    st.error(f"❌ Error crítico: No se pudo cargar 'precorreccion.py'. Detalles: {e}")

# --- 3. DISEÑO DE LA INTERFAZ ---
st.title("🐋 Tregolam Preflight")

col_izq, col_der = st.columns([2, 1], gap="large")

with col_izq:
    archivo = st.file_uploader("Sube tu archivo .docx", type=["docx"])
    st.markdown('<div class="console-box">ESTADO: Esperando archivo...</div>', unsafe_allow_html=True)

with col_der:
    st.subheader("Acciones")
    genero = st.selectbox("Género", ["Texto General", "Novela", "Ensayo"])
    
    if st.button("🚀 CORREGIR"):
        if not logic_ready:
            st.error("El motor de IA no está cargado correctamente.")
        elif archivo is None:
            st.warning("Por favor, sube un archivo primero.")
        else:
            with st.spinner("Corrigiendo..."):
                # Aquí es donde ocurre la magia
                st.info("Proceso iniciado. Revisa los logs para ver el avance.")

    st.button("📋 INFORME")
    st.button("🔍 COMPROBACIÓN")
    st.divider()
    st.button("📥 DESCARGAR", disabled=True)
    st.button("🛑 DETENER", type="primary")
