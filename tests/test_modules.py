"""
tests/test_modules.py — Sanity checks para módulos extraídos en Sprint 3-B2.
Sprint 6: tests clínicos (HDL/ratio, BUN alias, bil_total, rangos extraídos, nuevos marcadores).
Ejecutar: python tests/test_modules.py
"""
import sys
import unittest.mock as mock

# Mock streamlit antes de importar módulos que lo usan
st_mock = mock.MagicMock()
st_mock.cache_data = lambda f: f
sys.modules['streamlit'] = st_mock

sys.path.insert(0, '.')

from modules.file_extractor import safe_text_normalize, parse_values_and_ranges
from modules.exam_interpreter import classify_with_margin, normalize_marker
from ranges import get_range


def test_safe_text_normalize():
    assert safe_text_normalize('Glucósá') == 'Glucosa'
    assert safe_text_normalize(None) == ''
    assert safe_text_normalize('') == ''


def test_parse_values_and_ranges():
    vals, rngs = parse_values_and_ranges('Glucosa: 120 mg/dL (70-99)')
    assert vals.get('glucosa') == 120.0
    assert rngs.get('glucosa') == (70.0, 99.0)
    vals2, _ = parse_values_and_ranges('')
    assert vals2 == {}


def test_classify_with_margin():
    assert classify_with_margin(120, (70, 99), 5) == 'alto'
    assert classify_with_margin(80, (70, 99), 5) == 'normal'
    assert classify_with_margin(98, (70, 99), 5) == 'limite'   # cerca del hi
    assert classify_with_margin(69, (70, 99), 5) == 'limite'   # cerca del lo
    assert classify_with_margin(65, (70, 99), 5) == 'bajo'
    assert classify_with_margin(None, (70, 99), 5) is None
    assert classify_with_margin(80, None, 5) is None


def test_normalize_marker():
    assert normalize_marker('Colesterol total') == 'col_total'
    assert normalize_marker('GOT (AST)') == 'got_ast'
    assert normalize_marker('Glucosa') == 'glucosa'
    assert normalize_marker('RDW-CV') == 'rdw_cv'
    assert normalize_marker('Saturacion O2') == 'sat_o2'


def test_get_range():
    assert get_range('glucosa') == (70.0, 99.0)
    assert get_range('hemoglobina', 'M') == (13.5, 17.5)
    assert get_range('hemoglobina', 'F') == (12.0, 15.5)
    assert get_range('sodio') == (136.0, 145.0)
    assert get_range('marcador_inexistente') is None


# ── Sprint 6: Tests clínicos ─────────────────────────────────────────────────

def test_hdl_not_confused_with_ratio():
    """HDL no debe capturarse desde líneas de índice/razón."""
    text = "Colesterol Total: 190\nÍndice Col/HDL: 3.4\nColesterol HDL: 52 mg/dL (40-80)"
    vals, rngs = parse_values_and_ranges(text)
    # El valor de HDL debe ser 52, no 3.4
    assert vals.get('hdl') == 52.0, f"HDL esperado 52.0, obtenido {vals.get('hdl')}"
    assert rngs.get('hdl') == (40.0, 80.0)


def test_urea_bun_alias_not_bare_urea():
    """urea_bun debe capturarse via 'nitrogeno ureico'/'bun', no via 'urea' genérico."""
    text = "Nitrogeno Ureico: 18 mg/dL (7-25)\nUremia: 6.4 mmol/L"
    vals, _ = parse_values_and_ranges(text)
    assert vals.get('urea_bun') == 18.0, f"urea_bun esperado 18.0, obtenido {vals.get('urea_bun')}"
    # Asegurarse que uremia no se confunde con urea_bun
    assert vals.get('urea_bun') != 6.4


def test_bil_total_parsed():
    """bil_total ahora está en los aliases y debe parsearse correctamente."""
    text = "Bilirrubina Total: 0.8 mg/dL (0.2-1.2)"
    vals, rngs = parse_values_and_ranges(text)
    assert vals.get('bil_total') == 0.8, f"bil_total esperado 0.8, obtenido {vals.get('bil_total')}"
    assert rngs.get('bil_total') == (0.2, 1.2)


def test_new_markers_ranges():
    """TSH y VHS deben tener rangos definidos; VHS diferenciado por sexo."""
    assert get_range('tsh') == (0.4, 4.0)
    assert get_range('vhs', 'M') == (0.0, 15.0)
    assert get_range('vhs', 'F') == (0.0, 20.0)
    assert get_range('acido_urico', 'M') == (3.4, 7.0)
    assert get_range('vitamina_d') == (30.0, 100.0)
    assert get_range('vitamina_b12') == (200.0, 900.0)


def test_normalize_marker_new():
    """normalize_marker resuelve los nuevos marcadores correctamente."""
    assert normalize_marker('TSH') == 'tsh'
    assert normalize_marker('T4 libre') == 't4_libre'
    assert normalize_marker('VHS') == 'vhs'
    assert normalize_marker('Ácido úrico') == 'acido_urico'
    assert normalize_marker('Vitamina D') == 'vitamina_d'
    assert normalize_marker('Vitamina B12') == 'vitamina_b12'
    assert normalize_marker('Nitrógeno ureico / BUN') == 'urea_bun'


def test_altered_first_ordering():
    """classify_with_margin permite ordenar alterados antes que normales."""
    markers = [
        ("Glucosa", 120.0, (70.0, 99.0)),   # alto
        ("Sodio",   140.0, (136.0, 145.0)), # normal
        ("HDL",      30.0, (40.0, 80.0)),   # bajo
    ]
    altered = [(l, v, r) for l, v, r in markers
               if classify_with_margin(v, r, 5.0) not in (None, 'normal')]
    normals = [(l, v, r) for l, v, r in markers
               if classify_with_margin(v, r, 5.0) == 'normal']
    assert len(altered) == 2
    assert len(normals) == 1
    assert normals[0][0] == "Sodio"


if __name__ == '__main__':
    test_safe_text_normalize()
    test_parse_values_and_ranges()
    test_classify_with_margin()
    test_normalize_marker()
    test_get_range()
    # Sprint 6
    test_hdl_not_confused_with_ratio()
    test_urea_bun_alias_not_bare_urea()
    test_bil_total_parsed()
    test_new_markers_ranges()
    test_normalize_marker_new()
    test_altered_first_ordering()
    print('Todos los tests pasaron.')
