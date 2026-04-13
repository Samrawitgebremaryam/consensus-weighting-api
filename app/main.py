"""FastAPI entrypoint for the Consensus Weighting API."""

from __future__ import annotations

from fastapi import Body, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import AllocationIn, TargetWeightOut
from app.weighting import calculate_weights

app = FastAPI(
    title="Consensus Weighting API",
    description=(
        "A small take-home service that calculates quadratic-style weights for "
        "capital allocations while favoring broad participation."
    ),
    version="1.0.0",
)


def _format_validation_errors(exc: RequestValidationError) -> list[dict[str, str]]:
    """Transform FastAPI validation errors into a compact, client-friendly shape."""

    formatted_errors: list[dict[str, str]] = []

    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"])
        formatted_errors.append(
            {
                "field": location,
                "message": error["msg"],
            }
        )

    return formatted_errors


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return validation problems in a predictable JSON structure."""

    return JSONResponse(
        status_code=422,
        content={"detail": _format_validation_errors(exc)},
    )


@app.post(
    "/weights",
    response_model=list[TargetWeightOut],
    response_model_by_alias=True,
    summary="Calculate target weights",
)
async def calculate_target_weights(
    allocations: list[AllocationIn] = Body(
        ...,
        description="A raw JSON array of user allocations.",
    ),
) -> list[TargetWeightOut]:
    """Calculate consensus-aware weights for the submitted allocations."""

    return calculate_weights(allocations)
