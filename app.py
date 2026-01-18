import streamlit as st
import os
import time
import precorreccion

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

archivo = st.file_uploader("Sube tu manuscrito", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if archivo:
        # 1. Guardar la entrada
        with open("entrada.docx", "wb") as f:
            f.write(archivo.getbuffer())
        
        with st.status("IA trabajando... analizando archivos", expanded=True) as status:
            # Capturamos qué archivos hay ANTES de empezar
            archivos_antes = set(os.listdir('.'))
            
            # 2. Ejecutar tu lógica
            os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
            precorreccion.corregir_bloque("entrada.docx")
            
            # Pausa para que el disco escriba el archivo
            time.sleep(3)
            
            # 3. Capturamos qué archivos hay DESPUÉS
            archivos_despues = set(os.listdir('.'))
            
            # Diferencia: ¿Qué archivo nuevo ha aparecido?
            nuevos = list(archivos_despues - archivos_antes)
            
            # También buscamos por extensión por si acaso
            todos_docx = [f for f in os.listdir('.') if f.endswith('.docx') and f != "entrada.docx"]

            if nuevos:
                # Si hay un archivo nuevo, lo priorizamos
                archivo_final = nuevos[0]
                status.update(label=f"✅ ¡Logrado! Detectado: {archivo_final}", state="complete")
                with open(archivo_final, "rb") as f:
                    st.download_button("📥 DESCARGAR RESULTADO", f, file_name=f"Corregido_{archivo.name}")
            
            elif todos_docx:
                # Si no es nuevo pero hay un .docx que no es la entrada
                archivo_final = todos_docx[0]
                status.update(label=f"✅ ¡Encontrado! Archivo: {archivo_final}", state="complete")
                with open(archivo_final, "rb") as f:
                    st.download_button("📥 DESCARGAR RESULTADO", f, file_name=f"Corregido_{archivo.name}")
            
            else:
                st.error("❌ El motor terminó pero no creó ningún archivo .docx nuevo en la carpeta principal.")
                st.write("Archivos actuales en el servidor:", os.listdir('.'))
                st.info("💡 Consejo: Asegúrate de que en 'precorreccion.py' guardas el archivo usando una ruta relativa como 'resultado.docx' y no una ruta absoluta de tu ordenador C:/Users/...")

    else:
        st.warning("Sube un archivo primero.")
