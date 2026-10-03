"""
Moteur de diagnostic et de recommandations pour le calibrage Dirac Live ART.

Entrée : la liste du matériel déclaré par le client (`Speaker`), ses courbes
mesurées par enceinte (`SpeakerMeasurement`), le niveau de service choisi, et
en option les informations de pièce du niveau "Approfondi" (`RoomInfo`).

Sortie : un `DiagnosticReport` structuré et traçable — chaque recommandation
porte son `EvidenceLevel` (voir models.py) pour que rien ne soit présenté
comme une certitude inventée. Voir knowledge_base.py pour le détail et les
sources de chaque règle utilisée ici.
"""

from __future__ import annotations

import math

import knowledge_base as kb
from models import (
    AmplificationTopology,
    AmplifierChainSpec,
    Anomaly,
    DiagnosticReport,
    EvidenceLevel,
    Recommendation,
    Role,
    RoomInfo,
    ServiceLevel,
    Speaker,
    SpeakerMeasurement,
    TargetCurveControlPoint,
)

SPEED_OF_SOUND_MS = 343.0


# ---------------------------------------------------------------------------
# 1. Détection d'anomalies sur une courbe mesurée
# ---------------------------------------------------------------------------
def _ring_baseline(
    values: list[float], index: int, inner_radius: int = 3, outer_radius: int = 8
) -> float:
    """Tendance de référence en 'anneau' : moyenne des points situés entre
    `inner_radius` et `outer_radius` positions du point testé, EN EXCLUANT
    les points les plus proches (zone `inner_radius`).

    Pourquoi pas une simple moyenne mobile centrée : une moyenne mobile
    classique inclut le point anormal et ses voisins immédiats dans le
    calcul de sa propre référence, donc une anomalie large de plusieurs
    points abaisse (ou relève) sa propre tendance de comparaison et finit
    par se masquer elle-même. Testé et corrigé le 2026 sur ce prototype :
    un creux synthétique de 9 dB n'était détecté qu'à hauteur de 2,9 dB
    d'écart avec une moyenne mobile fenêtre=5, donc jamais signalé contre
    un seuil de 4 dB. L'anneau exclut la zone susceptible de contenir
    l'anomalie elle-même, donc la référence reste propre."""
    n = len(values)
    lo = max(0, index - outer_radius)
    hi = min(n, index + outer_radius + 1)
    ring = [values[j] for j in range(lo, hi) if abs(j - index) > inner_radius]
    if not ring:
        return values[index]
    return sum(ring) / len(ring)


def detect_anomalies(
    measurement: SpeakerMeasurement,
    threshold_db: float = 4.0,
    inner_radius: int = 3,
    outer_radius: int = 8,
) -> list[Anomaly]:
    """Repère les creux/pics qui s'écartent de plus de `threshold_db` d'une
    tendance de référence calculée en anneau (voir `_ring_baseline`).
    Détection volontairement simple : un prototype, pas un analyseur de
    courbes certifié — voir README.md, section Limites. Les rayons par
    défaut supposent un pas de mesure proche de 1-2 Hz dans la zone
    modale ; à ajuster si les courbes fournies ont un pas différent."""
    pts = [(p.freq_hz, p.spl_db) for p in sorted(
        measurement.points, key=lambda p: p.freq_hz
    )]
    if len(pts) < (2 * outer_radius + 1):
        return []  # pas assez de points pour construire un anneau fiable

    values = [spl for _, spl in pts]
    anomalies: list[Anomaly] = []
    for i, (freq, spl) in enumerate(pts):
        trend = _ring_baseline(values, i, inner_radius, outer_radius)
        delta = spl - trend
        if abs(delta) < threshold_db:
            continue
        kind = "creux" if delta < 0 else "pic"
        anomalies.append(
            Anomaly(
                speaker_name=measurement.speaker.name,
                freq_hz=freq,
                kind=kind,
                amplitude_db=round(abs(delta), 1),
            )
        )
    return _cluster_anomalies(anomalies)


def _cluster_anomalies(
    raw: list[Anomaly], max_gap_hz: float = 6.0
) -> list[Anomaly]:
    """Fusionne les points détectés adjacents et de même nature (creux ou
    pic) en une seule Anomaly représentative (celle de plus grande
    amplitude du groupe). Sans ce regroupement, un seul phénomène physique
    étalé sur plusieurs points de mesure produirait une ligne par point
    dans le rapport, redondante pour le client. `max_gap_hz` suppose un
    pas de mesure de l'ordre de 1-3 Hz dans la zone modale ; à ajuster si
    les courbes fournies ont un pas très différent."""
    if not raw:
        return []
    raw_sorted = sorted(raw, key=lambda a: a.freq_hz)
    clusters: list[list[Anomaly]] = [[raw_sorted[0]]]
    for anomaly in raw_sorted[1:]:
        prev = clusters[-1][-1]
        same_group = (
            anomaly.kind == prev.kind
            and (anomaly.freq_hz - prev.freq_hz) <= max_gap_hz
        )
        if same_group:
            clusters[-1].append(anomaly)
        else:
            clusters.append([anomaly])
    return [max(cluster, key=lambda a: a.amplitude_db) for cluster in clusters]


# ---------------------------------------------------------------------------
# 2. Modes propres d'une pièce rectangulaire (modes axiaux uniquement)
#    [Acoustique générale] — formule standard, domaine public.
# ---------------------------------------------------------------------------
def axial_room_modes(room: RoomInfo, max_freq_hz: float = 300.0) -> list[float]:
    """Retourne les fréquences des modes axiaux (un seul axe à la fois) en
    dessous de `max_freq_hz`. Les modes tangentiels/obliques, plus faibles
    et plus nombreux, sont volontairement ignorés dans ce prototype pour
    rester lisible — voir README.md, section Limites."""
    dims = [room.length_m, room.width_m, room.height_m]
    modes: list[float] = []
    for dim in dims:
        if dim <= 0:
            continue
        n = 1
        while True:
            freq = (SPEED_OF_SOUND_MS / 2.0) * (n / dim)
            if freq > max_freq_hz:
                break
            modes.append(round(freq, 1))
            n += 1
    return sorted(modes)


def _closest_mode(freq_hz: float, modes: list[float], tolerance_hz: float = 6.0):
    for mode in modes:
        if abs(mode - freq_hz) <= tolerance_hz:
            return mode
    return None


