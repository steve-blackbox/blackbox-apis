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

Observations réelles rapportées par Steve (03/10, voir knowledge_base.py
section 39 pour l'explication scientifique peer-reviewed, et section 40
pour la stratégie de calibration) :
- Le système, une fois calibré dans SA pièce, reproduit une fréquence
  minimale mesurée de 17 Hz — EN DESSOUS des 20 Hz de la fiche
  constructeur SVS (mesurée en conditions proches du champ libre).
  Steve confirme explicitement que "sa pièce joue un rôle important
  dans les basses fréquences" : l'extension observée est cohérente
  avec l'effet de "pressure-field chamber" documenté dans une étude
  AES peer-reviewed (Pedersen & Møller 2013, knowledge_base.py section
  39) — à très basse fréquence, la pièce elle-même agit comme une
  chambre de pression qui renforce/étend la réponse perçue au-delà de
  la seule capacité du haut-parleur en champ libre.
- Stratégie de calibration des caissons recommandée par Gemini :
  utiliser LE MICRO comme référence objective pour régler d'abord
  toutes les enceintes à un même niveau sonore mesuré, PUIS augmenter
  DIRECTEMENT LE GAIN PHYSIQUE DU CAISSON lui-même (réglage sur
  l'appareil SVS, pas un menu logiciel Marantz) de +8 dB au-dessus de
  cette référence, PENDANT l'étape de calibration manuelle des niveaux
  par tonalités de test (avant la mesure micro Dirac elle-même) ; le
  processeur Marantz/Dirac calcule ensuite automatiquement, à partir
  de cette mesure, une atténuation LOGICIELLE sur le canal caisson
  pour revenir à l'équilibre cible. Objectif double confirmé par
  Steve : exploiter au maximum le room gain naturel de la pièce, et
  conserver la réserve maximale de puissance de l'ampli INTERNE du
  caisson (headroom) pour éviter toute distorsion lors de transitoires
  intenses (explosions) à volume élevé — voir knowledge_base.py
  section 40 pour le détail complet et le lien avec le cas réel de
  surchauffe ampli (section 33).
  ⚠️ **État réel actuel, différent de la recommandation** : la
  calibration EFFECTIVEMENT utilisée par Steve aujourd'hui (le fichier
  déjà analysé ART_VOIX-CINEMA.liveproject, sections 36-37) a été
  calculée avec un gain caisson de +5 dB (et une atténuation logicielle
  calculée en conséquence de -3,5 dB), PAS encore +8 dB — Steve a
  obtenu l'information du +8 dB optimal APRÈS avoir fait cette
  calibration. Voir knowledge_base.py,
  CURRENT_STEVE_CALIBRATION_USES_SUBOPTIMAL_5DB_NOT_8DB (section 40),
  pour le détail de cet écart et la piste d'amélioration identifiée
  mais non encore appliquée (recalibration à +8 dB).
  ⚠️ **+8 dB n'est PAS une constante universelle** : Steve précise que
  Gemini a déterminé cette valeur en fonction de SA chaîne électronique
  précise (type de connexion XLR/RCA Buckeye, gains associés, capacités
  des pré-amplificateurs du CINEMA 30 — déjà documentés section 27,
  XLR_VS_RCA_REFERENCE_LEVEL_PRINCIPLE et
  BUCKEYE_INPUT_SENSITIVITY_VS_HEADROOM_CALCULATION). Voir
  knowledge_base.py,
  GEMINI_8DB_VALUE_IS_SYSTEM_SPECIFIC_NOT_A_UNIVERSAL_CONSTANT
  (section 40) : cette valeur ne doit jamais être réutilisée telle
  quelle pour un autre client, même avec des caissons identiques.
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
            freq_max_hz=230,  # CONFIRMÉ (03/10) : bande passante ±3dB
            # officielle "20 Hz – 230 Hz" (homecinesolutions.fr, fiche
            # technique citant la mesure constructeur quasi-anéchoïque à
            # 2m ; confirme aussi par comparaison la génération précédente
            # 23-240Hz, modèle distinct). Corrige une valeur précédente de
            # 120 Hz qui n'était pas sourcée (estimation non confirmée).
        ),
        Speaker(
            "Caisson 2 (SVS 3000 Micro R|Evolution)",
            Role.LFE,
            freq_min_hz=20,  # CONFIRMÉ officiellement (svsound.com)
            freq_max_hz=230,  # CONFIRMÉ par Steve (03/10) — voir Caisson 1.
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
