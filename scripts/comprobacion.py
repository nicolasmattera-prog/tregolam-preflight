import streamlit as st
import os
import sys
import pandas as pd

# 1. Configuración de rutas para encontrar la carpeta 'scripts'
# Aseguramos que el sistema encuentre comprobacion.py dentro de /scripts
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(BASE_PATH, "scripts")
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

# 2. Importación de tus herramientas con manejo de errores
try:
    import precorreccion
    import comprobacion
except ImportError as e:
    st.error(f"Error al importar scripts: {e}")

# Configuración de página ancha
st.set_page_config(page_title="Auditoría Tregolam", layout="wide")
st.title("🔍 Panel de Control: Auditoría Ortotipográfica")

# Asegurar que existan las carpetas necesarias
for folder in ["entrada", "salida"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

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
            # Definimos el nombre del informe en el estado de la sesión de inmediato
            nombre_final = f"Informe_{uploaded_file.name.replace('.docx', '.txt')}"
            st.session_state['informe_actual'] = nombre_final
            
            with st.spinner("Analizando manuscrito... Los resultados aparecerán abajo."):
                # Verificación de seguridad antes de llamar a la función
                if hasattr(comprobacion, 'comprobar_archivo'):
                    nombre_informe = comprobacion.comprobar_archivo(uploaded_file.name)
                    if "ERROR" in nombre_informe:
                        st.error(nombre_informe)
                    else:
                        st.success("¡Auditoría finalizada con éxito!")
                else:
                    st.error("Error técnico: La función 'comprobar_archivo' no se encuentra en el script.")

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

                    # --- DETALLE SOLICITADO: MARCAR ORIGINAL EN NEGRITA ---
                    df["Original"] = df["Original"].apply(lambda x: f"**{x}**")

                    # SECCIÓN ROJA: ORTOGRAFÍA
                    st.subheader("🔴 ERRORES ORTOGRÁFICOS")
                    df_orto = df[df["Categoría"].str.contains("ORTOGRAFIA|ORTOGRAFÍA", case=False, na=False)]
                    if not df_orto.empty:
                        st.data_editor(df_orto, use_container_width=True, hide_index=True, key="tabla_orto")
                    else:
                        st.write("✅ Sin errores de ortografía detectados.")

                    # SECCIÓN AMARILLA: FORMATO
                    st.subheader("🟡 ERRORES DE FORMATO")
                    df_form = df[df["Categoría"].str.contains("FORMATO", case=False, na=False)]
                    if not df_form.empty:
                        st.data_editor(df_form, use_container_width=True, hide_index=True, key="tabla_form")
                    else:
                        st.write("✅ Formato técnico correcto.")

                    # SECCIÓN VERDE: SUGERENCIAS
                    st.subheader("🟢 SUGERENCIAS Y ESTILO")
                    df_sug = df[df["Categoría"].str.contains("SUGERENCIA", case=False, na=False)]
                    if not df_sug.empty:
                        st.data_editor(df_sug, use_container_width=True, hide_index=True, key="tabla_sug")
                    else:
                        st.write("✅ Sin sugerencias adicionales.")
                    
                    with open(ruta_txt, "rb") as f:
                        st.download_button("📥 Descargar Informe (TXT)", f, file_name=st.session_state['informe_actual'])
                else:
                    st.info("Procesando datos... las tablas se actualizarán pronto.")
            
            except Exception as e:
                st.warning("Cargando nuevos resultados...")
