import streamlit as st
import os
import time
import precorreccion

st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋")
st.title("🐋 Tregolam Preflight")

# Panel lateral de estado para estar seguros
with st.sidebar:
    st.subheader("Estado del Sistema")
    if os.path.exists("precorreccion.py"):
        st.success("✅ Motor detectado")
    if "OPENAI_API_KEY" in st.secrets:
        st.success("✅ API Key lista")

archivo = st.file_uploader("Sube tu manuscrito", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if archivo:
        # 1. Limpieza de archivos previos para evitar confusiones
        for f in os.listdir('.'):
            if f.endswith(".docx") and f != "entrada.docx":
                try: os.remove(f)
                except: pass

        with st.status("Ejecutando motor de IA...", expanded=True) as status:
            # 2. Guardar el archivo de entrada
            with open("entrada.docx", "wb") as f:
                f.write(archivo.getbuffer())
            st.write(">> Archivo cargado correctamente...")

            try:
                # 3. Forzar la API Key en el entorno
                os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
                
                # 4. Llamada a tu script
                st.write(">> Conectando con OpenAI y procesando bloques...")
                precorreccion.corregir_bloque("entrada.docx")
                
                # Pausa técnica para que el servidor refresque el disco
                time.sleep(2)
                
                # 5. Buscar CUALQUIER .docx que no sea la entrada
                ficheros_luego = [f for f in os.listdir('.') if f.endswith('.docx') and f != "entrada.docx"]
                
                if ficheros_luego:
                    status.update(label="✅ ¡Corrección terminada!", state="complete")
                    archivo_final = ficheros_luego[0]
                    with open(archivo_final, "rb") as f:
                        st.download_button(
                            label="📥 DESCARGAR MANUSCRITO CORREGIDO",
                            data=f,
                            file_name=f"Corregido_{archivo.name}",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("El proceso terminó pero no se generó ningún archivo de salida. Revisa si tu script guarda el archivo en una subcarpeta.")
            
            except Exception as e:
                st.error(f"Error crítico en el motor: {str(e)}")
    else:
        st.warning("Sube un archivo primero.")
