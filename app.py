import streamlit as st
import os
import sys
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Auditoría Tregolam", layout="wide")

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "scripts"))
import precorreccion
import comprobacion

st.title("🔍 Panel de Control: Auditoría Ortotipográfica")

# --- LÓGICA DE CONTROL DE ESTADO ---
# Inicializamos variables si no existen
if 'procesando' not in st.session_state:
    st.session_state['procesando'] = False
if 'ultimo_fichero' not in st.session_state:
    st.session_state['ultimo_fichero'] = None

# 2. Subida de archivo
uploaded_file = st.file_uploader("Sube tu manuscrito (.docx)", type="docx", key="uploader_final")

if uploaded_file:
    # Si el usuario sube un archivo distinto, reseteamos todo el estado
    if st.session_state['ultimo_fichero'] != uploaded_file.name:
        st.session_state['ultimo_fichero'] = uploaded_file.name
        st.session_state['procesando'] = False
        if 'informe_actual' in st.session_state:
            del st.session_state['informe_actual']

    ruta_entrada = os.path.join("entrada", uploaded_file.name)
    os.makedirs("entrada", exist_ok=True)
    os.makedirs("salida", exist_ok=True)
    
    with open(ruta_entrada, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✨ 1. Ejecutar Precorrección", key="btn_pre"):
            with st.spinner("Limpiando..."):
                res = precorreccion.ejecutar_precorreccion(uploaded_file.name)
                st.success(res)

    with col2:
        if st.button("🤖 2. Iniciar Auditoría IA", key="btn_ia"):
            nombre_txt = f"Informe_{uploaded_file.name.replace('.docx', '.txt')}"
            ruta_txt = os.path.join("salida", nombre_txt)
            
            # BORRAMOS el informe viejo antes de empezar el nuevo
            if os.path.exists(ruta_txt):
                os.remove(ruta_txt)
                
            with st.spinner("Analizando con IA..."):
                comprobacion.comprobar_archivo(uploaded_file.name)
                st.session_state['informe_actual'] = nombre_txt
                st.session_state['procesando'] = True
                st.rerun()

    # --- RENDERIZADO (Solo si se ha pulsado el botón 2 en esta sesión) ---
    if st.session_state.get('procesando') and 'informe_actual' in st.session_state:
        ruta_txt = os.path.join("salida", st.session_state['informe_actual'])
        
        if os.path.exists(ruta_txt):
            datos = []
            with open(ruta_txt, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line:
                        partes = [p.strip() for p in line.split("|")]
                        if len(partes) >= 5:
                            datos.append({
                                "Categoría": partes[0], 
                                "ID": partes[1], 
                                "Original": partes[2], 
                                "Sugerencia": partes[3], 
                                "Motivo": partes[4]
                            })

            if datos:
                df = pd.DataFrame(datos)

                def mostrar_seccion(titulo, filtro, emoji, color_key):
                    st.subheader(f"{emoji} {titulo}")
                    mask = df["Categoría"].str.contains(filtro, case=False, na=False)
                    df_filtrado = df[mask].copy()
                    
                    if not df_filtrado.empty:
                        # Negritas reales sin asteriscos
                        st.dataframe(
                            df_filtrado.style.map(lambda x: 'font-weight: bold;', subset=['Original']),
                            width="stretch", 
                            hide_index=True,
                            key=f"tabla_{color_key}"
                        )
                    else:
                        st.success(f"✅ Sin errores en {titulo.lower()}.")

                mostrar_seccion("ERRORES ORTOGRÁFICOS", "ORTOGRAFIA|ORTOGRAFÍA", "🔴", "roja")
                mostrar_seccion("ERRORES DE FORMATO", "FORMATO", "🟡", "amarilla")
                mostrar_seccion("SUGERENCIAS Y ESTILO", "SUGERENCIA", "🟢", "verde")
                
                st.divider()
                with open(ruta_txt, "rb") as f:
                    st.download_button("📥 Descargar Informe", f, file_name=st.session_state['informe_actual'], key="btn_dl")
