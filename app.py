import streamlit as st
import os
import shutil
import precorreccion
import traceback
import time

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

btn_correccion = st.button("🚀 INICIAR CORRECCIÓN", use_container_width=True)
btn_comprobacion = st.button("🔍 INICIAR COMPROBACIÓN", use_container_width=True)

if btn_correccion or btn_comprobacion:
    if not archivo:
        st.warning("Por favor, sube un archivo primero.")
    else:
        try:
            # Limpiar
            for f in os.listdir(INPUT_FOLDER):
                if f != ".gitkeep":
                    try:
                        os.remove(os.path.join(INPUT_FOLDER, f))
                    except:
                        pass

            ruta_entrada = os.path.join(INPUT_FOLDER, archivo.name)
            with open(ruta_entrada, "wb") as f:
                f.write(archivo.getbuffer())

            if btn_correccion:
                with st.status("Procesando Corrección Total...") as status:
                    precorreccion.procesar_archivo(archivo.name)
                    time.sleep(1)
                    status.update(label="✅ Corrección completada", state="complete")

            elif btn_comprobacion:
                with st.status("Analizando sin modificar...") as status:
                    precorreccion.comprobar_archivo(archivo.name)
                    status.update(label="✅ Análisis finalizado", state="complete")

        except Exception as e:
            st.error(f"Error: {e}")
            st.code(traceback.format_exc())

# Resultados
if archivo:
    st.divider()
    nombre_base = archivo.name.replace(".docx", "")

    ruta_docx = os.path.join(OUTPUT_FOLDER, f"{nombre_base}_CORREGIDO.docx")
    if os.path.exists(ruta_docx):
        with open(ruta_docx, "rb") as f:
            st.download_button("⭐ DESCARGAR DOCX CORREGIDO", f, file_name=f"{nombre_base}_CORREGIDO.docx", use_container_width=True)

    ruta_txt = os.path.join(OUTPUT_FOLDER, f"VALIDACION_{nombre_base}.txt")
    if os.path.exists(ruta_txt):
        with open(ruta_txt, "r", encoding="utf-8") as f:
            st.download_button("📄 DESCARGAR INFORME DE ERRORES (.txt)", f.read(), file_name=f"validación_{nombre_base}.txt", use_container_width=True)
    else:
        st.warning("No se encontraron errores significativos o el informe no se generó.")