def diagnose_anomaly(
    anomaly: Anomaly, room: RoomInfo | None
) -> Anomaly:
    """Complète une anomalie détectée avec ses causes probables et l'action
    suggérée, en utilisant les dimensions de la pièce si elles sont
    disponibles (niveau Approfondi) pour affiner le diagnostic."""
    causes = list(
        kb.DIP_PROBABLE_CAUSES if anomaly.kind == "creux" else kb.PEAK_PROBABLE_CAUSES
    )

    if anomaly.freq_hz > kb.MODAL_REGION_UPPER_BOUND_HZ:
        causes = [
            c for c in causes if "mode de la pièce" not in c
        ] or causes
        anomaly.probable_causes = causes
        anomaly.suggested_action = (
            "Anomalie au-dessus de la zone modale typique : vérifier d'abord "
            "le haut-parleur et son environnement proche (mur, meuble) avant "
            "d'envisager un réglage logiciel."
        )
        return anomaly

    if room is not None:
        modes = axial_room_modes(room, max_freq_hz=kb.MODAL_REGION_UPPER_BOUND_HZ)
        matched = _closest_mode(anomaly.freq_hz, modes)
        if matched is not None:
            anomaly.probable_causes = [
                f"mode de la pièce probable (mode axial calculé à {matched} Hz "
                f"à partir des dimensions déclarées)"
            ]
            anomaly.suggested_action = (
                "Un mode de pièce avéré se corrige mal par la seule "
                "égalisation : tester d'abord un déplacement de l'enceinte "
                "ou du point d'écoute de 20 à 30 cm, puis ré-égaliser."
            )
            anomaly.is_confirmed_room_mode = True
            return anomaly
        anomaly.probable_causes = [
            c for c in causes if "mode de la pièce" not in c
        ] or causes
        anomaly.suggested_action = (
            "Aucun mode de pièce calculé ne correspond : cause plus "
            "probablement locale (proximité d'un mur/meuble ou phase avec un "
            "caisson). Tester un déplacement de l'enceinte en cause de "
            "quelques dizaines de centimètres."
        )
        return anomaly

    # Niveau Essentiel : pas de dimensions fournies, diagnostic non tranché.
    anomaly.probable_causes = causes
    anomaly.suggested_action = (
        "Dimensions de la pièce non fournies (niveau Essentiel) : "
        "plusieurs causes restent possibles. Le niveau Approfondi "
        "permettrait de trancher si c'est un mode de pièce calculable."
    )
    return anomaly


# ---------------------------------------------------------------------------
# 3. Recommandations de groupes de support et de plages de fréquence
# ---------------------------------------------------------------------------
def recommend_support_groups(speakers: list[Speaker]) -> list[Recommendation]:
    recs: list[Recommendation] = []
    subs = [s for s in speakers if s.is_subwoofer]

    if len(subs) >= 2:
        capacities = {round(s.freq_min_hz) for s in subs}
        if len(capacities) > 1:
            recs.append(
                Recommendation(
                    category="Groupes de support",
                    target=", ".join(s.name for s in subs),
                    action=(
                        "Séparer ces caissons en groupes individuels : ils "
                        "n'ont pas la même plage basse déclarée."
                    ),
                    evidence=EvidenceLevel.STORMAUDIO_OFFICIEL,
                    detail=(
                        "StormAudio recommande des groupes séparés pour les "
                        "enceintes/caissons de capacités différentes."
                    ),
                )
            )
        else:
            recs.append(
                Recommendation(
                    category="Groupes de support",
                    target=", ".join(s.name for s in subs),
                    action="Ces caissons peuvent partager un seul groupe de support.",
                    evidence=EvidenceLevel.STORMAUDIO_OFFICIEL,
                )
            )

    for speaker in speakers:
        hierarchy = kb.STORM_AUDIO_SUPPORT_HIERARCHY.get(speaker.role)
        if not hierarchy:
            continue
        recs.append(
            Recommendation(
                category="Hiérarchie de support",
                target=speaker.name,
                action=f"Ordre de support recommandé : {' > '.join(hierarchy)}.",
                evidence=EvidenceLevel.STORMAUDIO_OFFICIEL,
            )
        )

    recs.append(
        Recommendation(
            category="Fluidité des filtres (levier n°3)",
            target="ensemble du système",
            action=(
                "Limiter le support à un petit nombre d'enceintes pertinentes "
                "plutôt que d'activer tous les supports possibles."
            ),
            evidence=EvidenceLevel.HYPOTHESE_A_TESTER,
            detail=(
                "Indice de forum repris de la conversation source : limiter le "
                "support donnerait environ 90% du résultat avec de meilleurs "
                "graphiques de dispersion — un indice, pas une preuve. À "
                "confirmer par un test comparatif avant/après sur plusieurs cas."
            ),
        )
    )
    return recs


def _is_valid_support_donor(speaker: Speaker) -> bool:
    """Définition OFFICIELLE Dirac d'une enceinte de support valide (page
    'Why can't I select all support speakers?', voir
    knowledge_base.ART_CROSS_TERMS_COMPUTATIONAL_LIMIT) : 'any speaker
    capable of playing below 150 Hz [...] can be a support speaker.' Un
    caisson est toujours éligible par construction. Une enceinte
    satellite dont le plancher constructeur dépasse ce seuil ne peut
    PHYSIQUEMENT pas servir de support — la proposer serait une
    recommandation non pertinente (remarque explicite de Steve, 03/10 :
    'toutes les enceintes ne peuvent pas aider tout le monde, il faut
    que ça soit pertinent')."""
    return speaker.is_subwoofer or speaker.freq_min_hz <= kb.ART_UPPER_BOUND_HZ


