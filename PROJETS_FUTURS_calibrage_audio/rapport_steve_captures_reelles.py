"""
Rapport de diagnostic à partir des VRAIES captures d'écran Dirac Live de
Steve (une par enceinte, légende de couleur visible, ligne de mesure
"non corrigée" — case "Corrigée" décochée dans les options d'affichage).
Remplace les courbes synthétiques de `exemple_systeme_steve.py` par une
extraction automatique de pixels (`image_reader.py`) suivie d'un
ré-échantillonnage (`curve_resampling.py`) et du vrai moteur de
diagnostic (`diagnostic_engine.py`).

C'est la "piste retenue" documentée dans README.md, section "Pistes V2" :
relier `image_reader.py` au moteur de diagnostic sans étape manuelle,
en s'appuyant sur le nom d'enceinte déjà lisible sur chaque capture.

DONNÉES CLIENT HORS DÉPÔT : les captures elles-mêmes ne sont PAS
versionnées (données personnelles de Steve). Par défaut ce script lit
`~/Desktop/CAPTURE ECRAN COURBES/` ; passer un autre dossier en premier
argument de ligne de commande si besoin :
    python3 rapport_steve_captures_reelles.py [dossier_captures]

Chaque fichier attendu dans ce dossier (noms exacts, un par enceinte) :
    FRONT LEFT.png, FRONT RIGHT.png, CENTRALE.png,
    SURROUND LEFT.png, SURROUND RIGHT.png,
    SURROUND BACK LEFT.png, SURROUND BACK RIGHT.png,
    SUBWOOFERS.png  (Sub 1/LFE + Sub 2 superposés, Groupe ART 8 — une
    seule courbe disponible pour les 2 caissons, limite documentée dans
    l'avertissement ajouté au rapport ci-dessous).

CONFIGURATION PAR CANAL (pas un réglage universel unique) : 7 des 8
canaux s'extraient correctement avec la tolérance de couleur standard
(60, sans filtre de saturation). "Surround Right" est le seul exigeant
une configuration plus stricte (tolérance 40 + `min_saturation=0.5`)
car sa couleur de légende réelle (violet foncé) est anormalement proche
à la fois d'une ligne de grille à +20 dB et d'un dégradé de la bande
"plage détectée" de l'interface (distances de couleur ≈60 et ≈21,
sous la tolérance standard par pure coïncidence) — voir la docstring
d'en-tête de `image_reader.py` pour le détail complet des deux bugs
réels trouvés et corrigés. Une config universelle plus stricte a été
testée et rejetée : elle règle Surround Right mais troue 3 autres
canaux (Front Right, Surround Back Right, Subwoofers).
"""
from __future__ import annotations

import os
import sys

from curve_resampling import resample_linear
from diagnostic_engine import run_diagnostic
from exemple_systeme_steve import build_steve_system
from image_reader import (
    DIRAC_SCREENSHOT_2794x1538 as CALIBRATION,
    DIRAC_SCREENSHOT_2794x1538_PLOT_AREA as PLOT_AREA,
    detect_curve_color,
    extract_curve_points,
    validate_calibration_against_gridlines,
)
from models import MeasurementPoint, RoomInfo, ServiceLevel, Speaker, SpeakerMeasurement
from report_generator import generate_report

# Dimensions réelles de la pièce de Steve (confirmées par Steve le 03/10) :
# 5,50 m de long x 3,60 m de large x 2,50 m de haut. Permet au niveau
# Approfondi de confirmer formellement les modes axiaux (calcul physique),
# au lieu du seul clustering inter-canal (indice fort mais pas une preuve).
STEVE_ROOM = RoomInfo(length_m=5.50, width_m=3.60, height_m=2.50)

DEFAULT_CAPTURES_DIR = os.path.expanduser("~/Desktop/CAPTURE ECRAN COURBES")

# Mapping nom de fichier (sans extension) -> index dans build_steve_system().
# "Subwoofers" est traité à part plus bas (dupliqué vers les 2 caissons).
CAPTURE_FILE_TO_SPEAKER_INDEX = {
    "FRONT LEFT": 0,
    "FRONT RIGHT": 1,
    "CENTRALE": 2,
    "SURROUND LEFT": 3,
    "SURROUND RIGHT": 4,
    "SURROUND BACK LEFT": 5,
    "SURROUND BACK RIGHT": 6,
}
SUBWOOFERS_FILENAME = "SUBWOOFERS"
SUBWOOFER_SPEAKER_INDICES = (7, 8)

# color_tolerance, min_saturation par nom de fichier ; absent = défaut
# (60, 0.0). Voir le paragraphe "CONFIGURATION PAR CANAL" ci-dessus.
EXTRACTION_OVERRIDES: dict[str, tuple[float, float]] = {
    "SURROUND RIGHT": (40.0, 0.5),
}
DEFAULT_TOLERANCE_AND_SATURATION = (60.0, 0.0)

