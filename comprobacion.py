import os
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# PROMPT DE AUDITORÍA BASADO EN TUS 13 REGLAS
PROMPT_AUDITORIA = """Eres un AUDITOR DE ESTILO Y ORTOGRAFÍA. Tu objetivo es generar un informe de errores detallado.
Analiza el texto basándote estrictamente en estas reglas:

1. CIFRAS: 4 cifras juntas (4000), 5+ con espacio (20 000). Años sin puntos. Espacio antes de % (20 %).
2. SÍMBOLOS: Espacio obligatorio (12 kg, 37,5 °C).
3. ABREVIATURAS: EE. UU., n.º, pág.
4. DIÁLOGOS: Raya larga (—) pegada al texto.
5. COMILLAS: Solo latinas « ».
8. CONCORDANCIA: Género/número y colectivos (la mayoría decidió).
10. VOCATIVOS: Coma obligatoria (Marta, ven).
11/12. PEGOTES: Espacio tras signos de puntuación (palabra. Otra).
13. GRAMÁTICA: "Si habría" es incorrecto, debe ser "Si hubiera".
ESTILO: Detectar voz pasiva, gerundios de posterioridad y frases pesadas.

FORMATO DE SALIDA (ESTRICTO):
ID_X: "original" -> "corrección" (Explicación breve).

REGLA DE ORO: Si no hay errores en un ID, no lo mencIONES. Si todo el bloque está perfecto, responde únicamente: "No se encontraron errores." """

def comprobar_archivo(ruta_completa):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    if not os.path.exists(ruta_completa):
        return f"ERROR: No se encuentra el archivo en {ruta_completa}"

    try:
        doc = Document(ruta_completa)
        informe = [f"AUDITORÍA: {os.path.basename(ruta_completa)}\n" + "="*30]
        
        bloque = []
        for i, p in enumerate(doc.paragraphs):
            t = p.text.strip()
            if len(t) > 5:
                # Aquí es donde el ID se vincula al párrafo
                bloque.append(f"ID_{i+1}: {t}")
            
            if len(bloque) >= 15:
                res = llamar_ia("\n".join(bloque))
                # Filtramos para que no guarde el aviso de "No hay errores"
                if res and "No se encontraron errores" not in res:
                    informe.append(res)
                bloque = []
        
        if bloque:
            res = llamar_ia("\n".join(bloque))
            if res and "No se encontraron errores" not in res:
                informe.append(res)

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
            temperature=0, 
            timeout=20
        )
        return res.choices[0].message.content.strip()
    except:
        return None
