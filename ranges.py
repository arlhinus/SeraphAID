# ranges.py — Rangos universales de referencia para SeraphAID
# Sprint 2: expandido de 6 → 47 marcadores.
# Fuentes orientativas: MedlinePlus, AASLD, NKF/KDIGO, ATS, WHO.
# Ajustar según laboratorio y fuente clínica específica.
from typing import Optional, Tuple

# ── Rangos universales (sin diferencia por sexo) ──────────────────────
UNIVERSAL_RANGES: dict[str, Tuple[float, float]] = {
    # Metabolismo básico
    "glucosa":          (70.0,  99.0),
    "col_total":        (0.0,  199.0),
    "hdl":              (40.0,  80.0),
    "ldl":              (0.0,  129.0),
    "trigliceridos":    (0.0,  149.0),
    # Renal
    "creatinina":       (0.6,   1.3),   # varía con edad/sexo — ver SEX_SPECIFIC
    "urea_bun":         (7.0,   25.0),  # mg/dL (BUN)
    "vfg_ckd_epi":      (60.0, 120.0), # <60 = ERC probable
    # Hepático
    "bil_total":        (0.2,   1.2),
    "bil_directa":      (0.0,   0.3),
    "bil_indirecta":    (0.0,   0.9),
    "fosfatasa_alc":    (44.0, 147.0),
    "prot_totales":     (6.0,   8.3),
    "albumina":         (3.5,   5.0),
    "ggt":              (5.0,  61.0),   # amplio para cubrir M y F
    "globulinas":       (2.0,   3.5),
    "rel_albumina_glob":(1.0,   2.5),
    # Coagulación
    "tp_seg":           (11.0,  14.0),
    "tp_pct":           (70.0, 120.0),
    "inr":              (0.8,   1.2),   # solo válido sin anticoagulantes
    "ttpa":             (25.0,  35.0),
    # Electrolitos
    "sodio":            (136.0, 145.0),
    "potasio":          (3.5,   5.0),
    "cloro":            (98.0, 106.0),
    "fosforo":          (2.5,   4.5),
    "magnesio":         (1.7,   2.2),
    # Inflamación / infección
    "pcr":              (0.0,   5.0),   # mg/L
    "procalcitonina":   (0.0,   0.5),   # ng/mL; >2 sepsis probable
    "ferritina":        (12.0, 200.0),  # ng/mL — ampliar con sexo abajo
    # Hemograma (índices)
    "leucocitos":       (4.5,  11.0),   # 10^3/µL
    "plaquetas":        (150.0,400.0),  # 10^3/µL
    "vcm":              (80.0, 100.0),  # fL
    "hcm":              (27.0,  33.0),  # pg
    "chcm":             (32.0,  36.0),  # g/dL
    "rdw_cv":           (11.5,  14.5),  # %
    "vpm":              (7.5,  12.5),   # fL
    # Fórmula diferencial (%)
    "neutro":           (40.0,  75.0),
    "linf":             (20.0,  45.0),
    "mono":             (2.0,   10.0),
    "eos":              (1.0,   6.0),
    "baso":             (0.0,   1.0),
    # Gases en sangre (arterial, adulto a nivel del mar)
    "ph":               (7.35,  7.45),
    "pco2":             (35.0,  45.0),  # mmHg
    "po2":              (80.0, 100.0),  # mmHg
    "hco3":             (22.0,  26.0),  # mmol/L
    "exceso_base":      (-2.0,   2.0),
    "sat_o2":           (95.0,  99.0),  # %
    "tco2":             (23.0,  27.0),
    # Tiroides
    "tsh":              (0.4,   4.0),   # mIU/L (TSH ultrasensible)
    "t4_libre":         (0.8,   1.8),   # ng/dL
    "t3_libre":         (2.3,   4.2),   # pg/mL
    # Vitaminas / minerales
    "vitamina_d":       (30.0, 100.0),  # ng/mL (25-OH-D); <20 deficiencia, 20-30 insuficiencia
    "vitamina_b12":     (200.0, 900.0), # pg/mL
}

# ── Rangos con diferencia por sexo ────────────────────────────────────
SEX_SPECIFIC: dict[str, dict[str, Tuple[float, float]]] = {
    "hemoglobina": {
        "M": (13.5, 17.5),
        "F": (12.0, 15.5),
    },
    "hematocrito": {
        "M": (41.0, 53.0),
        "F": (36.0, 46.0),
    },
    "eritrocitos": {
        "M": (4.5, 5.5),   # 10^6/µL
        "F": (4.0, 5.0),
    },
    "got_ast": {
        "M": (10.0, 40.0),
        "F": (10.0, 35.0),
    },
    "gpt_alt": {
        "M": (7.0, 56.0),
        "F": (7.0, 45.0),
    },
    "ferritina": {
        "M": (30.0, 300.0),
        "F": (12.0, 150.0),
    },
    "creatinina": {
        "M": (0.7, 1.3),
        "F": (0.5, 1.1),
    },
    "vhs": {
        "M": (0.0, 15.0),   # mm/h (Westergren)
        "F": (0.0, 20.0),
    },
    "acido_urico": {
        "M": (3.4, 7.0),    # mg/dL
        "F": (2.4, 6.0),
    },
}


def get_range(marker: str, sexo: Optional[str] = None) -> Optional[Tuple[float, float]]:
    """
    Retorna el rango de referencia (lo, hi) para un marcador.
    Prioriza rangos por sexo si están disponibles y se provee sexo válido.
    """
    key = (marker or "").lower().strip()
    sex = (sexo or "").upper().strip() if sexo else None

    # 1) Buscar en rangos con diferencia por sexo
    if key in SEX_SPECIFIC:
        if sex in SEX_SPECIFIC[key]:
            return SEX_SPECIFIC[key][sex]
        # fallback: promedio aproximado entre M y F
        vals = list(SEX_SPECIFIC[key].values())
        lo = min(v[0] for v in vals)
        hi = max(v[1] for v in vals)
        return (lo, hi)

    # 2) Buscar en rangos universales
    if key in UNIVERSAL_RANGES:
        return UNIVERSAL_RANGES[key]

    return None
