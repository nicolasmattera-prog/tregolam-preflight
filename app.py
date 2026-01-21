import streamlit as st
import os
import sys
import pandas as pd

# 1. Configuración de página (SIEMPRE AL PRINCIPIO)
st.set_page_config(page_title="Auditoría Tregolam", layout="wide")

# Rutas para scripts
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(BASE_PATH, "scripts")
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

import precorreccion
import comprobacion

st.title("🔍 Panel de Control: Auditoría Ortotipográfica")

# Cargador de archivos con clave única para evitar errores de DuplicateID
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = "docx_uploader"

uploaded_file = st.file_uploader("Sube tu manuscrito (.docx)", type="docx", key=st.session_state.file_uploader_key)

if uploaded_file:
    ruta_entrada = os.path.join("entrada", uploaded_file.name)
    os.makedirs("entrada", exist_ok=True)
    os.makedirs("salida", exist_ok=True)
    
    with open(ruta_entrada, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✨ 1. Ejecutar Precorrección", key="btn_pre"):
            with st.spinner("Limpiando espacios..."):
                st.success(precorreccion.ejecutar_precorreccion(uploaded_file.name))

    with col2:
        if st.button("🤖 2. Iniciar Auditoría IA", key="btn_ia"):
            st.session_state['informe_actual'] = f"Informe_{uploaded_file.name.replace('.docx', '.txt')}"
            with st.spinner("Analizando con IA..."):
                comprobacion.comprobar_archivo(uploaded_file.name)
                st.rerun()

    # --- BLOQUE DE VISUALIZACIÓN UNIFICADO ---
    if 'informe_actual' in st.session_state:
        ruta_txt = os.path.join("salida", st.session_state['informe_actual'])
        
        if os.path.exists(ruta_txt):
            datos = []
            # PRIMERO: Leemos todo el archivo y acumulamos los datos
            with open(ruta_txt, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
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

            # SEGUNDO: Si hay datos, dibujamos las tablas UNA SOLA VEZ (Fuera del bucle for)
            if datos:
                df = pd.DataFrame(datos)

                def renderizar_tabla(titulo, filtro, emoji, id_tabla):
                    st.subheader(f"{emoji} {titulo}")
                    # Filtrado insensible a mayúsculas/tildes
                    mask = df["Categoría"].str.contains(filtro, case=False, na=False)
                    df_final = df[mask].copy()
                    
                    if not df_final.empty:
                        # Aplicar negrita visual a la columna Original
                        df_estilizado = df_final.style.map(lambda x: 'font-weight: bold;', subset=['Original'])
                        st.dataframe(df_estilizado, use_container_width=True, hide_index=True, key=f"tabla_{id_tabla}")
                    else:
                        st.write(f"✅ Sin incidencias en {titulo.lower()}.")

                # Dibujamos las 3 secciones
                renderizar_tabla("ERRORES ORTOGRÁFICOS", "ORTOGRAFIA|ORTOGRAFÍA", "🔴", "orto")
                renderizar_tabla("ERRORES DE FORMATO", "FORMATO", "🟡", "form")
                renderizar_tabla("SUGERENCIAS Y ESTILO", "SUGERENCIA", "🟢", "sug")
                
                st.divider()
                
                # Botón de descarga único
                with open(ruta_txt, "rb") as f:
                    st.download_button(
                        label="📥 Descargar Informe Completo (TXT)",
                        data=f,
                        file_name=st.session_state['informe_actual'],
                        mime="text/plain",
                        key="download_final_btn"
                    )
            else:
                st.info("El análisis no ha devuelto errores todavía...")
