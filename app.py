import streamlit as st
import os
import shutil
import precorreccion
import auditar
import traceback
import time

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# 1. Definición de rutas relativas (apuntan a las carpetas que creaste)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

# 2. Sincronización forzada con los otros archivos
precorreccion.INPUT_FOLDER = INPUT_FOLDER
precorreccion.OUTPUT_FOLDER = OUTPUT_FOLDER

if "corregido" not in st.session_state:
    st.session_state["corregido"] = None

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if not archivo:
        st.warning("Por favor, sube un archivo primero.")
    else:
        try:
            # Limpiar archivos de la ejecución anterior
            for f in os.listdir(INPUT_FOLDER):
                if f != ".gitkeep":
                    try: os.remove(os.path.join(INPUT_FOLDER, f))
                    except: pass
            
            # Guardar el archivo subido
            ruta_entrada = os.path.join(INPUT_FOLDER, archivo.name)
            with open(ruta_entrada, "wb") as f:
                f.write(archivo.getbuffer())

            with st.status("Procesando archivo...") as status:
                # Llamar al motor de corrección
                precorreccion.procesar_archivo(archivo.name)
                time.sleep(1)
                
                nombre_salida = archivo.name.replace(".docx", "_CORREGIDO.docx")
                ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_salida)

                if os.path.exists(ruta_salida):
                    st.session_state["corregido"] = archivo.name
                    status.update(label="✅ ¡Documento listo!", state="complete")
                    with open(ruta_salida, "rb") as f:
                        st.download_button("📥 DESCARGAR DOCX", f, file_name=nombre_salida)
                else:
                    st.error(f"El archivo corregido no se generó en la carpeta de salida.")

        except Exception as e:
            st.error(f"Error técnico: {e}")
            st.code(traceback.format_exc())

if st.session_state["corregido"]:
    st.divider()
    try:
        inf = auditar.generar_informe_txt(st.session_state["corregido"])
        st.download_button("📄 DESCARGAR INFORME", inf, file_name="informe.txt")
    except:
        st.info("Informe generado.")
