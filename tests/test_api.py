"""API tests for request validation and response behavior."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_weights_endpoint_returns_results_for_valid_allocations() -> None:
    """The API should return grouped weights using camelCase response fields."""

    response = client.post(
        "/weights",
        json=[
            {"userId": "user_1", "targetId": "A", "amount": 100},
            {"userId": "user_1", "targetId": "A", "amount": 100},
            {"userId": "user_2", "targetId": "A", "amount": 100},
        ],
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "targetId": "A",
            "rawTotal": 300.0,
            "uniqueUserCount": 2,
            "weight": 582.842712,
        }
    ]


def test_weights_endpoint_rejects_invalid_allocations() -> None:
    """The API should reject invalid payload fields with clear validation details."""

    response = client.post(
        "/weights",
        json=[
            {"userId": "", "targetId": "A", "amount": 100},
            {"userId": "user_2", "targetId": " ", "amount": 0},
        ],
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "field": "body.0.userId",
                "message": "String should have at least 1 character",
            },
            {
                "field": "body.1.targetId",
                "message": "String should have at least 1 character",
            },
            {
                "field": "body.1.amount",
                "message": "Input should be greater than 0",
            },
        ]
    }


def test_weights_endpoint_handles_empty_input() -> None:
    """An empty list is valid and should return an empty result set."""

    response = client.post("/weights", json=[])

    assert response.status_code == 200
    assert response.json() == []
