import streamlit as st
import os
import sys
import pandas as pd

# -------------------------------------------------
# CONFIGURACIÓN DE PÁGINA (Compacta y Centrada)
# -------------------------------------------------
st.set_page_config(
    page_title="Preflight® - Tregolam",
    page_icon="🔍",
    layout="wide"
)

# Estética para evitar el estiramiento y mejorar botones
st.markdown("""
    <style>
    .block-container { max-width: 1100px; padding-top: 2rem; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; }
    .header-box { background-color: #1E1E1E; padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# RUTAS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

os.makedirs(ENTRADA_DIR, exist_ok=True)
os.makedirs(SALIDA_DIR, exist_ok=True)

if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

# -------------------------------------------------
# IMPORTACIONES
# -------------------------------------------------
try:
    import precorreccion
    import comprobacion
    from regex_rules import RULES
except ImportError as e:
    st.error(f"Error crítico de importación: {e}")
    st.stop()

# -------------------------------------------------
# ESTADO DE SESIÓN
# -------------------------------------------------
if "informe" not in st.session_state:
    st.session_state.informe = None
if "procesado" not in st.session_state:
    st.session_state.procesado = False

# -------------------------------------------------
# SIDEBAR (Logo y Versión solicitada)
# -------------------------------------------------
with st.sidebar:
    logo_path = os.path.join(SCRIPTS_DIR, "isologo tregolma prefligth.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    
    st.divider()
    st.success(f"✅ Motor: {len(RULES)} reglas")
    st.divider()
    st.caption("v2.1 - Preflight® -  Tregolam Literatura S.L.")

# -------------------------------------------------
# CABECERA
# -------------------------------------------------
st.markdown('<div class="header-box"><h1>🔍 Panel de Auditoría Editorial</h1></div>', unsafe_allow_html=True)

# -------------------------------------------------
# SUBIDA DE ARCHIVO
# -------------------------------------------------
uploaded = st.file_uploader("Sube tu manuscrito (.docx)", type="docx")

if uploaded:
    ruta_entrada = os.path.join(ENTRADA_DIR, uploaded.name)
    with open(ruta_entrada, "wb") as f:
        f.write(uploaded.getbuffer())

    col1, col2 = st.columns(2)

    # PASO 1: CORRECCIÓN ORTOTIPOGRÁFICA
    with col1:
        st.subheader("Corrección Ortotipográfica")
        if st.button("✨ Ejecutar corrección"):
            with st.spinner("Aplicando motor Tregolam..."):
                precorreccion.procesar_archivo(uploaded.name)
            st.success("✅ Corrección completada")

            ruta_corregido = os.path.join(SALIDA_DIR, uploaded.name)
            if os.path.exists(ruta_corregido):
                with open(ruta_corregido, "rb") as f:
                    st.download_button(
                        label="📥 Descargar Word corregido",
                        data=f,
                        file_name=f"Corregido_{uploaded.name}",
                        use_container_width=True
                    )

    # PASO 2: COMPROBACIÓN DE ERRATAS
    with col2:
        st.subheader("Comprobación de erratas")
        if st.button("🤖 Iniciar Auditoría IA"):
            with st.spinner("Analizando con IA..."):
                nombre_informe = comprobacion.comprobar_archivo(uploaded.name)
                st.session_state.informe = nombre_informe
                st.session_state.procesado = True
            st.rerun()

# -------------------------------------------------
# VISUALIZACIÓN DE RESULTADOS (CORREGIDA)
# -------------------------------------------------
if st.session_state.procesado and st.session_state.informe:
    ruta_informe = os.path.join(SALIDA_DIR, st.session_state.informe)

    if os.path.exists(ruta_informe):
        datos = []
        with open(ruta_informe, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if "|" in linea and "ID_" in linea:
                    partes = [p.strip() for p in linea.split("|")]
                    if len(partes) >= 5:
                        datos.append({
                            "Categoría": partes[0].upper(),
                            "ID": partes[1],
                            "Original": partes[2],
                            "Corrección": partes[3],
                            "Motivo": partes[4]
                        })

        if datos:
            df = pd.DataFrame(datos)
            st.divider()
            st.subheader("📋 Resultados del Análisis")

            tab1, tab2, tab3 = st.tabs(["🔴 Ortografía", "🟡 Formato", "🟢 Sugerencias"])

            # Filtros mejorados con .str.contains para evitar errores por espacios
            with tab1:
                df_orto = df[df["Categoría"].str.contains("ORTOGRAFIA|ORTOGRAFÍA", na=False)]
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
            st.info("No se encontraron erratas en este bloque.")
