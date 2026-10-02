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
) -> list[MeasurementPoint]:
    """Digitalise une courbe de couleur `target_rgb` depuis une image de
    capture d'écran Dirac déjà calibrée (voir `AxisCalibration`).

    `plot_left_px`/`plot_right_px`/`plot_top_px`/`plot_bottom_px` limitent
    le balayage à la zone du graphique (recommandé : sans ça, le balayage
    inclut légendes/axes où une couleur proche de `target_rgb` pourrait
    exister par coïncidence). Si non fournis, toute l'image est balayée.

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
    for px in range(left, right + 1, max(1, column_step_px)):
        matches_y = [
            py
            for py in range(top, bottom + 1)
            if _color_distance(pixels[px, py], target_rgb) <= color_tolerance
        ]
        if not matches_y:
            continue
        # Plusieurs pixels peuvent matcher (épaisseur du trait) : on prend
        # le centre du groupe, pas la moyenne de tous (une grille éloignée
        # de la même teinte fausserait sinon le résultat).
        py_center = (min(matches_y) + max(matches_y)) / 2
        freq = calibration.pixel_to_freq(px)
        spl = calibration.pixel_to_db(py_center)
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
    exclude_rgbs: tuple[tuple[int, int, int], ...] = (UI_RANGE_INDICATOR_RGB,),
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
