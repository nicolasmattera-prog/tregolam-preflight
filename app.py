import streamlit as st
import os
import traceback
import time

# Configuración de página
st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# Intentar importar el motor
try:
    import precorreccion
    motor_cargado = True
except Exception as e:
    st.error(f"Error cargando el archivo precorreccion.py: {e}")
    motor_cargado = False

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if not archivo:
        st.warning("Sube un archivo primero.")
    elif not motor_cargado:
        st.error("El motor no está disponible.")
    else:
        # Limpiar restos anteriores
        if os.path.exists("resultado_final.docx"):
            os.remove("resultado_final.docx")

        # 1. Guardar archivo de entrada
        with open("entrada.docx", "wb") as f:
            f.write(archivo.getbuffer())
        
        with st.status("Procesando con IA...", expanded=True) as status:
            try:
                # 2. Ejecutar
                st.write("Ejecutando lógica de corrección...")
                precorreccion.corregir_bloque("entrada.docx")
                
                # Espera de escritura
                time.sleep(2)
                
                # 3. Verificar salida
                if os.path.exists("resultado_final.docx"):
                    status.update(label="✅ ¡CORRECCIÓN TERMINADA!", state="complete")
                    with open("resultado_final.docx", "rb") as f:
                        st.download_button(
                            label="📥 DESCARGAR RESULTADO",
                            data=f,
                            file_name=f"Corregido_{archivo.name}",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("El proceso terminó pero el archivo de salida no aparece en el servidor.")
                    st.write("Archivos detectados:", os.listdir('.'))
            
            except Exception:
                st.error("Se produjo un error durante la corrección:")
                st.code(traceback.format_exc()) # Esto te dirá la línea exacta del fallo
