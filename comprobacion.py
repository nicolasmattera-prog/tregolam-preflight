#!/usr/bin/env python3
import os
import re
from docx import Document
from spellchecker import SpellChecker
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
spell = SpellChecker(language='es')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def limpiar_palabra(palabra):
    return re.sub(r'[^\wáéíóúÁÉÍÓÚñÑ]', '', palabra)

def auditar_bloque_ia(bloque_textos):
    """Envía varios párrafos a la vez para ahorrar tiempo de conexión."""
    # Unimos los párrafos con un marcador para que la IA sepa separarlos
    contenido_unido = "\n---\n".join([f"P{i}: {t}" for i, t in bloque_textos])
    
    prompt = (
        "Actúa como auditor. Te enviaré varios párrafos numerados (P1, P2...). "
        "Para cada uno, si hay errores, pon: 'PX: Error -> Corrección'. "
        "Si un párrafo es correcto, no menciones su número. "
        "Respuesta mínima, sin introducciones."
    )
    
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": contenido_unido}],
            temperature=0
        )
        return res.choices[0].message.content.strip()
    except:
        return ""

def comprobar_archivo(name):
    doc = Document(os.path.join(INPUT_FOLDER, name))
    informe = [f"INFORME DE AUDITORÍA: {name}\n" + "="*40 + "\n"]
    sospechosos = []
    
    print(f"Leyendo y filtrando localmente...")
    for i, p in enumerate(doc.paragraphs):
        texto = p.text.strip()
        if len(texto) < 5: continue

        # Filtro local rápido
        mecanicos = []
        if "  " in texto: mecanicos.append("Doble espacio")
        
        palabras = [limpiar_palabra(w) for w in texto.split() if limpiar_palabra(w)]
        desconocidas = spell.unknown(palabras)

        if desconocidas or mecanicos:
            # Guardamos el índice y el texto para enviarlos en bloque
            sospechosos.append((i + 1, texto, mecanicos))

    # PROCESAMIENTO EN BLOQUES (BATCHING) de 15 en 15
    print(f"Enviando {len(sospechosos)} párrafos sospechosos a la IA en bloques...")
    resultados_finales = {}
    
    for j in range(0, len(sospechosos), 15):
        bloque = sospechosos[j:j+15]
        # Solo enviamos el índice y el texto a la IA
        peticion_ia = [(item[0], item[1]) for item in bloque]
        respuesta = auditar_bloque_ia(peticion_ia)
        
        # Guardamos la respuesta de la IA vinculada al número de párrafo
        for linea in respuesta.split('\n'):
            if ':' in linea and linea.startswith('P'):
                try:
                    num_p = int(linea.split(':')[0][1:])
                    resultados_finales[num_p] = linea.split(':', 1)[1].strip()
                except: continue

    # Construir el informe final combinando Regex e IA
    for num, texto, mecanicos in sospechosos:
        ia_sug = resultados_finales.get(num)
        if mecanicos or ia_sug:
            informe.append(f"📍 PÁRRAFO {num}\nTEXTO: {texto[:100]}...")
            for m in mecanicos: informe.append(f"   - [FORMATO]: {m}")
            if ia_sug: informe.append(f"   - [SUGERENCIA]: {ia_sug}")
            informe.append("-" * 30)

    with open(os.path.join(OUTPUT_FOLDER, f"AUDITORIA_{name}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(informe))

if __name__ == "__main__":
    for f in os.listdir(INPUT_FOLDER):
        if f.endswith(".docx"):
            comprobar_archivo(f)
            print(f"✅ Finalizado: {f}")