def recommend_support_pairings(speakers: list[Speaker]) -> list[Recommendation]:
    """Déduit le groupage de support DÉCISIF pour CHAQUE enceinte
    non-caisson, à partir du SEUL système réel déclaré par le client
    (rôles présents) — jamais d'un groupage renseigné manuellement par
    l'opérateur. Répond explicitement à la demande de Steve (03/10) :
    l'algorithme doit conseiller n'importe quel client à partir de SON
    système, pas reproduire un choix fait pour un autre système.

    Choix volontairement tranché, PAS une liste d'options à tester : le
    groupage avec le(s) caisson(s) est toujours la recommandation
    retenue quand des caissons existent (hiérarchie officielle
    STORM_AUDIO_SUPPORT_HIERARCHY, "caissons d'abord"/"caissons (LFE)"
    pour tous les rôles concernés) — jamais une instruction du type
    "essayez, et changez si l'enceinte se localise", jugée inexploitable
    par un client (remarque explicite de Steve, 03/10 : "il faut donner
    le réglage optimal tout de suite [...] ça c'est pas possible").
    Le niveau de support PRÉCIS correspondant (en dB, à partir des
    mesures réelles) est calculé séparément par run_diagnostic via
    calculate_precise_support_level_db, en utilisant ce même groupage
    par défaut (voir section "déduction automatique" dans run_diagnostic)."""
    subs = [s for s in speakers if s.is_subwoofer]
    recs: list[Recommendation] = []

    if not subs:
        return recs

    sub_names = ", ".join(s.name for s in subs)
    for speaker in speakers:
        if speaker.is_subwoofer:
            continue
        if speaker.role == Role.CENTER:
            recs.append(
                Recommendation(
                    category="Groupage de support recommandé",
                    target=speaker.name,
                    action=f"Support retenu : {sub_names}.",
                    evidence=EvidenceLevel.STORMAUDIO_OFFICIEL,
                    detail=(
                        "La Centrale ne doit JAMAIS servir de support à "
                        "une autre enceinte (porte déjà l'essentiel des "
                        "dialogues), mais elle peut et doit recevoir le "
                        "support des caissons comme les autres canaux."
                    ),
                )
            )
            continue

        recs.append(
            Recommendation(
                category="Groupage de support recommandé",
                target=speaker.name,
                action=f"Support retenu : {sub_names}.",
                evidence=EvidenceLevel.STORMAUDIO_OFFICIEL,
                detail=(
                    "Déduit automatiquement du système déclaré (présence "
                    "de caisson(s), rôle de l'enceinte), pas d'un choix "
                    "renseigné manuellement — conforme à la hiérarchie "
                    "officielle StormAudio qui place toujours le(s) "
                    "caisson(s) en premier pour ce rôle."
                ),
            )
        )

        alt_role = kb.SUPPORT_PAIRING_ROLE_MAP.get(speaker.role)
        alt_speaker = next((s for s in speakers if s.role == alt_role), None) if alt_role else None
        if alt_speaker is not None:
            if _is_valid_support_donor(alt_speaker):
                recs.append(
                    Recommendation(
                        category="Groupage de support — configuration alternative existante",
                        target=speaker.name,
                        action=(
                            f"Configuration croisée avec {alt_speaker.name} "
                            f"(enceinte à hauteur d'oreille) : pratiquée par "
                            f"certains clients, acceptée par la hiérarchie "
                            f"officielle, mais PAS la recommandation retenue "
                            f"ici — le support par caisson reste le réglage "
                            f"décisif par défaut."
                        ),
                        evidence=EvidenceLevel.STORMAUDIO_OFFICIEL,
                        detail=(
                            "Mentionné à titre informatif seulement : si cette "
                            "configuration alternative est effectivement en "
                            "place, son niveau de support précis peut être "
                            "calculé sur demande à partir des mesures réelles "
                            "(voir support_group_assignments de run_diagnostic)."
                        ),
                    )
                )
            else:
                # Pas une simple absence d'information : exclusion
                # explicite et justifiée, pour que le client comprenne
                # QUE cette enceinte-là ne peut pas rendre service à une
                # autre (pertinence réelle, pas un choix arbitraire).
                recs.append(
                    Recommendation(
                        category="Groupage de support — option écartée (non pertinente)",
                        target=speaker.name,
                        action=(
                            f"{alt_speaker.name} n'est PAS une option de "
                            f"support valide pour cette enceinte : son "
                            f"plancher déclaré ({alt_speaker.freq_min_hz:.0f} Hz) "
                            f"dépasse les {kb.ART_UPPER_BOUND_HZ:.0f} Hz au-"
                            f"dessus desquels Dirac n'autorise plus une "
                            f"enceinte comme support."
                        ),
                        evidence=EvidenceLevel.MARANTZ_DIRAC_OFFICIEL,
                        detail=(
                            "Définition officielle Dirac : 'any speaker "
                            "capable of playing below 150 Hz can be a "
                            "support speaker' — une enceinte dont le "
                            "constructeur ne garantit pas de descendre sous "
                            "ce seuil est écartée d'office, quel que soit "
                            "son rôle dans le système."
                        ),
                    )
                )

    recs.append(
        Recommendation(
            category="Limite de calcul du processeur (cross terms)",
            target="ensemble du système",
            action=(
                "Ne PAS cumuler plusieurs sources de support simultanées "
                "pour une même enceinte (ex. caisson(s) ET une enceinte "
                "satellite en même temps) : un seul groupage décisif par "
                "enceinte, celui retenu ci-dessus."
            ),
            evidence=EvidenceLevel.MARANTZ_DIRAC_OFFICIEL,
            detail=(
                "Contrainte matérielle réelle, pas un choix esthétique : "
                "'One cross term is allocated every time a speaker is "
                "selected to support another speaker [...] The maximum "
                "number of available cross terms is DSP DEPENDENT' "
                "(knowledge_base.ART_CROSS_TERMS_COMPUTATIONAL_LIMIT). "
                "Chaque relation de support (y compris une configuration "
                "alternative, voir ci-dessus) consomme ce budget partagé et "
                "limité du processeur — au-delà d'un certain nombre de "
                "relations activées, Dirac affiche une erreur et oblige à "
                "désélectionner des enceintes de support. Le groupage "
                "retenu ici reste volontairement minimal (le(s) caisson(s) "
                "seulement) pour rester dans ce budget sur n'importe quel "
                "système, même les plus chargés (9.1.6, etc.)."
            ),
        )
    )
    return recs


def recommend_frequency_ranges(speakers: list[Speaker]) -> list[Recommendation]:
    recs: list[Recommendation] = []
    for speaker in speakers:
        if speaker.is_subwoofer:
            continue
        low = max(speaker.freq_min_hz, kb.DIRAC_DEFAULT_LOW_FLOOR_HZ)
        recs.append(
            Recommendation(
                category="Plage de fréquence",
                target=speaker.name,
                action=(
                    f"Régler la fréquence basse de support à {low:.0f} Hz "
                    f"(fiche technique du constructeur), avec chevauchement "
                    f"d'environ {kb.RECOMMENDED_OVERLAP_HZ:.0f} Hz avec le(s) "
                    f"caisson(s)."
                ),
                evidence=EvidenceLevel.STORMAUDIO_OFFICIEL,
                detail=(
                    "Toujours se baser sur la fiche technique, jamais sur le "
                    "seul balayage mesuré en pièce (les modes de la pièce "
                    "faussent la mesure). Une plage trop basse mal choisie "
                    "peut endommager l'enceinte."
                ),
            )
        )
    return recs


