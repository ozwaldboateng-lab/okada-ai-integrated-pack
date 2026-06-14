from __future__ import annotations

from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1] / "specs" / "okada-ai-spec"
    expected = [
        root / "api" / "okada-governance.openapi.yaml",
        root / "registry" / "spec_registry.yaml",
        root / "schemas" / "diagnose-request.schema.json",
    ]
    missing = [str(p) for p in expected if not p.exists()]
    if missing:
        raise SystemExit(f"Missing required spec files: {missing}")
    print("Spec pack looks structurally valid.")


if __name__ == "__main__":
    main()
