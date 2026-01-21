import os
import sys
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

# Cargamos variables de entorno
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- CONFIGURACIÓN DE RUTAS ABSOLUTAS ---
# Localizamos la raíz del proyecto (subiendo un nivel desde 'scripts/')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

# Instrucción de "Silencio" mejorada para evitar ruidos y errores de estilo
PROMPT_AUDITORIA = """Actúa como un auditor ortotipográfico riguroso. 
Tu objetivo es encontrar errores TÉCNICOS, no de estilo.

REGLAS CRÍTICAS:
1. CIFRAS: Grupos de 3 con espacio de no ruptura (Ej: 20 000). No usar puntos ni comas.
2. COMILLAS: Usar siempre latinas « » para citas y títulos. Cambia "" o '' por « ».
3. RAYAS: Diálogos con raya larga —. Pegada al texto: —Hola.
4. SÍMBOLOS: Espacio entre cifra y símbolo (Ej: 10 %).
5. MAYÚSCULAS: Solo corregir si es un error ortográfico flagrante. NO sugieras cambios de estilo.

FORMATO DE SALIDA:
- Si el texto CUMPLE las reglas o no hay errores claros, responde SOLO: S_OK
- Si hay un ERROR, responde: ID_X: "original" -> "corrección" (Breve motivo).
- NUNCA respondas que algo es "Correcto". Si es correcto, di: S_OK"""

def comprobar_archivo(nombre_archivo):
    """
    Realiza la auditoría técnica usando rutas absolutas para evitar el AttributeError en Streamlit Cloud.
    """
    # Ruta de lectura corregida para apuntar a la raíz/entrada
    ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)
    
    try:
        # Verificación de seguridad
        if not os.path.exists(ruta_lectura):
            return f"ERROR: No se encuentra el archivo en {ruta_lectura}"

        doc = Document(ruta_lectura)
        informe_final = [f"INFORME DE AUDITORÍA: {nombre_archivo}\n" + "="*40]
        
        # Procesamos párrafos de 10 en 10
        bloque = []
        for i, p in enumerate(doc.paragraphs):
            texto = p.text.strip()
            if len(texto) > 5:
                bloque.append(f"ID_{i+1}: {texto}")
            
            if len(bloque) >= 10:
                respuesta = llamar_ia("\n".join(bloque))
                # Filtrado estricto para evitar imprimir "Correcto" o explicaciones vacías
                for linea in respuesta.split("\n"):
                    linea_limpia = linea.strip()
                    if linea_limpia and "S_OK" not in linea_limpia.upper() and "ID_" in linea_limpia:
                        informe_final.append(linea_limpia)
                bloque = []

        # Procesar resto del documento
        if bloque:
            respuesta = llamar_ia("\n".join(bloque))
            for linea in respuesta.split("\n"):
                linea_limpia = linea.strip()
                if linea_limpia and "S_OK" not in linea_limpia.upper() and "ID_" in linea_limpia:
                    informe_final.append(linea_limpia)

        if len(informe_final) <= 1:
            informe_final.append("No se detectaron violaciones técnicas de las reglas.")

        # Definimos nombre y ruta de salida absoluta (raíz/salida)
        nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
        ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)
        
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(informe_final))
            
        return nombre_txt

    except Exception as e:
        return f"ERROR en el proceso: {str(e)}"

def llamar_ia(texto_bloque):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT_AUDITORIA},
                {"role": "user", "content": texto_bloque}
            ],
            # Mantenemos temperatura 0 para que no haya variabilidad (estocasticidad)
            temperature=0
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR_IA: {str(e)}"