def recommend_target_curves(
    speakers: list[Speaker],
    target_curve_preference: str | None = None,
) -> list[Recommendation]:
    """`target_curve_preference` : préférence du CLIENT recueillie en
    amont ('harman' pour un usage mixte musique/cinéma, 'cinema_dedie'
    pour une salle dédiée au cinéma) — jamais déduite ni inventée par le
    moteur. Le choix entre les options de façade/caisson déjà
    documentées (kb.TARGET_CURVES_BY_ROLE) relève du GOÛT du client, pas
    d'un calcul physique : confirmé par le cas réel de la 'courbe
    maison.targetcurve' de Steve (voir
    kb.UMIK1_CALIBRATION_VS_CUSTOM_TARGET_CURVE_COMPARISON) — un choix
    de design volontaire, pas un artefact de mesure. Sans préférence
    connue, le moteur reste honnête et liste les options plutôt que d'en
    choisir une arbitrairement."""
    recs: list[Recommendation] = []
    has_front = any(s.role in {Role.FRONT_LEFT, Role.FRONT_RIGHT, Role.CENTER} for s in speakers)
    if has_front:
        facade_options = kb.TARGET_CURVES_BY_ROLE["façade (G/D/centre)"]
        if target_curve_preference == "harman":
            chosen = next(o for o in facade_options if "Harman" in o)
            recs.append(
                Recommendation(
                    category="Courbe cible",
                    target="façade (gauche/droite/centre)",
                    action=f"Appliquer la courbe cible : {chosen}.",
                    evidence=EvidenceLevel.PRINCIPE_ACOUSTIQUE,
                    detail=(
                        "Préférence client déclarée : usage mixte musique/cinéma. "
                        + kb.TARGET_CURVE_COHERENCE_RULE
                    ),
                )
            )
        elif target_curve_preference == "cinema_dedie":
            chosen = next(o for o in facade_options if "Cinema Target" in o)
            recs.append(
                Recommendation(
                    category="Courbe cible",
                    target="façade (gauche/droite/centre)",
                    action=f"Appliquer la courbe cible : {chosen}.",
                    evidence=EvidenceLevel.PRINCIPE_ACOUSTIQUE,
                    detail=(
                        "Préférence client déclarée : salle dédiée au cinéma. "
                        + kb.TARGET_CURVE_COHERENCE_RULE
                    ),
                )
            )
        else:
            recs.append(
                Recommendation(
                    category="Courbe cible",
                    target="façade (gauche/droite/centre)",
                    action="Options : " + " ; ".join(facade_options),
                    evidence=EvidenceLevel.PRINCIPE_ACOUSTIQUE,
                    detail=(
                        kb.TARGET_CURVE_COHERENCE_RULE
                        + " Ce choix dépend du goût du client, pas d'un calcul "
                        "physique (cas réel déjà documenté : une courbe cible "
                        "personnalisée peut être un choix de design volontaire) "
                        "— demander explicitement sa préférence (cinéma dédié "
                        "ou usage mixte musique/cinéma) avant de trancher."
                    ),
                )
            )
    if any(s.is_subwoofer for s in speakers):
        sub_options = kb.TARGET_CURVES_BY_ROLE["caisson(s) / LFE"]
        if target_curve_preference == "cinema_dedie":
            chosen = next(o for o in sub_options if "Cinema Target" in o)
            recs.append(
                Recommendation(
                    category="Courbe cible",
                    target="caisson(s) / LFE",
                    action=f"Appliquer la courbe cible : {chosen}.",
                    evidence=EvidenceLevel.PRINCIPE_ACOUSTIQUE,
                    detail="Préférence client déclarée : salle dédiée au cinéma.",
                )
            )
        else:
            detail = ""
            if target_curve_preference == "harman":
                detail = (
                    "Préférence client déclarée : usage mixte musique/cinéma — "
                    "reste à préciser 6 ou 8 dB selon l'impact recherché, "
                    "aucune règle sourcée ne permet de trancher ce dernier "
                    "point à la place du client."
                )
            recs.append(
                Recommendation(
                    category="Courbe cible",
                    target="caisson(s) / LFE",
                    action="Options : " + " ; ".join(sub_options),
                    evidence=EvidenceLevel.PRINCIPE_ACOUSTIQUE,
                    detail=detail,
                )
            )
    if any(s.role in kb.STORM_AUDIO_SUPPORT_HIERARCHY and s.role not in {Role.FRONT_LEFT, Role.FRONT_RIGHT, Role.CENTER, Role.LFE} for s in speakers):
        # Une seule option documentée ici (pas d'ambiguïté de goût comme
        # pour la façade/le caisson) : recommandation ferme directement.
        recs.append(
            Recommendation(
                category="Courbe cible",
                target="surround / hauteur",
                action=(
                    "Appliquer la courbe cible : "
                    f"{kb.TARGET_CURVES_BY_ROLE['surround / hauteur'][0]}."
                ),
                evidence=EvidenceLevel.PRINCIPE_ACOUSTIQUE,
            )
        )
    return recs


def recommend_support_level(trigger_notes: list[str]) -> Recommendation:
    if trigger_notes:
        return Recommendation(
            category="Niveau de support",
            target="ensemble du système",
            action=(
                f"Affiner par pas de {kb.SUPPORT_LEVEL_STEP_DB} dB autour de "
                f"{kb.SUPPORT_LEVEL_DEFAULT_DB} dB (plage légale "
                f"{kb.SUPPORT_LEVEL_MIN_DB} dB = contribution MAXIMALE à "
                f"{kb.SUPPORT_LEVEL_MAX_DB} dB = contribution MINIMALE — "
                f"⚠️ échelle contre-intuitive : {kb.SUPPORT_LEVEL_MIN_DB} dB "
                f"a PLUS d'effet que {kb.SUPPORT_LEVEL_MAX_DB} dB, malgré "
                f"un nombre numériquement plus négatif), en comparant les "
                f"filtres calculés à chaque pas."
            ),
            evidence=EvidenceLevel.RETOUR_EXPERIENCE_STEVE,
            detail=(
                "Déclencheur(s) identifié(s) : " + "; ".join(trigger_notes) +
                ". Rappel : le seuil d'audibilité d'un écart de niveau est "
                "généralement cité autour de 1 dB — un réglage à 0,5 dB près "
                "n'a d'effet garanti que sur les filtres calculés, pas "
                "forcément à l'oreille. Voir SUPPORT_LEVEL_SCALE_IS_"
                "COUNTERINTUITIVE (section 32) pour l'échelle inversée."
            ),
        )
    return Recommendation(
        category="Niveau de support",
        target="ensemble du système",
        action=f"Garder la valeur par défaut ({kb.SUPPORT_LEVEL_DEFAULT_DB} dB).",
        evidence=EvidenceLevel.STORMAUDIO_OFFICIEL,
        detail="Aucun déclencheur identifié ne justifie un réglage fin.",
    )


