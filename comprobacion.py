import os
import re
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- FILTRO LOCAL (TU "LIBRERÍA" DE SOSPECHAS) ----------
def tiene_error_potencial(texto):
    """
    Analiza el texto con Regex para detectar fallos técnicos 
    antes de decidir si gastar tokens en la IA.
    """
    patrones = [
        r'\d%',                # Porcentaje pegado (10%)
        r'\d°C',               # Temperatura pegada (37°C)
        r'\d{5,}',             # 5+ cifras sin espacio (25000)
        r'[“”"]',              # Comillas no latinas
        r'[sS]i [aA]bría',     # Error gramatical específico
        r'\.\w',               # Pegote (punto seguido de letra)
        r' ,',                 # Espacio antes de coma
        r'  ',                 # Dobles espacios
        r'—\s|\s—'             # Rayas de diálogo mal espaciadas
    ]
    return any(re.search(p, texto) for p in patrones)

# ---------- PROMPT DE AUDITORÍA (EL JUEZ) ----------
PROMPT_AUDITORIA = """Eres un AUDITOR TÉCNICO. Tu única función es reportar errores basados en estas reglas:
1. Cifras: 5+ dígitos con espacio (20 000). % y °C con espacio previo.
2. Comillas: Solo latinas « ».
3. Gramática: "Si hubiera" en vez de "Si habría". Concordancia de colectivos.
4. Espacios: Un espacio tras puntuación. Sin pegotes.

FORMATO: ID_X: "error" -> "corrección" (Breve motivo).
REGLA DE ORO: Si no hay errores técnicos, responde: "SIN_ERRORES"."""

def comprobar_archivo(ruta_completa):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    try:
        doc = Document(ruta_completa)
        informe = [f"AUDITORÍA FINAL: {os.path.basename(ruta_completa)}\n" + "="*30]
        
        bloque = []
        for i, p in enumerate(doc.paragraphs):
            t = p.text.strip()
            
            # SOLO procesamos si el filtro local detecta algo sospechoso
            if len(t) > 5 and tiene_error_potencial(t):
                bloque.append(f"ID_{i+1}: {t}")
            
            # Enviamos a la IA en bloques de 10 para mayor precisión
            if len(bloque) >= 10:
                res = llamar_ia("\n".join(bloque))
                if res and "SIN_ERRORES" not in res:
                    informe.append(res)
                bloque = []
        
        if bloque:
            res = llamar_ia("\n".join(bloque))
            if res and "SIN_ERRORES" not in res:
                informe.append(res)

        # Si el informe solo tiene la cabecera, es que el texto está perfecto
        if len(informe) == 1:
            informe.append("No se detectaron errores técnicos en el documento.")

        nombre_txt = f"INFORME_{os.path.basename(ruta_completa).replace('.docx', '.txt')}"
        ruta_txt = os.path.join(OUTPUT_FOLDER, nombre_txt)
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(informe))
            
        return nombre_txt
    except Exception as e:
        return f"ERROR CRÍTICO: {str(e)}"

def llamar_ia(texto):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT_AUDITORIA},
                {"role": "user", "content": texto}
            ],
            temperature=0
        )
        return res.choices[0].message.content.strip()
    except:
        return None
