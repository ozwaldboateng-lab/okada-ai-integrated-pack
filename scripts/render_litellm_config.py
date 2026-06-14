from __future__ import annotations

import argparse
import os
from pathlib import Path
from string import Template

REQUIRED_ENV = [
    "OPENAI_API_BASE",
    "OPENAI_API_KEY",
    "LITELLM_MASTER_KEY",
    "CHEAP_MODEL_NAME",
    "STRONG_MODEL_NAME",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Render LiteLLM config from template")
    parser.add_argument("--template", required=True, help="Path to template YAML")
    parser.add_argument(
        "--route-map",
        default=os.getenv("OKADA_ROUTE_MAP_PATH"),
        help="Path to the LiteLLM route map exposed to the Okada callback",
    )
    parser.add_argument("--output", required=True, help="Output path for rendered YAML")
    args = parser.parse_args()

    missing = [key for key in REQUIRED_ENV if not os.getenv(key)]
    if missing:
        raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")
    if args.route_map:
        route_map_path = Path(args.route_map)
        if not route_map_path.exists():
            raise SystemExit(f"Route map not found: {route_map_path}")
        os.environ["OKADA_ROUTE_MAP_PATH"] = str(route_map_path)

    template_path = Path(args.template)
    output_path = Path(args.output)
    content = template_path.read_text(encoding="utf-8")
    rendered = Template(content).safe_substitute(os.environ)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(f"Rendered LiteLLM config: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
