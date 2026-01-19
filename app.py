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

# 2. Sincronizar módulos
precorreccion.INPUT_FOLDER = INPUT_FOLDER
precorreccion.OUTPUT_FOLDER = OUTPUT_FOLDER
auditar.ORIGINAL_FOLDER = INPUT_FOLDER
auditar.CORREGIDO_FOLDER = OUTPUT_FOLDER

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

if "archivo_listo" not in st.session_state:
    st.session_state["archivo_listo"] = None

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
                # 1. Corrección
                precorreccion.procesar_archivo(archivo.name)
                time.sleep(1)
                
                # 2. Auditoría
                auditar.auditar_archivos(archivo.name)
                
                st.session_state["archivo_listo"] = archivo.name
                status.update(label="✅ ¡Todo procesado correctamente!", state="complete")

        except Exception as e:
            st.error(f"Error: {e}")
            st.code(traceback.format_exc())

# --- SECCIÓN DE DESCARGAS (Visible siempre que el proceso haya terminado) ---
if st.session_state["archivo_listo"]:
    st.divider()
    st.subheader("📥 Resultados disponibles")
    
    nombre_base = st.session_state["archivo_listo"].replace(".docx", "")
    ruta_docx = os.path.join(OUTPUT_FOLDER, f"{nombre_base}_CORREGIDO.docx")
    ruta_txt = os.path.join(OUTPUT_FOLDER, f"MUESTRAS_CAMBIO_{nombre_base}.txt")
    ruta_html = os.path.join(OUTPUT_FOLDER, f"AUDITORIA_{nombre_base}.html")

    # Botón Principal de Corrección
    if os.path.exists(ruta_docx):
        with open(ruta_docx, "rb") as f:
            st.download_button(
                label="⭐ DESCARGAR MANUSCRITO CORREGIDO (.docx)",
                data=f,
                file_name=f"{nombre_base}_CORREGIDO.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
    
    st.write("---")
    
    # Botones de Informe
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists(ruta_txt):
            with open(ruta_txt, "r", encoding="utf-8") as f:
                st.download_button("📄 Informe de Cambios (.txt)", f.read(), file_name=f"informe_{nombre_base}.txt")
    
    with col2:
        if os.path.exists(ruta_html):
            with open(ruta_html, "r", encoding="utf-8") as f:
                st.download_button("🌐 Auditoría Visual (HTML)", f.read(), file_name=f"auditoria_{nombre_base}.html")
