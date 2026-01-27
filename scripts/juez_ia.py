from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = (
    "Eres un editor profesional. Tu tarea es corregir errores en una frase. "
    "Si encuentras un error, devuelve la FRASE COMPLETA corregida y pon la palabra o fragmento que has cambiado entre etiquetas <b> y </b>. "
    "Ejemplo: El coche es <b>rojo</b>. "
    "Si no hay error, responde: CORRECTA. "
    "No des explicaciones, solo la frase corregida o la palabra CORRECTA."
)

def validar_con_ia(palabra: str, contexto: str) -> str:
    prompt = f"Frase original: {contexto}\nPalabra sospechosa: {palabra}\nCorrige la frase si es necesario:"
    
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=150 
    )
    
    return resp.choices[0].message.content.strip()
