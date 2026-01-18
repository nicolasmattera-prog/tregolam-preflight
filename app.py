import streamlit as st
import os
import time

# --- 1. CONEXIÓN CON TU LÓGICA ---
try:
    from precorreccion import corregir_bloque
    motor_listo = True
except ImportError as e:
    motor_listo = False
    error_msg = str(e)

# --- 2. CONFIGURACIÓN VISUAL (ESTILO PREMIUM TREGOLAM) ---
st.set_page_config(page_title="Tregolam Preflight", page_icon="🐋", layout="wide")

st.markdown("""
    <style>
    /* Fondo oscuro y degradado tecnológico */
    .stApp {
        background: radial-gradient(circle at top right, #001f3f, #050505);
        color: white;
    }
    
    /* Botones con los colores de la marca */
    .stButton > button {
        background: linear-gradient(90deg, #00AEEF, #0054A6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        height: 55px;
        width: 100%;
        font-weight: bold;
        font-size: 16px;
        text-transform: uppercase;
        transition: 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0px 0px 15px rgba(0, 174, 239, 0.6);
        transform: translateY(-2px);
    }

    /* Caja de estado estilo Terminal/Consola */
    .console-box {
        background-color: #000000;
        color: #00ffcc;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #00AEEF;
        font-family: 'Courier New', monospace;
        min-height: 180px;
        margin-top: 10px;
        line-height: 1.5;
    }
    
    /* Estilo para los inputs */
    div[data-testid="stFileUploadDropzone"] {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed #00AEEF;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ENCABEZADO ---
# Asegúrate de que el nombre del logo coincida con el de tu GitHub
if os.path.exists("isologo tregolma prefligth.png"):
    st.image("isologo tregolma prefligth.png", width=220)
st.title("🐋 Tregolam Preflight")
st.write("---")

if not motor_listo:
    st.error(f"⚠️ Error: No se pudo conectar con 'precorreccion.py'. Detalles: {error_msg}")
    st.stop()

# --- 4. DISEÑO DE COLUMNAS (TU CROQUIS) ---
col_izq, col_der = st.columns([2, 1], gap="large")

with col_izq:
    st.subheader("📁 Carga de Documento")
    archivo = st.file_uploader("Sube el manuscrito en formato .docx", type=["docx"])
    
    # Cuadro de estado dinámico
    placeholder_consola = st.empty()
    placeholder_consola.markdown('<div class="console-box">SISTEMA INICIALIZADO...<br>> Esperando carga de archivo...</div>', unsafe_allow_html=True)

with col_der:
    st.subheader("⚙️ Panel de Control")
    genero = st.selectbox("Selecciona el Género", ["Texto General", "Novela", "Ensayo", "Poesía"])
    
    # Botón Principal de Acción
    if st.button("🚀 INICIAR CORRECCIÓN"):
        if archivo is not None:
            placeholder_consola.markdown('<div class="console-box">INICIANDO MOTOR DE IA...<br>> Leyendo documento...<br>> Ejecutando corrección ortotipográfica...<br>> Por favor, no cierres esta ventana.</div>', unsafe_allow_html=True)
            
            try:
                # 1. Guardar archivo temporalmente para que la función lo lea
                nombre_temp = "entrada_temp.docx"
                with open(nombre_temp, "wb") as f:
                    f.write(archivo.getbuffer())
                
                # Registramos el tiempo de inicio
                inicio = time.time()
                
                # 2. LLAMADA A TU LÓGICA (1 solo argumento como pide tu función)
                corregir_bloque(nombre_temp)
                
                fin = time.time()
                tiempo_total = round(fin - inicio, 2)
                
                # 3. DETECTAR EL ARCHIVO DE SALIDA
                # Buscamos cualquier .docx nuevo que no sea el de entrada
                archivos_docx = [f for f in os.listdir('.') if f.endswith('.docx') and f != nombre_temp]
                
                if archivos_docx:
                    # Suponemos que el último archivo creado es el corregido
                    nombre_resultado = archivos_docx[-1] 
                    
                    placeholder_consola.markdown(f'<div class="console-box" style="color:#00ff00;">¡PROCESO COMPLETADO!<br>> Tiempo: {tiempo_total} seg.<br>> Archivo generado: {nombre_resultado}<br>> Ya puede descargar el resultado.</div>', unsafe_allow_html=True)
                    st.balloons()
                    
                    # Mostrar botón de descarga con el archivo encontrado
                    with open(nombre_resultado, "rb") as file:
                        st.download_button(
                            label="📥 DESCARGAR MANUSCRITO CORREGIDO",
                            data=file,
                            file_name=f"Tregolam_Preflight_{archivo.name}",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    placeholder_consola.markdown('<div class="console-box" style="color:#ffcc00;">ADVERTENCIA:<br>> El proceso terminó pero no se detectó el archivo de salida.<br>> Revisa que tu función guarde el archivo correctamente.</div>', unsafe_allow_html=True)
            
            except Exception as e:
                placeholder_consola.markdown(f'<div class="console-box" style="color:#ff4b4b;">ERROR CRÍTICO DURANTE EL PROCESO:<br>> {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Primero debes subir un archivo .docx.")

    # Otros botones (Beta)
    st.button("📋 GENERAR INFORME DETALLADO")
    st.button("🔍 ANÁLISIS DE ESTILO")
    st.divider()
    st.button("🛑 CANCELAR", type="secondary")
