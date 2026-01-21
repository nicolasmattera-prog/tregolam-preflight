# scripts/tooltip_helper.py
from docx.shared import RGBColor

def add_tooltip(run, original: str, corrected: str):
    """
    Añade texto visible con el cambio: [original→corregido]
    """
    run.text += f" [{original}→{corrected}]"
    run.font.superscript = True
    run.font.color.rgb = RGBColor(0, 0, 180)
