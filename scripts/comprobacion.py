import os
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Instrucción de "Silencio": Si no hay error real, la IA debe responder OK.
PROMPT_AUDITORIA = """Actúa como un auditor técnico de ortotipografía. 
REGLAS: Cifras (20 000), Símbolos (10 %), Comillas (« »), Rayas de diálogo (—).
TAREA: Si un párrafo tiene errores técnicos, lístalos como: ID_X: "original" -> "corrección" (Motivo).
IMPORTANTE: Si el párrafo es correcto o no viola las reglas técnicas, responde ÚNICAMENTE la palabra: OK"""

def comprobar_archivo(nombre_archivo):
    # Rutas basadas en la raíz del proyecto
    ruta_lectura = os.path.join("entrada", nombre_archivo)
    ruta_salida_folder = "salida"
    
    try:
        doc = Document(ruta_lectura)
        informe_final = [f"INFORME DE AUDITORÍA: {nombre_archivo}\n" + "="*40]
        
        # Procesamos párrafos de 10 en 10 para que la rueda se mueva constante
        bloque = []
        for i, p in enumerate(doc.paragraphs):
            texto = p.text.strip()
            if len(texto) > 5:
                bloque.append(f"ID_{i+1}: {texto}")
            
            if len(bloque) >= 10:
                respuesta = llamar_ia("\n".join(bloque))
                # Solo añadimos al informe lo que NO sea un "OK"
                for linea in respuesta.split("\n"):
                    if "OK" not in linea.upper() and "ID_" in linea:
                        informe_final.append(linea)
                bloque = []

        # Procesar resto
        if bloque:
            respuesta = llamar_ia("\n".join(bloque))
            for linea in respuesta.split("\n"):
                if "OK" not in linea.upper() and "ID_" in linea:
                    informe_final.append(linea)

        if len(informe_final) <= 1:
            informe_final.append("No se detectaron violaciones técnicas de las reglas.")

        nombre_txt = f"Informe_{nombre_archivo.replace('.docx', '.txt')}"
        ruta_txt = os.path.join(ruta_salida_folder, nombre_txt)
        
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
            temperature=0
        )
        return res.choices[0].message.content.strip()
    except:
        return "ERROR_COMUNICACION"
