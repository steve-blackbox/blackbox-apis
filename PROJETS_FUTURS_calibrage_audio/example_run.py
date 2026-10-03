"""
Exemple complet d'exécution du moteur de diagnostic sur un système 5.1.4
fictif mais réaliste. Lancer avec : python3 example_run.py

Ce script sert aussi de démonstration minimale pour Steve : il montre
l'algorithme tourner de bout en bout, sans capture d'écran réelle (voir
README.md, section Limites — il n'y a pas de lecture d'image automatique
dans ce prototype, les mesures sont saisies/exportées en points fréquence/dB).
"""

from __future__ import annotations

import math

from diagnostic_engine import run_diagnostic
from models import (
    MeasurementPoint,
    Role,
    RoomInfo,
    ServiceLevel,
    Speaker,
    SpeakerMeasurement,
)
from report_generator import generate_report


def _synthetic_curve(
    base_db: float = 75.0,
    dip_at_hz: float | None = None,
    dip_db: float = 8.0,
    peak_at_hz: float | None = None,
    peak_db: float = 6.0,
) -> list[MeasurementPoint]:
    """Génère une courbe plate avec une anomalie injectée, pour avoir un
    cas de test reproductible sans vraie capture d'écran Dirac."""
    points = []
    freq = 20.0
    while freq <= 300.0:
        spl = base_db
        if dip_at_hz and abs(freq - dip_at_hz) < 4:
            spl -= dip_db * math.exp(-((freq - dip_at_hz) ** 2) / 20)
        if peak_at_hz and abs(freq - peak_at_hz) < 4:
            spl += peak_db * math.exp(-((freq - peak_at_hz) ** 2) / 20)
        points.append(MeasurementPoint(freq_hz=round(freq, 1), spl_db=round(spl, 1)))
        freq += 2.0
    return points


def build_example_system() -> list[Speaker]:
    return [
        Speaker("Façade Gauche", Role.FRONT_LEFT, freq_min_hz=45),
        Speaker("Façade Droite", Role.FRONT_RIGHT, freq_min_hz=45),
        Speaker("Centrale", Role.CENTER, freq_min_hz=60),
        Speaker("Surround Gauche", Role.SURROUND_LEFT, freq_min_hz=55),
        Speaker("Surround Droite", Role.SURROUND_RIGHT, freq_min_hz=55),
        Speaker("Hauteur Avant Gauche", Role.HEIGHT_FRONT_LEFT, freq_min_hz=70),
        Speaker("Hauteur Avant Droite", Role.HEIGHT_FRONT_RIGHT, freq_min_hz=70),
        Speaker("Caisson 1", Role.LFE, freq_min_hz=18, freq_max_hz=120),
        Speaker("Caisson 2", Role.LFE, freq_min_hz=16, freq_max_hz=150),
    ]


def main() -> None:
    speakers = build_example_system()

    # Mode de pièce calculable (~57 Hz pour une longueur de 6 m) injecté sur
    # la façade gauche, et une anomalie "hors mode" (~250 Hz) sur la façade
    # droite, pour exercer les deux branches du diagnostic.
    measurements = [
        SpeakerMeasurement(
            speakers[0],
            _synthetic_curve(dip_at_hz=57.0, dip_db=9.0),
        ),
        SpeakerMeasurement(
            speakers[1],
            _synthetic_curve(peak_at_hz=250.0, peak_db=7.0),
        ),
    ]

    room = RoomInfo(length_m=6.0, width_m=4.5, height_m=2.5, subwoofer_count=2)

    print("=" * 78)
    print("CAS 1 — Niveau ESSENTIEL (pas de dimensions de pièce)")
    print("=" * 78)
    report_essentiel = run_diagnostic(
        speakers=speakers,
        measurements=measurements,
        service_level=ServiceLevel.ESSENTIEL,
        support_level_triggers=[],
    )
    print(generate_report(report_essentiel, client_name="Cas de démonstration"))

    print("\n" + "=" * 78)
    print("CAS 2 — Niveau APPROFONDI (avec dimensions de pièce 6 x 4.5 x 2.5 m)")
    print("=" * 78)
    report_approfondi = run_diagnostic(
        speakers=speakers,
        measurements=measurements,
        service_level=ServiceLevel.APPROFONDI,
        room=room,
        support_level_triggers=[
            "réponses très différentes entre Surround Gauche et Surround Droite"
        ],
    )
    print(generate_report(report_approfondi, client_name="Cas de démonstration"))

    print("\n" + "=" * 78)
    print(
        "CAS 3 — Niveau APPROFONDI + préférence client déclarée "
        "(salle dédiée cinéma) : la courbe cible est tranchée, pas listée "
        "en options"
    )
    print("=" * 78)
    report_preference = run_diagnostic(
        speakers=speakers,
        measurements=measurements,
        service_level=ServiceLevel.APPROFONDI,
        room=room,
        support_level_triggers=[
            "réponses très différentes entre Surround Gauche et Surround Droite"
        ],
        target_curve_preference="cinema_dedie",
    )
    print(generate_report(report_preference, client_name="Cas de démonstration"))


if __name__ == "__main__":
    main()
