import streamlit as st
import os
import time
import precorreccion

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if archivo:
        # 1. Guardar la entrada
        with open("entrada.docx", "wb") as f:
            f.write(archivo.getbuffer())
        
        with st.status("IA trabajando... analizando archivos", expanded=True) as status:
            try:
                # 2. Ejecutar la lógica
                st.write("Conectando con el motor...")
                precorreccion.corregir_bloque("entrada.docx")
                
                # 3. Esperar un poco a que el servidor suelte el archivo
                time.sleep(3)
                
                # 4. Verificar si el archivo existe
                if os.path.exists("resultado_final.docx"):
                    status.update(label="✅ ¡CORRECCIÓN COMPLETADA!", state="complete")
                    with open("resultado_final.docx", "rb") as f:
                        st.download_button(
                            label="📥 DESCARGAR MANUSCRITO CORREGIDO",
                            data=f,
                            file_name=f"Corregido_{archivo.name}",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("No se encontró el archivo 'resultado_final.docx' después de la ejecución.")
                    st.write("Archivos actuales:", os.listdir('.'))
            except Exception as e:
                st.error(f"Error en el motor: {e}")
    else:
        st.warning("Primero sube un archivo.")
