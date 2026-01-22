import os
import re
import sys
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

# Importamos tu motor de reglas físicas
# Aseguramos la ruta para evitar errores de importación
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from regex_rules1 import aplicar_regex_editorial 
except ImportError:
    # Fallback por si el archivo tiene el nombre original sin el '1'
    from regex_rules import aplicar_regex_editorial

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

# ---------- SOLUCIÓN AGUJEROS 1 Y 2: NORMALIZACIÓN TOTAL ----------

def texto_limpio(texto_crudo):
    """Devuelve el texto normalizado tras pasar por el motor de reglas físicas."""
    if not texto_crudo: return ""
    # Aplicamos el motor de reglas que ya limpia NBSP y unifica comillas
    return aplicar_regex_editorial(texto_crudo)

def contiene_caracteres_especiales(texto):
    """Detecta comillas bajas, latinas, dobles o espacios de no ruptura."""
    especiales = ('„', '“', '”', '«', '»', '\u00A0', '\u202f')
    return any(c in texto for c in especiales)

# ------------------------------------------------------------------

PROMPT_AUDITORIA = """Actúa como un auditor editorial profesional.
FORMATO OBLIGATORIO: CATEGORIA | ID | ORIGINAL | CORRECCION | MOTIVO
REGLAS:
1. Solo reporta errores de ORTOGRAFIA, FORMATO o SUGERENCIA.
2. Si no hay cambios reales, no reportes nada.
3. Si el texto ya es correcto, devuelve S_OK."""

def comprobar_archivo(nombre_archivo):
    ruta_lectura = os.path.join(SALIDA_DIR, nombre_archivo)
    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)
    
    open(ruta_txt, "w", encoding="utf-8").close()

    try:
        doc = Document(ruta_lectura)
        parrafos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]
        
        bloque = []
        for i, texto in enumerate(parrafos):
            bloque.append(f"ID_{i+1}: {texto}")
            if len(bloque) >= 10:
                respuesta = llamar_ia("\n".join(bloque))
                procesar_y_guardar(respuesta, ruta_txt)
                bloque = []

        if bloque:
            respuesta = llamar_ia("\n".join(bloque))
            procesar_y_guardar(respuesta, ruta_txt)
            
        return nombre_txt
    except Exception as e:
        return f"ERROR: {str(e)}"

def procesar_y_guardar(respuesta, ruta_dest):
    if not respuesta or "S_OK" in respuesta.upper():
        return
        
    lineas_ia = respuesta.split("\n")
    lineas_validadas = []
    
    for linea in lineas_ia:
        # AGUJERO 3: Validación estricta de formato tabular
        partes = [p.strip() for p in linea.split("|")]
        
        if len(partes) == 5 and all(partes):
            original = partes[2]
            sugerencia = partes[3]
            
            # AGUJERO 1: Comparación tras limpieza real
            if texto_limpio(original) == texto_limpio(sugerencia):
                continue
                
            # AGUJERO 2: Blindaje de caracteres especiales (NBSP y Comillas)
            if contiene_caracteres_especiales(original) and not contiene_caracteres_especiales(sugerencia):
                # Si la IA intenta "limpiar" nuestros caracteres especiales, la ignoramos
                continue

            # Validación final de cambio real
            if original != sugerencia:
                lineas_validadas.append(" | ".join(partes))
                
    if lineas_validadas:
        with open(ruta_dest, "a", encoding="utf-8") as f:
            f.write("\n".join(lineas_validadas) + "\n")

def llamar_ia(texto_bloque):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT_AUDITORIA},
                {"role": "user", "content": texto_bloque}
            ],
            temperature=0
        )
        return res.choices[0].message.content.strip()
    except:
        return "S_OK"
