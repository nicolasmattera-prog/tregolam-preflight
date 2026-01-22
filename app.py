import streamlit as st
import os
import sys
import pandas as pd
import time
from docx import Document

# 1. Configuración de página
st.set_page_config(
    page_title="Auditoría Editorial Tregolam", 
    page_icon="🔍",
    layout="wide"
)

# --- ESTÉTICA PERSONALIZADA (CSS) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
        background-color: #fffafa;
    }
    .section-header {
        padding: 15px;
        border-radius: 8px;
        background-color: #1E1E1E;
        color: white;
        margin-bottom: 25px;
        text-align: center;
    }
    .stDataFrame {
        border: 1px solid #f0f2f6;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Gestión de Rutas y Carpetas
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_path, "scripts"))
entrada_dir = os.path.join(base_path, "entrada")
salida_dir = os.path.join(base_path, "salida")
os.makedirs(entrada_dir, exist_ok=True)
os.makedirs(salida_dir, exist_ok=True)

# 3. Carga del Motor de Reglas (Punto solicitado)
try:
    import precorreccion
    from regex_rules import RULES
    categorias_activas = list(set([r[0] for r in RULES]))
except ImportError:
    st.error("❌ Error crítico: No se encuentra 'regex_rules.py' o 'precorreccion.py' en /scripts.")
    st.stop()

# --- GESTIÓN DE ESTADO ---
if 'fichero_procesado' not in st.session_state:
    st.session_state['fichero_procesado'] = False
if 'nombre_informe' not in st.session_state:
    st.session_state['nombre_informe'] = None

# --- CABECERA ---
st.markdown('<div class="section-header"><h1>🔍 Panel de Auditoría Ortotipográfica</h1></div>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://www.tregolam.com/wp-content/uploads/2018/11/logo_tregolam_letras.png", width=200)
    st.divider()
    st.success(f"✅ Motor cargado: {len(RULES)} reglas")
    # Resumen de categorías en el sidebar
    for cat in categorias_activas:
        st.write(f"✔️ {cat.capitalize()}")
    st.divider()
    st.caption("v2.1 - Tregolam AI Edition")

# 4. Subida de Archivo
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
        st.subheader("Paso 1: Estructura")
        if st.button("✨ Ejecutar Precorrección", key="btn_pre"):
            # Resumen dinámico (Punto solicitado)
            resumen_txt = ", ".join([c.lower() for c in categorias_activas])
            info_p = st.empty()
            info_p.caption(f"🚀 Disparando motor editorial: {resumen_txt}...")
            
            with st.spinner("Procesando IA + Motor de Regex..."):
                precorreccion.procesar_archivo(uploaded_file.name)
            
            info_p.empty()
            st.success("¡Documento procesado!")
            
            ruta_docx_corregido = os.path.join(salida_dir, uploaded_file.name)
            if os.path.exists(ruta_docx_corregido):
                with open(ruta_docx_corregido, "rb") as f_out:
                    st.download_button(
                        label="📥 Descargar DOCX corregido",
                        data=f_out,
                        file_name=f"CORREGIDO_{uploaded_file.name}",
                        use_container_width=True
                    )

    with col2:
        st.subheader("Paso 2: Análisis")
        if st.button("🤖 Iniciar Auditoría IA", key="btn_ia"):
            with st.spinner("Analizando con IA..."):
                # Aquí llamarías a comprobacion.comprobar_archivo(uploaded_file.name)
                # Simulamos la creación del informe para la visualización
                st.session_state['nombre_informe'] = f"Informe_{uploaded_file.name.replace('.docx', '.txt')}"
                st.session_state['fichero_procesado'] = True
                st.rerun()

    # --- RENDERIZADO DE RESULTADOS (TABLAS) ---
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
                st.markdown("### 📊 Hallazgos Detectados")
                
                tab1, tab2, tab3 = st.tabs(["🔴 Ortografía", "🟡 Formato", "🟢 Sugerencias"])
                
                with tab1:
                    mask = df["Categoría"].str.contains("ORTOGRAFIA|ORTOGRAFÍA", case=False, na=False)
                    st.dataframe(df[mask], use_container_width=True, hide_index=True)
                
                with tab2:
                    mask = df["Categoría"].str.contains("FORMATO", case=False, na=False)
                    st.dataframe(df[mask], use_container_width=True, hide_index=True)
                
                with tab3:
                    mask = df["Categoría"].str.contains("SUGERENCIA", case=False, na=False)
                    st.dataframe(df[mask], use_container_width=True, hide_index=True)

                st.divider()
                with open(ruta_txt, "rb") as f_descarga:
                    st.download_button(
                        label="📥 Descargar Informe Completo (TXT)",
                        data=f_descarga,
                        file_name=st.session_state['nombre_informe'],
                        key="btn_descarga_txt_final"
                    )
