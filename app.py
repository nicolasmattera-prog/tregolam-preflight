import streamlit as st
import os
import sys
import pandas as pd
import time
from docx import Document

# 1. Configuración de página (Debe ser lo primero)
st.set_page_config(page_title="Auditoría Tregolam", page_icon="🔍", layout="wide")

# --- ESTÉTICA PERSONALIZADA (CSS) ---
st.markdown("""
    <style>
    /* Contenedor principal para evitar que se estire demasiado */
    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
    }
    /* Estilo para los botones */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    /* Encabezado elegante */
    .header-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #1E1E1E;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Gestión de Rutas y Carpetas
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_path, "scripts"))

# Importación de módulos locales (CORREGIDO: Descomentado y verificado)
try:
    import precorreccion
    import comprobacion
    from regex_rules1 import RULES
    categorias_activas = list(set([r[0] for r in RULES]))
except ImportError as e:
    st.error(f"Error al cargar módulos en /scripts: {e}")
    st.stop()

entrada_dir = os.path.join(base_path, "entrada")
salida_dir = os.path.join(base_path, "salida")
os.makedirs(entrada_dir, exist_ok=True)
os.makedirs(salida_dir, exist_ok=True)

# --- SIDEBAR ---
with st.sidebar:
    # Inclusión de Logo (Punto solicitado)
    logo_path = os.path.join(base_path, "scripts", "isologo tregolma prefligth.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    else:
        st.info("Logo no encontrado en /scripts")
    
    st.divider()
    st.success(f"✅ Motor cargado: {len(RULES)} reglas")
    for cat in categorias_activas:
        st.write(f"✔️ {cat.capitalize()}")
    
    st.divider()
    # Versión actualizada (Punto solicitado)
    st.caption("v2.1 - Preflight® - Tregolam Literatura S.L.")

# --- CUERPO PRINCIPAL ---
st.markdown('<div class="header-box"><h1>🔍 Panel de Auditoría Ortotipográfica</h1></div>', unsafe_allow_html=True)

# Gestión de Estado
if 'fichero_procesado' not in st.session_state:
    st.session_state['fichero_procesado'] = False
if 'nombre_informe' not in st.session_state:
    st.session_state['nombre_informe'] = None

# Subida de archivo compacta
uploaded_file = st.file_uploader("Sube tu manuscrito (.docx)", type="docx", key="uploader_v3")

if uploaded_file:
    if st.session_state.get('ultimo_nombre') != uploaded_file.name:
        st.session_state['fichero_procesado'] = False
        st.session_state['ultimo_nombre'] = uploaded_file.name

    ruta_archivo_entrada = os.path.join(entrada_dir, uploaded_file.name)
    with open(ruta_archivo_entrada, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Columnas para botones (Punto solicitado: nombres actualizados)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Corrección Ortotipográfica")
        if st.button("✨ Ejecutar Corrección", key="btn_pre"):
            with st.spinner("Procesando motor de reglas..."):
                # Asegúrate que precorreccion tenga esta función o cámbiala por la correcta
                msg = precorreccion.ejecutar_precorreccion(uploaded_file.name)
                st.success(msg)
                
                ruta_out = os.path.join(salida_dir, uploaded_file.name)
                if os.path.exists(ruta_out):
                    with open(ruta_out, "rb") as f_out:
                        st.download_button("📥 Descargar DOCX", f_out, f"corregido_{uploaded_file.name}")

    with col2:
        st.subheader("Comprobación de erratas")
        if st.button("🤖 Iniciar Auditoría IA", key="btn_ia"):
            with st.spinner("Analizando con IA..."):
                # EJECUCIÓN: Llama a la función del script comprobacion.py
                comprobacion.comprobar_archivo(uploaded_file.name)
                
                st.session_state['nombre_informe'] = f"Informe_{uploaded_file.name.replace('.docx', '.txt')}"
                st.session_state['fichero_procesado'] = True
                st.rerun()

    # --- TABLAS DE RESULTADOS ---
    if st.session_state['fichero_procesado'] and st.session_state['nombre_informe']:
        st.divider()
        ruta_txt = os.path.join(salida_dir, st.session_state['nombre_informe'])
        
        if os.path.exists(ruta_txt):
            datos = []
            with open(ruta_txt, "r", encoding="utf-8") as f:
                for linea in f:
                    if "|" in linea:
                        partes = [p.strip() for p in linea.split("|")]
                        if len(partes) >= 5:
                            datos.append({
                                "Categoría": partes[0], "Original": partes[2], 
                                "Sugerencia": partes[3], "Motivo": partes[4]
                            })
            
            if datos:
                df = pd.DataFrame(datos)
                tab1, tab2, tab3 = st.tabs(["🔴 Ortografía", "🟡 Formato", "🟢 Sugerencias"])
                
                with tab1:
                    st.dataframe(df[df["Categoría"].str.contains("ORTOGRAFIA|ORTOGRAFÍA", case=False)], use_container_width=True, hide_index=True)
                with tab2:
                    st.dataframe(df[df["Categoría"].str.contains("FORMATO", case=False)], use_container_width=True, hide_index=True)
                with tab3:
                    st.dataframe(df[df["Categoría"].str.contains("SUGERENCIA", case=False)], use_container_width=True, hide_index=True)

                st.download_button("📥 Descargar Informe Completo (TXT)", open(ruta_txt, "rb"), st.session_state['nombre_informe'])
