import streamlit as st
import os
from precorreccion import corregir_bloque # Asegúrate que tu función se llame así

# --- DISEÑO ---
st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋", layout="wide")
st.markdown("""<style>.stApp { background: radial-gradient(circle at top right, #001f3f, #050505); color: white; }</style>""", unsafe_allow_html=True)

st.title("🐋 Tregolam Preflight")

col1, col2 = st.columns([2, 1])

with col1:
    archivo = st.file_uploader("Sube tu manuscrito (.docx)", type=["docx"])
    consola = st.empty()
    consola.info("Esperando archivo...")

with col2:
    if st.button("🚀 CORREGIR"):
        if archivo is not None:
            consola.warning("⚙️ Procesando con IA... Por favor, no cierres la pestaña.")
            
            # 1. GUARDAR ARCHIVO TEMPORAL
            with open("temp.docx", "wb") as f:
                f.write(archivo.getbuffer())
            
            # 2. EJECUTAR TU LÓGICA (Aquí es donde 'trabaja')
            try:
                # IMPORTANTE: Aquí llamamos a tu función de precorreccion.py
                # Ajusta el nombre de la función si en tu archivo es distinto
                resultado_path = "manuscrito_corregido.docx" 
                
                # Ejemplo de llamada (ajusta según tus parámetros reales):
                corregir_bloque("temp.docx", resultado_path) 
                
                consola.success("✅ ¡Corrección finalizada con éxito!")
                
                # 3. MOSTRAR BOTÓN DE DESCARGA
                with open(resultado_path, "rb") as file:
                    st.download_button(
                        label="📥 DESCARGAR ARCHIVO CORREGIDO",
                        data=file,
                        file_name="Tregolam_Corregido.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                consola.error(f"Error durante el proceso: {e}")
        else:
            st.error("Sube un archivo primero.")
