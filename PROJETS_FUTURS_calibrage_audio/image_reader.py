"""
Lecture de courbes depuis une capture d'écran Dirac Live (le seul format
d'entrée visé par ce projet — précision explicite de Steve : "mon projet
ne sera que pour dirac donc qu'avec les captures d'ecran des courbes
dirac"). Ce module remplace la saisie manuelle point par point envisagée
en V1 par une vraie extraction depuis l'image.

MÉTHODE (digitalisation de graphique, technique générale et éprouvée —
même principe que des outils connus comme WebPlotDigitizer, appliqué ici
à Dirac Live, pas une astuce spécifique inventée pour Dirac) :

  1. On calibre les axes à partir de repères pixel -> valeur réelle,
     donnés par le client ou un opérateur qui regarde l'image (2 repères
     sur l'axe fréquence, 2 repères sur l'axe dB). L'axe fréquence est
     traité en échelle logarithmique (standard pour ce type de graphique
     acoustique), l'axe dB en échelle linéaire.
  2. On balaye l'image colonne de pixels par colonne de pixels, on repère
     les pixels proches d'une couleur cible (celle de la courbe mesurée
     affichée par Dirac), et on convertit leur position en (fréquence, dB).

CALIBRATION RÉELLE (validée sur les 8 captures fournies par Steve le
29/09/2026, dossier "CAPTURE ECRAN COURBES" du Bureau — une capture par
enceinte, interface Dirac Live en français, résolution 2794x1538) :
  - Axe X (fréquence, log) : repère "10 Hz" à x=31.5 px, repère "1000 Hz"
    à x=1421.5 px (une décade = 696 px, vérifié à deux reprises sur des
    graduations indépendantes : 10/20 Hz et 100/1000 Hz donnent le même
    écart). Piège identifié : la ligne verticale pointillée vers
    x=847.5 n'est PAS une graduation d'axe, c'est le marqueur de
    crossover ("150 Hz", spécifique à la configuration de Steve) — à ne
    pas confondre lors d'une détection automatique de grille.
  - Axe Y (dB, linéaire) : repère "+20 dB" à y=181.5 px, repère "-30 dB"
    à y=1083.5 px (18.05 px/dB, confirmé par lecture directe du texte sur
    3 graduations : +20, +10, -10 dB, écarts tous égaux à 180.5 px).
  - Zone de tracé utile : le graphique couvre presque toute la largeur
    de l'image, mais une légende flottante (rectangles de couleur par
    enceinte) et le panneau de groupes la recouvrent à partir de
    x≈2016 px, et des barres "plage détectée" colorées recouvrent le bas
    à partir de y≈1240 px. Pour l'usage de ce projet (modes de pièce
    <300 Hz, zone ART <150 Hz), on se limite par sécurité à
    x∈[20, 1900], y∈[90, 1200], ce qui couvre largement 10 Hz à plusieurs
    kHz sans jamais toucher ces éléments d'interface.
  - Couleur de la courbe mesurée (bruitée, à extraire) : CHANGE selon
    l'enceinte sélectionnée dans Dirac (confirmé en comparant 4 captures :
    Front Left=(137,41,131) magenta, Centrale=(41,137,122) turquoise,
    Subwoofers=(137,41,41) rouge, Surround Left=(98,41,137) violet). Il
    n'y a donc PAS une seule couleur cible fixe : `detect_curve_color`
    la retrouve automatiquement par image plutôt qu'une valeur codée en
    dur. Un seul élément d'interface a une couleur stable sur toutes les
    captures et doit être exclu explicitement : le bleu "+X dB"/"-X dB"
    de l'indicateur de plage détectée, UI_RANGE_INDICATOR_RGB=(10,110,160).
  - Courbe pâle/désaturée (ex. (178,125,175) pour Front Left vs
    (137,41,131) mesurée — distance euclidienne ≈103, grande marge par
    rapport à la tolérance de couleur par défaut de 40 : pas de confusion
    observée entre les deux). ⚠️ CORRECTION (03/10, suite 24) : d'abord
    supposée être une "courbe lissée/tendance" ou la courbe "Corrigé"
    (résultat du filtre ART), cette hypothèse a été INFIRMÉE par mesure :
    en comparant chiffre par chiffre la valeur de cette courbe pâle et de
    la courbe mesurée à plusieurs fréquences identiques, la courbe pâle
    s'éloigne PARFOIS DAVANTAGE de 0 dB que la mesure brute (ex. Surround
    Gauche à 60 Hz : mesuré=+1,7 dB, pâle=+4,3 dB) — un vrai résultat de
    filtre ne peut jamais s'éloigner plus de sa cible que la mesure brute
    ne l'était déjà. Cette courbe pâle est donc très probablement la
    **courbe CIBLE** (la consigne visée, indépendante de la mesure),
    PAS le résultat réel après correction ART. Confirmé par Steve que
    ces captures sont "les courbes brutes réglées en automatique par
    Dirac, aucun réglage manuel" : la courbe "Corrigé" réelle n'a pas pu
    être identifiée avec certitude sur ces captures (peut-être
    superposée visuellement à la cible, peut-être non affichée) — ne
    pas présenter la courbe pâle comme "ce qu'ART obtient en pratique".

DEUX BUGS RÉELS TROUVÉS ET CORRIGÉS EN EXTRAYANT LES 8 VRAIES COURBES DE
STEVE (dossier "CAPTURE ECRAN COURBES", 29/09) :
  1. Un label de texte épais (ex. "+2,8 dB", valeur de la courbe cible
     affichée en haut à gauche du graphique) peut avoir une couleur assez
     proche de `target_rgb` pour être confondu avec tolérance par défaut.
     L'ancienne version de `extract_curve_points` prenait le centre
     min/max de TOUS les pixels matchés par colonne, donc un label épais
     faussait complètement le résultat pour les colonnes qu'il recouvre
     (vu sur "Surround Back Left" : premier point à +2,7 dB au lieu de
     -30/-36 dB comme les 7 autres canaux). Corrigé en séparant les
     pixels matchés par colonne en groupes contigus et en parcourant les
     colonnes de DROITE à GAUCHE (la zone haute fréquence, à droite, est
     toujours loin des labels) pour établir une continuité fiable avant
     d'atteindre une éventuelle zone de label ; un saut trop brutal par
     rapport au dernier point valide est rejeté plutôt qu'accepté à tort.
  2. La ligne de grille horizontale (graduation "ronde" de l'axe dB, ex.
     +20 dB, couleur stable `UI_GRIDLINE_RGB=(62,68,83)` sur les 8
     captures) peut, par coïncidence, être à une distance de couleur
     limite d'un `target_rgb` donné (vu sur "Surround Right" : couleur de
     courbe (41,54,137), distance ≈59,6 de la grille — juste sous une
     tolérance de 60), menant à une extraction plate fausse sur toute la
     largeur. Corrigée en excluant explicitement `UI_GRIDLINE_RGB` (comme
     `UI_RANGE_INDICATOR_RGB` déjà exclu) et, pour les cas où même la
     couleur de légende reste proche d'un élément d'interface en dégradé
     (bandeau "plage détectée"), en filtrant aussi par saturation minimale
     (`min_saturation`) — la grille et les dégradés d'interface sont
     nettement moins saturés qu'un vrai trait de courbe.

Ce qui n'a PAS encore été revalidé : une résolution de capture différente
de 2794x1538, une interface Dirac dans une autre langue, ou une version
différente du logiciel. `DIRAC_SCREENSHOT_2794x1538` ci-dessous documente
explicitement le contexte où cette calibration est valable.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from models import MeasurementPoint

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - dépendance déclarée dans README
    raise ImportError(
        "La lecture d'image nécessite Pillow : pip install Pillow"
    ) from exc


# Couleur stable sur toutes les captures observées : le bandeau bleu qui
# affiche "+X dB" / "-X dB" (plage détectée). Ce n'est pas la courbe —
# à exclure explicitement lors de la détection automatique de couleur.
UI_RANGE_INDICATOR_RGB: tuple[int, int, int] = (10, 110, 160)

# Couleur stable des lignes de grille horizontales (graduations "rondes"
# de l'axe dB, ex. +20 dB) — confirmée identique sur les 8 captures de
# Steve à (62, 68, 83). Non filtrée par `detect_curve_color` (saturation
# trop basse, ~0.25, sous le seuil `min_saturation` par défaut), mais
# PEUT entrer en collision avec `extract_curve_points` pour une couleur
# de courbe qui lui est, par coïncidence, assez proche (bug réel trouvé
# sur la capture "Surround Right" : couleur de courbe (41,54,137), à une
# distance euclidienne de seulement ≈59.6 de cette grille — juste sous
# une tolérance de 60, provoquant une extraction plate fausse à +20 dB
# sur toute la largeur). À exclure explicitement comme pour le bandeau
# ci-dessus.
UI_GRIDLINE_RGB: tuple[int, int, int] = (62, 68, 83)


@dataclass
class AxisCalibration:
    """Deux repères pixel -> valeur réelle par axe, pour convertir une
    position en pixels de la capture en une valeur (Hz, dB). Les repères
    sont à prendre sur les graduations visibles de l'image (ex: la
    graduation "20 Hz" et la graduation "200 Hz" pour l'axe fréquence)."""

    x_pixel_a: float
    x_freq_hz_a: float
    x_pixel_b: float
    x_freq_hz_b: float
    y_pixel_a: float
    y_db_a: float
    y_pixel_b: float
    y_db_b: float

    def pixel_to_freq(self, px: float) -> float:
        """Interpolation log : les graphiques de réponse en fréquence
        utilisent un axe X logarithmique (20 Hz à 20 kHz)."""
        log_a = math.log10(self.x_freq_hz_a)
        log_b = math.log10(self.x_freq_hz_b)
        t = (px - self.x_pixel_a) / (self.x_pixel_b - self.x_pixel_a)
        return 10 ** (log_a + t * (log_b - log_a))

    def pixel_to_db(self, py: float) -> float:
        """Interpolation linéaire : l'axe dB est linéaire."""
        t = (py - self.y_pixel_a) / (self.y_pixel_b - self.y_pixel_a)
        return self.y_db_a + t * (self.y_db_b - self.y_db_a)


