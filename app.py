import streamlit as st
import os
import shutil
import precorreccion
import traceback
import auditar  # <-- nuevo

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# 1. Crear estructura de carpetas que requiere tu script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if archivo:
        # Limpiar carpetas de intentos previos
        shutil.rmtree(INPUT_FOLDER)
        os.makedirs(INPUT_FOLDER)
        shutil.rmtree(OUTPUT_FOLDER)
        os.makedirs(OUTPUT_FOLDER)

        # 2. Guardar el archivo donde tu script lo espera (carpeta entrada)
        ruta_entrada = os.path.join(INPUT_FOLDER, archivo.name)
        with open(ruta_entrada, "wb") as f:
            f.write(archivo.getbuffer())

        with st.status("Ejecutando corrección quirúrgica...", expanded=True) as status:
            try:
                # 3. Lanzar la función principal de TU script
                precorreccion.procesar_archivo(archivo.name)

                # 4. Buscar el resultado en la carpeta 'salida'
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

                    # --- BOTÓN OPCIONAL: DESCARGAR INFORME ---
                    if st.button("📄 Descargar informe de correcciones"):
                        informe = auditar.generar_informe_txt(archivo.name)
                        nombre_informe = archivo.name.replace(".docx", "_INFORME.txt")
                        st.download_button(
                            label="📥 DESCARGAR INFORME",
                            data=informe,
                            file_name=nombre_informe,
                            mime="text/plain"
                        )

                else:
                    st.error("El proceso terminó pero no se encontró el archivo en la carpeta 'salida'.")

            except Exception:
                st.error("Error técnico en la ejecución:")
                st.code(traceback.format_exc())
    else:
        st.warning("Por favor, carga un archivo .docx")
