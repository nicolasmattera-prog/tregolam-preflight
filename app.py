import os
import sys
import base64
import streamlit as st

# =========================
# CONFIGURACIÓN VISUAL (ESTILO ADOBE)
# =========================
st.set_page_config(
    page_title="Tregolam · Preflight",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>

/* --- BASE --- */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Roboto, Helvetica, Arial, sans-serif;
    background-color: #f5f5f5;
}

/* --- CONTENEDOR PRINCIPAL --- */
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 2.5rem;
    max-width: 720px;
}

/* --- TÍTULOS --- */
h1, h2, h3 {
    font-weight: 600;
    color: #1f1f1f;
    letter-spacing: -0.01em;
}

/* --- TEXTO --- */
p, label {
    color: #3a3a3a;
    font-size: 0.95rem;
}

/* --- FILE UPLOADER --- */
section[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 1.2rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

/* --- BOTONES --- */
.stButton > button {
    width: 100%;
    background-color: #1f1f1f;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 0.6rem 1rem;
    font-weight: 500;
}

.stButton > button:hover {
    background-color: #000000;
}

/* --- BOTONES DOWNLOAD --- */
.stDownloadButton > button {
    background-color: #ffffff;
    color: #1f1f1f;
    border: 1px solid #d0d0d0;
}

.stDownloadButton > button:hover {
    background-color: #f0f0f0;
}

/* --- MENSAJES --- */
.stAlert {
    border-radius: 6px;
    font-size: 0.9rem;
}

</style>
""", unsafe_allow_html=True)

# =========================
# LOGO (DESDE /assets)
# =========================
def mostrar_logo(ruta_logo, ancho=180):
    if not os.path.exists(ruta_logo):
        return

    with open(ruta_logo, "rb") as f:
        datos = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom: 1.5rem;">
            <img src="data:image/png;base64,{datos}" width="{ancho}">
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# LÓGICA ORIGINAL (SIN TOCAR)
# =========================

# 1. ESTO ARREGLA LA IMPORTACIÓN:
# Como app.py está fuera y tus scripts dentro de /scripts,
# añadimos la carpeta al path para que Python los encuentre.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(BASE_DIR, "scripts")
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

import comprobacion
import precorreccion

# 2. CONFIGURACIÓN DE RUTAS (Raíz)
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =========================
# INTERFAZ
# =========================
mostrar_logo("assets/logo.png", ancho=180)

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
