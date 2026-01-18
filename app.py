import streamlit as st
import os
import precorreccion # Tu archivo

st.set_page_config(page_title="Tregolam Debug", layout="wide")
st.title("🐋 Probador de Conexión Tregolam")

archivo = st.file_uploader("Sube un archivo pequeño para probar", type=["docx"])

if st.button("🚀 INICIAR PRUEBA"):
    if archivo:
        log = st.status("Registrando pasos...", expanded=True)
        
        # PASO 1: Guardar
        with open("entrada.docx", "wb") as f:
            f.write(archivo.getbuffer())
        log.write("✅ 1. Archivo 'entrada.docx' guardado en el servidor.")

        # PASO 2: Verificar la Key
        if "OPENAI_API_KEY" in st.secrets:
            log.write("✅ 2. API Key detectada en Secrets.")
            os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        else:
            log.error("❌ 2. No se encuentra la API Key en Secrets.")
            st.stop()

        # PASO 3: Ejecutar tu función
        try:
            log.write("⏳ 3. Llamando a tu función en precorreccion.py...")
            # Aquí es donde el programa suele "quedarse mudo"
            precorreccion.corregir_bloque("entrada.docx") 
            log.write("✅ 4. La función terminó de ejecutarse.")
        except Exception as e:
            log.error(f"❌ Error dentro de tu archivo precorreccion.py: {e}")
            st.stop()

        # PASO 4: Buscar el resultado
        archivos = [f for f in os.listdir('.') if f.endswith('.docx') and f != "entrada.docx"]
        if archivos:
            st.success(f"¡LOGRADO! Archivo encontrado: {archivos[0]}")
            with open(archivos[0], "rb") as f:
                st.download_button("📥 DESCARGAR", f, file_name="resultado.docx")
        else:
            st.warning("⚠️ El código corrió pero no creó ningún archivo nuevo. Revisa si tu script tiene la ruta de guardado fija.")
    else:
        st.info("Sube un archivo para empezar.")