RESAMPLE_STEP_HZ = 1.5
RESAMPLE_F_MIN_HZ = 20.0
RESAMPLE_F_MAX_HZ = 300.0
SUBWOOFER_RESAMPLE_F_MAX_HZ = 257.0  # évite d'extrapoler au-delà du roll-off visible


def _extract_measurement(captures_dir: str, filename: str) -> list[MeasurementPoint]:
    path = os.path.join(captures_dir, f"{filename}.png")
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Capture manquante : {path}\n"
            "Vérifier le dossier passé en argument ou le contenu de "
            f"'{captures_dir}'."
        )
    tolerance, min_saturation = EXTRACTION_OVERRIDES.get(filename, DEFAULT_TOLERANCE_AND_SATURATION)
    # Garde-fou (04/10) : CALIBRATION est figée pour une résolution/zoom
    # précis (voir note "GARDE-FOU AJOUTÉ" dans image_reader.py). Si ce
    # script sert un jour à un autre client, cette vérification empêche
    # une extraction silencieusement fausse sur une capture différente.
    calibration_warnings = validate_calibration_against_gridlines(CALIBRATION, path, **PLOT_AREA)
    if calibration_warnings:
        raise RuntimeError(
            f"Calibration des axes incohérente pour '{path}' :\n- "
            + "\n- ".join(calibration_warnings)
            + "\nCette capture ne correspond probablement pas à la "
            "résolution/zoom validés pour DIRAC_SCREENSHOT_2794x1538 : "
            "ne pas extraire tant qu'une nouvelle calibration n'a pas été "
            "établie pour ce format, sous peine de recommander des "
            "réglages faux (ex. fréquence de coupure dangereuse)."
        )
    color = detect_curve_color(path, **PLOT_AREA)
    raw_points = extract_curve_points(
        path, CALIBRATION, color,
        color_tolerance=tolerance, min_saturation=min_saturation,
        **PLOT_AREA,
    )
    f_max = SUBWOOFER_RESAMPLE_F_MAX_HZ if filename == SUBWOOFERS_FILENAME else RESAMPLE_F_MAX_HZ
    return resample_linear(raw_points, step_hz=RESAMPLE_STEP_HZ, f_min=RESAMPLE_F_MIN_HZ, f_max=f_max)


def build_real_measurements(speakers: list[Speaker], captures_dir: str) -> list[SpeakerMeasurement]:
    measurements = []
    for filename, idx in CAPTURE_FILE_TO_SPEAKER_INDEX.items():
        points = _extract_measurement(captures_dir, filename)
        measurements.append(SpeakerMeasurement(speakers[idx], points))

    subwoofer_points = _extract_measurement(captures_dir, SUBWOOFERS_FILENAME)
    for idx in SUBWOOFER_SPEAKER_INDICES:
        # Même capture (Sub1/LFE + Sub2 superposés sur Groupe ART 8)
        # utilisée pour les 2 caissons — voir avertissement ajouté au
        # rapport dans main().
        measurements.append(SpeakerMeasurement(speakers[idx], list(subwoofer_points)))
    return measurements


def main() -> None:
    captures_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CAPTURES_DIR
    if not os.path.isdir(captures_dir):
        raise SystemExit(
            f"Dossier de captures introuvable : {captures_dir}\n"
            "Ces captures sont des données client, non versionnées dans "
            "le dépôt. Passer le bon chemin en argument : python3 "
            "rapport_steve_captures_reelles.py /chemin/vers/captures"
        )

    speakers = build_steve_system()
    measurements = build_real_measurements(speakers, captures_dir)

    report = run_diagnostic(
        speakers=speakers,
        measurements=measurements,
        service_level=ServiceLevel.APPROFONDI,
        room=STEVE_ROOM,
        support_level_triggers=[],
        # Groupage croisé RÉEL pratiqué par Steve (section 18/22 de la
        # base de connaissance) : la Surround Back Droite supporte la
        # Surround Droite, pas la hiérarchie standard. Fréquence de
        # croisement 80 Hz = valeur d'usine Marantz CINEMA 30 pour toutes
        # les enceintes hors Front (MANUAL_CROSSOVER_DEFAULT_OTHERS_HZ) ;
        # à confirmer/ajuster si Steve l'a modifiée manuellement.
        support_group_assignments=[
            ("Surround Back Droite (Elipson Prestige Facet II 14LCR)",
             "Surround Droite (Elipson Prestige Facet II 14LCR)",
             80.0),
        ],
    )
    report.warnings.insert(
        0,
        "Mesure des 2 caissons : une seule capture d'écran disponible "
        "affichant Subwoofer 1/LFE et Subwoofer 2 superposés (même Groupe "
        "ART 8) — la même courbe a été utilisée pour les deux par défaut, "
        "ce n'est PAS une mesure séparée confirmée par caisson.",
    )
    print(generate_report(report, client_name="Steve — Marantz CINEMA 30 7.2", include_studies=False))


if __name__ == "__main__":
    main()
