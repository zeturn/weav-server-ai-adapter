from __future__ import annotations

from typing import Any

from weav_ai_runtime import AIRuntime, AIRuntimeContext, ModelSpec, UsageRecord


class DbCredentialStore:
    """CredentialStore backed by the weav-server API key table."""

    def get_api_key(self, provider: str, context: AIRuntimeContext) -> str | None:
        provider_norm = (provider or "").strip().lower()
        if not provider_norm:
            return None
        from weav_server.models.sql.base import get_session
        from weav_server.services.model_manager import ModelManager

        with get_session() as session:
            row = self._query_one(session, provider_norm, context.tenant)
            if row is None and context.tenant and provider_norm == "zhipu":
                row = self._query_one(session, provider_norm, None)
            if row is None:
                return None
            return ModelManager._decrypt_key(row.api_key)

    def get_base_url(self, provider: str, context: AIRuntimeContext) -> str | None:
        defaults = {
            "ollama": "http://localhost:11434",
            "deepseek": "https://api.deepseek.com",
            "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "zhipu": "https://open.bigmodel.cn/api/paas/v4",
        }
        return defaults.get((provider or "").strip().lower())

    @staticmethod
    def _query_one(session: Any, provider: str, tenant: str | None) -> Any | None:
        from sqlalchemy import desc, func
        from sqlmodel import select

        from weav_server.models.sql.api_key import ApiKeySQL

        stmt = select(ApiKeySQL).where(
            (func.lower(ApiKeySQL.provider) == provider) & ApiKeySQL.is_active.is_(True)
        )
        if tenant:
            stmt = stmt.where(ApiKeySQL.tenant == tenant)
        stmt = stmt.order_by(desc(ApiKeySQL.updated_at))
        return session.exec(stmt).first()


class DbModelCatalog:
    """ModelCatalog backed by ModelManager's existing model table facade."""

    def list_models(self, context: AIRuntimeContext, provider: str | None = None) -> dict[str, list[str]]:
        from weav_server.services.model_manager import ModelManager

        return ModelManager.get_available_models(context.tenant or "default", provider=provider)

    def resolve_model(
        self,
        context: AIRuntimeContext,
        provider: str | None = None,
        model: str | None = None,
    ) -> ModelSpec:
        return ModelSpec(provider=provider or "openai", model=model or "gpt-4o")


class TenantUsageSink:
    """UsageSink backed by the server tenant usage service."""

    def record(self, usage: UsageRecord) -> None:
        from weav_server.services.tenants import record_usage

        record_usage(
            usage.tenant,
            user_id=usage.user_id,
            tokens=int(usage.tokens),
            cost=float(usage.cost),
            provider=usage.provider,
            model=usage.model,
        )


def build_server_ai_runtime(
    *,
    tenant: str | None = None,
    user_id: str | None = None,
    purpose: str | None = None,
) -> AIRuntime:
    context = AIRuntimeContext(tenant=tenant, user_id=user_id, purpose=purpose)
    return AIRuntime(
        context=context,
        credentials=DbCredentialStore(),
        model_catalog=DbModelCatalog(),
        usage_sink=TenantUsageSink(),
    )
