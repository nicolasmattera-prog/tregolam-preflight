import streamlit as st
import os
import shutil
import precorreccion
import traceback
import auditar
import time

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

# Aseguramos carpetas
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

if "corregido" not in st.session_state:
    st.session_state["corregido"] = None

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if archivo:
        try:
            # Limpieza previa
            if os.path.exists(INPUT_FOLDER): shutil.rmtree(INPUT_FOLDER)
            if os.path.exists(OUTPUT_FOLDER): shutil.rmtree(OUTPUT_FOLDER)
            os.makedirs(INPUT_FOLDER)
            os.makedirs(OUTPUT_FOLDER)

            ruta_entrada = os.path.join(INPUT_FOLDER, archivo.name)
            with open(ruta_entrada, "wb") as f:
                f.write(archivo.getbuffer())

            with st.status("Corrigiendo...", expanded=True) as status:
                try:
                    precorreccion.procesar_archivo(archivo.name)
                    time.sleep(1)

                    nombre_salida = archivo.name.replace(".docx", "_CORREGIDO.docx")
                    ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_salida)

                    if os.path.exists(ruta_salida):
                        status.update(label="✅ FINALIZADO", state="complete")
                        with open(ruta_salida, "rb") as f:
                            st.download_button(
                                label="📥 DESCARGAR CORREGIDO",
                                data=f,
                                file_name=nombre_salida,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        st.session_state["corregido"] = archivo.name
                    else:
                        st.error(f"No se encontró el archivo en: {ruta_salida}")
                except Exception as e:
                    st.error(f"Error en motor: {str(e)}")
                    st.code(traceback.format_exc())
        except Exception as e:
            st.error(f"Error de carpetas: {str(e)}")
    else:
        st.warning("Sube un archivo primero.")

if st.session_state["corregido"]:
    st.divider()
    try:
        informe = auditar.generar_informe_txt(st.session_state["corregido"])
        st.download_button(
            label="📄 Descargar informe",
            data=informe,
            file_name=st.session_state["corregido"].replace(".docx", "_INFORME.txt"),
            mime="text/plain"
        )
    except:
        st.info("Informe no disponible todavía.")
