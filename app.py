import streamlit as st
import os
import shutil
import precorreccion
import traceback
import auditar
import time

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# RUTAS FORZADAS PARA STREAMLIT CLOUD
BASE_DIR = os.getcwd() # Esto obtiene la raíz exacta en el servidor
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

# Crear carpetas si no existen
if not os.path.exists(INPUT_FOLDER): os.makedirs(INPUT_FOLDER)
if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)

if "corregido" not in st.session_state:
    st.session_state["corregido"] = None

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if not archivo:
        st.warning("Por favor, sube un archivo primero.")
    else:
        try:
            # Limpiar carpetas antes de empezar
            for f in os.listdir(INPUT_FOLDER): os.remove(os.path.join(INPUT_FOLDER, f))
            for f in os.listdir(OUTPUT_FOLDER): os.remove(os.path.join(OUTPUT_FOLDER, f))

            # Guardar archivo subido
            ruta_entrada = os.path.join(INPUT_FOLDER, archivo.name)
            with open(ruta_entrada, "wb") as f:
                f.write(archivo.getbuffer())

            with st.status("Procesando...") as status:
                # LLAMADA AL MOTOR
                precorreccion.procesar_archivo(archivo.name)
                
                nombre_salida = archivo.name.replace(".docx", "_CORREGIDO.docx")
                ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_salida)

                if os.path.exists(ruta_salida):
                    st.session_state["corregido"] = archivo.name
                    status.update(label="✅ ¡Hecho!", state="complete")
                    with open(ruta_salida, "rb") as f:
                        st.download_button("📥 DESCARGAR DOCX", f, file_name=nombre_salida)
                else:
                    st.error(f"El archivo corregido no aparece en: {ruta_salida}")

        except Exception as e:
            st.error(f"Error en el proceso: {e}")
            st.code(traceback.format_exc())

# Sección de informe (fuera del botón para que no desaparezca)
if st.session_state["corregido"]:
    st.divider()
    try:
        inf = auditar.generar_informe_txt(st.session_state["corregido"])
        st.download_button("📄 DESCARGAR INFORME", inf, file_name="informe.txt")
    except:
        st.info("Generando informe...")
