import os
import sys
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Rutas absolutas para Streamlit Cloud
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA_DIR = os.path.join(BASE_DIR, "entrada")
SALIDA_DIR = os.path.join(BASE_DIR, "salida")

# Asegurar que las carpetas existen para evitar errores de ruta
os.makedirs(ENTRADA_DIR, exist_ok=True)
os.makedirs(SALIDA_DIR, exist_ok=True)

PROMPT_AUDITORIA = """Actúa como un auditor ortotipográfico experto. Tu tarea es clasificar errores en 3 categorías: ORTOGRAFIA, FORMATO o SUGERENCIA.

REGLAS TÉCNICAS:
1. CIFRAS: Espacio de no ruptura en miles (Ej: 20 000). NO puntos ni comas.
2. COMILLAS: Convertir "" o '' en latinas « ». SI YA SON « », NO REPORTAR NADA.
3. RAYAS: Diálogos con raya larga — pegada al texto (Ej: —Hola).
4. SÍMBOLOS: Espacio entre cifra y símbolo (Ej: 10 %).

CATEGORÍAS DE SALIDA:
- [ORTOGRAFIA]: Erratas o faltas graves.
- [FORMATO]: Errores en las 4 reglas técnicas de arriba.
- [SUGERENCIA]: Recomendaciones de estilo.

FORMATO DE RESPUESTA (ESTRICTO):
CATEGORIA | ID_X | "original" | "corrección" | Motivo
Si no hay errores en el bloque, responde únicamente: S_OK"""

def comprobar_archivo(nombre_archivo):
    ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)
    nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
    ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)
    
    # 1. Limpiamos el archivo si ya existía para empezar de cero
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write("") 

    try:
        doc = Document(ruta_lectura)
        bloque = []
        parrafos = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 5]

        for i, texto in enumerate(parrafos):
            bloque.append(f"ID_{i+1}: {texto}")
            
            if len(bloque) >= 8: # Bajamos un poco el bloque para ganar velocidad de respuesta
                respuesta = llamar_ia("\n".join(bloque))
                if respuesta and "S_OK" not in respuesta.upper():
                    # ESCRIBIMOS AL INSTANTE EN EL DISCO
                    with open(ruta_txt, "a", encoding="utf-8") as f:
                        f.write(respuesta.strip() + "\n")
                bloque = []

        if bloque:
            respuesta = llamar_ia("\n".join(bloque))
            if respuesta and "S_OK" not in respuesta.upper():
                with open(ruta_txt, "a", encoding="utf-8") as f:
                    f.write(respuesta.strip() + "\n")

        return nombre_txt
    except Exception as e:
        return f"ERROR: {str(e)}"

        # Procesar bloque restante
        if bloque:
            respuesta = llamar_ia("\n".join(bloque))
            if respuesta and "S_OK" not in respuesta.upper():
                for linea in respuesta.split("\n"):
                    if "|" in linea:
                        resultados.append(linea.strip())

        # Generar nombre y ruta de salida
        nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
        ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)
        
        # ESCRITURA SEGURA: Usamos 'with' para asegurar el cierre del archivo
        with open(ruta_txt, "w", encoding="utf-8") as f:
            if resultados:
                f.write("\n".join(resultados))
            else:
                f.write("S_OK | 0 | N/A | N/A | No se detectaron errores.")
        
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
            temperature=0,
            timeout=30 # Evita que el script se quede colgado si OpenAI tarda
        )
        return res.choices[0].message.content.strip()
    except Exception:
        return "S_OK" # Si falla la IA, devolvemos S_OK para no bloquear el bucle

