"""Pydantic models for the Consensus Weighting API."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
PositiveAmount = Annotated[float, Field(gt=0)]


class AllocationIn(BaseModel):
    """A single user allocation submitted to the API."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: NonEmptyString = Field(alias="userId")
    target_id: NonEmptyString = Field(alias="targetId")
    amount: PositiveAmount


class TargetWeightOut(BaseModel):
    """The computed weighting result for a single target."""

    model_config = ConfigDict(populate_by_name=True)

    target_id: str = Field(alias="targetId")
    raw_total: float = Field(alias="rawTotal")
    unique_user_count: int = Field(alias="uniqueUserCount")
    weight: float
