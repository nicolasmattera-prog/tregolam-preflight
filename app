import os
import sys
import streamlit as st
from pathlib import Path

# ------------------------------------------------------
# 1. CONFIGURACIÓN DE RUTAS (REPO)
# ------------------------------------------------------
# Detectamos la raíz del repositorio de forma dinámica
BASE_DIR = Path(__file__).resolve().parent 
SCRIPTS_DIR = BASE_DIR / "scripts"
INPUT_DIR   = BASE_DIR / "entrada"
OUTPUT_DIR  = BASE_DIR / "salida"

# Añadimos la carpeta 'scripts' al path de Python para que encuentre los módulos
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Creamos las carpetas de trabajo si no existen
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------
# 2. IMPORTACIÓN DE TUS MÓDULOS
# ------------------------------------------------------
try:
    import comprobacion
    import precorreccion
except ModuleNotFoundError as e:
    st.error(f"No se pudieron cargar los scripts de la carpeta /scripts: {e}")
    st.stop()

# ------------------------------------------------------
# 3. INTERFAZ DE STREAMLIT
# ------------------------------------------------------
st.set_page_config(page_title="Tregolam · Preflight", layout="centered")
st.title("Tregolam · Preflight Word")

archivo = st.file_uploader("Sube un archivo .docx", type=["docx"])

if archivo is not None:
    # 1. Guardamos el archivo físicamente en la carpeta /entrada
    nombre_original = archivo.name
    ruta_original = INPUT_DIR / nombre_original
    
    with open(ruta_original, "wb") as f:
        f.write(archivo.getbuffer())

    st.success(f"Archivo cargado correctamente")
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Comprobar"):
            with st.spinner("Analizando..."):
                # ¡SOLUCIÓN!: Pasamos la ruta completa (Path) convertida a texto
                # Así el script de comprobación siempre encuentra el archivo
                nombre_informe = comprobacion.comprobar_archivo(str(ruta_original))
                
                ruta_informe = OUTPUT_DIR / nombre_informe
                
                if ruta_informe.exists():
                    with open(ruta_informe, "r", encoding="utf-8") as f:
                        st.download_button(
                            label="Descargar Informe",
                            data=f.read(),
                            file_name=nombre_informe
                        )
                else:
                    st.error("El proceso terminó pero no se encontró el archivo de informe.")

    with col2:
        if st.button("Corregir"):
            with st.spinner("Corrigiendo..."):
                # Aplicamos la misma lógica para el script de corrección
                precorreccion.procesar_archivo(str(ruta_original))
                
                nombre_corregido = nombre_original.replace(".docx", "_CORREGIDO.docx")
                ruta_corregido = OUTPUT_DIR / nombre_corregido
                
                if ruta_corregido.exists():
                    with open(ruta_corregido, "rb") as f:
                        st.download_button(
                            label="Descargar Word Corregido",
                            data=f.read(),
                            file_name=nombre_corregido
                        )
                else:
                    st.error("No se encontró el archivo corregido en la carpeta de salida.")

