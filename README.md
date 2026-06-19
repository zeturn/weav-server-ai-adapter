# weav-server-ai-adapter

Server-side adapter package for WeavInt AI runtime.

`weav-server-ai-adapter` connects reusable AI runtime contracts to `weav_server` infrastructure such as SQLModel sessions, encrypted API keys, tenant usage accounting, and model catalog records.

## Scope

This package exposes:

- `DbCredentialStore` for server-backed provider credentials
- `DbModelCatalog` for server-backed model discovery
- `TenantUsageSink` for tenant usage accounting
- `build_server_ai_runtime()` for assembling a server-ready `AIRuntime`

## Package Relationship

The AI packages are intended to be consumed in this order:

1. `weav-ai-core` provides shared primitives and compatibility imports.
2. `weav-ai-providers` exposes provider construction and model discovery.
3. `weav-ai-runtime` assembles credentials, model catalog, routing, and usage contracts.
4. `weav-server-ai-adapter` connects the reusable runtime to `weav_server` infrastructure.

## Installation

```bash
python -m pip install git+https://github.com/zeturn/weav-server-ai-adapter.git@main
```

For local development:

```bash
python -m pip install -e ".[dev]" --no-deps
```

This adapter imports `weav_server` internals at runtime. It is intended for the WeavInt server environment, not as a standalone provider package.

## Usage

```python
from weav_server_ai_adapter import build_server_ai_runtime

runtime = build_server_ai_runtime(tenant="default", user_id="user_123", purpose="chat")
router = runtime.build_router()
```

## Development

Run the local quality checks:

```bash
python -m pytest
python -m build --wheel
```

## Release Notes

This package is currently in migration bootstrap status. Before cutting a production release, pin `weav-ai-runtime` to a tag or published package version instead of tracking `main`.
