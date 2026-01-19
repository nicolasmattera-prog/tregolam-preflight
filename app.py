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

# 1. Definición de rutas absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")

# 2. Sincronización de carpetas con los módulos externos
# Esto asegura que precorreccion y auditar miren a las mismas carpetas que app.py
for modulo in [precorreccion, auditar]:
    modulo.INPUT_FOLDER = INPUT_FOLDER
    modulo.OUTPUT_FOLDER = OUTPUT_FOLDER

# Crear carpetas si no existen (aunque ya las creaste en GitHub con .gitkeep)
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

if "corregido" not in st.session_state:
    st.session_state["corregido"] = None

# Interfaz de subida
archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if not archivo:
        st.warning("Por favor, sube un archivo primero.")
    else:
        try:
            # Limpiar archivos previos para evitar confusiones
            for f in os.listdir(INPUT_FOLDER):
                if f != ".gitkeep":
                    try: os.remove(os.path.join(INPUT_FOLDER, f))
                    except: pass
            
            # Guardar el archivo subido en la carpeta de entrada
            ruta_entrada = os.path.join(INPUT_FOLDER, archivo.name)
            with open(ruta_entrada, "wb") as f:
                f.write(archivo.getbuffer())

            with st.status("Procesando documento...") as status:
                # Ejecutar el motor de corrección
                precorreccion.procesar_archivo(archivo.name)
                time.sleep(1) # Pausa de seguridad para el sistema de archivos
                
                nombre_salida = archivo.name.replace(".docx", "_CORREGIDO.docx")
                ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_salida)

                if os.path.exists(ruta_salida):
                    st.session_state["corregido"] = archivo.name
                    status.update(label="✅ ¡Documento listo!", state="complete")
                    
                    with open(ruta_salida, "rb") as f:
                        st.download_button(
                            label="📥 DESCARGAR DOCX CORREGIDO",
                            data=f,
                            file_name=nombre_salida,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("Error: El archivo corregido no se encontró en la carpeta de salida.")

        except Exception as e:
            st.error(f"Error técnico en el proceso: {e}")
            st.code(traceback.format_exc())

# --- SECCIÓN DEL INFORME (.txt) ---
if st.session_state["corregido"]:
    st.divider()
    st.subheader("📋 Informe de cambios")
    try:
        # Intentamos detectar la función correcta dinámicamente
        # Probamos los nombres más comunes si el estándar falla
        func_informe = None
        for nombre in ['generar_informe_txt', 'generar_informe', 'crear_informe', 'generar_auditoria']:
            if hasattr(auditar, nombre):
                func_informe = getattr(auditar, nombre)
                break
        
        if func_informe:
            contenido_txt = func_informe(st.session_state["corregido"])
            st.download_button(
                label="📄 DESCARGAR INFORME (.txt)",
                data=contenido_txt,
                file_name=f"informe_{st.session_state['corregido']}.txt",
                mime="text/plain"
            )
        else:
            st.error("No se encontró la función de informe en auditar.py. Revisa el nombre de la función.")
            
    except Exception as e:
        st.error(f"Error al generar el archivo de texto: {e}")
