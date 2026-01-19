import streamlit as st
import os
import shutil
import precorreccion
import traceback
import auditar
import time

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

if "corregido" not in st.session_state:
    st.session_state["corregido"] = None

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if not archivo:
        st.warning("Por favor, sube un archivo primero.")
    else:
        try:
            # Limpieza total
            if os.path.exists(INPUT_FOLDER): shutil.rmtree(INPUT_FOLDER)
            if os.path.exists(OUTPUT_FOLDER): shutil.rmtree(OUTPUT_FOLDER)
            os.makedirs(INPUT_FOLDER)
            os.makedirs(OUTPUT_FOLDER)

            ruta_entrada = os.path.join(INPUT_FOLDER, archivo.name)
            with open(ruta_entrada, "wb") as f:
                f.write(archivo.getbuffer())

            with st.status("Procesando...") as status:
                precorreccion.procesar_archivo(archivo.name)
                time.sleep(1)
                
                nombre_salida = archivo.name.replace(".docx", "_CORREGIDO.docx")
                ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_salida)

                if os.path.exists(ruta_salida):
                    st.session_state["corregido"] = archivo.name
                    status.update(label="✅ ¡Hecho!", state="complete")
                    with open(ruta_salida, "rb") as f:
                        st.download_button("📥 DESCARGAR DOCX", f, file_name=nombre_salida)
                else:
                    st.error("No se encontró el archivo de salida.")
        except Exception as e:
            st.error(f"Error: {e}")
            st.code(traceback.format_exc())

if st.session_state["corregido"]:
    st.divider()
    try:
        inf = auditar.generar_informe_txt(st.session_state["corregido"])
        st.download_button("📄 DESCARGAR INFORME", inf, file_name="informe.txt")
    except:
        st.info("Informe en proceso...")
