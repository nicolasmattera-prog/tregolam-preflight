import streamlit as st
import os
import sys
import pandas as pd

# 1. Configuración de página (Debe ser lo primero)
st.set_page_config(page_title="Auditoría Tregolam", layout="wide")

# 2. Solución al problema de Rutas (Punto 4)
# Aseguramos que las carpetas existan antes de cualquier operación
base_path = os.path.dirname(os.path.abspath(__file__))
entrada_dir = os.path.join(base_path, "entrada")
salida_dir = os.path.join(base_path, "salida")
os.makedirs(entrada_dir, exist_ok=True)
os.makedirs(salida_dir, exist_ok=True)

# Importación de módulos locales
sys.path.append(os.path.join(base_path, "scripts"))
import precorreccion
import comprobacion

st.title("🔍 Panel de Auditoría Ortotipográfica")

# --- GESTIÓN DE ESTADO (SESSION STATE) ---
if 'fichero_procesado' not in st.session_state:
    st.session_state['fichero_procesado'] = False
if 'nombre_informe' not in st.session_state:
    st.session_state['nombre_informe'] = None

# 3. Subida de archivo con KEY ÚNICO (Punto 1)
uploaded_file = st.file_uploader(
    "Sube tu manuscrito (.docx)", 
    type="docx", 
    key="uploader_manuscrito_unico" 
)

if uploaded_file:
    # Si el usuario sube un archivo nuevo, reseteamos el estado
    if st.session_state.get('ultimo_nombre') != uploaded_file.name:
        st.session_state['fichero_procesado'] = False
        st.session_state['ultimo_nombre'] = uploaded_file.name

    ruta_archivo_entrada = os.path.join(entrada_dir, uploaded_file.name)
    with open(ruta_archivo_entrada, "wb") as f:
        f.write(uploaded_file.getbuffer())

    col1, col2 = st.columns(2)

    with col1:
        # Botón 1 con Key único
        if st.button("✨ 1. Precorrección", key="btn_ejecutar_pre"):
            with st.spinner("Limpiando espacios y dobles párrafos..."):
                precorreccion.ejecutar_precorreccion(uploaded_file.name)
                st.success("Precorrección completada.")

    with col2:
        # Botón 2 con Key único e invocación a función correcta (Punto 2)
        if st.button("🤖 2. Iniciar Auditoría IA", key="btn_ejecutar_ia"):
            with st.spinner("Analizando con IA..."):
                # Llamada a la función exacta requerida: comprobar_archivo
                comprobacion.comprobar_archivo(uploaded_file.name)
                
                # Guardamos en el estado para habilitar la vista de resultados
                st.session_state['nombre_informe'] = f"Informe_{uploaded_file.name.replace('.docx', '.txt')}"
                st.session_state['fichero_procesado'] = True
                st.rerun()

    # --- RENDERIZADO DE RESULTADOS ---
    if st.session_state['fichero_procesado'] and st.session_state['nombre_informe']:
        ruta_txt = os.path.join(salida_dir, st.session_state['nombre_informe'])
        
        if os.path.exists(ruta_txt):
            # Leemos el archivo para mostrarlo en tablas
            datos = []
            with open(ruta_txt, "r", encoding="utf-8") as f:
                for linea in f:
                    if "|" in linea:
                        partes = [p.strip() for p in linea.split("|")]
                        if len(partes) >= 5:
                            datos.append({
                                "Categoría": partes[0], "ID": partes[1], 
                                "Original": partes[2], "Sugerencia": partes[3], 
                                "Motivo": partes[4]
                            })
            
            if datos:
                df = pd.DataFrame(datos)
                
                # Función interna para dibujar tablas usando width='stretch' (Punto 3)
                def mostrar_tabla(titulo, filtro, color_key):
                    st.subheader(titulo)
                    mask = df["Categoría"].str.contains(filtro, case=False, na=False)
                    df_filtrado = df[mask]
                    
                    if not df_filtrado.empty:
                        st.dataframe(
                            df_filtrado, 
                            width="stretch", # Solución Punto 3
                            hide_index=True, 
                            key=f"tabla_resultado_{color_key}" # Key único
                        )
                    else:
                        st.info(f"No se detectaron hallazgos en {titulo}.")

                mostrar_tabla("🔴 Ortografía", "ORTOGRAFIA|ORTOGRAFÍA", "orto")
                mostrar_tabla("🟡 Formato", "FORMATO", "form")
                mostrar_tabla("🟢 Sugerencias", "SUGERENCIA", "sug")

                # Botón de Descarga con Key Dinámico (Punto 1)
                st.divider()
                with open(ruta_txt, "rb") as f_descarga:
                    st.download_button(
                        label="📥 Descargar Informe Completo",
                        data=f_descarga,
                        file_name=st.session_state['nombre_informe'],
                        key=f"btn_descarga_{st.session_state['nombre_informe']}" # Key dinámico único
                    )
