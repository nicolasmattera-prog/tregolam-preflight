import streamlit as st
import os
import sys
import importlib

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋", layout="wide")
st.markdown("""<style>.stApp { background: #000; color: white; } .stButton>button { background: #00AEEF !important; }</style>""", unsafe_allow_html=True)

st.image("https://tregolam.com/wp-content/uploads/2021/01/logo-tregolam.png", width=200) # Backup del logo
st.title("🐋 Tregolam Preflight")

# --- CONEXIÓN DINÁMICA ---
try:
    import precorreccion
    importlib.reload(precorreccion) # Forzamos que lea los cambios de GitHub
    motor_listo = True
except Exception as e:
    st.error(f"Error de conexión: {e}")
    motor_listo = False

archivo = st.file_uploader("Sube tu manuscrito .docx", type=["docx"])

if st.button("🚀 INICIAR CORRECCIÓN"):
    if not archivo:
        st.warning("Primero sube un archivo.")
    elif not motor_listo:
        st.error("El motor de corrección no está cargado.")
    else:
        with st.spinner("IA trabajando... por favor espera."):
            try:
                # 1. Creamos el archivo de entrada
                with open("entrada.docx", "wb") as f:
                    f.write(archivo.getbuffer())
                
                # 2. Intentamos todas las formas posibles de llamar a tu función
                # Probamos con 'corregir_bloque' que es lo estándar en tu repo
                if hasattr(precorreccion, 'corregir_bloque'):
                    precorreccion.corregir_bloque("entrada.docx")
                else:
                    # Si tu función se llama distinto, esto nos dirá qué funciones hay
                    funciones_disponibles = [f for f in dir(precorreccion) if not f.startswith('_')]
                    st.error(f"No encuentro la función 'corregir_bloque'. En tu archivo existen: {funciones_disponibles}")
                    st.stop()

                # 3. BUSCAR EL RESULTADO
                # Miramos qué archivos .docx hay ahora en la carpeta
                ficheros = [f for f in os.listdir('.') if f.endswith('.docx') and f != "entrada.docx"]
                
                if ficheros:
                    st.success("¡Corrección finalizada!")
                    with open(ficheros[0], "rb") as f:
                        st.download_button("📥 DESCARGAR ARCHIVO CORREGIDO", f, file_name=f"Corregido_{archivo.name}")
                else:
                    st.error("El proceso terminó pero no se generó ningún archivo nuevo. Revisa los logs.")

            except Exception as e:
                st.exception(e) # Esto nos dará el error exacto de Python
