import streamlit as st
import os
import sys
import pandas as pd

# 1. Configuración de rutas para encontrar la carpeta 'scripts'
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))

# 2. Importación de tus herramientas
import precorreccion
import comprobacion

# Configuración de página ancha para que las tablas se vean bien
st.set_page_config(page_title="Auditoría Tregolam", layout="wide")
st.title("🔍 Panel de Control: Auditoría Ortotipográfica")

# Asegurar que las carpetas existen
os.makedirs("entrada", exist_ok=True)
os.makedirs("salida", exist_ok=True)

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu manuscrito (.docx)", type="docx")

if uploaded_file:
    ruta_entrada = os.path.join("entrada", uploaded_file.name)
    with open(ruta_entrada, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.info(f"Archivo cargado: {uploaded_file.name}")
    
    col1, col2 = st.columns(2)

    # --- BOTÓN 1: PRECORRECCIÓN ---
    with col1:
        if st.button("✨ 1. Ejecutar Precorrección"):
            with st.spinner("Limpiando espacios y formatos..."):
                resultado = precorreccion.ejecutar_precorreccion(uploaded_file.name)
                st.success(resultado)

    # --- BOTÓN 2: COMPROBACIÓN (IA) ---
    with col2:
        if st.button("🤖 2. Iniciar Auditoría IA"):
            progreso_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("Analizando manuscrito... Esto puede tardar unos minutos."):
                nombre_informe = comprobacion.comprobar_archivo(uploaded_file.name)
                
                if "ERROR" in nombre_informe:
                    st.error(nombre_informe)
                else:
                    st.session_state['informe_actual'] = nombre_informe
                    progreso_bar.progress(100)
                    status_text.success("¡Auditoría finalizada con éxito!")

    # --- RENDERIZADO DEL PANEL DE COLORES ---
    if 'informe_actual' in st.session_state:
        ruta_txt = os.path.join("salida", st.session_state['informe_actual'])
        
        if os.path.exists(ruta_txt):
            with open(ruta_txt, "r", encoding="utf-8") as f:
                lineas = f.readlines()

            datos = []
            for line in lineas:
                if "|" in line:
                    # Limpiamos espacios y posibles corchetes de la categoría
                    partes = [p.strip().replace("[", "").replace("]", "") for p in line.split("|")]
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

                # SECCIÓN ROJA: ORTOGRAFÍA
                st.subheader("🔴 ERRORES ORTOGRÁFICOS")
                df_orto = df[df["Categoría"].str.contains("ORTOGRAFIA|ORTOGRAFÍA", case=False, na=False)]
                if not df_orto.empty:
                    st.data_editor(df_orto, use_container_width=True, hide_index=True, key="tabla_orto")
                else:
                    st.success("✅ Sin errores de ortografía detectados.")

                # SECCIÓN AMARILLA: FORMATO
                st.subheader("🟡 ERRORES DE FORMATO")
                df_form = df[df["Categoría"].str.contains("FORMATO", case=False, na=False)]
                if not df_form.empty:
                    st.data_editor(df_form, use_container_width=True, hide_index=True, key="tabla_form")
                else:
                    st.success("✅ Formato técnico correcto (Rayas, comillas, cifras).")

                # SECCIÓN VERDE: SUGERENCIAS
                st.subheader("🟢 SUGERENCIAS Y ESTILO")
                df_sug = df[df["Categoría"].str.contains("SUGERENCIA", case=False, na=False)]
                if not df_sug.empty:
                    st.data_editor(df_sug, use_container_width=True, hide_index=True, key="tabla_sug")
                else:
                    st.success("✅ Sin sugerencias adicionales.")
                
                # Opción de descarga
                with open(ruta_txt, "rb") as f:
                    st.download_button("📥 Descargar Informe Completo (TXT)", f, file_name=st.session_state['informe_actual'])
            else:
                st.warning("El informe no contiene errores detectados o el formato no es compatible.")
