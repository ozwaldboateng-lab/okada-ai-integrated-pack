# 52. Local Development Quickstart

## Quick path
1. Create a virtual environment.
2. Install package in editable mode with dev extras.
3. Run `uvicorn app.main:app --reload`.
4. Run `python scripts/integration_demo.py`.
5. Run `pytest`.

## Recommended commands
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

In another shell:
```bash
python scripts/integration_demo.py
python scripts/dev_status.py
pytest
```
