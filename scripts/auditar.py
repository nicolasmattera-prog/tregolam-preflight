import os
from docx import Document
import difflib
import re

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAL_FOLDER = os.path.join(BASE_DIR, "entrada")
CORREGIDO_FOLDER = os.path.join(BASE_DIR, "salida")

def extraer_datos(ruta):
    doc = Document(ruta)
    parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    texto_total = " ".join(parrafos)
    palabras = len(texto_total.split())
    return parrafos, palabras

def auditar_archivos(nombre_original):
    nombre_corregido = nombre_original.replace(".docx", "_CORREGIDO.docx")
    ruta_ori = os.path.join(ORIGINAL_FOLDER, nombre_original)
    ruta_cor = os.path.join(CORREGIDO_FOLDER, nombre_corregido)

    if not os.path.exists(ruta_cor):
        print(f"❌ No se encontró: {nombre_corregido}")
        return

    parrafos_ori, pal_ori = extraer_datos(ruta_ori)
    parrafos_cor, pal_cor = extraer_datos(ruta_cor)

    print(f"\n" + "="*50)
    print(f"AUDITORÍA TÉCNICA: {nombre_original}")
    print(f"="*50)

    # 1. MÉTRICAS DE VOLUMEN
    dif_palabras = pal_cor - pal_ori
    print(f"📊 Palabras: Original {pal_ori} | Corregido {pal_cor} ({'+' if dif_palabras>0 else ''}{dif_palabras})")
    
    if abs(dif_palabras) > (pal_ori * 0.05):
        print(f"⚠️  ALERTA: Variación de palabras superior al 5%. ¡Revisar posibles omisiones!")

    # 2. DETECCIÓN DE PÁRRAFOS PERDIDOS
    if len(parrafos_ori) != len(parrafos_cor):
        print(f"❌ ERROR CRÍTICO: El número de párrafos NO coincide ({len(parrafos_ori)} vs {len(parrafos_cor)})")
    else:
        print(f"✅ Integridad estructural: OK")

    # 3. ESCÁNER DE CAMBIOS AGRESIVOS U OMISIONES
    anomalias = []
    cambios_grandes = []   # <<< NUEVO

    for i, (ori, cor) in enumerate(zip(parrafos_ori, parrafos_cor)):
        largo_o = len(ori)
        largo_c = len(cor)

        # Omisión potencial
        if largo_o - largo_c > 50:
            anomalias.append(f"Párrafo {i+1}: Posible omisión de texto (Original era mucho más largo).")

        # Similitud
        ratio = difflib.SequenceMatcher(None, ori, cor).ratio()
        if ratio < 0.7:
            anomalias.append(f"Párrafo {i+1}: Cambio agresivo detectado (La IA podría haber reescrito la idea).")
            cambios_grandes.append((i+1, ori, cor, ratio))  # <<< NUEVO

    if anomalias:
        print(f"\n🚨 ANOMALÍAS DETECTADAS:")
        for a in anomalias[:10]:
            print(f"   - {a}")
        if len(anomalias) > 10:
            print(f"   ... y {len(anomalias)-10} más.")
    else:
        print(f"\n✅ No se detectaron cambios sospechosos de reescritura.")

    # 3B. MUESTRAS CONCRETAS DE ANTES/DESPUÉS (TOP 15)
    if cambios_grandes:
        ruta_muestra = os.path.join(CORREGIDO_FOLDER, f"MUESTRAS_CAMBIO_{nombre_original.replace('.docx','')}.txt")
        with open(ruta_muestra, "w", encoding="utf-8") as f:
            f.write("=== TOP 15 CAMBIOS AGRESIVOS ===\n\n")
            for idx, ori, cor, ratio in cambios_grandes[:150]:
                f.write(f"PÁRRAFO {idx} (similitud: {ratio:.2f})\n")
                f.write("--- ORIGINAL ---\n")
                f.write(ori.strip() + "\n")
                f.write("--- CORREGIDO ---\n")
                f.write(cor.strip() + "\n")
                f.write("=========================\n\n")
        print(f"📝 Muestras guardadas en: {ruta_muestra}")

    # 4. GENERAR COMPARATIVA VISUAL HTML
    comparador = difflib.HtmlDiff()
    html_contenido = comparador.make_file(parrafos_ori, parrafos_cor, "Original", "Corregido por IA")
    
    nombre_informe = f"AUDITORIA_{nombre_original.replace('.docx', '')}.html"
    ruta_html = os.path.join(CORREGIDO_FOLDER, nombre_informe)
    
    with open(ruta_html, "w", encoding="utf-8") as f:
        f.write(html_contenido)
    
    print(f"\n📄 Informe visual detallado: {nombre_informe}")

def main():
    archivos = [f for f in os.listdir(ORIGINAL_FOLDER) if f.endswith(".docx") and not f.startswith("~$")]
    for arc in archivos:
        auditar_archivos(arc)

if __name__ == "__main__":
    main()
