import streamlit as st
import os
import time
import glob

# --- 1. CONEXIÓN ---
try:
    import precorreccion
    motor_listo = True
except Exception as e:
    st.error(f"Error al cargar precorreccion.py: {e}")
    motor_listo = False

# --- 2. DISEÑO ---
st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋", layout="wide")
st.markdown("""<style>.stApp { background: #050505; color: white; } .stButton>button { background: #00AEEF !important; color: white !important; }</style>""", unsafe_allow_html=True)

st.title("🐋 Tregolam Preflight")

# --- 3. LÓGICA ---
archivo = st.file_uploader("Sube tu .docx", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if archivo and motor_listo:
        # Limpiamos rastros de intentos anteriores
        for f in glob.glob("*.docx"):
            if f != "entrada.docx": os.remove(f)
            
        with st.status("Ejecutando corrección... (No cierres esta pestaña)", expanded=True) as status:
            try:
                # Guardamos el archivo
                with open("entrada.docx", "wb") as f:
                    f.write(archivo.getbuffer())
                
                # LLAMADA A TU FUNCIÓN
                # Usamos getattr por si hay dudas con el nombre
                precorreccion.corregir_bloque("entrada.docx")
                
                # Pausa de seguridad para que el servidor termine de escribir el disco
                time.sleep(3)
                
                # BUSCAR EL RESULTADO (Cualquier docx que no sea la entrada)
                resultados = [f for f in os.listdir('.') if f.endswith('.docx') and f != "entrada.docx"]
                
                if resultados:
                    status.update(label="✅ ¡Completado!", state="complete")
                    archivo_final = resultados[0]
                    with open(archivo_final, "rb") as f:
                        st.download_button("📥 DESCARGAR RESULTADO", f, file_name=f"Corregido_{archivo.name}")
                else:
                    st.error("El proceso terminó pero no se creó el archivo. Puede ser un error interno de OpenAI o de permisos de escritura.")
            except Exception as e:
                st.error(f"Error en la ejecución: {e}")
    else:
        st.warning("Asegúrate de haber subido un archivo.")
