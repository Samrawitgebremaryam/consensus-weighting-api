"""Unit tests for quadratic weighting logic."""

from __future__ import annotations

import pytest

from app.schemas import AllocationIn
from app.weighting import calculate_weights


def test_concentrated_and_distributed_cases_favor_broad_consensus() -> None:
    """A distributed target should outperform a concentrated target with equal capital."""

    concentrated_allocations = [
        AllocationIn(userId="user_1", targetId="A", amount=10_000),
    ]
    distributed_allocations = [
        AllocationIn(userId=f"user_{index}", targetId="B", amount=100)
        for index in range(1, 101)
    ]

    concentrated_result = calculate_weights(concentrated_allocations)[0]
    distributed_result = calculate_weights(distributed_allocations)[0]

    assert concentrated_result.target_id == "A"
    assert concentrated_result.raw_total == pytest.approx(10_000)
    assert concentrated_result.unique_user_count == 1

    assert distributed_result.target_id == "B"
    assert distributed_result.raw_total == pytest.approx(10_000)
    assert distributed_result.unique_user_count == 100
    assert distributed_result.weight >= concentrated_result.weight * 2


def test_multiple_allocations_from_same_user_are_combined_before_weighting() -> None:
    """Repeated allocations from the same user should count as one contributor."""

    allocations = [
        AllocationIn(userId="user_1", targetId="A", amount=25),
        AllocationIn(userId="user_1", targetId="A", amount=75),
        AllocationIn(userId="user_2", targetId="A", amount=100),
    ]

    result = calculate_weights(allocations)[0]

    assert result.raw_total == pytest.approx(200)
    assert result.unique_user_count == 2
    assert result.weight == pytest.approx(400)


def test_empty_allocation_list_returns_no_results() -> None:
    """An empty payload should produce an empty response list."""

    assert calculate_weights([]) == []


def test_allocations_are_grouped_independently_per_target() -> None:
    """The same user can support multiple targets without cross-target merging."""

    allocations = [
        AllocationIn(userId="user_1", targetId="A", amount=100),
        AllocationIn(userId="user_1", targetId="B", amount=100),
        AllocationIn(userId="user_2", targetId="B", amount=100),
    ]

    results = calculate_weights(allocations)

    assert len(results) == 2

    first_result, second_result = results

    assert first_result.target_id == "B"
    assert first_result.raw_total == pytest.approx(200)
    assert first_result.unique_user_count == 2
    assert first_result.weight == pytest.approx(400)

    assert second_result.target_id == "A"
    assert second_result.raw_total == pytest.approx(100)
    assert second_result.unique_user_count == 1
    assert second_result.weight == pytest.approx(100)
