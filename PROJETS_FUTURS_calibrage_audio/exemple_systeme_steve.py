"""
Test de bout en bout du moteur de diagnostic sur le VRAI système de Steve
(Marantz CINEMA 30, 7.2), pour vérifier que l'algorithme fonctionne avant
d'aller plus loin. Lancer avec : python3 exemple_systeme_steve.py

Important — ce que ce script est, et ce qu'il n'est PAS :
- Le matériel déclaré ci-dessous (marques, modèles, rôles) est réel.
- Les `freq_min_hz` des enceintes Elipson sont des ESTIMATIONS PRUDENTES,
  pas des fiches constructeur vérifiées : malgré plusieurs tentatives de
  recherche (voir PROJETS_FUTURS.md, suite 15), aucune fiche technique
  chiffrée n'a pu être trouvée pour les Elipson Legacy 3220 / Facet 2.0
  14C / Facet 2.0 LCR (site Elipson sans tableau de specs exploitable,
  moteurs de recherche externes bloqués). Chaque valeur estimée est
  marquée `# ESTIMATION NON VÉRIFIÉE` ligne par ligne ci-dessous.
- Les courbes de mesure sont SYNTHÉTIQUES (générées par `_synthetic_curve`,
  comme dans `example_run.py`) : aucune vraie capture d'écran Dirac ni
  fichier `.liveproject` de Steve n'est disponible dans ce dossier de
  travail au moment de l'écriture de ce script. Ce test valide donc que
  le PIPELINE fonctionne techniquement (détection d'anomalie → diagnostic
  différentiel → rapport), pas un vrai diagnostic de la pièce de Steve.
  Pour un vrai diagnostic, remplacer `measurements` par des points lus sur
  de vraies captures Dirac (saisie manuelle) ou un vrai `.liveproject`
  (voir `liveproject_reader.py` et `image_reader.py`).

Config réelle (7.2, pas de hauteurs Atmos actives) :
  Marantz CINEMA 30 + Buckeye NCx252MP (ampli de puissance 8 canaux)
  - Façades : 2x Elipson Legacy 3220 (colonne 2.5 voies)
  - Centrale : 1x Elipson Facet 2.0 14C
  - Surround + Surround Back : 4x Elipson Facet 2.0 LCR
  - Caissons : 2x SVS 3000 Micro R|Evolution (specs officielles confirmées :
    extension jusqu'à 20 Hz, dual 9" actifs — voir svsound.com)
"""

from __future__ import annotations

from diagnostic_engine import run_diagnostic
from models import Role, RoomInfo, ServiceLevel, Speaker, SpeakerMeasurement
from example_run import _synthetic_curve
from report_generator import generate_report


def build_steve_system() -> list[Speaker]:
    return [
        Speaker(
            "Façade Gauche (Elipson Legacy 3220)",
            Role.FRONT_LEFT,
            freq_min_hz=45,  # ESTIMATION NON VÉRIFIÉE (colonne 2.5 voies, 2x 6.5")
        ),
        Speaker(
            "Façade Droite (Elipson Legacy 3220)",
            Role.FRONT_RIGHT,
            freq_min_hz=45,  # ESTIMATION NON VÉRIFIÉE (idem)
        ),
        Speaker(
            "Centrale (Elipson Facet 2.0 14C)",
            Role.CENTER,
            freq_min_hz=65,  # ESTIMATION NON VÉRIFIÉE (gamme compacte)
        ),
        Speaker(
            "Surround Gauche (Elipson Facet 2.0 LCR)",
            Role.SURROUND_LEFT,
            freq_min_hz=70,  # ESTIMATION NON VÉRIFIÉE (gamme compacte)
        ),
        Speaker(
            "Surround Droite (Elipson Facet 2.0 LCR)",
            Role.SURROUND_RIGHT,
            freq_min_hz=70,  # ESTIMATION NON VÉRIFIÉE (idem)
        ),
        Speaker(
            "Surround Back Gauche (Elipson Facet 2.0 LCR)",
            Role.SURROUND_BACK_LEFT,
            freq_min_hz=70,  # ESTIMATION NON VÉRIFIÉE (idem)
        ),
        Speaker(
            "Surround Back Droite (Elipson Facet 2.0 LCR)",
            Role.SURROUND_BACK_RIGHT,
            freq_min_hz=70,  # ESTIMATION NON VÉRIFIÉE (idem)
        ),
        Speaker(
            "Caisson 1 (SVS 3000 Micro R|Evolution)",
            Role.LFE,
            freq_min_hz=20,  # CONFIRMÉ officiellement (svsound.com)
            freq_max_hz=120,
        ),
        Speaker(
            "Caisson 2 (SVS 3000 Micro R|Evolution)",
            Role.LFE,
            freq_min_hz=20,  # CONFIRMÉ officiellement (svsound.com)
            freq_max_hz=120,
        ),
    ]


def main() -> None:
    speakers = build_steve_system()

    # Anomalies synthétiques injectées pour vérifier que le pipeline réagit
    # correctement sur un système à 7 canaux + 2 caissons (pas de vraie
    # mesure disponible — voir docstring d'en-tête).
    measurements = [
        SpeakerMeasurement(
            speakers[0],  # Façade Gauche
            _synthetic_curve(dip_at_hz=63.0, dip_db=8.0),
        ),
        SpeakerMeasurement(
            speakers[1],  # Façade Droite
            _synthetic_curve(peak_at_hz=63.0, peak_db=6.0),
        ),
        SpeakerMeasurement(
            speakers[2],  # Centrale
            _synthetic_curve(),  # courbe plate, pas d'anomalie injectée
        ),
        SpeakerMeasurement(
            speakers[3],  # Surround Gauche
            _synthetic_curve(dip_at_hz=120.0, dip_db=5.0),
        ),
        SpeakerMeasurement(
            speakers[4],  # Surround Droite
            _synthetic_curve(),
        ),
        SpeakerMeasurement(
            speakers[7],  # Caisson 1
            _synthetic_curve(peak_at_hz=45.0, peak_db=7.0),
        ),
        SpeakerMeasurement(
            speakers[8],  # Caisson 2
            _synthetic_curve(dip_at_hz=90.0, dip_db=6.0),
        ),
    ]

    print("=" * 78)
    print("SYSTÈME RÉEL DE STEVE — Niveau ESSENTIEL")
    print("(courbes SYNTHÉTIQUES — voir docstring d'en-tête de ce script)")
    print("=" * 78)
    report = run_diagnostic(
        speakers=speakers,
        measurements=measurements,
        service_level=ServiceLevel.ESSENTIEL,
        support_level_triggers=[],
    )
    print(generate_report(report, client_name="Steve — Marantz CINEMA 30 7.2"))


if __name__ == "__main__":
    main()
