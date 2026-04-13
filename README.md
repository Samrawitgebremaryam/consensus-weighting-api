# The Consensus Weighting API

## Project Overview

This project is a small FastAPI service built for a take-home assessment. It accepts a raw JSON array of allocations and returns a weighted score for each `targetId`.

The main design goal is to reward broad consensus more than concentrated capital. A single large contributor should not easily overpower many smaller contributors supporting the same target.

## Weighting Formula

The service uses a quadratic-funding style formula:

```text
weight = (sum(sqrt(each user's total contribution to that target))) ^ 2
```

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
- Empty input lists return an empty list.
- `amount` must be numeric and greater than `0`.
- `userId` and `targetId` must be non-empty strings.
- Validation errors are returned in a compact and readable format.
- Results are returned in deterministic order by highest weight first, then `targetId`.

## AI Process Log

This project was built with help from AI tools, primarily OpenAI Codex/ChatGPT, to speed up scaffolding, refine the formula explanation, and generate a clean initial test suite.

How AI was used:

- To propose a small production-style FastAPI structure.
- To validate the grouping approach before applying the weighting formula.
- To check that the implementation combines repeated allocations from the same user before scoring.
- To generate the required pytest cases for concentrated versus distributed participation.

What I verified manually:

- The grouping logic is done per `targetId`, then per `userId`.
- Repeated allocations from the same user do not create fake consensus.
- The distributed test case produces a weight at least 2x greater than the concentrated case.
- Request validation and empty-input behavior work as expected.

One AI-driven design decision that was reviewed carefully:

- A simpler dampening formula such as `sum(sqrt(contribution))` was considered initially, but the final implementation uses the quadratic-funding style formula requested in the prompt: `(sum(sqrt(contribution)))^2`.