# ---------------------------------------------------------------------------
# 4. Calculs précis chiffrés (fréquence + dB) — 100% génériques : ne
#    dépendent que des paramètres reçus, jamais d'un système particulier.
#    Répond à la demande de Steve de produire des valeurs actionnables
#    (quelle fréquence, quel niveau en dB, quelle plage) plutôt que des
#    recommandations qualitatives seules.
# ---------------------------------------------------------------------------
def _interpolate_spl_at(
    measurement: SpeakerMeasurement, freq_hz: float, window_hz: float
) -> float | None:
    """Moyenne des points mesurés dans une fenêtre [freq_hz-window,
    freq_hz+window] — lisse le bruit de mesure ponctuel plutôt que de
    prendre un seul point exact qui pourrait être un artefact. Retourne
    None si aucun point mesuré ne tombe dans cette fenêtre (plutôt que
    d'extrapoler/deviner une valeur)."""
    nearby = [
        p.spl_db for p in measurement.points
        if abs(p.freq_hz - freq_hz) <= window_hz
    ]
    if not nearby:
        return None
    return sum(nearby) / len(nearby)


def calculate_precise_support_level_db(
    main_measurement: SpeakerMeasurement,
    support_measurement: SpeakerMeasurement,
    crossover_hz: float,
    window_hz: float = kb.SUPPORT_LEVEL_INTERPOLATION_WINDOW_HZ,
) -> Recommendation:
    """Calcule un niveau de Support Level PRÉCIS (arrondi au pas réel de
    0,5 dB confirmé empiriquement, clampé dans la plage légale officielle
    -24 à -1 dB) à partir de l'écart de SPL RÉELLEMENT MESURÉ entre
    l'enceinte principale et l'enceinte de support, à leur fréquence de
    croisement déclarée — pas une valeur par défaut générique. Fonctionne
    pour N'IMPORTE QUELLE paire d'enceintes groupées, y compris un
    groupage personnalisé/croisé (ex. Surround Back supportant Surround,
    comme pratiqué par Steve)."""
    main_spl = _interpolate_spl_at(main_measurement, crossover_hz, window_hz)
    support_spl = _interpolate_spl_at(support_measurement, crossover_hz, window_hz)

    if main_spl is None or support_spl is None:
        return Recommendation(
            category="Niveau de support (précis)",
            target=f"{support_measurement.speaker.name} -> {main_measurement.speaker.name}",
            action=(
                f"Pas assez de points mesurés autour de {crossover_hz:.0f} Hz "
                f"pour calculer une valeur précise : garder la valeur par "
                f"défaut ({kb.SUPPORT_LEVEL_DEFAULT_DB} dB) en attendant une "
                f"mesure plus dense à cette fréquence."
            ),
            evidence=EvidenceLevel.STORMAUDIO_OFFICIEL,
        )

    raw_level_db = support_spl - main_spl
    stepped = round(raw_level_db / kb.SUPPORT_LEVEL_STEP_DB) * kb.SUPPORT_LEVEL_STEP_DB
    clamped = max(kb.SUPPORT_LEVEL_MIN_DB, min(kb.SUPPORT_LEVEL_MAX_DB, stepped))

    clamp_note = ""
    if clamped != stepped:
        if clamped == kb.SUPPORT_LEVEL_MIN_DB:
            clamp_note = (
                f" (écart brut hors plage légale, plafonné à "
                f"{kb.SUPPORT_LEVEL_MIN_DB} dB = contribution MAXIMALE "
                f"autorisée)"
            )
        else:
            clamp_note = (
                f" (écart brut hors plage légale, plafonné à "
                f"{kb.SUPPORT_LEVEL_MAX_DB} dB = contribution MINIMALE "
                f"autorisée)"
            )

    return Recommendation(
        category="Niveau de support (précis)",
        target=f"{support_measurement.speaker.name} -> {main_measurement.speaker.name}",
        action=(
            f"Régler le Support Level à {clamped:+.1f} dB (pas de "
            f"{kb.SUPPORT_LEVEL_STEP_DB} dB){clamp_note}."
        ),
        evidence=EvidenceLevel.CALCUL_DEPUIS_MESURE_REELLE,
        precise_value_db=clamped,
        detail=(
            f"Calculé à partir de l'écart RÉEL mesuré à {crossover_hz:.0f} Hz "
            f"± {window_hz:.0f} Hz : {support_measurement.speaker.name} = "
            f"{support_spl:.1f} dB SPL, {main_measurement.speaker.name} = "
            f"{main_spl:.1f} dB SPL, écart brut = {raw_level_db:+.1f} dB, "
            f"arrondi au pas réel puis clampé dans la plage officielle "
            f"[{kb.SUPPORT_LEVEL_MIN_DB} dB = contribution MAXIMALE, "
            f"{kb.SUPPORT_LEVEL_MAX_DB} dB = contribution MINIMALE] "
            f"(ART_PARAMETER_SUPPORT_LEVEL_OFFICIAL_TABLE, section 17 — "
            f"⚠️ échelle contre-intuitive, voir SUPPORT_LEVEL_SCALE_IS_"
            f"COUNTERINTUITIVE, section 32)."
        ),
    )


