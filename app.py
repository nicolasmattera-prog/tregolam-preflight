"""
Tregolam – Preflight Word
Streamlit app
"""

import os
import sys
import base64
import streamlit as st
from pathlib import Path

# ------------------------------------------------------
# 1.  CSS  (inyección simple, compatible con cualquier versión)
# ------------------------------------------------------
CSS = """
<style>
/* Marco general */
[data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
}
[data-testid="stAppViewContainer"] > [data-testid="stAppViewBlockContainer"] {
    border: 2px solid #d1d5db;
    border-radius: 8px;
    padding: 2.5rem;
    margin: 2rem auto;
    max-width: 1100px;
}

/* Botones st.button */
.stButton > button:first-of-type {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    padding: 0.65rem 1.4rem !important;
    font-weight: 600 !important;
    border: none !important;
}
.stButton > button:first-of-type:hover {
    background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
    transform: translateY(-1px) !important;
}
</style>
"""

st.write(CSS, unsafe_allow_html=True)

# ------------------------------------------------------
# 2.  FUNCIONES AUXILIARES
# ------------------------------------------------------
def mostrar_logo(ruta_logo: str, ancho: int = 200) -> None:
    """Muestra el logo centrado si existe."""
    if not os.path.isfile(ruta_logo):
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
        unsafe_allow_html=True,
    )

# ------------------------------------------------------
# 3.  PREPARACIÓN DE RUTAS  (compatible local + cloud)
# ------------------------------------------------------
BASE_DIR = Path.cwd()                       # /mount/src/tregolam-preflight en cloud
SCRIPTS_DIR = BASE_DIR / "scripts"
INPUT_DIR   = BASE_DIR / "entrada"
OUTPUT_DIR  = BASE_DIR / "salida"

# Añadimos scripts al PYTHONPATH
sys.path.insert(0, str(SCRIPTS_DIR))

# Creamos carpetas si no existen
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------
# 4.  IMPORTS DE MÓDULOS PROPIOS
# ------------------------------------------------------
try:
    import comprobacion
    import precorreccion
except ModuleNotFoundError as e:
    st.error(f"Módulo no encontrado: {e}")
    st.stop()

# ------------------------------------------------------
# 5.  INTERFAZ
# ------------------------------------------------------
mostrar_logo("assets/logo-tregolam-completo.png", ancho=200)
st.title("Tregolam · Preflight Word")

archivo = st.file_uploader("Sube un archivo .docx", type=["docx"])

if archivo is not None:
    nombre_original = archivo.name
    ruta_original   = INPUT_DIR / nombre_original

    # Guardar archivo subido
    with open(ruta_original, "wb") as f:
        f.write(archivo.getbuffer())
    st.success(f"Archivo cargado: {nombre_original}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Comprobar"):
            with st.spinner("Analizando…"):
                informe = comprobacion.comprobar_archivo(nombre_original)
                ruta_informe = OUTPUT_DIR / informe

                if ruta_informe.exists():
                    st.download_button(
                        label     = "Descargar Informe",
                        data      = ruta_informe.read_text(encoding="utf-8"),
                        file_name = informe
                    )

    with col2:
        if st.button("Corregir"):
            with st.spinner("Corrigiendo…"):
                precorreccion.procesar_archivo(nombre_original)

                nombre_corregido = nombre_original.replace(".docx", "_CORREGIDO.docx")
                ruta_corregido   = OUTPUT_DIR / nombre_corregido

                if ruta_corregido.exists():
                    st.download_button(
                        label     = "Descargar Word Corregido",
                        data      = ruta_corregido.read_bytes(),
                        file_name = nombre_corregido
                    )
