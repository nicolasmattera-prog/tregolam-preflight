import streamlit as st
import os
import sys
import pandas as pd
import time

# 1. Configuración de página
st.set_page_config(page_title="Auditoría Tregolam", layout="wide")

# Rutas para scripts
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(BASE_PATH, "scripts")
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

import precorreccion
import comprobacion

st.title("🔍 Panel de Control: Auditoría Ortotipográfica")

# Evitar errores de ID con llaves únicas
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 100

uploaded_file = st.file_uploader("Sube tu manuscrito (.docx)", type="docx", key=st.session_state.uploader_key)

if uploaded_file:
    ruta_entrada = os.path.join("entrada", uploaded_file.name)
    os.makedirs("entrada", exist_ok=True)
    os.makedirs("salida", exist_ok=True)
    
    with open(ruta_entrada, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✨ 1. Ejecutar Precorrección", key="btn_p"):
            with st.spinner("Limpiando..."):
                st.success(precorreccion.ejecutar_precorreccion(uploaded_file.name))

    with col2:
        if st.button("🤖 2. Iniciar Auditoría IA", key="btn_i"):
            nombre_inf = f"Informe_{uploaded_file.name.replace('.docx', '.txt')}"
            st.session_state['informe_actual'] = nombre_inf
            
            with st.spinner("Analizando con IA..."):
                # Ejecutamos y forzamos refresco al terminar
                comprobacion.comprobar_archivo(uploaded_file.name)
                st.rerun()

    # --- ZONA DE RENDERIZADO (OPTIMIZADA) ---
    if 'informe_actual' in st.session_state:
        ruta_txt = os.path.join("salida", st.session_state['informe_actual'])
        
        if os.path.exists(ruta_txt):
            datos = []
            try:
                # Leemos el archivo de una sola vez
                with open(ruta_txt, "r", encoding="utf-8") as f:
                    contenido = f.readlines()
                
                for line in contenido:
                    if "|" in line:
                        partes = [p.strip() for p in line.split("|")]
                        if len(partes) >= 5:
                            datos.append({
                                "Categoría": partes[0].replace("[","").replace("]",""),
                                "ID": partes[1],
                                "Original": partes[2],
                                "Sugerencia": partes[3],
                                "Motivo": partes[4]
                            })

                if datos:
                    df = pd.DataFrame(datos)

                    # Función de renderizado para evitar repeticiones
                    def render_seccion(titulo, filtro, emoji, clave):
                        st.subheader(f"{emoji} {titulo}")
                        mask = df["Categoría"].str.contains(filtro, case=False, na=False)
                        df_sub = df[mask].copy()
                        
                        if not df_sub.empty:
                            # APLICAR NEGRITA VISUAL REAL
                            styled = df_sub.style.map(lambda x: 'font-weight: bold;', subset=['Original'])
                            st.dataframe(styled, use_container_width=True, hide_index=True, key=f"t_{clave}")
                        else:
                            st.write("✅ Todo correcto.")

                    render_seccion("ERRORES ORTOGRÁFICOS", "ORTOGRAFIA|ORTOGRAFÍA", "🔴", "o")
                    render_seccion("ERRORES DE FORMATO", "FORMATO", "🟡", "f")
                    render_seccion("SUGERENCIAS Y ESTILO", "SUGERENCIA", "🟢", "s")
                    
                    st.divider()
                    with open(ruta_txt, "rb") as f:
                        st.download_button("📥 Descargar TXT", f, file_name=st.session_state['informe_actual'], key="dl")
                else:
                    st.info("Generando informe... por favor, espera unos segundos.")
                    time.sleep(2)
                    st.rerun()
            except:
                st.warning("Leyendo datos...")