def calculate_support_frequency_range(
    speaker: Speaker, fsiso_hz: float = kb.DEFAULT_FSISO_HZ
) -> Recommendation:
    """F-support Low = la plus haute entre la limite basse constructeur
    et le plancher officiel (50 Hz pour une enceinte non-caisson, 20 Hz
    pour un caisson — ART_PARAMETER_F_SUPPORT_LOW_HIGH_OFFICIAL, section
    17). F-support High = Fsiso par défaut (point de départ officiel : la
    doc Dirac indique de partir haut puis de redescendre SEULEMENT si une
    enceinte de support devient localisable — processus itératif, pas un
    calcul unique), MAIS jamais au-delà de ce que l'enceinte peut
    physiquement reproduire (fiche constructeur, `freq_max_hz`) — remarque
    explicite de Steve (03/10) : 'il faut respecter les caractéristiques
    des hauts-parleurs'. Note de vérification (03/10) : les caissons de
    Steve (SVS 3000 Micro R|Evolution) ont en réalité une bande passante
    officielle 20-230 Hz (±3dB, homecinesolutions.fr) — AU-DESSUS de
    Fsiso (150 Hz), donc ce clamp matériel ne s'y déclenche PAS pour son
    système précis ; il reste nécessaire pour toute enceinte (caisson ou
    satellite) dont la fiche constructeur indique un plafond sous Fsiso,
    cas générique couvert par cette fonction pour n'importe quel client."""
    floor_hz = 20.0 if speaker.is_subwoofer else kb.DIRAC_DEFAULT_LOW_FLOOR_HZ
    f_support_low = max(speaker.freq_min_hz, floor_hz)
    f_support_high = min(fsiso_hz, speaker.freq_max_hz)
    clamped_by_hardware = f_support_high < fsiso_hz
    # Garde-fou : une fiche constructeur mal renseignée ne doit jamais
    # produire une plage inversée (High < Low).
    f_support_high = max(f_support_high, f_support_low)

    return Recommendation(
        category="Plage de fréquence de support",
        target=speaker.name,
        action=(
            f"F-support Low = {f_support_low:.0f} Hz, F-support High = "
            f"{f_support_high:.0f} Hz"
            + (
                f" (plafonné : {speaker.name} ne reproduit pas au-delà de "
                f"{speaker.freq_max_hz:.0f} Hz selon sa fiche constructeur)"
                if clamped_by_hardware
                else " (point de départ ; à redescendre progressivement "
                f"seulement si {speaker.name} devient localisable "
                "individuellement dans le résultat)"
            )
            + "."
        ),
        evidence=EvidenceLevel.MARANTZ_DIRAC_OFFICIEL,
        freq_range_hz=(round(f_support_low, 1), round(f_support_high, 1)),
        detail=(
            f"F-support Low basé sur la fiche constructeur "
            f"({speaker.freq_min_hz:.0f} Hz) plafonné au plancher officiel "
            f"({floor_hz:.0f} Hz pour "
            f"{'un caisson' if speaker.is_subwoofer else 'une enceinte non-caisson'}"
            f"). F-support High part de Fsiso ({fsiso_hz:.0f} Hz, valeur par "
            f"défaut officielle ou personnalisée si réglée) mais ne dépasse "
            f"jamais la limite haute déclarée par le constructeur "
            f"({speaker.freq_max_hz:.0f} Hz) — demander à Dirac d'appliquer "
            f"une correction de support au-delà de ce que l'enceinte peut "
            f"reproduire n'aurait aucun sens acoustique. Plage légale "
            f"F-support Low à Fsiso, ici réduite par la fiche constructeur."
        ),
    )



def calculate_room_mode_control_points(
    anomalies: list[Anomaly],
) -> list[TargetCurveControlPoint]:
    """Calcule des points de contrôle de courbe cible pour les PICS et
    les CREUX confirmés comme modes de pièce — jamais en BOOSTANT, dans
    aucun des deux cas (limite physique déjà documentée, section 14, et
    confirmée par un cas RÉEL vécu par Steve : des gains de correction
    automatique jusqu'à 12dB — soit environ x15,85 en puissance
    électrique — ont fait chauffer dangereusement son ampli, section 33).
    Pour un PIC : abaisser la cible réduit l'agressivité de la correction
    automatique. Pour un CREUX : abaisser la cible (PAS la remonter)
    permet à la cible de suivre partiellement le creux naturel, ce qui
    EMPÊCHE Dirac de tenter un boost automatique massif pour le combler
    — c'est le correctif direct du problème vécu par Steve. Dans les
    deux cas, seule une fraction prudente de l'écart mesuré est visée
    (ROOM_MODE_TARGET_REDUCTION_FACTOR, section 30), pas 100%, car un
    mode n'a pas la même amplitude à toutes les positions d'écoute."""
    points: list[TargetCurveControlPoint] = []
    for a in anomalies:
        if not a.is_confirmed_room_mode:
            continue
        reduction_db = round(a.amplitude_db * kb.ROOM_MODE_TARGET_REDUCTION_FACTOR, 1)
        if a.kind == "pic":
            reason = (
                f"Pic de mode de pièce confirmé à {a.freq_hz:.0f} Hz "
                f"(+{a.amplitude_db:.1f} dB mesuré sur {a.speaker_name}) — "
                f"cible abaissée de {reduction_db:.1f} dB "
                f"({int(kb.ROOM_MODE_TARGET_REDUCTION_FACTOR * 100)}% de "
                f"l'écart, pas 100%) pour réduire l'agressivité de la "
                f"correction automatique."
            )
        else:  # creux
            reason = (
                f"Creux de mode de pièce confirmé à {a.freq_hz:.0f} Hz "
                f"(-{a.amplitude_db:.1f} dB mesuré sur {a.speaker_name}) — "
                f"cible ABAISSÉE (pas remontée) de {reduction_db:.1f} dB "
                f"pour que Dirac n'essaie PAS de forcer un boost massif "
                f"ici : un creux de mode est une annulation acoustique, "
                f"la combler électriquement demanderait un gain "
                f"disproportionné sans régler la cause physique — cas "
                f"RÉEL vécu par Steve (gains jusqu'à 12dB ayant fait "
                f"chauffer son ampli, section 33)."
            )
        points.append(
            TargetCurveControlPoint(
                freq_hz=a.freq_hz,
                gain_db=-reduction_db,
                speaker_name=a.speaker_name,
                reason=reason,
            )
        )
    return points


def detect_dangerous_gain_anomalies(anomalies: list[Anomaly]) -> list[str]:
    """Génère un avertissement pour TOUTE anomalie (pic ou creux, mode de
    pièce confirmé ou non) dont l'amplitude mesurée dépasse le seuil de
    prudence (DANGEROUS_EQ_GAIN_THRESHOLD_DB, section 33) — directement
    motivé par le cas réel vécu par Steve (gains jusqu'à 12dB ayant fait
    chauffer son ampli). S'applique à TOUTES les anomalies, pas
    seulement celles confirmées comme modes de pièce : même un creux
    local (proximité mur/meuble, SBIR) peut inciter Dirac à tenter un
    gain de correction tout aussi dangereux."""
    warnings: list[str] = []
    for a in anomalies:
        if a.amplitude_db >= kb.DANGEROUS_EQ_GAIN_THRESHOLD_DB:
            power_ratio = 10 ** (a.amplitude_db / 10)
            warnings.append(
                f"⚠️ {a.speaker_name} à {a.freq_hz:.0f} Hz : écart mesuré de "
                f"{a.amplitude_db:.1f} dB (≈x{power_ratio:.1f} en puissance "
                f"électrique si Dirac tentait de le combler entièrement) — "
                f"au-delà du seuil de prudence de "
                f"{kb.DANGEROUS_EQ_GAIN_THRESHOLD_DB:.0f} dB. Vérifier "
                f"qu'un point de contrôle de courbe cible limite bien la "
                f"correction automatique à cette fréquence (voir "
                f"STEVE_AMPLIFIER_OVERHEATING_FROM_MASSIVE_EQ_GAIN, "
                f"section 33 — cas réel de surchauffe ampli)."
            )
    return warnings


