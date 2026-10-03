"""
Transforme un DiagnosticReport en rapport texte lisible, livrable à un
client. Respecte l'ordre de priorité déjà validé dans la conversation
source (placement > traitement acoustique > réglages logiciels) et inclut
systématiquement les avertissements obligatoires (knowledge_base.MANDATORY_DISCLAIMERS).
"""

from __future__ import annotations

import knowledge_base as kb
from models import DiagnosticReport


def _section(title: str) -> str:
    bar = "-" * len(title)
    return f"\n{title}\n{bar}\n"


def _build_support_map_lines(report: DiagnosticReport) -> list[str]:
    """Consolide, enceinte par enceinte, QUI aide QUI (quel support,
    quelle valeur en dB) en une seule table lisible — réponse directe à
    la demande de Steve (03/10) : 'il faut établir aussi dans le rapport
    quelle enceinte aide qui', plutôt que de laisser cette information
    éclatée entre plusieurs catégories de recommandations que le client
    devrait recouper lui-même."""
    precise_by_main: dict[str, list[tuple[str, float]]] = {}
    for rec in report.recommendations:
        if rec.category == "Niveau de support (précis)" and rec.precise_value_db is not None:
            if " -> " not in rec.target:
                continue
            support_name, main_name = rec.target.split(" -> ", 1)
            precise_by_main.setdefault(main_name, []).append(
                (support_name, rec.precise_value_db)
            )

    retained_by_main: dict[str, str] = {}
    for rec in report.recommendations:
        if rec.category == "Groupage de support recommandé":
            retained_by_main.setdefault(rec.target, rec.action)

    excluded_by_main: dict[str, list[str]] = {}
    for rec in report.recommendations:
        if rec.category == "Groupage de support — option écartée (non pertinente)":
            excluded_by_main.setdefault(rec.target, []).append(rec.action)

    all_mains = list(dict.fromkeys(
        list(retained_by_main.keys()) + list(precise_by_main.keys())
    ))
    if not all_mains:
        return []

    lines: list[str] = []
    for main_name in all_mains:
        lines.append(f"  • {main_name}")
        supports = precise_by_main.get(main_name)
        if supports:
            for support_name, value_db in supports:
                lines.append(
                    f"      ← aidée par : {support_name} "
                    f"(Support Level : {value_db:+.1f} dB)"
                )
        elif main_name in retained_by_main:
            lines.append(f"      ← {retained_by_main[main_name]}")
        for note in excluded_by_main.get(main_name, []):
            lines.append(f"      (écarté) {note}")
    return lines


def generate_report(
    report: DiagnosticReport,
    client_name: str = "Client",
    include_studies: bool = True,
) -> str:
    lines: list[str] = []
    lines.append(f"RAPPORT DE CALIBRAGE DIRAC LIVE ART — {client_name}")
    lines.append(f"Niveau de service : {report.service_level.value.capitalize()}")

    lines.append(_section("Avertissements"))
    for disclaimer in kb.MANDATORY_DISCLAIMERS:
        lines.append(f"  • {disclaimer}")

    if report.warnings:
        lines.append(_section("Remarques sur les données fournies"))
        for warning in report.warnings:
            lines.append(f"  • {warning}")

    lines.append(_section("Ordre de priorité recommandé"))
    for step in kb.PRIORITY_ORDER:
        lines.append(f"  {step}")

    if report.anomalies:
        lines.append(_section("Anomalies détectées sur les courbes mesurées"))
        for a in report.anomalies:
            lines.append(
                f"  • {a.speaker_name} — {a.kind} de {a.amplitude_db} dB à "
                f"{a.freq_hz:.0f} Hz"
            )
            if a.probable_causes:
                lines.append(f"      Causes probables : {', '.join(a.probable_causes)}")
            if a.suggested_action:
                lines.append(f"      Action suggérée : {a.suggested_action}")

    support_map_lines = _build_support_map_lines(report)
    if support_map_lines:
        lines.append(_section("Qui aide qui : tableau de synthèse du groupage de support"))
        lines.extend(support_map_lines)

    if report.recommendations:
        lines.append(_section("Recommandations de réglage"))
        by_category: dict[str, list] = {}
        for rec in report.recommendations:
            by_category.setdefault(rec.category, []).append(rec)
        for category, recs in by_category.items():
            lines.append(f"  [{category}]")
            for rec in recs:
                lines.append(f"    - {rec.target} : {rec.action}")
                if rec.precise_value_db is not None:
                    lines.append(f"      ➜ Valeur précise : {rec.precise_value_db:+.1f} dB")
                if rec.freq_range_hz is not None:
                    lines.append(
                        f"      ➜ Plage de fréquence : "
                        f"{rec.freq_range_hz[0]:.0f} Hz – {rec.freq_range_hz[1]:.0f} Hz"
                    )
                if rec.control_points:
                    by_speaker: dict[str, list] = {}
                    for cp in rec.control_points:
                        by_speaker.setdefault(cp.speaker_name or rec.target, []).append(cp)
                    for sp_name, points in by_speaker.items():
                        lines.append(
                            f"      ➜ Points de contrôle de courbe cible — {sp_name} :"
                        )
                        for i, cp in enumerate(points, start=1):
                            lines.append(
                                f"          Point {i} : {cp.freq_hz:.0f} Hz / "
                                f"{cp.gain_db:+.1f} dB"
                            )
                            if cp.reason:
                                lines.append(f"            Pourquoi : {cp.reason}")
                lines.append(f"      Source : {rec.evidence.value}")
                if rec.detail:
                    lines.append(f"      Détail : {rec.detail}")

    lines.append(_section("Les cinq facteurs de l'immersion (rappel pédagogique)"))
    for factor, note in kb.IMMERSION_FACTORS:
        lines.append(f"  • {factor} — {note}")

    lines.append(_section("Prérequis techniques à vérifier avant calcul ART"))
    for prereq in kb.TECHNICAL_PREREQUISITES:
        lines.append(f"  • {prereq}")

    if include_studies and kb.CITED_STUDIES:
        lines.append(
            _section(
                "Annexe pédagogique : études scientifiques consultées "
                "(recherche web, pas une garantie de résultat)"
            )
        )
        by_domain: dict[str, list] = {}
        for study in kb.CITED_STUDIES:
            by_domain.setdefault(study.domain, []).append(study)
        for domain, studies in by_domain.items():
            lines.append(f"  [{domain}]")
            for s in studies:
                lines.append(f"    - {s.title} ({s.venue_or_authors}, {s.year})")
                lines.append(f"      Source : {s.source_url}")
                lines.append(f"      Vérification : {s.verification}")
                lines.append(f"      Ce qu'on en retient : {s.takeaway}")

    return "\n".join(lines)
