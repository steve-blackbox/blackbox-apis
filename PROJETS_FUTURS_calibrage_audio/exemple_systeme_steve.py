"""
Test de bout en bout du moteur de diagnostic sur le VRAI système de Steve
(Marantz CINEMA 30, 7.2), pour vérifier que l'algorithme fonctionne avant
d'aller plus loin. Lancer avec : python3 exemple_systeme_steve.py

Important — ce que ce script est, et ce qu'il n'est PAS :
- Le matériel déclaré ci-dessous (marques, modèles, rôles) est réel, et
  TOUTES les fiches techniques (Elipson, Buckeye) sont désormais de
  vraies valeurs constructeur officielles (voir knowledge_base.py,
  section 15, pour la méthode de récupération et les citations
  complètes) — ce n'est plus le cas des estimations prudentes utilisées
  avant le 03/10 (suite 22), qui restaient marquées comme telles.
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
  Marantz CINEMA 30 (pré-ampli/processeur)
    --[câbles RCA(M) à XLR(M) Buckeye, Canare L-4E6S Star Quad, schéma
       anti-ronflement de masse recommandé par Purifi/Hypex]-->
  Buckeye NCx252MP 8 canaux (4 modules Hypex NCx252MP, 250W/4Ω par canal,
  THD 0,0007 % @125W/4Ω, S/N 120dB — un canal du bloc 8 canaux inutilisé
  en config 7.2, sans souci de performance selon le fabricant)
  - Façades : 2x Elipson Legacy 3220 (colonne 2.5 voies, 35Hz-30kHz, 6Ω,
    89dB, 150W RMS)
  - Centrale : 1x Elipson Prestige Facet II 14C (2 voies, 43Hz-25kHz
    ±3dB, 6Ω nominal/4,5Ω min @180Hz, 93dB, 150W RMS)
  - Surround + Surround Back : 4x Elipson Prestige Facet II 14LCR (2
    voies, 53Hz-25kHz ±3dB, 6Ω nominal/4,6Ω min @202Hz, 93dB, 150W RMS)
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
            freq_min_hz=35,  # CONFIRMÉ officiellement (elipson.com)
            freq_max_hz=30000,
            impedance_nominal_ohms=6,
            sensitivity_db_1w1m=89,
            power_rms_w=150,
        ),
        Speaker(
            "Façade Droite (Elipson Legacy 3220)",
            Role.FRONT_RIGHT,
            freq_min_hz=35,  # CONFIRMÉ officiellement (elipson.com)
            freq_max_hz=30000,
            impedance_nominal_ohms=6,
            sensitivity_db_1w1m=89,
            power_rms_w=150,
        ),
        Speaker(
            "Centrale (Elipson Prestige Facet II 14C)",
            Role.CENTER,
            freq_min_hz=43,  # CONFIRMÉ officiellement (elipson.com, ±3dB)
            freq_max_hz=25000,
            impedance_nominal_ohms=6,
            sensitivity_db_1w1m=93,
            power_rms_w=150,
        ),
        Speaker(
            "Surround Gauche (Elipson Prestige Facet II 14LCR)",
            Role.SURROUND_LEFT,
            freq_min_hz=53,  # CONFIRMÉ officiellement (elipson.com, ±3dB)
            freq_max_hz=25000,
            impedance_nominal_ohms=6,
            sensitivity_db_1w1m=93,
            power_rms_w=150,
        ),
        Speaker(
            "Surround Droite (Elipson Prestige Facet II 14LCR)",
            Role.SURROUND_RIGHT,
            freq_min_hz=53,  # CONFIRMÉ officiellement (idem)
            freq_max_hz=25000,
            impedance_nominal_ohms=6,
            sensitivity_db_1w1m=93,
            power_rms_w=150,
        ),
        Speaker(
            "Surround Back Gauche (Elipson Prestige Facet II 14LCR)",
            Role.SURROUND_BACK_LEFT,
            freq_min_hz=53,  # CONFIRMÉ officiellement (idem)
            freq_max_hz=25000,
            impedance_nominal_ohms=6,
            sensitivity_db_1w1m=93,
            power_rms_w=150,
        ),
        Speaker(
            "Surround Back Droite (Elipson Prestige Facet II 14LCR)",
            Role.SURROUND_BACK_RIGHT,
            freq_min_hz=53,  # CONFIRMÉ officiellement (idem)
            freq_max_hz=25000,
            impedance_nominal_ohms=6,
            sensitivity_db_1w1m=93,
            power_rms_w=150,
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
            speakers[6],  # Surround Back Droite — mesure ajoutée pour
            # démontrer le calcul de niveau de support précis ci-dessous
            # (groupage croisé réellement pratiqué par Steve : "j'ai
            # regroupé la back right avec la surround right"). base_db
            # abaissé de 7dB par rapport aux autres (75.0 par défaut)
            # pour simuler un écart mesuré réaliste entre les deux.
            _synthetic_curve(base_db=68.0),
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
        # Groupage croisé RÉEL de Steve (section 18/22) : la Surround Back
        # Droite supporte la Surround Droite — pas la hiérarchie standard
        # par défaut. La fréquence de croisement (80 Hz) n'est PAS une
        # valeur confirmée par Steve, juste un exemple de démonstration
        # du calcul (voir avertissement dans le rapport).
        support_group_assignments=[
            ("Surround Back Droite (Elipson Prestige Facet II 14LCR)",
             "Surround Droite (Elipson Prestige Facet II 14LCR)",
             80.0),
        ],
    )
    print(generate_report(report, client_name="Steve — Marantz CINEMA 30 7.2"))


if __name__ == "__main__":
    main()