def evaluate_subwoofer_pre_gain_headroom_strategy(
    chain: AmplifierChainSpec,
    proposed_input_gain_increase_db: float,
    baseline_required_output_vrms: float | None = None,
) -> tuple[float | None, str]:
    """Généralise à N'IMPORTE QUEL client la stratégie de pré-gain caisson
    rapportée par Steve (knowledge_base.py, section 40-41) : augmenter le
    gain d'entrée physique du caisson de X dB AVANT la mesure Dirac
    réduit d'autant le signal que le préampli/processeur doit fournir
    pour le même niveau SPL de référence, ce qui préserve d'autant sa
    marge de sortie (headroom de tension) pour les transitoires
    (explosions) — calcul d'électronique analogique de base
    (20*log10 d'un ratio de tensions), pas une formule Dirac/SVS
    officielle ni une valeur inventée.

    Précision importante sur `chain.topology` (remarque explicite de
    Steve, 03/10) : un caisson reste, dans la quasi-totalité des
    installations, un appareil ACTIF alimenté par une sortie ligne LFE
    dédiée du processeur — même sur un système où les ENCEINTES
    PRINCIPALES utilisent les amplis INTÉGRÉS de l'AVR plutôt qu'un
    ampli de puissance externe (cas de Steve). Le calcul en Vrms
    ci-dessous reste donc structurellement applicable au canal caisson
    dans les 2 topologies. La nuance réelle entre les 2 cas porte sur
    la FIABILITÉ de `preamp_max_output_vrms` lui-même : un processeur
    conçu et utilisé comme préampli pur (AmplificationTopology.
    EXTERNAL_POWER_AMP, toutes sorties en ligne y compris vers les
    enceintes principales) soigne généralement cette caractéristique de
    façon plus homogène qu'un AVR tout-intégré où la sortie LFE est une
    fonction annexe moins mise en avant — d'où l'avertissement
    supplémentaire ajouté au message quand topology=INTEGRATED_AMP.

    Retourne (marge_apres_pre_gain_db, message) :
    - Si `chain.preamp_max_output_vrms` ET `baseline_required_output_vrms`
      sont fournis : calcule la marge RÉELLE en dB avant/après le
      pré-gain proposé.
    - Sinon (cas réel de Steve : le niveau de sortie max du CINEMA 30
      n'a jamais été retrouvé, voir section 27) : retourne None pour la
      valeur chiffrée plutôt que d'inventer un chiffre, mais confirme
      littéralement le principe qualitatif dans le message — le gain de
      marge attendu est, par construction mathématique directe, égal au
      gain d'entrée ajouté (tant qu'aucun maillon n'est déjà saturé)."""
    topology_caveat = ""
    if chain.topology == AmplificationTopology.INTEGRATED_AMP:
        topology_caveat = (
            " ⚠️ Topologie INTEGRATED_AMP déclarée pour le reste du "
            "système : la sortie LFE dédiée au caisson reste une "
            "sortie ligne distincte (le calcul ci-dessous reste "
            "applicable), mais sa valeur Vrms max est généralement "
            "moins documentée/mise en avant par le fabricant que sur "
            "un appareil conçu comme préampli pur — vérifier la fiche "
            "constructeur avec une prudence accrue avant d'utiliser ce "
            "chiffre."
        )

    if (
        chain.preamp_max_output_vrms is None
        or baseline_required_output_vrms is None
    ):
        return None, (
            "Marge non chiffrable : il manque le niveau de sortie "
            "maximal du préampli/processeur avant distorsion et/ou le "
            "niveau de signal requis au point de référence (donnée "
            "manquante chez Steve lui-même — voir section 27, "
            "BUCKEYE_INPUT_SENSITIVITY_VS_HEADROOM_CALCULATION). Le "
            "PRINCIPE reste valable sans ce chiffre : augmenter le "
            f"gain d'entrée du caisson de "
            f"{proposed_input_gain_increase_db:.1f} dB réduit d'autant "
            "le signal que le préampli doit fournir pour le même "
            "niveau de référence, ce qui préserve d'autant sa marge de "
            "sortie pour les transitoires — à condition qu'aucun "
            f"maillon de la chaîne ne soit déjà saturé.{topology_caveat}"
        )

    baseline_margin_db = 20 * math.log10(
        chain.preamp_max_output_vrms / baseline_required_output_vrms
    )
    new_required_output_vrms = baseline_required_output_vrms / (
        10 ** (proposed_input_gain_increase_db / 20)
    )
    new_margin_db = 20 * math.log10(
        chain.preamp_max_output_vrms / new_required_output_vrms
    )
    return new_margin_db, (
        f"Marge de sortie du préampli avant pré-gain : "
        f"{baseline_margin_db:.1f} dB. Après un pré-gain caisson de "
        f"+{proposed_input_gain_increase_db:.1f} dB : "
        f"{new_margin_db:.1f} dB (gain de marge de "
        f"{new_margin_db - baseline_margin_db:.1f} dB)."
        f"{topology_caveat}"
    )