# Calibration validée par ingénierie inverse sur les 8 vraies captures
# Dirac Live fournies par Steve (interface FR, 2794x1538 px — voir le
# détail des repères dans l'en-tête du module). À revalider si la
# résolution, la langue ou la version du logiciel diffère.
DIRAC_SCREENSHOT_2794x1538 = AxisCalibration(
    x_pixel_a=31.5, x_freq_hz_a=10.0,
    x_pixel_b=1421.5, x_freq_hz_b=1000.0,
    y_pixel_a=181.5, y_db_a=20.0,
    y_pixel_b=1083.5, y_db_b=-30.0,
)

# Zone de tracé à utiliser avec la calibration ci-dessus : évite la
# légende flottante / le panneau de groupes (à droite, x>=2016 environ)
# et les barres "plage détectée" colorées (en bas, y>=1240 environ).
# Couvre largement 10 Hz à plusieurs kHz, très au-delà de ce dont ce
# projet a besoin (modes de pièce <300 Hz, zone ART <150 Hz).
DIRAC_SCREENSHOT_2794x1538_PLOT_AREA = {
    "plot_left_px": 20.0,
    "plot_right_px": 1900.0,
    "plot_top_px": 90.0,
    "plot_bottom_px": 1200.0,
}


def _color_distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def extract_curve_points(
    image_path: str,
    calibration: AxisCalibration,
    target_rgb: tuple[int, int, int],
    color_tolerance: float = 40.0,
    column_step_px: int = 2,
    plot_left_px: float | None = None,
    plot_right_px: float | None = None,
    plot_top_px: float | None = None,
    plot_bottom_px: float | None = None,
    max_line_thickness_px: int = 12,
    max_continuity_jump_px: int = 250,
    exclude_rgbs: tuple[tuple[int, int, int], ...] = (UI_RANGE_INDICATOR_RGB, UI_GRIDLINE_RGB),
    exclude_tolerance: float = 20.0,
    min_saturation: float = 0.0,
) -> list[MeasurementPoint]:
    """Digitalise une courbe de couleur `target_rgb` depuis une image de
    capture d'écran Dirac déjà calibrée (voir `AxisCalibration`).

    `plot_left_px`/`plot_right_px`/`plot_top_px`/`plot_bottom_px` limitent
    le balayage à la zone du graphique (recommandé : sans ça, le balayage
    inclut légendes/axes où une couleur proche de `target_rgb` pourrait
    exister par coïncidence). Si non fournis, toute l'image est balayée.

    MÉTHODE (corrigée suite à un bug réel trouvé sur les captures de
    Steve) : les colonnes sont parcourues de DROITE à GAUCHE — la zone de
    droite (haute fréquence) est toujours sans ambiguïté (loin des labels
    de texte qui n'apparaissent qu'en haut à gauche du graphique), ce qui
    permet d'établir une continuité fiable avant d'atteindre une
    éventuelle zone de label. À chaque colonne, les pixels qui
    correspondent à `target_rgb` sont séparés en groupes contigus
    (`max_line_thickness_px` distingue un trait fin d'un bloc de texte
    épais) ; le groupe retenu est celui le plus proche en position du
    dernier point valide, et un saut trop brutal (`max_continuity_jump_px`,
    250px par défaut — valeur validée sur les 8 vraies captures de Steve :
    certaines courbes ont des flancs quasi verticaux entre un creux et un
    pic voisins, qu'une valeur plus basse comme 150px rejette à tort)
    est rejeté plutôt qu'accepté à tort — mieux vaut un petit trou qu'un
    point faux. `exclude_rgbs`/`exclude_tolerance` ignorent les éléments
    d'interface de couleur stable (bandeau "+X dB", grille) qui pourraient
    sinon être confondus avec `target_rgb` ; `min_saturation` filtre en
    plus les pixels trop désaturés (fond, dégradés d'interface) quand la
    couleur de courbe est elle-même proche d'un de ces éléments (cas
    rencontré : bug initial pris pour un centre min/max global biaisé par
    un label "+X,X dB" de teinte proche de la courbe mesurée — un label
    épais fausse alors complètement le centre calculé pour les colonnes
    qu'il recouvre).

    Retourne une liste de `MeasurementPoint` triée par fréquence
    croissante. Une colonne de pixels sans correspondance de couleur est
    simplement ignorée (pas d'interpolation automatique des trous — un
    trou visible doit être vérifié manuellement plutôt que deviné)."""
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    pixels = img.load()

    left = int(plot_left_px) if plot_left_px is not None else 0
    right = int(plot_right_px) if plot_right_px is not None else width - 1
    top = int(plot_top_px) if plot_top_px is not None else 0
    bottom = int(plot_bottom_px) if plot_bottom_px is not None else height - 1

    points: list[MeasurementPoint] = []
    last_py: float | None = None
    for px in range(right, left - 1, -max(1, column_step_px)):
        matches_y = []
        for py in range(top, bottom + 1):
            rgb = pixels[px, py]
            if _color_distance(rgb, target_rgb) > color_tolerance:
                continue
            if any(_color_distance(rgb, excl) <= exclude_tolerance for excl in exclude_rgbs):
                continue
            if min_saturation > 0.0:
                mx, mn = max(rgb), min(rgb)
                saturation = 0.0 if mx == 0 else (mx - mn) / mx
                if saturation < min_saturation:
                    continue
            matches_y.append(py)
        if not matches_y:
            continue

        # Séparer en groupes de pixels contigus (gap > 2px = nouveau groupe) :
        # une grille ou un label éloigné de la même teinte ne doit jamais
        # être mélangé avec le vrai trait de mesure dans un même centre.
        groups = []
        group = [matches_y[0]]
        for y in matches_y[1:]:
            if y - group[-1] <= 2:
                group.append(y)
            else:
                groups.append(group)
                group = [y]
        groups.append(group)

        # Ne garder que les groupes fins (ligne de mesure), pas les blocs
        # épais (label de texte) — sauf si aucun groupe fin n'existe.
        thin_groups = [g for g in groups if (max(g) - min(g)) <= max_line_thickness_px]
        candidates = thin_groups if thin_groups else groups

        if last_py is not None:
            best = min(candidates, key=lambda g: abs((min(g) + max(g)) / 2 - last_py))
            best_center = (min(best) + max(best)) / 2
            if abs(best_center - last_py) > max_continuity_jump_px:
                continue  # saut aberrant (probable label) : on ignore cette colonne
        else:
            best = min(candidates, key=lambda g: (max(g) - min(g)))  # le plus fin
            best_center = (min(best) + max(best)) / 2

        last_py = best_center
        freq = calibration.pixel_to_freq(px)
        spl = calibration.pixel_to_db(best_center)
        points.append(MeasurementPoint(freq_hz=round(freq, 1), spl_db=round(spl, 1)))

    return sorted(points, key=lambda p: p.freq_hz)


