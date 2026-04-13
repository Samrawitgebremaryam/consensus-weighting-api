"""Business logic for consensus-based quadratic weighting."""

from __future__ import annotations

from collections import defaultdict
from math import sqrt
from typing import Iterable

from app.schemas import AllocationIn, TargetWeightOut


def _aggregate_user_totals(
    allocations: Iterable[AllocationIn],
) -> dict[str, dict[str, float]]:
    """Combine repeated allocations by the same user for the same target."""

    user_totals_by_target: dict[str, dict[str, float]] = defaultdict(
        lambda: defaultdict(float)
    )

    for allocation in allocations:
        user_totals_by_target[allocation.target_id][allocation.user_id] += allocation.amount

    return user_totals_by_target


def calculate_weights(allocations: Iterable[AllocationIn]) -> list[TargetWeightOut]:
    """Calculate quadratic-style weights for each target.

    The algorithm first combines multiple allocations from the same user to the same
    target. It then applies a quadratic-funding style formula:

        weight = (sum(sqrt(each user's total contribution))) ** 2

    This rewards broad participation more than concentrated capital.
    """

    aggregated_totals = _aggregate_user_totals(allocations)
    weighted_targets: list[TargetWeightOut] = []

    for target_id, user_totals in aggregated_totals.items():
        raw_total = sum(user_totals.values())
        root_sum = sum(sqrt(amount) for amount in user_totals.values())
        weight = root_sum**2

        weighted_targets.append(
            TargetWeightOut(
                targetId=target_id,
                rawTotal=round(raw_total, 6),
                uniqueUserCount=len(user_totals),
                weight=round(weight, 6),
            )
        )

    return sorted(weighted_targets, key=lambda result: (-result.weight, result.target_id))
