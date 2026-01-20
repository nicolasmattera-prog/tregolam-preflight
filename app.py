import streamlit as st
import os
import sys

# 1. Configuración de rutas para encontrar la carpeta 'scripts'
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))

# 2. Importación de tus herramientas (ahora dentro de scripts/)
import precorreccion
import comprobacion

st.set_page_config(page_title="Auditoría Tregolam", layout="centered")
st.title("🔍 Auditoría Ortotipográfica")

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu manuscrito (.docx)", type="docx")

if uploaded_file:
    # Guardamos el archivo físicamente en la carpeta 'entrada'
    ruta_entrada = os.path.join("entrada", uploaded_file.name)
    with open(ruta_entrada, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.info(f"Archivo cargado: {uploaded_file.name}")
    
    col1, col2 = st.columns(2)

    # --- BOTÓN 1: PRECORRECCIÓN ---
    with col1:
        if st.button("✨ Ejecutar Precorrección"):
            with st.spinner("Limpiando espacios y formatos..."):
                # Llamada al archivo en scripts/precorreccion.py
                resultado = precorreccion.ejecutar_precorreccion(uploaded_file.name)
                if "ERROR" in resultado:
                    st.error(resultado)
                else:
                    st.success("¡Limpieza completada!")
                    st.write(resultado)

    # --- BOTÓN 2: COMPROBACIÓN (IA) ---
    with col2:
        if st.button("🤖 Ejecutar Auditoría"):
            with st.spinner("Analizando con Inteligencia Artificial..."):
                # Llamada al archivo en scripts/comprobacion.py
                nombre_informe = comprobacion.comprobar_archivo(uploaded_file.name)
                
                if "ERROR" in nombre_informe:
                    st.error(nombre_informe)
                else:
                    ruta_salida = os.path.join("salida", nombre_informe)
                    # Ofrecer la descarga del informe generado
                    with open(ruta_salida, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Informe",
                            data=f,
                            file_name=nombre_informe,
                            mime="text/plain"
                        )
                    st.success("Auditoría finalizada.")
