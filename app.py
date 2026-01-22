import streamlit as st
import os
import sys
import pandas as pd
import time

# 1. Configuración de página
st.set_page_config(page_title="Auditoría Tregolam", page_icon="🔍", layout="wide")

# --- ESTÉTICA PERSONALIZADA ---
st.markdown("""
    <style>
    .block-container { max-width: 1100px; padding-top: 2rem; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .header-box { padding: 20px; border-radius: 10px; background-color: #1E1E1E; color: white; text-align: center; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Gestión de Rutas y Carpetas
base_path = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(base_path, "scripts")

# Añadimos scripts al path para que Python encuentre los módulos
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

# --- IMPORTACIÓN SEGURA DE MÓDULOS ---
try:
    import precorreccion
    import comprobacion
    # Intentamos importar del archivo correcto: regex_rules1
    from regex_rules1 import RULES, aplicar_regex_editorial
    categorias_activas = list(set([r[0] for r in RULES]))
except ImportError as e:
    st.error(f"❌ Error de importación: {e}")
    st.info("Asegúrate de que el archivo se llame 'regex_rules1.py' dentro de la carpeta 'scripts'.")
    st.stop()

entrada_dir = os.path.join(base_path, "entrada")
salida_dir = os.path.join(base_path, "salida")
os.makedirs(entrada_dir, exist_ok=True)
os.makedirs(salida_dir, exist_ok=True)

# --- SIDEBAR ---
with st.sidebar:
    logo_path = os.path.join(scripts_path, "isologo tregolma prefligth.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    
    st.divider()
    st.success(f"✅ Motor cargado: {len(RULES)} reglas")
    for cat in categorias_activas:
        st.write(f"✔️ {cat.capitalize()}")
    
    st.divider()
    st.caption("v2.1 - Preflight® - Tregolam Literatura S.L.")

# --- CUERPO PRINCIPAL ---
st.markdown('<div class="header-box"><h1>🔍 Panel de Auditoría Ortotipográfica</h1></div>', unsafe_allow_html=True)

if 'fichero_procesado' not in st.session_state:
    st.session_state['fichero_procesado'] = False
if 'nombre_informe' not in st.session_state:
    st.session_state['nombre_informe'] = None

uploaded_file = st.file_uploader("Sube tu manuscrito (.docx)", type="docx", key="uploader_v3")

if uploaded_file:
    if st.session_state.get('ultimo_nombre') != uploaded_file.name:
        st.session_state['fichero_procesado'] = False
        st.session_state['ultimo_nombre'] = uploaded_file.name

    ruta_archivo_entrada = os.path.join(entrada_dir, uploaded_file.name)
    with open(ruta_archivo_entrada, "wb") as f:
        f.write(uploaded_file.getbuffer())

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Corrección Ortotipográfica")
        if st.button("✨ Ejecutar Corrección", key="btn_pre"):
            with st.spinner("Procesando motor de reglas..."):
                # Se asume que precorreccion tiene la función ejecutar_precorreccion o procesar_archivo
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
                nombre_inf = comprobacion.comprobar_archivo(uploaded_file.name)
                st.session_state['nombre_informe'] = nombre_inf
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
                    if "|" in linea and "RESUMEN" not in linea:
                        partes = [p.strip() for p in linea.split("|")]
                        if len(partes) >= 5:
                            datos.append({
                                "Categoría": partes[0], "Original": partes[2], 
                                "Sugerencia": partes[3], "Motivo": partes[4]
                            })
            
            if datos:
                df = pd.DataFrame(datos)
                t1, t2, t3 = st.tabs(["🔴 Ortografía", "🟡 Formato", "🟢 Sugerencias"])
                with t1: st.dataframe(df[df["Categoría"].str.contains("ORTOGRAFIA", case=False)], use_container_width=True, hide_index=True)
                with t2: st.dataframe(df[df["Categoría"].str.contains("FORMATO", case=False)], use_container_width=True, hide_index=True)
                with t3: st.dataframe(df[df["Categoría"].str.contains("SUGERENCIA", case=False)], use_container_width=True, hide_index=True)

                with open(ruta_txt, "rb") as f_desc:
                    st.download_button("📥 Descargar Informe Completo", f_desc, st.session_state['nombre_informe'])
