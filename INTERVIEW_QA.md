# rag-llm-observability-platform — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does rag-llm-observability-platform address, and what can you demonstrate?

This is a local laptop proof. It does not call a hosted model and it does not apply production changes.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/ragobs/main.py`](src/ragobs/main.py): Implementation or supporting configuration.
- [`src/ragobs/analyze.py`](src/ragobs/analyze.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/ragobs/__init__.py`](src/ragobs/__init__.py): Implementation or supporting configuration.
- [`tests/test_analyze.py`](tests/test_analyze.py): Executable checks and regression examples.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): GitHub Actions job definitions.
- [`README.md`](README.md): Project explanations or operating notes.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `analyze` and explain the decision it makes?

The main walkthrough here is `analyze(rows)` in [`src/ragobs/analyze.py`](src/ragobs/analyze.py#L5).

```python
def analyze(rows):
    if not isinstance(rows, list) or not rows or not all(isinstance(r, dict) for r in rows):
        raise InputError("rows must be a non-empty list of objects")
    values = []
    groups = {}
    skipped = 0
    for row in rows:
        raw = row.get("hit")
        try:
            number = float(raw)
        except (TypeError, ValueError):
            skipped += 1
            continue
        values.append(number)
        key = str(row.get("pipeline", "unknown"))
        groups.setdefault(key, []).append(number)
    if not values:
        raise InputError("no numeric hit values")
    values.sort()
    mid = len(values) // 2
```

This is an excerpt; follow the source link for the rest of the branches.

The implementation calls `InputError`, `all`, `float`, `groups.items`, `groups.setdefault`, `groups.setdefault(key, []).append`, `isinstance`, `len`, `round`. In an interview, trace those calls in execution order using a fixture input.

## 4. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `InputError('rows must be a non-empty list of objects')` in [`src/ragobs/analyze.py`](src/ragobs/analyze.py#L7).
- `InputError('no numeric hit values')` in [`src/ragobs/analyze.py`](src/ragobs/analyze.py#L22).
- `HTTPException(status_code=422, detail=str(exc))` in [`src/ragobs/main.py`](src/ragobs/main.py#L17).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 5. Which test would you use to demonstrate correctness?

[`tests/test_analyze.py`](tests/test_analyze.py#L7) contains `test_summary`:

```python
def test_summary():
    payload = client.post("/analyze", json={"rows": [{'pipeline': 'hybrid', 'hit': 1}, {'pipeline': 'hybrid', 'hit': 1}, {'pipeline': 'bm25', 'hit': 1}]}).json()
    assert payload["mean"] == 1.0
    assert payload["by_pipeline"]["hybrid"]
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 6. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/ragobs/main.py`](src/ragobs/main.py#L8).
- `POST /analyze` → `post_analyze` in [`src/ragobs/main.py`](src/ragobs/main.py#L13).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 7. How would you investigate data ownership and persistence?

Trace the data/configuration files and the code that reads or writes them in the component table. Identify which files are examples, which records are mutable, and which external store is actually configured. I would document those facts before discussing retention, backup, or tenant isolation.

## 8. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 9. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 10. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 11. What is the input-to-output contract of `analyze`?

In [`src/ragobs/analyze.py`](src/ragobs/analyze.py#L5), `analyze(rows)` receives the inputs. The function computes these intermediate values:

- `values = []`
- `groups = {}`
- `skipped = 0`
- `mid = len(values) // 2`
- `median = values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2`
- `by_group = {name: round(sum(nums) / len(nums), 4) for name, nums in groups.items()}`

Its result is defined by:

- `{'rows': len(rows), 'skipped': skipped, 'mean': round(sum(values) / len(values), 4), 'median': median, 'min': values[0], 'max': values[-1], 'by_pipeline': by_group}`

## 12. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/ragobs/analyze.py`](src/ragobs/analyze.py#L5) branches on:

- `not isinstance(rows, list) or not rows or (not all((isinstance(r, dict) for r in rows)))`
- `not values`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.