# ---------------------------------------------------------------------------
# 5. Point d'entrée principal
# ---------------------------------------------------------------------------
def run_diagnostic(
    speakers: list[Speaker],
    measurements: list[SpeakerMeasurement],
    service_level: ServiceLevel,
    room: RoomInfo | None = None,
    support_level_triggers: list[str] | None = None,
    support_group_assignments: list[tuple[str, str, float]] | None = None,
    fsiso_hz: float = kb.DEFAULT_FSISO_HZ,
    target_curve_preference: str | None = None,
) -> DiagnosticReport:
    """`support_group_assignments` est volontairement une liste libre de
    triplets (nom enceinte support, nom enceinte principale, fréquence de
    croisement en Hz) plutôt qu'une règle déduite automatiquement du rôle
    : ceci permet de représenter N'IMPORTE QUEL schéma de groupage choisi
    par le client, standard OU personnalisé/croisé (ex. Surround Back
    Right supportant Surround Right, comme pratiqué par Steve), condition
    nécessaire pour que l'algorithme s'adapte à n'importe quelle
    configuration cliente plutôt qu'à un seul cas particulier.
    `target_curve_preference` : voir recommend_target_curves — préférence
    du client ('harman' ou 'cinema_dedie'), à recueillir explicitement
    pour que le rapport tranche au lieu de lister un menu d'options."""
    report = DiagnosticReport(service_level=service_level)

    if service_level == ServiceLevel.ESSENTIEL and room is not None:
        report.warnings.append(
            "Informations de pièce fournies mais niveau Essentiel choisi : "
            "elles ne seront pas utilisées pour affiner le diagnostic modal."
        )
        room = None
    if service_level == ServiceLevel.APPROFONDI and room is None:
        report.warnings.append(
            "Niveau Approfondi choisi sans informations de pièce : "
            "diagnostic dégradé au niveau Essentiel pour les modes de pièce."
        )

    for measurement in measurements:
        for anomaly in detect_anomalies(measurement):
            report.anomalies.append(diagnose_anomaly(anomaly, room))

    report.warnings.extend(detect_dangerous_gain_anomalies(report.anomalies))

    report.recommendations.extend(recommend_support_groups(speakers))
    report.recommendations.extend(recommend_support_pairings(speakers))
    report.recommendations.extend(recommend_frequency_ranges(speakers))
    report.recommendations.extend(
        recommend_target_curves(speakers, target_curve_preference)
    )
    report.recommendations.append(
        recommend_support_level(support_level_triggers or [])
    )

    # Calculs précis génériques : plage de fréquence par enceinte.
    for speaker in speakers:
        report.recommendations.append(
            calculate_support_frequency_range(speaker, fsiso_hz=fsiso_hz)
        )

    # Calculs précis génériques : niveau de support à 0,5 dB près, pour
    # CHAQUE relation support->principal — DÉDUITE automatiquement par
    # défaut (caisson(s) supportant chaque enceinte non-caisson/non
    # déjà couverte par une déclaration explicite du client), complétée
    # par les relations personnalisées/croisées explicitement déclarées
    # (support_group_assignments). Répond à la demande de Steve (03/10) :
    # l'algorithme doit conseiller n'importe quel client à partir de SON
    # système, pas seulement calculer ce qu'on lui a dit de calculer, et
    # produire une valeur décisive, pas une hypothèse à tester en salle.
    measurements_by_name = {m.speaker.name: m for m in measurements}
    declared_assignments = list(support_group_assignments or [])
    declared_main_names = {main_name for _, main_name, _ in declared_assignments}

    auto_assignments: list[tuple[str, str, float]] = []
    subs = [s for s in speakers if s.is_subwoofer]
    if subs:
        sub_name = subs[0].name
        for speaker in speakers:
            if speaker.is_subwoofer or speaker.name in declared_main_names:
                continue
            auto_assignments.append(
                (sub_name, speaker.name, kb.MANUAL_CROSSOVER_DEFAULT_OTHERS_HZ)
            )
        if auto_assignments:
            report.warnings.append(
                f"Niveau de support calculé automatiquement pour "
                f"{len(auto_assignments)} enceinte(s) en supposant un "
                f"groupage par défaut avec {sub_name} à "
                f"{kb.MANUAL_CROSSOVER_DEFAULT_OTHERS_HZ:.0f} Hz (crossover "
                f"d'usine Marantz pour les canaux hors Front) — à ajuster "
                f"uniquement si le crossover réellement configuré diffère."
            )

    for support_name, main_name, crossover_hz in declared_assignments + auto_assignments:
        support_m = measurements_by_name.get(support_name)
        main_m = measurements_by_name.get(main_name)
        if support_m is None or main_m is None:
            report.warnings.append(
                f"Groupage déclaré '{support_name}' -> '{main_name}' ignoré : "
                f"mesure introuvable pour l'un des deux noms."
            )
            continue
        if not _is_valid_support_donor(support_m.speaker):
            # Pertinence réelle, pas seulement un indice qualitatif :
            # calculer un niveau précis pour un donneur physiquement
            # incapable de descendre sous 150 Hz serait une valeur sans
            # sens acoustique (définition officielle Dirac, voir
            # _is_valid_support_donor). On avertit au lieu de calculer.
            report.warnings.append(
                f"Groupage déclaré '{support_name}' -> '{main_name}' ignoré "
                f"pour le calcul précis : {support_name} n'est pas une "
                f"enceinte de support valide (plancher déclaré "
                f"{support_m.speaker.freq_min_hz:.0f} Hz > "
                f"{kb.ART_UPPER_BOUND_HZ:.0f} Hz, seuil officiel Dirac)."
            )
            continue
        report.recommendations.append(
            calculate_precise_support_level_db(main_m, support_m, crossover_hz)
        )

    # Calculs précis génériques : points de contrôle de courbe cible pour
    # les pics confirmés comme modes de pièce (jamais pour un creux).
    control_points = calculate_room_mode_control_points(report.anomalies)
    if control_points:
        report.recommendations.append(
            Recommendation(
                category="Points de contrôle courbe cible (modes de pièce)",
                target=", ".join(sorted({p.speaker_name for p in control_points if p.speaker_name})) or "voir détail",
                action="; ".join(
                    f"{p.freq_hz:.0f} Hz : {p.gain_db:+.1f} dB" for p in control_points
                ),
                evidence=EvidenceLevel.HYPOTHESE_A_TESTER,
                control_points=control_points,
                detail=(
                    "Rappel important (section 26) : si Bass Control est "
                    "actif, la partie basse fréquence de la courbe cible est "
                    "COMMUNE à tout le système — un point sous le crossover "
                    "du groupe affecte tous les groupes, pas seulement "
                    "l'enceinte visée ici. Justification de chaque point : "
                    "voir 'Pourquoi' ci-dessous."
                ),
            )
        )

    if service_level == ServiceLevel.APPROFONDI and room is not None:
        report.recommendations.append(
            Recommendation(
                category="Placement",
                target="caisson(s)",
                action=(
                    "Vérifier la symétrie gauche/droite des distances aux "
                    "murs ; un caisson isolé dans un coin renforce "
                    "généralement les modes plutôt que de les atténuer."
                ),
                evidence=EvidenceLevel.PRINCIPE_ACOUSTIQUE,
            )
        )

    return report
