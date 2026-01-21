# scripts/tooltip_helper.py
from docx.oxml.shared import qn
from docx.oxml import OxmlElement

def add_tooltip(run, original: str, corrected: str):
    """
    Añade un bookmark XML al run con un tooltip:
    original: palabra antes
    corrected: palabra después
    """
    r = run._r
    bookmark_id = f"tip{id(run)}"  # único
    tooltip_text = f"original: {original}\ncorregido: {corrected}"

    # Crear bookmarkStart
    bookmark_start = OxmlElement('w:bookmarkStart')
    bookmark_start.set(qn('w:id'), bookmark_id)
    bookmark_start.set(qn('w:name'), bookmark_id)
    r.append(bookmark_start)

    # Atributo descripción (Word lo muestra como ScreenTip)
    rPr = run._element.get_or_add_rPr()
    rPr.set(qn('w:tooltip'), tooltip_text)

    # Crear bookmarkEnd
    bookmark_end = OxmlElement('w:bookmarkEnd')
    bookmark_end.set(qn('w:id'), bookmark_id)
    r.append(bookmark_end)
