import streamlit as st
import os
import shutil
import precorreccion
import auditar
import traceback
import time

# Configuración de página
st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# 1. Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

# 2. Sincronizar carpetas con los módulos
precorreccion.INPUT_FOLDER = INPUT_FOLDER
precorreccion.OUTPUT_FOLDER = OUTPUT_FOLDER
auditar.ORIGINAL_FOLDER = INPUT_FOLDER
auditar.CORREGIDO_FOLDER = OUTPUT_FOLDER

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
            # Limpiar carpetas
            for f in os.listdir(INPUT_FOLDER):
                if f != ".gitkeep":
                    try: os.remove(os.path.join(INPUT_FOLDER, f))
                    except: pass
            
            ruta_entrada = os.path.join(INPUT_FOLDER, archivo.name)
            with open(ruta_entrada, "wb") as f:
                f.write(archivo.getbuffer())

            with st.status("Procesando documento...") as status:
                # Ejecutar corrección
                precorreccion.procesar_archivo(archivo.name)
                time.sleep(1)
                
                # Ejecutar auditoría (esto crea los archivos .txt y .html en la carpeta 'salida')
                auditar.auditar_archivos(archivo.name)
                
                nombre_salida = archivo.name.replace(".docx", "_CORREGIDO.docx")
                ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_salida)

                if os.path.exists(ruta_salida):
                    st.session_state["corregido"] = archivo.name
                    status.update(label="✅ ¡Hecho!", state="complete")
                    
                    with open(ruta_salida, "rb") as f:
                        st.download_button("📥 DESCARGAR DOCX", f, file_name=nombre_salida)
                else:
                    st.error("No se generó el archivo corregido.")

        except Exception as e:
            st.error(f"Error: {e}")
            st.code(traceback.format_exc())

# --- SECCIÓN DEL INFORME REPARADA ---
if st.session_state["corregido"]:
    st.divider()
    st.subheader("📋 Informes de Auditoría")
    
    # Buscamos los archivos que tu auditar.py acaba de crear
    nombre_base = st.session_state["corregido"].replace(".docx", "")
    ruta_txt = os.path.join(OUTPUT_FOLDER, f"MUESTRAS_CAMBIO_{nombre_base}.txt")
    ruta_html = os.path.join(OUTPUT_FOLDER, f"AUDITORIA_{nombre_base}.html")

    col1, col2 = st.columns(2)

    with col1:
        if os.path.exists(ruta_txt):
            with open(ruta_txt, "r", encoding="utf-8") as f:
                st.download_button("📄 DESCARGAR INFORME (.txt)", f.read(), file_name=f"informe_{nombre_base}.txt")
        else:
            st.info("Generando informe TXT...")

    with col2:
        if os.path.exists(ruta_html):
            with open(ruta_html, "r", encoding="utf-8") as f:
                st.download_button("🌐 DESCARGAR COMPARATIVA (HTML)", f.read(), file_name=f"auditoria_{nombre_base}.html")
