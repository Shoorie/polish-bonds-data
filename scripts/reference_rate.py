from dataclasses import dataclass


@dataclass(frozen=True)
class RateChange:
    effective_from: str
    basis_points: int


def changes_in_force_since(changes: list[RateChange], day: str) -> list[RateChange]:
    in_force = [change for change in changes if change.effective_from <= day][-1:]
    return in_force + [change for change in changes if change.effective_from > day]


def with_latest_decision(changes: list[RateChange], latest: RateChange) -> list[RateChange]:
    if latest.effective_from > changes[-1].effective_from:
        return changes + [latest] if latest.basis_points != changes[-1].basis_points else changes
    if rate_on(changes, latest.effective_from) != latest.basis_points:
        raise ValueError(f"NBP gives {latest} but the history has {rate_on(changes, latest.effective_from)} bp")
    return changes


def rate_on(changes: list[RateChange], day: str) -> int:
    in_force = [change for change in changes if change.effective_from <= day]
    if not in_force:
        raise ValueError(f"no reference rate known on {day}")
    return in_force[-1].basis_points
