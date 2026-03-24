"""Rampenprofile für den Schrittmotor des Leckage-Simulators.

Dieses Modul ist bewusst hardware-neutral gehalten:
- Es berechnet zeitdiskrete Schrittvorgaben in Intervallen.
- Es kann daraus direkt serielle Bewegungsbefehle (`<n>a` / `<n>z`) ableiten.
- Für die 10 Standardprofile werden identische Weibull-Parameter verwendet;
  nur die Gesamtdauer (Zeitskalierung bis zum Ausfall) variiert.

Integration:
- In `prototype_leakage/collectBaseline.py` kann eine geplante Rampe zyklisch
  abgearbeitet werden, statt nur mit konstantem `STEP_SIZE` zu fahren.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List


@dataclass(frozen=True)
class RampPoint:
    """Ein Sollwertpunkt in der Rampe."""

    second: int
    step_delta: int


@dataclass(frozen=True)
class RampProfile:
    """Profilbeschreibung für einen vollständigen Öffnungsverlauf."""

    profile_id: int
    name: str
    total_steps: int
    interval_seconds: int
    points: List[RampPoint]


def _weibull_cdf(t: float, shape_k: float, scale_lambda: float) -> float:
    """Weibull-CDF für normierte Verläufe (0..1)."""
    if t <= 0:
        return 0.0
    return 1 - math.exp(-((t / scale_lambda) ** shape_k))


def _normalized_exponential(t: float, growth_beta: float) -> float:
    """Normierte Exponentialfunktion (0..1) mit langsamen Start und schnellem Ende."""
    if t <= 0:
        return 0.0
    if growth_beta <= 0:
        raise ValueError("growth_beta muss > 0 sein")
    numerator = math.exp(growth_beta * t) - 1
    denominator = math.exp(growth_beta) - 1
    return numerator / denominator


def build_weibull_profile(
    profile_id: int,
    shape_k: float,
    scale_lambda: float,
    *,
    total_steps: int = 2500,
    duration_seconds: int = 1800,
    interval_seconds: int = 30,
) -> RampProfile:
    """Erzeugt ein Rampenprofil aus Weibull-Parametern.

    Die resultierenden `step_delta` sind jeweils positive Öffnungsschritte.
    """
    intervals = duration_seconds // interval_seconds
    if intervals < 1:
        raise ValueError("duration_seconds muss >= interval_seconds sein")

    points: List[RampPoint] = []
    previous_target = 0

    for i in range(1, intervals + 1):
        t_norm = i / intervals
        cdf = _weibull_cdf(t_norm, shape_k=shape_k, scale_lambda=scale_lambda)
        cdf_clamped = min(max(cdf, 0.0), 1.0)

        target_steps = round(total_steps * cdf_clamped)
        delta = max(0, target_steps - previous_target)

        points.append(RampPoint(second=i * interval_seconds, step_delta=delta))
        previous_target = target_steps

    # Restschritte auf letzten Punkt aufschlagen, damit total_steps erreicht wird.
    remainder = total_steps - sum(point.step_delta for point in points)
    if remainder > 0:
        last = points[-1]
        points[-1] = RampPoint(second=last.second, step_delta=last.step_delta + remainder)

    return RampProfile(
        profile_id=profile_id,
        name=f"weibull-k{shape_k}-lambda{scale_lambda}",
        total_steps=total_steps,
        interval_seconds=interval_seconds,
        points=points,
    )


def build_exponential_profile(
    profile_id: int,
    growth_beta: float = 4.0,
    *,
    total_steps: int = 2500,
    duration_seconds: int = 1800,
    interval_seconds: int = 30,
) -> RampProfile:
    """Erzeugt ein Rampenprofil mit langsamem Beginn und starkem Anstieg am Ende.

    Diese Funktion ist als einfacher Startpunkt gedacht, bis eine externe
    datenbasierte Degradationsfunktion vorliegt.
    """
    intervals = duration_seconds // interval_seconds
    if intervals < 1:
        raise ValueError("duration_seconds muss >= interval_seconds sein")

    points: List[RampPoint] = []
    previous_target = 0

    for i in range(1, intervals + 1):
        t_norm = i / intervals
        exp_value = _normalized_exponential(t_norm, growth_beta=growth_beta)
        exp_clamped = min(max(exp_value, 0.0), 1.0)

        target_steps = round(total_steps * exp_clamped)
        delta = max(0, target_steps - previous_target)

        points.append(RampPoint(second=i * interval_seconds, step_delta=delta))
        previous_target = target_steps

    remainder = total_steps - sum(point.step_delta for point in points)
    if remainder > 0:
        last = points[-1]
        points[-1] = RampPoint(second=last.second, step_delta=last.step_delta + remainder)

    return RampProfile(
        profile_id=profile_id,
        name=f"exp-beta{growth_beta}",
        total_steps=total_steps,
        interval_seconds=interval_seconds,
        points=points,
    )


def default_profiles() -> Dict[int, RampProfile]:
    """Liefert 10 vordefinierte Rampenprofile.

    Alle Profile verwenden denselben physikalischen Mechanismus
    (identische Weibull-Parameter). Die Unterscheidung erfolgt nur
    über die Dauer bis zum Ausfall (Zeitskalierung):
    - Profil 1: schnellster Ausfall
    - Profil 5: mittlere Ausfallzeit
    - Profil 10: längste Ausfallzeit
    """
    base_shape_k = 3.0
    base_scale_lambda = 1.0

    # Reine Zeitskalierung von schnell (1) nach langsam (10):
    # längster Versuch = 30 Minuten, in 10 gleich große Zeitfenster geteilt.
    # Damit entstehen Profile mit 3, 6, 9, ..., 30 Minuten.
    durations_seconds = [profile_id * 180 for profile_id in range(1, 11)]

    return {
        profile_id: build_weibull_profile(
            profile_id=profile_id,
            shape_k=base_shape_k,
            scale_lambda=base_scale_lambda,
            duration_seconds=duration_seconds,
        )
        for profile_id, duration_seconds in enumerate(durations_seconds, start=1)
    }


def serial_commands_for_profile(profile: RampProfile, direction: str = "a") -> List[str]:
    """Wandelt Rampenpunkte in serielle Kommandos um.

    direction:
    - "a" = öffnen
    - "z" = schließen
    """
    if direction not in {"a", "z"}:
        raise ValueError("direction muss 'a' oder 'z' sein")

    return [f"{point.step_delta}{direction}" for point in profile.points if point.step_delta > 0]


def default_exponential_profiles() -> Dict[int, RampProfile]:
    """10 Zeit-skalierte Exponentialprofile mit gleicher Beta-Form."""
    growth_beta = 4.0
    durations_seconds = [profile_id * 180 for profile_id in range(1, 11)]
    return {
        profile_id: build_exponential_profile(
            profile_id=profile_id,
            growth_beta=growth_beta,
            duration_seconds=duration_seconds,
        )
        for profile_id, duration_seconds in enumerate(durations_seconds, start=1)
    }


def print_profile_overview() -> None:
    """Einfache CLI-Ausgabe für schnelle Sichtprüfung."""
    print("Weibull-Profile:")
    profiles = default_profiles()
    for profile_id, profile in profiles.items():
        command_count = len(serial_commands_for_profile(profile))
        print(
            f"  Profil {profile_id:02d}: {profile.name}, "
            f"Interval={profile.interval_seconds}s, "
            f"Kommandos={command_count}, Gesamt={profile.total_steps} Schritte"
        )

    print("Exponential-Profile:")
    profiles = default_exponential_profiles()
    for profile_id, profile in profiles.items():
        command_count = len(serial_commands_for_profile(profile))
        print(
            f"  Profil {profile_id:02d}: {profile.name}, "
            f"Interval={profile.interval_seconds}s, "
            f"Kommandos={command_count}, Gesamt={profile.total_steps} Schritte"
        )


if __name__ == "__main__":
    print_profile_overview()
