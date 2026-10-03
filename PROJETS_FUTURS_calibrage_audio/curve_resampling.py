"""
Ré-échantillonnage à pas constant d'une courbe mesurée extraite par
`image_reader.extract_curve_points`.

POURQUOI CE MODULE EST NÉCESSAIRE : `diagnostic_engine.detect_anomalies`
suppose un pas de mesure proche de 1-2 Hz dans la zone modale (c'est la
base de ses rayons d'anneau par défaut, `inner_radius=3`/`outer_radius=8`
points — voir la docstring de `_ring_baseline`). Mais une extraction par
balayage de pixels sur un axe fréquence logarithmique produit un pas très
fin et IRRÉGULIER (ex. ~0,3 Hz vers 50 Hz, bien plus large vers 1 kHz) :
testé directement sur les 8 vraies courbes de Steve, ce pas fin fragmente
un vrai pic/creux large en une alternance de petits pics/creux très
proches (bruit de mesure fin), que `detect_anomalies` ne reconnaît plus
comme un seul phénomène. Un ré-échantillonnage linéaire à pas constant
(validé à 1,5 Hz entre 20 Hz et 300 Hz sur ces données réelles) restaure
la cohérence attendue par le moteur de diagnostic.
"""
from __future__ import annotations

from models import MeasurementPoint


def resample_linear(
    points: list[MeasurementPoint],
    step_hz: float = 1.5,
    f_min: float = 10.0,
    f_max: float = 300.0,
) -> list[MeasurementPoint]:
    """Interpole linéairement `points` (triés ou non, pas supposé régulier)
    vers un nouveau pas constant `step_hz` entre `f_min` et `f_max`.

    Les fréquences cibles hors de la plage couverte par `points` sont
    ignorées (pas d'extrapolation : une valeur devinée hors mesure serait
    trompeuse). Retourne une liste de `MeasurementPoint` triée par
    fréquence croissante."""
    pts = sorted(points, key=lambda p: p.freq_hz)
    freqs = [p.freq_hz for p in pts]
    dbs = [p.spl_db for p in pts]

    out: list[MeasurementPoint] = []
    f = f_min
    while f <= f_max:
        if f < freqs[0] or f > freqs[-1]:
            f += step_hz
            continue
        i = 0
        while i < len(freqs) - 1 and freqs[i + 1] < f:
            i += 1
        f0, f1 = freqs[i], freqs[min(i + 1, len(freqs) - 1)]
        d0, d1 = dbs[i], dbs[min(i + 1, len(freqs) - 1)]
        if f1 == f0:
            db = d0
        else:
            t = (f - f0) / (f1 - f0)
            db = d0 + t * (d1 - d0)
        out.append(MeasurementPoint(freq_hz=round(f, 2), spl_db=round(db, 2)))
        f += step_hz
    return out
