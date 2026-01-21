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
            # Marcamos que el proceso ha empezado
            st.session_state['informe_actual'] = f"Informe_{uploaded_file.name.replace('.docx', '.txt')}"
            
            with st.spinner("Procesando manuscrito..."):
                nombre_informe = comprobacion.comprobar_archivo(uploaded_file.name)
                st.success("¡Análisis finalizado!")

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

# --- RENDERIZADO DEL PANEL DE COLORES CON NEGRITAS REALES ---
                if datos:
                    df = pd.DataFrame(datos)

                    # Función interna para procesar y mostrar cada tabla con estilo
                    def mostrar_seccion(titulo, filtro, emoji, clave_tabla):
                        st.subheader(f"{emoji} {titulo}")
                        
                        # Filtramos por categoría (insensible a mayúsculas/minúsculas)
                        mask = df["Categoría"].str.contains(filtro, case=False, na=False)
                        df_filtrado = df[mask]
                        
                        if not df_filtrado.empty:
                            # APLICAR NEGRITA REAL: Usamos Styler de Pandas para la columna Original
                            # Esto lo pone en negrita visualmente sin añadir asteriscos al texto
                            df_estilizado = df_filtrado.style.map(
                                lambda x: 'font-weight: bold;', 
                                subset=['Original']
                            )
                            
                            st.dataframe(
                                df_estilizado, 
                                use_container_width=True, 
                                hide_index=True,
                                key=clave_tabla
                            )
                        else:
                            st.success(f"✅ Sin incidencias en {titulo.lower()}.")

                    # 1. SECCIÓN ROJA: ORTOGRAFÍA
                    mostrar_seccion("ERRORES ORTOGRÁFICOS", "ORTOGRAFIA|ORTOGRAFÍA", "🔴", "tabla_orto")

                    # 2. SECCIÓN AMARILLA: FORMATO
                    mostrar_seccion("ERRORES DE FORMATO", "FORMATO", "🟡", "tabla_form")

                    # 3. SECCIÓN VERDE: SUGERENCIAS
                    mostrar_seccion("SUGERENCIAS Y ESTILO", "SUGERENCIA", "🟢", "tabla_sug")
                    
                    # Espacio extra y botón de descarga
                    st.divider()
                    with open(ruta_txt, "rb") as f:
                        st.download_button(
                            label="📥 Descargar Informe Completo (TXT)",
                            data=f,
                            file_name=st.session_state['informe_actual'],
                            mime="text/plain"
                        )
                else:
                    st.warning("El informe está vacío o el formato no es compatible.")