def dominant_non_background_color(
    image_path: str,
    plot_left_px: float,
    plot_right_px: float,
    plot_top_px: float,
    plot_bottom_px: float,
    background_rgb: tuple[int, int, int],
    background_tolerance: float = 15.0,
) -> tuple[int, int, int]:
    """Aide à trouver `target_rgb` automatiquement : compte les couleurs de
    la zone du graphique autres que le fond, retourne la plus fréquente.

    Heuristique utile pour une première estimation, PAS un remplacement
    de la vérification visuelle : si l'image contient aussi une courbe
    cible ou une grille colorée, cette fonction peut se tromper de
    couleur. À confirmer à l'œil avant d'appeler `extract_curve_points`."""
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()
    counts: dict[tuple[int, int, int], int] = {}
    for px in range(int(plot_left_px), int(plot_right_px) + 1):
        for py in range(int(plot_top_px), int(plot_bottom_px) + 1):
            rgb = pixels[px, py]
            if _color_distance(rgb, background_rgb) <= background_tolerance:
                continue
            counts[rgb] = counts.get(rgb, 0) + 1
    if not counts:
        raise ValueError(
            "Aucun pixel hors fond trouvé dans la zone donnée : vérifier "
            "les coordonnées de la zone de graphique ou la couleur de fond."
        )
    return max(counts, key=counts.get)


