# tests/test_regex_rules.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from regex_rules import corregir_texto

def test_tildes():
    assert corregir_texto("habia") == "había"
    assert corregir_texto("estan") == "están"

def test_comillas():
    assert corregir_texto('"hola"') == '«hola»'

def test_pasiva():
    assert corregir_texto("fue escrito por Juan") == "Juan escrito"

if __name__ == "__main__":
    test_tildes(); test_comillas(); test_pasiva()
    print("✅ Todos los tests pasan")
