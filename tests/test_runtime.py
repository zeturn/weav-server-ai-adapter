import importlib
import sys
import types
from dataclasses import dataclass


def import_adapter(monkeypatch):
    runtime = types.ModuleType("weav_ai_runtime")

    @dataclass
    class AIRuntimeContext:
        tenant: str | None = None
        user_id: str | None = None
        purpose: str | None = None

    @dataclass
    class ModelSpec:
        provider: str
        model: str

    @dataclass
    class UsageRecord:
        tokens: int
        cost: float
        provider: str | None = None
        model: str | None = None
        tenant: str | None = None
        user_id: str | None = None
        purpose: str | None = None

    class AIRuntime:
        def __init__(self, *, context, credentials, model_catalog=None, usage_sink=None):
            self.context = context
            self.credentials = credentials
            self.model_catalog = model_catalog
            self.usage_sink = usage_sink

    runtime.AIRuntime = AIRuntime
    runtime.AIRuntimeContext = AIRuntimeContext
    runtime.ModelSpec = ModelSpec
    runtime.UsageRecord = UsageRecord

    monkeypatch.setitem(sys.modules, "weav_ai_runtime", runtime)
    for name in ["weav_server_ai_adapter", "weav_server_ai_adapter.runtime"]:
        sys.modules.pop(name, None)
    return importlib.import_module("weav_server_ai_adapter")


def test_build_server_ai_runtime_wires_default_adapters(monkeypatch):
    adapter = import_adapter(monkeypatch)

    runtime = adapter.build_server_ai_runtime(tenant="default", user_id="user-1", purpose="chat")

    assert runtime.context.tenant == "default"
    assert runtime.context.user_id == "user-1"
    assert runtime.context.purpose == "chat"
    assert isinstance(runtime.credentials, adapter.DbCredentialStore)
    assert isinstance(runtime.model_catalog, adapter.DbModelCatalog)
    assert isinstance(runtime.usage_sink, adapter.TenantUsageSink)


def test_default_base_urls_are_normalized(monkeypatch):
    adapter = import_adapter(monkeypatch)
    store = adapter.DbCredentialStore()

    assert store.get_base_url(" OLLAMA ", object()) == "http://localhost:11434"
    assert store.get_base_url("deepseek", object()) == "https://api.deepseek.com"
    assert store.get_base_url("unknown", object()) is None
