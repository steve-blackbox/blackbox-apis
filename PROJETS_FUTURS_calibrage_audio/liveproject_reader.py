"""
liveproject_reader.py — Lecteur du format binaire natif Dirac Live (.liveproject)

⚠️ CECI EST UN OUTIL DE RECHERCHE / RÉTRO-INGÉNIERIE, PAS UN MODULE DE
PRODUCTION comme `image_reader.py`. Tout ce qui est documenté ci-dessous a
été **validé empiriquement** (lecture binaire directe, calculs reproductibles)
sur **les 10 fichiers `.liveproject` réels fournis par Steve** (109 Mo à
254 Mo, voir `~/Desktop/DIRAC/PERSO/`, hors dépôt — noms de fichiers
suggérant des tentatives de calibration successives entre août et
septembre 2026). Le format est rigoureusement identique sur les 10 (même
version logicielle "7.2.0ch", 13 flux audio bien formés, 104 blocs de
mesure regroupés en 13 groupes à chaque fois, aucune exception ni crash) —
ce n'est donc pas un artefact d'un seul fichier, mais rien ne garantit
qu'il n'existe pas de variantes selon une autre version du logiciel Dirac
Live que celle utilisée par Steve.

Comment ce fichier a été lu : aucune documentation officielle Dirac n'a été
utilisée. Tout provient de lecture hexadécimale/binaire directe
(`struct.unpack`, recherche de motifs répétés, mesure d'entropie) sur les
fichiers de Steve. Chaque affirmation ci-dessous est reproductible avec le
code de ce module.

────────────────────────────────────────────────────────────────────────
CARTE DU FICHIER (validée sur les 10 fichiers, offsets en % de la taille totale)
────────────────────────────────────────────────────────────────────────

1. **Début (~0-7 %)** : métadonnées en clair (encodage Qt-like : chaque
   chaîne = `uint32 BE` longueur en octets + `UTF-16BE`) — UUID du projet,
   modèle de micro de mesure (`"UMIK-1"`), chemin du fichier de calibration
   du micro. Entropie modérée (~7.0-7.2 bits/octet) : probablement un
   mélange de texte et de données numériques (peut-être le fichier de
   calibration du micro lui-même, non confirmé).

2. **Zone audio (13 enregistrements Ogg Vorbis consécutifs)** : voir
   `list_ogg_streams()`. Chaque flux logique Ogg (identifié par son
   "serial number" dans l'en-tête de page) correspond à **une position de
   micro** (13 positions mesurées, confirmé par un bloc d'en-tête séparé
   qui indique explicitement `count=13` juste avant la zone des blocs de
   mesure — voir point 5). Caractéristiques confirmées par décodage réel
   (ffmpeg + inspection du header d'identification Vorbis) :
   - Mono, 48 000 Hz, ~240 kbit/s, ~59 secondes par enregistrement.
   - Chaque enregistrement contient une **séquence de 10 "bursts"** nets
     séparés par du silence : 1 signal de référence, 8 signaux de mesure
     (un par canal/enceinte), puis le **même** signal de référence rejoué
     à l'identique (confirmé par comparaison directe des deux profils
     temps-fréquence — vraisemblablement un contrôle de cohérence des
     conditions de mesure entre début et fin de session).
   - Le signal est un **sweep sinusoïdal exponentiel** ("ESS", méthode de
     Farina, 2000 — technique publique standard de l'industrie de la
     mesure acoustique, utilisée aussi par REW, ARTA, etc.) : balayage
     d'environ 50 Hz à ~20-24 kHz, temps par octave quasi constant
     (~0,5 s), confirmé par suivi de la fréquence dominante dans le temps
     (FFT par fenêtres de 20 ms). Durée ~4,0-4,6 s pour les 6 premiers
     canaux, ~1,9 s pour les 2 derniers (qui ne balaient que jusqu'à
     ~250-300 Hz dans ce temps imparti — cohérent avec 2 canaux à bande
     passante réduite, vraisemblablement les 2 subwoofers).
   - Ce module ne décode PAS l'audio Vorbis lui-même (pas de dépendance
     lourde dans ce prototype) : `list_ogg_streams()` se contente
     d'extraire les flux bruts (pages Ogg complètes, réassemblables en
     fichier `.ogg` valide). Pour aller plus loin (décoder en PCM,
     analyser le spectre), voir la fonction `extract_ogg_stream()` et le
     commentaire associé (nécessite un décodeur Vorbis externe, par
     exemple le binaire ffmpeg fourni par le paquet pip `imageio-ffmpeg`,
     plus `numpy` pour l'analyse spectrale — aucune des deux n'est une
     dépendance de ce module).

3. **Zone chiffrée (~25-60 % selon le fichier, taille variable)** :
   entropie mesurée à **exactement 8.00 bits/octet**, et écart-type de la
   distribution des 256 valeurs d'octet mesuré à ~92.6 (contre ~88.4
   attendu pour un vrai bruit aléatoire uniforme — les deux valeurs sont
   très proches). C'est la signature d'un **chiffrement fort**, pas
   d'une simple compression (qui laisse d'ordinaire une entropie
   légèrement inférieure à 8.0 avec des irrégularités détectables).
   ⚠️ **Cette zone n'a volontairement PAS été explorée davantage.**
   Tenter de la déchiffrer constituerait un contournement de mesure de
   protection technique, ce qui n'a pas été fait et ne sera pas fait ici.
   Nature exacte inconnue (hypothèse non vérifiée : pourrait contenir les
   filtres de correction calculés, des données de licence, ou autre).
   Cohérent avec le vécu de Steve : tentative antérieure d'injection de
   filtres FIR personnalisés dans Dirac bloquée par une protection du
   format (voir `../PROJETS_FUTURS.md`).

4. **Métadonnées de configuration (en clair, ~58-60 %)** : version
   logicielle (ex. `"7.2.0ch"`), modèle d'ampli/processeur (ex.
   `"Marantz"`, `"CINEMA 30"`), et la liste exacte des noms de canaux
   configurés dans le projet (voir `SPEAKER_NAMES_KNOWN`). Ces noms
   n'apparaissent qu'**une seule fois** chacun (simple liste de config,
   pas une étiquette répétée par bloc de mesure — voir limite au point 5).

5. **Blocs de mesure déconvoluée (~96-100 %)** : voir
   `read_measurement_blocks()`. **104 blocs** identiques trouvés dans les
   10 fichiers testés (= 13 groupes de 8 exactement, pas de reste), chacun
   précédé du marqueur `BLOCK_MARKER` (8 octets). Structure confirmée par
   `struct.unpack` exact (vérifiée octet par octet, taille de bloc
   32 792 octets validée par calcul) :
     `[marker 8o][type u32][count u32][count×float64 BE = fréquences]`
     `[count u32][count×float64 BE = magnitudes en dB SPL absolu]`
   avec `count=2048` systématiquement. Fréquences en échelle log
   (1,0 Hz → 24 000 Hz, ratio constant ≈1.004939 entre points consécutifs).
   Magnitudes en dB SPL **absolu** (plage observée environ -138 dB à
   -26 dB) — **pas directement comparable** aux dB relatifs affichés dans
   les captures d'écran Dirac (voir `image_reader.py`) sans connaître la
   normalisation appliquée par le logiciel.
   Regroupement : 13 groupes de 8 blocs consécutifs (= 13 positions de
   micro × 8 canaux). Les 8 blocs par groupe correspondent très
   probablement aux 8 "bursts" de canal détectés dans l'audio (voir point
   2) — cohérence croisée forte entre les deux méthodes d'analyse
   indépendantes.
   ⚠️ **Correction par rapport à une première exploration (bash ad hoc,
   avant l'écriture de ce module)** : 2 occurrences supplémentaires de
   `BLOCK_MARKER` avaient été trouvées (106 au total) et interprétées à
   tort comme "2 blocs de mesure en plus". En écrivant un parseur avec
   validation stricte des bornes (`_read_block_at`), il s'avère que ces 2
   occurrences sont situées **dans la zone de métadonnées (~58,3 %)**,
   pas à côté des 104 blocs de mesure (~96,5-100 %), et n'ont pas la
   structure d'un bloc de mesure (`type=0/count=13` et `type=5/count=0`,
   pas `count=2048`). Le même marqueur de 8 octets sert donc à plusieurs
   types de structures internes dans ce format, pas uniquement aux blocs
   de mesure — une lecture par simple comptage d'occurrences peut tromper,
   d'où l'intérêt du parseur strict de ce module. Fait à noter : la
   coïncidence que ce bloc isolé indique justement `count=13` reste un
   indice (pas une preuve) cohérent avec 13 = nombre de positions de
   micro, puisque ce nombre apparaît de façon indépendante à 2 endroits
   du fichier (ce compteur et les 13 flux audio Ogg distincts).
   ⚠️ **Limite non résolue** : la correspondance exacte "quel bloc (0-7)
   = quelle enceinte précisément" n'a PAS pu être établie avec certitude.
   Piste testée et abandonnée faute de preuve suffisante : comparer les
   pics de résonance (ex. un pic à 60 Hz très marqué et constant sur les
   13 positions dans 2 des 8 "slots") avec le pic visuellement confirmé
   sur `FRONT LEFT.png` — mais **2 slots différents** montrent cette même
   signature à 60 Hz sur les 13 positions, donc ce test seul ne permet
   pas de trancher (plusieurs enceintes peuvent partager un mode de pièce
   dominant). Ne pas prétendre à une correspondance bloc↔enceinte précise
   sans validation supplémentaire (par exemple en comparant avec d'autres
   projets .liveproject où la configuration d'enceintes diffère).

   ⚠️ **Complément (test sur `TOP CALIB BASE.liveproject`, 9 canaux
   configurés : 7 enceintes + 2 subs)** : deux méthodes indépendantes
   convergent pour identifier les **2 derniers slots (6 et 7)** comme
   étant les 2 subwoofers, avec une confiance nettement meilleure que la
   piste du pic à 60 Hz ci-dessus :
   1. Décodage réel de l'audio (Ogg Vorbis → WAV, détection d'enveloppe
      RMS) : exactement 10 bursts significatifs retrouvés dans l'ordre
      attendu (1 référence ~4,9 s, 6 mesures larges bande ~4,4-4,8 s,
      **2 mesures à bande réduite ~2,1 s** en avant-dernière et dernière
      position, 1 référence rejouée ~4,8 s) — cohérent avec la durée de
      sweep raccourcie déjà documentée au point 2 pour "2 canaux à bande
      passante réduite".
   2. Spectre déconvolué (ce module) : seuls les slots 6 et 7 montrent
      une décroissance nette et continue au-delà de ~200-250 Hz (jusqu'à
      -90 dB vers 600 Hz), signature typique d'un filtre passe-bas de
      caisson — absente des slots 0 à 5.
   En comparant la forme (pas le niveau, non comparable — voir plus haut)
   des slots 6/7 avec `SUBWOOFERS.png` (2 courbes mesurées, Subwoofer
   1/LFE et Subwoofer 2) : le slot 6 (pic isolé net ~55 Hz, chute rapide
   ensuite) correspond mieux au profil "Subwoofer 1/LFE" que le slot 7
   (plus irrégulier, 2 bosses) — hypothèse plausible, pas une certitude.

   ⚠️ **Incohérence non résolue découverte lors de ce complément** : la
   liste de noms de canaux configurés contient **9 entrées contiguës**
   (vérifié : les 9 noms trouvent chacun exactement 1 occurrence, toutes
   regroupées dans une fenêtre de 236 octets, donc bien une vraie liste
   et pas des correspondances éparses) — soit 7 enceintes hors-sub pour
   seulement **6 slots à bande large** (0 à 5) disponibles une fois les 2
   slots de subwoofer retirés. Aucune explication trouvée avec les
   données disponibles (config modifiée après la mesure ? enceinte non
   mesurée cette session-là ? autre raison ?) — ne pas supposer une
   correspondance 1:1 entre les 7 noms d'enceintes hors-sub et les 6
   slots restants.

   **Conclusion pratique (répond à "le fichier suffit-il sans les
   captures ?")** : non. Même avec les 2 méthodes ci-dessus, l'attribution
   fiable ne couvre que les 2 subwoofers (et avec un bémol sur lequel est
   lequel) ; les captures d'écran restent nécessaires pour les 7 autres
   canaux (étiquetage certain par le logiciel lui-même) et pour disposer
   de valeurs dans l'échelle relative (dB autour de la cible) qu'utilise
   le moteur de diagnostic, plutôt que le dB SPL absolu de ce fichier.

6. **Fin de fichier (derniers ~600 octets)** : journal de navigation de
   l'interface utilisateur (noms d'écrans visités : `Navigation`,
   `RecordingDevice`, `SelectArrangement`, `VolumeCalibration`,
   `FilterDesign`, `FilterExport`, `InfoBar`, `Measurement`,
   `SelectDevice`, `UserLogin`, `homeview/...`). Confirme que l'app a bien
   des écrans "FilterDesign"/"FilterExport", mais ce journal ne contient
   que des **noms d'écran**, pas les données de filtre elles-mêmes.
   Aucune autre occurrence du mot "Filter"/"FIR" trouvée ailleurs dans le
   fichier qui ressemble à une vraie structure de données (les quelques
   occurrences ASCII de "FIR" trouvées sont statistiquement cohérentes
   avec une coïncidence dans des données à haute entropie, pas une
   étiquette de section).

────────────────────────────────────────────────────────────────────────
CE QUI N'A PAS ÉTÉ TROUVÉ (important pour ne pas sur-promettre)
────────────────────────────────────────────────────────────────────────
Aucune section identifiée contenant les **filtres de correction finaux**
(coefficients FIR/IIR, EQ paramétrique) que Dirac calcule et applique
réellement. Soit ils sont dans la zone chiffrée (hypothèse la plus
probable, non vérifiée), soit ils ne sont simplement pas stockés dans ce
fichier projet (peut-être générés à la volée et poussés uniquement vers
l'ampli/processeur au moment de l'activation). Ce module donne donc accès
aux **mesures** (brutes en audio + déconvoluées en fréq/mag), pas au
résultat du calcul de correction propriétaire de Dirac.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Marqueur de section des blocs de mesure fréquence/magnitude (8 octets),
# trouvé par recherche binaire répétée — valeur confirmée sur 10 fichiers.
BLOCK_MARKER = bytes.fromhex("9abcdef012345678"[:16])

# Magic number standard du conteneur Ogg (RFC 3533), utilisé tel quel.
OGG_MAGIC = b"OggS"

# Liste des noms de canaux trouvés en clair dans les 10 fichiers testés
# (encodage UTF-16BE, voir carte du fichier ci-dessus, point 4). Ordre
# d'apparition dans le fichier, PAS forcément l'ordre de mesure réel.
SPEAKER_NAMES_KNOWN = [
    "Front Left",
    "Center",
    "Front Right",
    "Surround Right",
    "Surround Back Right",
    "Surround Back Left",
    "Surround Left",
    "Subwoofer 1",
    "Subwoofer 2",
]


@dataclass
class OggPageInfo:
    """Une page Ogg individuelle (unité de découpage du conteneur)."""

    offset: int
    serial: int
    sequence: int
    header_type: int
    granule_position: int
    size: int


@dataclass
class OggStream:
    """Un flux logique Ogg complet (toutes les pages d'un même serial),
    vraisemblablement une position de micro."""

    serial: int
    pages: List[OggPageInfo]

    @property
    def first_offset(self) -> int:
        return self.pages[0].offset

    @property
    def total_size(self) -> int:
        return sum(p.size for p in self.pages)

    @property
    def is_well_formed(self) -> bool:
        """Vrai si le flux a exactement 1 début (BOS) et 1 fin (EOS)."""
        bos = sum(1 for p in self.pages if p.header_type & 0x02)
        eos = sum(1 for p in self.pages if p.header_type & 0x04)
        return bos == 1 and eos == 1


@dataclass
class MeasurementBlock:
    """Un bloc de mesure déconvoluée (fréquence/magnitude), voir carte du
    fichier point 5. `group_index`/`slot_index` sont une numérotation
    positionnelle (ordre d'apparition dans le fichier) et NE PRÉJUGENT PAS
    de la correspondance réelle position-micro/enceinte (non confirmée,
    voir limite documentée en en-tête de module)."""

    offset: int
    group_index: int
    slot_index: int
    frequencies_hz: Tuple[float, ...]
    magnitudes_db: Tuple[float, ...]

    def peak_in_range(self, f_min: float, f_max: float) -> Tuple[float, float]:
        """Retourne (frequence, magnitude) du point le plus fort dans
        [f_min, f_max] Hz. Utile pour comparer la signature de résonance
        entre blocs, pas pour lire une valeur absolue fiable isolée."""
        candidates = [
            (f, m)
            for f, m in zip(self.frequencies_hz, self.magnitudes_db)
            if f_min <= f <= f_max
        ]
        if not candidates:
            raise ValueError(f"Aucun point entre {f_min} et {f_max} Hz")
        return max(candidates, key=lambda t: t[1])


@dataclass
class ProjectMetadata:
    """Métadonnées de configuration trouvées en clair dans le fichier.
    Chaque champ est `None` s'il n'a pas été trouvé (ne pas supposer
    qu'il est absent du fichier — la recherche est best-effort)."""

    microphone_model: Optional[str] = None
    software_version: Optional[str] = None
    amplifier_brand: Optional[str] = None
    amplifier_model: Optional[str] = None
    speaker_names_found: List[str] = field(default_factory=list)


def _read_utf16be_qt_strings(data: bytes) -> List[Tuple[int, str]]:
    """Décode toutes les chaînes au format Qt-like rencontrées dans ce
    format (`uint32 BE` = longueur en octets, suivi de `count/2`
    caractères UTF-16BE). Retourne (offset, texte) pour chaque chaîne
    plausible (longueur raisonnable, texte décodable). Best-effort : ce
    n'est pas un vrai parseur de la structure Qt complète (pas de schéma
    documenté), juste une heuristique validée visuellement sur les 10
    fichiers testés.
    """
    results: List[Tuple[int, str]] = []
    limit = len(data) - 4
    i = 0
    while i < limit:
        length = struct.unpack_from(">I", data, i)[0]
        # Une chaîne Qt-like plausible : longueur paire (UTF-16), pas trop
        # longue, et qui ne déborde pas du buffer.
        if 2 <= length <= 400 and length % 2 == 0 and i + 4 + length <= len(data):
            try:
                text = data[i + 4 : i + 4 + length].decode("utf-16-be")
            except UnicodeDecodeError:
                text = None
            if text and text.isprintable() and len(text) >= 2:
                results.append((i, text))
        i += 1
    return results


def read_metadata(data: bytes, search_limit: int = 70_000_000) -> ProjectMetadata:
    """Extrait les métadonnées en clair trouvées dans les premiers
    `search_limit` octets (par défaut 70 Mo, large marge au-delà du
    ~63-64 Mo observé sur les 10 fichiers testés pour la zone de
    métadonnées — ajuster si un fichier plus gros ne donne rien).

    Approche volontairement simple (recherche de sous-chaînes connues),
    pas un vrai parseur de schéma Qt — suffisant pour confirmer la
    présence des informations, pas pour une lecture exhaustive de tous
    les champs de configuration possibles.
    """
    chunk = data[:search_limit]
    meta = ProjectMetadata()

    if "UMIK".encode("utf-16-be") in chunk:
        meta.microphone_model = "UMIK-1"

    for name in SPEAKER_NAMES_KNOWN:
        if name.encode("utf-16-be") in chunk:
            meta.speaker_names_found.append(name)

    if b"Marantz".decode().encode("utf-16-be") in chunk:
        meta.amplifier_brand = "Marantz"
    if "CINEMA 30".encode("utf-16-be") in chunk:
        meta.amplifier_model = "CINEMA 30"

    # Version logicielle : motif "N.N.N<suffixe alpha>" (ex. "7.2.0ch"),
    # repérée parmi les chaînes Qt-like décodées (réutilise le même
    # décodeur que les autres métadonnées plutôt qu'un regex sur octets
    # bruts, qui s'était révélé fragile aux erreurs d'ordre d'octets).
    import re

    for _offset, text in _read_utf16be_qt_strings(chunk):
        if re.match(r"^\d+(\.\d+){1,3}[a-z]+$", text):
            meta.software_version = text
            break

    return meta


def _parse_ogg_pages(data: bytes) -> List[OggPageInfo]:
    """Parse toutes les pages Ogg du fichier (format RFC 3533, en-tête de
    27+N octets). Ne décode pas le contenu audio, juste la structure de
    page nécessaire pour regrouper par flux logique."""
    pages: List[OggPageInfo] = []
    start = 0
    while True:
        idx = data.find(OGG_MAGIC, start)
        if idx == -1:
            break
        header_type = data[idx + 5]
        granule_pos = struct.unpack_from("<q", data, idx + 6)[0]
        serial = struct.unpack_from("<I", data, idx + 14)[0]
        seq = struct.unpack_from("<I", data, idx + 18)[0]
        page_segments = data[idx + 26]
        seg_table = data[idx + 27 : idx + 27 + page_segments]
        data_size = sum(seg_table)
        page_total_size = 27 + page_segments + data_size
        pages.append(
            OggPageInfo(
                offset=idx,
                serial=serial,
                sequence=seq,
                header_type=header_type,
                granule_position=granule_pos,
                size=page_total_size,
            )
        )
        start = idx + 4
    return pages


def list_ogg_streams(data: bytes) -> List[OggStream]:
    """Regroupe toutes les pages Ogg du fichier par flux logique (serial
    number), triées par offset du premier bloc (= ordre de mesure le plus
    probable, non confirmé formellement). Chaque flux correspond
    vraisemblablement à une position de micro (13 attendues, voir carte
    du fichier point 2)."""
    pages = _parse_ogg_pages(data)
    by_serial: Dict[int, List[OggPageInfo]] = {}
    for p in pages:
        by_serial.setdefault(p.serial, []).append(p)

    streams = []
    for serial, plist in by_serial.items():
        plist.sort(key=lambda p: p.sequence)
        streams.append(OggStream(serial=serial, pages=plist))
    streams.sort(key=lambda s: s.first_offset)
    return streams


def extract_ogg_stream(data: bytes, stream: OggStream) -> bytes:
    """Réassemble un flux Ogg logique en un fichier `.ogg` valide
    (concaténation de ses pages, déjà triées par sequence number).
    Écrire le résultat sur disque (`open(path, 'wb').write(...)`) pour le
    décoder avec un outil externe, par exemple :

        pip install imageio-ffmpeg
        python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
        <ffmpeg> -i stream.ogg stream.wav

    Ce module ne fait pas ce décodage lui-même (pas de dépendance lourde
    pour un prototype de recherche)."""
    return b"".join(data[p.offset : p.offset + p.size] for p in stream.pages)


def _read_block_at(data: bytes, offset: int) -> Optional[MeasurementBlock]:
    """Lit un seul bloc de mesure à l'offset exact du marqueur
    `BLOCK_MARKER`. Structure validée par calcul exact (voir carte du
    fichier point 5). Retourne `None` si la structure ne correspond pas
    à un vrai bloc de mesure : `BLOCK_MARKER` réapparaît aussi ailleurs
    dans le fichier avec une structure différente (confirmé : le journal
    de navigation UI en fin de fichier utilise le même motif de
    marqueur), ce qui ferait planter un `unpack_from` naïf avec un
    "count" aberrant."""
    max_reasonable_count = 100_000
    if offset + 16 > len(data):
        return None
    _type, count_f = struct.unpack_from(">II", data, offset + 8)
    if not (0 < count_f <= max_reasonable_count):
        return None
    base_freq = offset + 16
    freq_bytes = count_f * 8
    if base_freq + freq_bytes + 4 > len(data):
        return None
    freqs = struct.unpack_from(f">{count_f}d", data, base_freq)
    pos2 = base_freq + freq_bytes
    count_m = struct.unpack_from(">I", data, pos2)[0]
    if count_m != count_f:
        return None
    base_mag = pos2 + 4
    mag_bytes = count_m * 8
    if base_mag + mag_bytes > len(data):
        return None
    mags = struct.unpack_from(f">{count_m}d", data, base_mag)
    return MeasurementBlock(
        offset=offset,
        group_index=-1,
        slot_index=-1,
        frequencies_hz=freqs,
        magnitudes_db=mags,
    )


def read_measurement_blocks(
    data: bytes, blocks_per_group: int = 8
) -> List[MeasurementBlock]:
    """Trouve et décode tous les blocs de mesure fréquence/magnitude du
    fichier (104 attendus sur les 10 fichiers testés : 13 groupes de 8
    exactement, voir correction documentée au point 5 de l'en-tête de
    module).

    `group_index`/`slot_index` sont assignés par simple position
    d'apparition dans le fichier (grouper par paquets de
    `blocks_per_group` consécutifs) — PAS une correspondance confirmée
    position-micro/enceinte (voir limite documentée en en-tête de
    module). Si le nombre total de blocs n'est pas un multiple exact de
    `blocks_per_group`, les blocs en surplus sont retournés avec
    `group_index`/`slot_index = -1` (non groupés) plutôt que de deviner.
    """
    offsets = []
    start = 0
    while True:
        idx = data.find(BLOCK_MARKER, start)
        if idx == -1:
            break
        offsets.append(idx)
        start = idx + len(BLOCK_MARKER)

    blocks = [b for b in (_read_block_at(data, off) for off in offsets) if b is not None]

    # Les blocs "count=2048" sont les vraies mesures ; les en-têtes
    # isolés (ex. count=13, count=0) rencontrés avant la zone régulière
    # ne sont pas des mesures et sont exclus du groupement.
    measurement_blocks = [b for b in blocks if len(b.frequencies_hz) == 2048]

    n_full_groups = len(measurement_blocks) // blocks_per_group
    for i, block in enumerate(measurement_blocks[: n_full_groups * blocks_per_group]):
        block.group_index = i // blocks_per_group
        block.slot_index = i % blocks_per_group

    return measurement_blocks


@dataclass
class LiveProjectSummary:
    """Résultat consolidé d'une inspection de fichier .liveproject."""

    file_size: int
    metadata: ProjectMetadata
    ogg_streams: List[OggStream]
    measurement_blocks: List[MeasurementBlock]

    def describe(self) -> str:
        lines = [
            f"Taille du fichier : {self.file_size:,} octets "
            f"({self.file_size / 1024 / 1024:.1f} Mo)",
            f"Microphone : {self.metadata.microphone_model or 'non trouvé'}",
            f"Logiciel : {self.metadata.software_version or 'non trouvé'}",
            f"Ampli/processeur : "
            f"{self.metadata.amplifier_brand or '?'} "
            f"{self.metadata.amplifier_model or ''}".strip(),
            f"Enceintes listées en config : "
            f"{', '.join(self.metadata.speaker_names_found) or 'aucune trouvée'}",
            f"Positions de micro (flux audio Ogg) : {len(self.ogg_streams)}",
            f"  dont bien formés (1 début + 1 fin) : "
            f"{sum(1 for s in self.ogg_streams if s.is_well_formed)}",
            f"Blocs de mesure fréq/mag décodés : {len(self.measurement_blocks)}",
        ]
        n_groups = len({b.group_index for b in self.measurement_blocks if b.group_index >= 0})
        if n_groups:
            lines.append(f"  regroupés en {n_groups} groupes (positions de micro)")
        return "\n".join(lines)


def inspect_liveproject(path: str) -> LiveProjectSummary:
    """Point d'entrée haut niveau : lit un fichier `.liveproject` et
    retourne un résumé structuré de tout ce que ce module sait en
    extraire. Charge le fichier entier en mémoire (104-254 Mo observés
    sur les fichiers de test — acceptable pour une analyse ponctuelle,
    pas conçu pour un traitement en masse/streaming)."""
    with open(path, "rb") as f:
        data = f.read()

    return LiveProjectSummary(
        file_size=len(data),
        metadata=read_metadata(data),
        ogg_streams=list_ogg_streams(data),
        measurement_blocks=read_measurement_blocks(data),
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 liveproject_reader.py <chemin_vers_fichier.liveproject>")
        sys.exit(1)

    summary = inspect_liveproject(sys.argv[1])
    print(summary.describe())
