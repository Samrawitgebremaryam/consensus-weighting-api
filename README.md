# The Consensus Weighting API

## Project Overview

This project is a small FastAPI service that calculates consensus-aware weights for capital allocations. It accepts a raw JSON array of allocations and returns a weighted score for each `targetId`.

The main design goal is to reward broad consensus more than concentrated capital. A single large contributor should not easily overpower many smaller contributors supporting the same target.

## Weighting Formula

The service uses a quadratic-funding style formula:

```text
weight = (sum(sqrt(each user's total contribution to that target))) ^ 2
```

For background on quadratic funding, see [P2P Foundation explainer](https://wiki.p2pfoundation.net/Quadratic_Funding)

Important implementation detail:

- Multiple allocations from the same user to the same target are combined first.

This matters because it prevents one user from splitting a large allocation into many smaller allocations to artificially boost the score.

### Why this favors distributed participation

If one user contributes `10,000`, the weight is:

```text
sqrt(10000)^2 = 100^2 = 10,000
```

If one hundred unique users each contribute `100`, the weight is:

```text
(100 * sqrt(100))^2 = (100 * 10)^2 = 1,000,000
```

Both targets receive the same raw capital, but the distributed case receives a far larger weight because consensus is valued more highly than concentration.

## Project Structure

```text
app/
  main.py        # FastAPI application and endpoint
  schemas.py     # Request and response models
  weighting.py   # Core business logic
tests/
  test_api.py
  test_weighting.py
```

## Run Instructions

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If you are using Git Bash on Windows, do not use the PowerShell `Activate.ps1` command. Use `source .venv/Scripts/activate` instead.

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000/weights`
- Interactive docs: `http://127.0.0.1:8000/docs`

### 4. Example request

Using `curl` on macOS, Linux, or Git Bash:

```bash
curl -X POST "http://127.0.0.1:8000/weights" \
  -H "Content-Type: application/json" \
  -d '[{"userId":"user_1","targetId":"A","amount":10000},{"userId":"user_2","targetId":"B","amount":50}]'
```

Using PowerShell:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/weights `
  -ContentType "application/json" `
  -Body '[{"userId":"user_1","targetId":"A","amount":10000},{"userId":"user_2","targetId":"B","amount":50}]'
```

## Test Instructions

Run the full test suite with:

```bash
python -m pytest
```

## Edge Cases Handled

- Multiple allocations from the same user to the same target are aggregated before weighting.
- The same user can contribute to multiple targets and is counted independently per target.
- Empty input lists return an empty list.
- The top-level request body must be a raw JSON array.
- `amount` must be numeric and greater than `0`.
- Numeric-looking strings such as `"100"` are rejected to keep the API contract strict.
- `userId` and `targetId` must be non-empty strings.
- Validation errors are returned in a compact and readable format.
- Results are returned in deterministic order by highest weight first, then `targetId`.

## Assumptions and Limitations

- This API assumes `userId` values are trustworthy and uniquely represent real users.
- Like any quadratic funding model, the weighting is only as sybil-resistant as the identity layer behind it.

## AI Process Log

This project was built with help from AI tools, primarily OpenAI Codex/ChatGPT, but the weighting approach and final verification decisions were reviewed manually.

Which AI tools were used:

- OpenAI Codex / ChatGPT for project scaffolding, formula discussion, and test generation support.

How the AI was prompted for the math and grouping logic:

- I first researched weighting approaches that reward broad consensus over concentrated capital and chose a quadratic funding style formula because it is a widely used and well-regarded approach for rewarding broad participation, especially in systems that use matching funds.
- After selecting the formula, I prompted the AI to implement the exact equation I chose: `(sum(sqrt(each user's total contribution to that target)))^2`.
- I specified that allocations must first be grouped by `targetId`, then aggregated by `userId` within each target before the weighting formula is applied.
- I also asked for automated tests covering the concentrated case, the distributed case, and validation behavior for invalid inputs.

How AI was used:

- To help scaffold a clean FastAPI project structure.
- To implement the grouping and weighting logic based on the formula I selected.
- To generate an initial set of pytest cases for the concentrated and distributed benchmark scenarios.
- To help draft the README and improve the explanation of the formula and edge cases.

What I verified manually:

- The choice of quadratic funding as the best-fit approach for this challenge before implementation, based on its strong alignment with broad-participation incentives and its practical use in platforms such as Gitcoin.
- The grouping logic is done per `targetId`, then per `userId`.
- Repeated allocations from the same user do not create fake consensus.
- The distributed test case produces a weight at least 2x greater than the concentrated case.
- Request validation and empty-input behavior work as expected.

AI mistakes or draft issues that were manually corrected:

- During exploration, a simpler square-root dampening formula such as `sum(sqrt(contribution))` was considered as an alternative, but the final implementation keeps the quadratic-funding-style formula that was selected for this project: `(sum(sqrt(contribution)))^2`.
- One early generated API test had an incorrect expected `rawTotal`; it was manually corrected after verifying that repeated allocations from the same user still contribute to the target's raw total even though they count as a single unique user for consensus purposes.
- An earlier validation draft relied on default type coercion, which would have accepted numeric-looking strings such as `"100"` for `amount`; this was tightened so the API now expects real numeric JSON values.
