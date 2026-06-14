from __future__ import annotations

import os
from pathlib import Path

import yaml

PREFERRED_COMPOSE_FILE = Path('ops/integrated/docker-compose.kernel-gateway-ui.yml')
PREFERRED_ENV_FILE = Path('ops/integrated/.env.example')

REQUIRED_FILES = [
    PREFERRED_COMPOSE_FILE,
    PREFERRED_ENV_FILE,
    Path('examples/litellm/route_map.json'),
    Path('examples/openwebui/okada_governance_pipe.py'),
    Path('examples/openwebui/okada_audit_filter.py'),
]

REQUIRED_ENV = [
    'OKADA_BASE_URL',
    'LITELLM_MASTER_KEY',
    'OPENAI_API_KEY',
]


def load_compose(path: Path = PREFERRED_COMPOSE_FILE) -> dict:
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def load_env_example(path: Path = PREFERRED_ENV_FILE) -> set[str]:
    keys: set[str] = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '=' not in stripped:
            continue
        keys.add(stripped.split('=', 1)[0])
    return keys


def check_compose_contract(compose: dict) -> list[str]:
    errors: list[str] = []
    services = compose.get('services', {})
    expected_services = {'okada-kernel-service', 'litellm-proxy', 'open-webui'}
    missing_services = expected_services - set(services)
    if missing_services:
        errors.append(f'missing compose services: {sorted(missing_services)}')

    litellm_env = services.get('litellm-proxy', {}).get('environment', {})
    if 'OKADA_BASE_URL' not in litellm_env:
        errors.append('litellm-proxy must use OKADA_BASE_URL')
    if 'OKADA_KERNEL_URL' in litellm_env:
        errors.append('litellm-proxy still references deprecated OKADA_KERNEL_URL')
    if 'CHEAP_MODEL_NAME' not in litellm_env or 'STRONG_MODEL_NAME' not in litellm_env:
        errors.append('litellm-proxy must expose CHEAP_MODEL_NAME and STRONG_MODEL_NAME')

    openwebui_env = services.get('open-webui', {}).get('environment', {})
    if 'OKADA_BASE_URL' not in openwebui_env:
        errors.append('open-webui must receive OKADA_BASE_URL for installed pipe/filter artifacts')
    return errors


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED_FILES:
        if not path.exists():
            errors.append(f'missing file: {path}')
    if not errors:
        errors.extend(check_compose_contract(load_compose()))
        env_keys = load_env_example()
        for required in REQUIRED_ENV:
            if required not in env_keys:
                errors.append(f'missing env example key: {required}')
    for name in REQUIRED_ENV:
        if not os.getenv(name):
            errors.append(f'missing env: {name}')

    if errors:
        print('E2E preflight failed:')
        for err in errors:
            print(f'- {err}')
        return 1

    print('E2E preflight passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
