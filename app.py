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

# 1. Rutas y Sincronización
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

precorreccion.INPUT_FOLDER = INPUT_FOLDER
precorreccion.OUTPUT_FOLDER = OUTPUT_FOLDER
auditar.ORIGINAL_FOLDER = INPUT_FOLDER
auditar.CORREGIDO_FOLDER = OUTPUT_FOLDER

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Estados de la sesión
if "modo" not in st.session_state:
    st.session_state["modo"] = None # Puede ser 'correccion' o 'comprobacion'
if "archivo_nombre" not in st.session_state:
    st.session_state["archivo_nombre"] = None

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

# --- INTERFAZ DE BOTONES ---
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    btn_correccion = st.button("🚀 INICIAR CORRECCIÓN", use_container_width=True, type="primary")

with col_btn2:
    # El tipo 'secondary' suele ser gris/azul según el tema de Streamlit
    btn_comprobacion = st.button("🔍 INICIAR COMPROBACIÓN", use_container_width=True)

# --- LÓGICA DE PROCESAMIENTO ---
if btn_correccion or btn_comprobacion:
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

            st.session_state["archivo_nombre"] = archivo.name

            if btn_correccion:
                st.session_state["modo"] = "correccion"
                with st.status("Procesando Corrección Total...") as status:
                    precorreccion.procesar_archivo(archivo.name)
                    time.sleep(1)
                    auditar.auditar_archivos(archivo.name)
                    status.update(label="✅ Corrección completada", state="complete")
            
                        elif btn_comprobacion:
                st.session_state["modo"] = "comprobacion"
                with st.status("Analizando sin modificar...") as status:
                    # Crear archivo "corregido" falso (igual al original) para que auditar tenga con qué comparar
                    nombre_corregido = archivo.name.replace(".docx", "_CORREGIDO.docx")
                    ruta_corregido = os.path.join(OUTPUT_FOLDER, nombre_corregido)
                    shutil.copy(ruta_entrada, ruta_corregido)  # ← copia idéntica
                    # Ahora sí ejecutamos auditar
                    auditar.auditar_archivos(archivo.name)
                    status.update(label="✅ Análisis finalizado", state="complete")

        except Exception as e:
            st.error(f"Error: {e}")
            st.code(traceback.format_exc())

# --- SECCIÓN DE RESULTADOS ---
if st.session_state["archivo_nombre"]:
    st.divider()
    nombre_base = st.session_state["archivo_nombre"].replace(".docx", "")
    
    if st.session_state["modo"] == "correccion":
        st.subheader("📥 Resultados de Corrección")
        ruta_docx = os.path.join(OUTPUT_FOLDER, f"{nombre_base}_CORREGIDO.docx")
        if os.path.exists(ruta_docx):
            with open(ruta_docx, "rb") as f:
                st.download_button("⭐ DESCARGAR DOCX CORREGIDO", f, file_name=f"{nombre_base}_CORREGIDO.docx", use_container_width=True)
    
    elif st.session_state["modo"] == "comprobacion":
        st.subheader("📋 Informe de Validación (Solo Lectura)")
        st.info("Se han detectado errores sin modificar el documento original.")

    # Botones de Informe (Comunes a ambos modos)
    ruta_txt = os.path.join(OUTPUT_FOLDER, f"MUESTRAS_CAMBIO_{nombre_base}.txt")
    if os.path.exists(ruta_txt):
        with open(ruta_txt, "r", encoding="utf-8") as f:
            st.download_button("📄 DESCARGAR INFORME DE ERRORES (.txt)", f.read(), file_name=f"validación_{nombre_base}.txt", use_container_width=True)
    else:
        st.warning("No se encontraron errores significativos o el informe no se generó.")

