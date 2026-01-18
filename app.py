import streamlit as st
import os
import precorreccion
import traceback
import time

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

archivo = st.file_uploader("Sube el manuscrito (.docx)", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if archivo:
        # Limpieza de archivos viejos
        if os.path.exists("resultado_final.docx"):
            os.remove("resultado_final.docx")
            
        # Guardar archivo que subes
        with open("entrada.docx", "wb") as f:
            f.write(archivo.getbuffer())
        
        with st.status("Procesando...", expanded=True) as status:
            try:
                # Llamamos al motor que está en el otro archivo
                precorreccion.corregir_bloque("entrada.docx")
                time.sleep(2) # Espera técnica
                
                if os.path.exists("resultado_final.docx"):
                    status.update(label="✅ ¡TERMINADO!", state="complete")
                    with open("resultado_final.docx", "rb") as f:
                        st.download_button("📥 DESCARGAR RESULTADO", f, file_name="corregido.docx")
                else:
                    st.error("El motor no generó el archivo de salida.")
            
            except Exception:
                st.error("Error detectado:")
                st.code(traceback.format_exc())
    else:
        st.warning("Por favor, sube un archivo.")
