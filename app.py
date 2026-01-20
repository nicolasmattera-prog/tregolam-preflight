import sys
import os

# Esto es lo que permite que app.py "vea" lo que hay dentro de /scripts
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))

import precorreccion
import comprobacion

st.title("Auditoría Tregolam")

uploaded_file = st.file_uploader("Sube tu archivo .docx", type="docx")

if uploaded_file:
    # Guardar en carpeta entrada
    ruta_entrada = os.path.join("entrada", uploaded_file.name)
    with open(ruta_entrada, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("Comprobar"):
        with st.spinner("Analizando..."):
            # Pasamos la ruta relativa limpia
            nombre_informe = comprobacion.comprobar_archivo(uploaded_file.name)
            
            if "ERROR" in nombre_informe:
                st.error(nombre_informe)
            else:
                ruta_salida = os.path.join("salida", nombre_informe)
                with open(ruta_salida, "rb") as f:
                    st.download_button("Descargar Informe", f, file_name=nombre_informe)
                st.success("Análisis finalizado.")
