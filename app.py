import streamlit as st
import os
import shutil
import precorreccion
import traceback
import auditar

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# Rutas alineadas con precorreccion.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

# Inicializar estado
if "corregido" not in st.session_state:
    st.session_state["corregido"] = None

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if archivo:
        # 1. Limpieza total de carpetas antes de empezar
        if os.path.exists(INPUT_FOLDER): shutil.rmtree(INPUT_FOLDER)
        if os.path.exists(OUTPUT_FOLDER): shutil.rmtree(OUTPUT_FOLDER)
        os.makedirs(INPUT_FOLDER); os.makedirs(OUTPUT_FOLDER)

        # 2. Guardar en la carpeta 'entrada' que tu script necesita
        ruta_entrada = os.path.join(INPUT_FOLDER, archivo.name)
        with open(ruta_entrada, "wb") as f:
            f.write(archivo.getbuffer())

        with st.status("Ejecutando corrección quirúrgica...", expanded=True) as status:
            try:
                # 3. Lanzamos tu función de precorreccion.py
                precorreccion.procesar_archivo(archivo.name)

                # 4. Tu script genera el nombre con "_CORREGIDO.docx"
                nombre_salida = archivo.name.replace(".docx", "_CORREGIDO.docx")
                ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_salida)

                if os.path.exists(ruta_salida):
                    status.update(label="✅ ¡PROCESO COMPLETADO!", state="complete")
                    with open(ruta_salida, "rb") as f:
                        st.download_button(
                            label="📥 DESCARGAR MANUSCRITO CORREGIDO",
                            data=f,
                            file_name=nombre_salida,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    st.session_state["corregido"] = archivo.name
                else:
                    st.error(f"Error: El archivo no se encontró en {ruta_salida}")
            
            except Exception:
                st.error("Error técnico detectado:")
                st.code(traceback.format_exc())
    else:
        st.warning("Por favor, carga un archivo .docx")

# Sección de informe (Solo aparece si se completó)
if st.session_state["corregido"]:
    st.divider()
    try:
        informe = auditar.generar_informe_txt(st.session_state["corregido"])
        st.download_button(
            label="📄 Descargar informe de correcciones",
            data=informe,
            file_name=st.session_state["corregido"].replace(".docx", "_INFORME.txt"),
            mime="text/plain"
        )
    except:
        pass