def detect_curve_color(
    image_path: str,
    plot_left_px: float,
    plot_right_px: float,
    plot_top_px: float,
    plot_bottom_px: float,
    exclude_rgbs: tuple[tuple[int, int, int], ...] = (UI_RANGE_INDICATOR_RGB, UI_GRIDLINE_RGB),
    exclude_tolerance: float = 20.0,
    min_saturation: float = 0.5,
    min_value: int = 120,
    sample_step_px: int = 2,
) -> tuple[int, int, int]:
    """Trouve automatiquement la couleur de la courbe mesurée active dans
    une capture Dirac — NÉCESSAIRE car cette couleur change selon
    l'enceinte sélectionnée (confirmé sur 4 captures réelles : magenta
    pour Front Left, turquoise pour Centrale, rouge pour Subwoofers,
    violet pour Surround Left — il n'y a pas de couleur fixe universelle).

    Fonctionne en ne retenant que les pixels "vifs" (saturation et
    luminosité élevées : `min_saturation`/`min_value`), ce qui élimine le
    fond sombre et la grille sans avoir besoin de connaître leur couleur
    exacte, puis en excluant les couleurs d'interface connues comme
    stables (`exclude_rgbs`, par défaut le bandeau bleu "+X dB"), puis en
    retournant la couleur vive restante la plus fréquente.

    Remarque : la courbe lissée ("tendance") est nettement moins saturée
    que la courbe mesurée et n'est normalement pas retenue par le filtre
    de saturation par défaut (vérifié sur Front Left : courbe mesurée
    saturation ≈0.70, courbe lissée ≈0.30)."""
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()
    counts: dict[tuple[int, int, int], int] = {}
    for px in range(int(plot_left_px), int(plot_right_px) + 1, max(1, sample_step_px)):
        for py in range(int(plot_top_px), int(plot_bottom_px) + 1, max(1, sample_step_px)):
            r, g, b = pixels[px, py]
            mx, mn = max(r, g, b), min(r, g, b)
            saturation = 0.0 if mx == 0 else (mx - mn) / mx
            if saturation < min_saturation or mx < min_value:
                continue
            if any(_color_distance((r, g, b), excl) <= exclude_tolerance for excl in exclude_rgbs):
                continue
            counts[(r, g, b)] = counts.get((r, g, b), 0) + 1
    if not counts:
        raise ValueError(
            "Aucune couleur vive trouvée dans la zone donnée : vérifier "
            "les coordonnées de la zone de graphique ou abaisser min_saturation."
        )
    return max(counts, key=counts.get)
