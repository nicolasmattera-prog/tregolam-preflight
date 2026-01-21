import streamlit as st
import os
import sys
import pandas as pd
import time

# 1. Configuración de página (Debe ser lo primero)
st.set_page_config(page_title="Auditoría Tregolam", layout="wide")

# Rutas para scripts
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(BASE_PATH, "scripts")
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

try:
    import precorreccion
    import comprobacion
except ImportError:
    st.error("No se encontraron los scripts en la carpeta /scripts")

st.title("🔍 Panel de Control: Auditoría Ortotipográfica")

# SOLUCIÓN DUPLICADOS: Clave fija para el uploader
uploaded_file = st.file_uploader("Sube tu manuscrito (.docx)", type="docx", key="main_uploader_unique")

if uploaded_file:
    ruta_entrada = os.path.join("entrada", uploaded_file.name)
    os.makedirs("entrada", exist_ok=True)
    os.makedirs("salida", exist_ok=True)
    
    with open(ruta_entrada, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✨ 1. Ejecutar Precorrección", key="btn_precorr_fixed"):
            with st.spinner("Limpiando..."):
                st.success(precorreccion.ejecutar_precorreccion(uploaded_file.name))

    with col2:
        if st.button("🤖 2. Iniciar Auditoría IA", key="btn_ia_fixed"):
            st.session_state['informe_actual'] = f"Informe_{uploaded_file.name.replace('.docx', '.txt')}"
            with st.spinner("Analizando con IA... esto puede tardar un minuto"):
                comprobacion.comprobar_archivo(uploaded_file.name)
                st.rerun()

    # --- ZONA DE RENDERIZADO (UNIFICADA) ---
    if 'informe_actual' in st.session_state:
        ruta_txt = os.path.join("salida", st.session_state['informe_actual'])
        
        if os.path.exists(ruta_txt):
            datos = []
            try:
                # Leemos todo de golpe para no bloquear el archivo
                with open(ruta_txt, "r", encoding="utf-8") as f:
                    lineas = f.readlines()
                
                for line in lineas:
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

                    def render_final(titulo, filtro, emoji, key_table):
                        st.subheader(f"{emoji} {titulo}")
                        mask = df["Categoría"].str.contains(filtro, case=False, na=False)
                        df_view = df[mask].copy()
                        
                        if not df_view.empty:
                            # Negritas reales vía Styler
                            st.dataframe(
                                df_view.style.map(lambda x: 'font-weight: bold;', subset=['Original']),
                                width="stretch", # Actualizado según el log
                                hide_index=True,
                                key=f"table_{key_table}"
                            )
                        else:
                            st.write("✅ Sin errores.")

                    render_final("ERRORES ORTOGRÁFICOS", "ORTOGRAFIA|ORTOGRAFÍA", "🔴", "orto")
                    render_final("ERRORES DE FORMATO", "FORMATO", "🟡", "form")
                    render_final("SUGERENCIAS Y ESTILO", "SUGERENCIA", "🟢", "sug")
                    
                    st.divider()
                    with open(ruta_txt, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Informe",
                            data=f,
                            file_name=st.session_state['informe_actual'],
                            mime="text/plain",
                            key="download_btn_final" # KEY FIJA
                        )
                else:
                    st.info("Procesando resultados... espera un momento.")
                    time.sleep(3)
                    st.rerun()
            except Exception as e:
                st.info("Cargando informe...")
