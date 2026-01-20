import os
import sys
import base64
import streamlit as st

# ======================================================
# CONFIGURACIÓN STREAMLIT (CLAVE)
# ======================================================
st.markdown("""
<style>

/* FONDO GLOBAL */
[data-testid="stAppViewContainer"] {
    background-color: #f5f5f5;
}

/* CONTENEDOR PRINCIPAL */
[data-testid="stAppViewContainer"] > .main {
    max-width: 820px;
    margin: auto;
    padding: 2.5rem 2.5rem;
}

/* ===== HEADER (NO TARJETA) ===== */
.app-header {
    text-align: center;
    margin-bottom: 2.5rem;
}

.app-header h1 {
    font-weight: 600;
    color: #1f1f1f;
    letter-spacing: -0.02em;
    margin-top: 0.5rem;
}

/* ===== TARJETAS SOLO DONDE TOCA ===== */
.card {
    background: #ffffff;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    margin-bottom: 1.5rem;
}

/* BOTONES */
button[kind="primary"] {
    background-color: #1f1f1f !important;
    color: white !important;
    border-radius: 6px !important;
    padding: 0.6rem 1.2rem !important;
    border: none !important;
}

button[kind="primary"]:hover {
    background-color: #000000 !important;
}

/* BOTONES DESCARGA */
[data-testid="stDownloadButton"] button {
    background-color: #ffffff !important;
    color: #1f1f1f !important;
    border: 1px solid #cccccc !important;
    border-radius: 6px !important;
}

/* OCULTAR FOOTER */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# LOGO (DESDE assets/)
# ======================================================
def mostrar_logo(ruta_logo, ancho=200):
    if not os.path.exists(ruta_logo):
        st.error(f"No se encuentra el logo en {ruta_logo}")
        return

    with open(ruta_logo, "rb") as f:
        datos = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom: 2rem;">
            <img src="data:image/png;base64,{datos}" width="{ancho}">
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================================================
# LÓGICA ORIGINAL (SIN TOCAR)
# ======================================================

# Ajuste de imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(BASE_DIR, "scripts")
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

import comprobacion
import precorreccion

# Rutas
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ======================================================
# INTERFAZ
# ======================================================
mostrar_logo("assets/Logo-tregolam.png", ancho=200)

st.title("Tregolam · Preflight Word")

archivo = st.file_uploader("Sube un archivo .docx", type=["docx"])

if archivo is not None:
    nombre_original = archivo.name
    ruta_original = os.path.join(INPUT_FOLDER, nombre_original)

    with open(ruta_original, "wb") as f:
        f.write(archivo.getbuffer())

    st.success(f"Archivo cargado: {nombre_original}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Comprobar"):
            with st.spinner("Analizando..."):
                informe = comprobacion.comprobar_archivo(nombre_original)
                ruta_informe = os.path.join(OUTPUT_FOLDER, informe)

                if os.path.exists(ruta_informe):
                    with open(ruta_informe, "r", encoding="utf-8") as f:
                        st.download_button(
                            "Descargar Informe",
                            f.read(),
                            file_name=informe
                        )

    with col2:
        if st.button("Corregir"):
            with st.spinner("Corrigiendo..."):
                precorreccion.procesar_archivo(nombre_original)

                nombre_corregido = nombre_original.replace(".docx", "_CORREGIDO.docx")
                ruta_corregido = os.path.join(OUTPUT_FOLDER, nombre_corregido)

                if os.path.exists(ruta_corregido):
                    with open(ruta_corregido, "rb") as f:
                        st.download_button(
                            "Descargar Word Corregido",
                            f,
                            file_name=nombre_corregido
                        )

