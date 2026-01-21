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

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu manuscrito (.docx)", type="docx")

if uploaded_file:
    # Guardamos el archivo físicamente en la carpeta 'entrada'
    ruta_entrada = os.path.join("entrada", uploaded_file.name)
    if not os.path.exists("entrada"):
        os.makedirs("entrada")
    
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
            # Establecemos el nombre del informe en el estado de la sesión
            st.session_state['informe_actual'] = f"Informe_{uploaded_file.name.replace('.docx', '.txt')}"
            
            with st.spinner("Analizando manuscrito... Los resultados aparecerán abajo conforme se generen."):
                nombre_informe = comprobacion.comprobar_archivo(uploaded_file.name)
                
                if "ERROR" in nombre_informe:
                    st.error(nombre_informe)
                else:
                    st.success("¡Auditoría finalizada con éxito!")

    # --- RENDERIZADO DEL PANEL DE COLORES ---
    if 'informe_actual' in st.session_state:
        ruta_txt = os.path.join("salida", st.session_state['informe_actual'])
        
        if os.path.exists(ruta_txt):
            try:
                with open(ruta_txt, "r", encoding="utf-8") as f:
                    lineas = f.readlines()

                datos = []
                for line in lineas:
                    line = line.strip()
                    if "|" in line:
                        # Procesamiento de columnas según el formato estricto del motor
                        partes = [p.strip() for p in line.split("|")]
                        if len(partes) >= 5:
                            datos.append({
                                "Categoría": partes[0].replace("[", "").replace("]", ""),
                                "ID": partes[1],
                                "Original": partes[2],
                                "Sugerencia": partes[3],
                                "Motivo": partes[4]
                            })

                if datos:
                    df = pd.DataFrame(datos)

                    # --- DETALLE: MARCAR ORIGINAL EN NEGRITA ---
                    # Aplicamos negritas usando formato Markdown para resaltar erratas 
                    df["Original"] = df["Original"].apply(lambda x: f"**{x}**")

                    # SECCIÓN ROJA: ORTOGRAFÍA
                    st.subheader("🔴 ERRORES ORTOGRÁFICOS")
                    df_orto = df[df["Categoría"].str.contains("ORTOGRAFIA|ORTOGRAFÍA", case=False, na=False)]
                    if not df_orto.empty:
                        st.data_editor(df_orto, use_container_width=True, hide_index=True, key="tabla_orto")
                    else:
                        st.write("✅ Sin errores de ortografía detectados aún.")

                    # SECCIÓN AMARILLA: FORMATO
                    st.subheader("🟡 ERRORES DE FORMATO")
                    df_form = df[df["Categoría"].str.contains("FORMATO", case=False, na=False)]
                    if not df_form.empty:
                        st.data_editor(df_form, use_container_width=True, hide_index=True, key="tabla_form")
                    else:
                        st.write("✅ Formato técnico correcto (Rayas, comillas, cifras).")

                    # SECCIÓN VERDE: SUGERENCIAS
                    st.subheader("🟢 SUGERENCIAS Y ESTILO")
                    df_sug = df[df["Categoría"].str.contains("SUGERENCIA", case=False, na=False)]
                    if not df_sug.empty:
                        st.data_editor(df_sug, use_container_width=True, hide_index=True, key="tabla_sug")
                    else:
                        st.write("✅ Sin sugerencias adicionales.")
                    
                    # Opción de descarga del informe original (sin negritas para limpieza) 
                    with open(ruta_txt, "rb") as f:
                        st.download_button("📥 Descargar Informe en Bruto (TXT)", f, file_name=st.session_state['informe_actual'])
                else:
                    st.info("El análisis está en curso. Las tablas se llenarán automáticamente...")
            
            except Exception as e:
                st.warning("Actualizando visualización de datos...")
