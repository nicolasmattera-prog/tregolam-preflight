import streamlit as st
import os
import sys
import pandas as pd

# -------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -------------------------------------------------
st.set_page_config(
    page_title="Auditoría Editorial Tregolam",
    page_icon="🔍",
    layout="wide"
)

# -------------------------------------------------
# RUTAS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

os.makedirs(ENTRADA_DIR, exist_ok=True)
os.makedirs(SALIDA_DIR, exist_ok=True)

sys.path.append(SCRIPTS_DIR)

# -------------------------------------------------
# IMPORTACIONES CRÍTICAS
# -------------------------------------------------
try:
    import comprobacion
    from regex_rules import RULES
except ImportError as e:
    st.error(f"Error crítico de importación: {e}")
    st.stop()

# -------------------------------------------------
# ESTADO
# -------------------------------------------------
if "informe" not in st.session_state:
    st.session_state.informe = None
if "procesado" not in st.session_state:
    st.session_state.procesado = False

# -------------------------------------------------
# CABECERA
# -------------------------------------------------
st.title("🔍 Panel de Auditoría Editorial")
st.caption("Motor IA + reglas editoriales Tregolam")

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.subheader("Motor cargado")
    st.write(f"Reglas activas: {len(RULES)}")
    st.divider()
    st.caption("v3.0 estable")

# -------------------------------------------------
# SUBIDA DE ARCHIVO
# -------------------------------------------------
uploaded = st.file_uploader("Sube un archivo DOCX", type="docx")

if uploaded:
    ruta_entrada = os.path.join(ENTRADA_DIR, uploaded.name)
    with open(ruta_entrada, "wb") as f:
        f.write(uploaded.getbuffer())

    col1, col2 = st.columns(2)

    # -------------------------------------------------
    # PASO 2
    # -------------------------------------------------
    with col2:
        st.subheader("Paso 2 · Auditoría IA")
        if st.button("🤖 Ejecutar auditoría"):
            with st.spinner("Analizando documento..."):
                nombre_informe = comprobacion.comprobar_archivo(uploaded.name)
                st.session_state.informe = nombre_informe
                st.session_state.procesado = True
            st.success("Auditoría completada")

# -------------------------------------------------
# VISUALIZACIÓN DE RESULTADOS
# -------------------------------------------------
if st.session_state.procesado and st.session_state.informe:
    ruta_informe = os.path.join(SALIDA_DIR, st.session_state.informe)

    if os.path.exists(ruta_informe):
        datos = []
        errores_tecnicos = []
        resumen = []

        with open(ruta_informe, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()

                if linea.startswith("ERROR_"):
                    errores_tecnicos.append(linea)
                    continue

                if linea.startswith("RESUMEN") or linea.startswith("-") or linea.startswith("TOTAL"):
                    resumen.append(linea)
                    continue

                if "|" in linea:
                    partes = [p.strip() for p in linea.split("|")]
                    if len(partes) == 5:
                        datos.append({
                            "Categoría": partes[0],
                            "ID": partes[1],
                            "Original": partes[2],
                            "Corrección": partes[3],
                            "Motivo": partes[4]
                        })

        if errores_tecnicos:
            st.warning("Errores técnicos detectados")
            for e in errores_tecnicos:
                st.code(e)

        if resumen:
            st.subheader("📊 Resumen")
            for r in resumen:
                st.write(r)

        if datos:
            df = pd.DataFrame(datos)
            st.subheader("📋 Hallazgos")

            tab1, tab2, tab3 = st.tabs(["🔴 Ortografía", "🟡 Formato", "🟢 Sugerencias"])

            with tab1:
                st.dataframe(
                    df[df["Categoría"] == "ORTOGRAFIA"],
                    use_container_width=True,
                    hide_index=True
                )

            with tab2:
                st.dataframe(
                    df[df["Categoría"] == "FORMATO"],
                    use_container_width=True,
                    hide_index=True
                )

            with tab3:
                st.dataframe(
                    df[df["Categoría"] == "SUGERENCIA"],
                    use_container_width=True,
                    hide_index=True
                )

        with open(ruta_informe, "rb") as f:
            st.download_button(
                "📥 Descargar informe completo",
                data=f,
                file_name=st.session_state.informe
            )
