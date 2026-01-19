import streamlit as st
import os
import shutil
import precorreccion
import auditar
import traceback
import time

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# 1. Definición de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

# 2. Sincronización para TODOS los módulos
precorreccion.INPUT_FOLDER = INPUT_FOLDER
precorreccion.OUTPUT_FOLDER = OUTPUT_FOLDER
auditar.INPUT_FOLDER = INPUT_FOLDER
auditar.OUTPUT_FOLDER = OUTPUT_FOLDER

if "corregido" not in st.session_state:
    st.session_state["corregido"] = None

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if not archivo:
        st.warning("Por favor, sube un archivo primero.")
    else:
        try:
            # Limpiar archivos de la ejecución anterior (respetando el .gitkeep)
            for f in os.listdir(INPUT_FOLDER):
                if f != ".gitkeep":
                    try: os.remove(os.path.join(INPUT_FOLDER, f))
                    except: pass
            
            ruta_entrada = os.path.join(INPUT_FOLDER, archivo.name)
            with open(ruta_entrada, "wb") as f:
                f.write(archivo.getbuffer())

            with st.status("Procesando archivo...") as status:
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
                    st.error("El archivo corregido no se generó.")

        except Exception as e:
            st.error(f"Error técnico: {e}")
            st.code(traceback.format_exc())

# --- SECCIÓN DEL INFORME MEJORADA ---
if st.session_state["corregido"]:
    st.divider()
    st.subheader("📋 Informe de cambios")
    try:
        # Generamos el contenido del informe
        contenido_informe = auditar.generar_informe_txt(st.session_state["corregido"])
        
        # Si el informe tiene contenido, mostramos el botón
        if contenido_informe:
            st.download_button(
                label="📄 DESCARGAR INFORME",
                data=contenido_informe,
                file_name=f"informe_{st.session_state['corregido']}.txt",
                mime="text/plain"
            )
        else:
            st.warning("El informe se generó vacío.")
            
    except Exception as e:
        st.error(f"No se pudo generar el botón de descarga: {e}")
