import streamlit as st
import os
import shutil
import precorreccion
import traceback
import auditar

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# Crear carpetas necesarias
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if archivo:
        # Limpiar carpetas
        shutil.rmtree(INPUT_FOLDER)
        os.makedirs(INPUT_FOLDER)
        shutil.rmtree(OUTPUT_FOLDER)
        os.makedirs(OUTPUT_FOLDER)

        ruta_entrada = os.path.join(INPUT_FOLDER, archivo.name)
        with open(ruta_entrada, "wb") as f:
            f.write(archivo.getbuffer())

        with st.status("Ejecutando corrección quirúrgica...", expanded=True) as status:
            try:
                precorreccion.procesar_archivo(archivo.name)

                nombre_salida = archivo.name.replace(".docx", "_CORREGIDO.docx")
                ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_salida)

                if os.path.exists(ruta_salida):
                    status.update(label="✅ ¡CORRECCIÓN FINALIZADA!", state="complete")
                    with open(ruta_salida, "rb") as f:
                        st.download_button(
                            label="📥 DESCARGAR MANUSCRITO CORREGIDO",
                            data=f,
                            file_name=nombre_salida,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    st.session_state["corregido"] = archivo.name
                else:
                    st.error("El proceso terminó pero no se encontró el archivo en la carpeta 'salida'.")

            except Exception:
                st.error("Error técnico en la ejecución:")
                st.code(traceback.format_exc())
    else:
        st.warning("Por favor, carga un archivo .docx")

# Botón opcional: descargar informe
if st.session_state.get("corregido"):
    informe = auditar.generar_informe_txt(st.session_state["corregido"])
    nombre_informe = st.session_state["corregido"].replace(".docx", "_INFORME.txt")
    st.download_button(
        label="📄 Descargar informe de correcciones",
        data=informe,
        file_name=nombre_informe,
        mime="text/plain"
    )
