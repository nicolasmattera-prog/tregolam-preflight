import streamlit as st
import os
import sys
import pandas as pd

# ---------------------------------------------
# CONFIGURACIÓN DE PÁGINA (SIEMPRE PRIMERO)
# ---------------------------------------------
st.set_page_config(
    page_title="Preflight® - Tregolam",
    page_icon="🔍",
    layout="wide"
)

# ---------------------------------------------
# RUTAS
# ---------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

os.makedirs(ENTRADA_DIR, exist_ok=True)
os.makedirs(SALIDA_DIR, exist_ok=True)

if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

# ---------------------------------------------
# IMPORTACIONES INTERNAS
# ---------------------------------------------
from comprobacion import comprobar_archivo
from regex_rules import RULES

# ---------------------------------------------
# ESTILOS
# ---------------------------------------------
st.markdown("""
<style>
.block-container { max-width: 1100px; padding-top: 2rem; }
.stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; }
.header-box {
    background:#1E1E1E;
    padding:25px;
    border-radius:12px;
    color:white;
    text-align:center;
    margin-bottom:2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------
# ESTADO DE SESIÓN
# ---------------------------------------------
if "informe" not in st.session_state:
    st.session_state.informe = None
if "procesado" not in st.session_state:
    st.session_state.procesado = False

# ---------------------------------------------
# SIDEBAR
# ---------------------------------------------
with st.sidebar:
    st.success(f"Motor activo: {len(RULES)} reglas")
    st.caption("Preflight® · Tregolam Literatura S.L.")

# ---------------------------------------------
# CABECERA
# ---------------------------------------------
st.markdown(
    '<div class="header-box"><h1>🔍 Panel de Auditoría Editorial</h1></div>',
    unsafe_allow_html=True
)

# ---------------------------------------------
# SUBIDA DE ARCHIVO
# ---------------------------------------------
uploaded = st.file_uploader("Sube tu manuscrito (.docx)", type="docx")

if uploaded:
    ruta_entrada = os.path.join(ENTRADA_DIR, uploaded.name)
    with open(ruta_entrada, "wb") as f:
        f.write(uploaded.getbuffer())

    col1, col2 = st.columns(2)

    # -----------------------------------------
    # PASO 1: AUDITORÍA
    # -----------------------------------------
    with col2:
        st.subheader("Comprobación de erratas")
        if st.button("🤖 Iniciar Auditoría IA"):
            with st.spinner("Analizando documento..."):
                nombre_informe = comprobar_archivo(uploaded.name)
                st.session_state.informe = nombre_informe
                st.session_state.procesado = True
            st.rerun()

# ---------------------------------------------
# VISUALIZACIÓN DE RESULTADOS (CRÍTICA)
# ---------------------------------------------
if st.session_state.procesado and st.session_state.informe:
    ruta_informe = os.path.join(SALIDA_DIR, st.session_state.informe)

    if os.path.exists(ruta_informe):
        filas = []

        with open(ruta_informe, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if "|" in linea and "ID_" in linea:
                    partes = [p.strip() for p in linea.split("|")]
                    if len(partes) >= 5:
                        filas.append({
                            "Categoría": partes[0].upper(),
                            "ID": partes[1],
                            "Original": partes[2],
                            "Corrección": partes[3],
                            "Motivo": partes[4]
                        })

        if filas:
            df = pd.DataFrame(filas)

            st.divider()
            st.subheader("📋 Resultados del Análisis")

            tab1, tab2, tab3 = st.tabs([
                "🔴 Ortografía",
                "🟡 Formato",
                "🟢 Sugerencias"
            ])

            with tab1:
                df_orto = df[df["Categoría"].str.contains("ORTOGRAFIA", na=False)]
                st.dataframe(df_orto, use_container_width=True, hide_index=True)

            with tab2:
                df_form = df[df["Categoría"].str.contains("FORMATO", na=False)]
                st.dataframe(df_form, use_container_width=True, hide_index=True)

            with tab3:
                df_sug = df[df["Categoría"].str.contains("SUGERENCIA", na=False)]
                st.dataframe(df_sug, use_container_width=True, hide_index=True)

            st.divider()
            with open(ruta_informe, "rb") as f:
                st.download_button(
                    "📥 Descargar informe completo (.txt)",
                    data=f,
                    file_name=st.session_state.informe,
                    key="download_txt"
                )
        else:
            st.info("No se detectaron erratas en este documento.")
