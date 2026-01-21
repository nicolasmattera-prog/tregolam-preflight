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

PROMPT_AUDITORIA = """Actúa como un auditor ortotipográfico experto. Tu tarea es clasificar errores en 3 categorías: ORTOGRAFIA, FORMATO o SUGERENCIA.

REGLAS TÉCNICAS (Solo reportar si se incumplen):
1. CIFRAS: Espacio de no ruptura en miles (Ej: 20 000). NO puntos ni comas.
2. COMILLAS: Convertir "" o '' en latinas « ». SI YA SON « », NO REPORTAR NADA.
3. RAYAS: Diálogos con raya larga — pegada al texto (Ej: —Hola).
4. SÍMBOLOS: Espacio entre cifra y símbolo (Ej: 10 %).

CATEGORÍAS DE SALIDA:
- [ORTOGRAFIA]: Erratas, concordancia o faltas graves.
- [FORMATO]: Errores en las 4 reglas técnicas de arriba.
- [SUGERENCIA]: Recomendaciones de estilo o dudas (como nombres propios).

FORMATO DE RESPUESTA (ESTRICTO):
- Si hay error: CATEGORIA | ID_X | "original" | "corrección" | Motivo
- Si el párrafo es correcto o tienes dudas leves: S_OK
- NUNCA expliques nada fuera de este formato."""

def comprobar_archivo(nombre_archivo):
    ruta_lectura = os.path.join(ENTRADA_DIR, nombre_archivo)
    
    try:
        if not os.path.exists(ruta_lectura):
            return f"ERROR: Archivo no encontrado en {ruta_lectura}"

        doc = Document(ruta_lectura)
        # El informe ahora será una lista de datos estructurados
        resultados = []
        
        bloque = []
        for i, p in enumerate(doc.paragraphs):
            texto = p.text.strip()
            if len(texto) > 5:
                bloque.append(f"ID_{i+1}: {texto}")
            
            if len(bloque) >= 10:
                respuesta = llamar_ia("\n".join(bloque))
                for linea in respuesta.split("\n"):
                    if "S_OK" not in linea.upper() and "|" in linea:
                        resultados.append(linea.strip())
                bloque = []

        if bloque:
            respuesta = llamar_ia("\n".join(bloque))
            for linea in respuesta.split("\n"):
                if "S_OK" not in linea.upper() and "|" in linea:
                    resultados.append(linea.strip())

        # Guardamos el informe temporalmente como TXT, pero estructurado por "|"
        nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
        ruta_txt = os.path.join(SALIDA_DIR, nombre_txt)
        
        with open(ruta_txt, "w", encoding="utf-8") as f:
            if not resultados:
                f.write("S_OK")
            else:
                f.write("\n".join(resultados))
            
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
            temperature=0
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR_IA: {str(e)}"
