#!/usr/bin/env python3
import os
import re
from docx import Document
from spellchecker import SpellChecker
from openai import OpenAI
from dotenv import load_dotenv

# ---------- CONFIGURACIÓN ----------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Diccionario local en español para filtrar palabras comunes (Coste 0)
spell = SpellChecker(language='es')

# Rutas relativas al proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FOLDER = os.path.join(BASE_DIR, "entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "salida")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def limpiar_palabra(palabra):
    """
    Elimina signos de puntuación, exclamaciones e interrogaciones 
    para que el diccionario reconozca la palabra limpia.
    """
    return re.sub(r'[^\wáéíóúÁÉÍÓÚñÑ]', '', palabra)

def auditar_con_ia(texto):
    """
    Consulta a la IA solo como último recurso. 
    Pide un formato de salida mínimo para ahorrar tokens.
    """
    prompt = (
        "Actúa como un auditor ortográfico estricto. "
        "Analiza el texto y devuelve ÚNICAMENTE los errores encontrados "
        "en formato: 'Error -> Corrección'. "
        "Si el texto es correcto, responde solo 'OK'."
    )
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": texto}
            ],
            temperature=0
        )
        respuesta = res.choices[0].message.content.strip()
        return None if respuesta.upper() == "OK" else respuesta
    except Exception as e:
        return f"Error API: {str(e)}"

def comprobar_archivo(name):
    ruta_entrada = os.path.join(INPUT_FOLDER, name)
    doc = Document(ruta_entrada)
    informe = [f"INFORME DE AUDITORÍA: {name}\n" + "="*40 + "\n"]
    hay_hallazgos = False

    for i, p in enumerate(doc.paragraphs):
        texto = p.text.strip()
        # Ignorar párrafos vacíos o demasiado cortos (ruido)
        if not texto or len(texto) < 3:
            continue

        errores_mecanicos = []

        # 1. FILTRO DE REGLAS MECÁNICAS (Regex - Gratis)
        if "  " in texto:
            errores_mecanicos.append("Doble espacio detectado")
        
        # Corregido: Detecta falta de espacio tras signos sin romper el código
        if re.search(r'[.,;!?:»][a-zA-ZáéíóúÁÉÍÓÚ]', texto):
            errores_mecanicos.append("Falta espacio tras signo de puntuación")
            
        if re.search(r'\s+[.,;!?:»]', texto):
            errores_mecanicos.append("Espacio innecesario antes de signo de puntuación")

        # 2. FILTRO DE DICCIONARIO LOCAL (Gratis)
        # Extraemos palabras y las limpiamos de signos (¡Hola! -> Hola)
        palabras_crudas = texto.split()
        palabras_limpias = [limpiar_palabra(w) for w in palabras_crudas if limpiar_palabra(w)]
        
        # Buscamos palabras que el diccionario no conoce
        desconocidas = spell.unknown(palabras_limpias)

        # 3. FILTRO FINAL DE IA (Solo si hay sospechas)
        # Si el diccionario duda o hay errores mecánicos, la IA audita
        resultado_ia = None
        if desconocidas or errores_mecanicos:
            resultado_ia = auditar_con_ia(texto)

        # 4. CONSTRUCCIÓN DEL RESULTADO
        if errores_mecanicos or resultado_ia:
            hay_hallazgos = True
            informe.append(f"📍 PÁRRAFO {i+1}")
            informe.append(f"TEXTO ORIGINAL: \"{texto}\"")
            
            for err in errores_mecanicos:
                informe.append(f"   - [FORMATO]: {err}")
            
            if resultado_ia:
                informe.append(f"   - [SUGERENCIA]: {resultado_ia}")
            
            informe.append("-" * 30)

    if not hay_hallazgos:
        informe.append("No se han encontrado errores evidentes en este documento.")

    # Guardar informe en la carpeta de salida
    nombre_informe = f"AUDITORIA_{name.replace('.docx', '.txt')}"
    ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_informe)
    
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(informe))
    
    return nombre_informe

if __name__ == "__main__":
    # Modo terminal: procesa todo lo que haya en la carpeta entrada
    archivos = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".docx")]
    if not archivos:
        print("No se encontraron archivos .docx en la carpeta 'entrada'.")
    else:
        for f in archivos:
            print(f"Iniciando auditoría de: {f}...")
            resultado = comprobar_archivo(f)
            print(f"✅ Informe generado en: salida/{resultado}")
