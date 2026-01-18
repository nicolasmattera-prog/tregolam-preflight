import streamlit as st
import os
import time

# --- 1. CONEXIÓN CON TU LÓGICA ---
# Intentamos importar tu función. Si falla, mostramos un aviso claro.
try:
    from precorreccion import corregir_bloque
    motor_listo = True
except ImportError as e:
    motor_listo = False
    error_msg = str(e)

# --- 2. CONFIGURACIÓN VISUAL (ESTILO PREMIUM) ---
st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋", layout="wide")

st.markdown("""
    <style>
    /* Fondo oscuro y degradado */
    .stApp {
        background: radial-gradient(circle at top right, #001f3f, #050505);
        color: white;
    }
    
    /* Botones principales en azul Tregolam */
    .stButton > button {
        background: linear-gradient(90deg, #00AEEF, #0054A6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        height: 50px;
        width: 100%;
        font-weight: bold;
    }

    /* Caja de estado estilo consola */
    .console-box {
        background-color: #000000;
        color: #00ffcc;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #00AEEF;
        font-family: 'Courier New', monospace;
        min-height: 150px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ESTRUCTURA DE LA INTERFAZ ---
st.image("isologo tregolma prefligth.png", width=200)
st.title("🐋 Tregolam Preflight")

if not motor_listo:
    st.error(f"⚠️ No se pudo cargar el motor de IA. Revisa que 'precorreccion.py' esté en GitHub. Error: {error_msg}")
    st.stop()

col_izq, col_der = st.columns([2, 1], gap="large")

with col_izq:
    st.subheader("📁 Carga de Manuscrito")
    archivo = st.file_uploader("Arrastra tu archivo .docx aquí", type=["docx"])
    
    # Cuadro de estado dinámico
    placeholder_consola = st.empty()
    placeholder_consola.markdown('<div class="console-box">SISTEMA LISTO<br>> Esperando archivo del usuario...</div>', unsafe_allow_html=True)

with col_der:
    st.subheader("⚙️ Panel de Control")
    genero = st.selectbox("Género literario", ["Texto General", "Novela", "Ensayo", "Poesía"])
    
    # BOTÓN DE ACCIÓN
    if st.button("🚀 INICIAR CORRECCIÓN"):
        if archivo is not None:
            placeholder_consola.markdown('<div class="console-box">PROCESANDO...<br>> Leyendo documento docx...<br>> Conectando con OpenAI GPT-4o...<br>> Esto puede tardar unos minutos según la extensión.</div>', unsafe_allow_html=True)
            
            try:
                # Guardamos el archivo subido de forma temporal
                nombre_temp = "input_temp.docx"
                with open(nombre_temp, "wb") as f:
                    f.write(archivo.getbuffer())
                
                # EJECUCIÓN DE TU LÓGICA (Corregido a 1 solo argumento)
                # Tu función corregir_bloque procesará 'input_temp.docx'
                corregir_bloque(nombre_temp)
                
                placeholder_consola.markdown('<div class="console-box" style="color:#00ff00;">¡FINALIZADO!<br>> El documento ha sido procesado con éxito.</div>', unsafe_allow_html=True)
                st.balloons()
                
                # BOTÓN DE DESCARGA (Se activa al terminar)
                # Nota: Asegúrate de que tu script genera un archivo llamado 'corregido.docx' 
                # o cambia el nombre abajo al que use tu script.
                if os.path.exists("corregido.docx"):
                    with open("corregido.docx", "rb") as file:
                        st.download_button(
                            label="📥 DESCARGAR RESULTADO",
                            data=file,
                            file_name=f"Tregolam_Preflight_{archivo.name}",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.warning("El proceso terminó pero no se encontró el archivo de salida. Revisa el nombre en tu script.")
                    
            except Exception as e:
                placeholder_consola.markdown(f'<div class="console-box" style="color:red;">ERROR EN PROCESO:<br>> {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Por favor, sube un archivo antes de empezar.")

    st.button("📋 GENERAR INFORME (BETA)")
    st.divider()
    st.button("🛑 DETENER PROCESO", type="secondary")
