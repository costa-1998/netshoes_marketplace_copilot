"""Aplicação FastAPI: criação, handler global de erros e health check."""

from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from kam_agent.api.dependencies import obter_settings
from kam_agent.api.routes import router
from kam_agent.config import Settings
from kam_agent.domain.exceptions import DomainError

logger = logging.getLogger(__name__)

_MENSAGEM_GENERICA = "Falha interna ao processar a solicitação."


def _correlation_id(request: Request) -> str:
    return request.headers.get("X-Correlation-Id") or str(uuid.uuid4())


def create_app(settings: Settings | None = None) -> FastAPI:
    """Cria a aplicação, falhando na inicialização se a configuração é inválida."""
    if settings is None:
        settings = obter_settings()

    app = FastAPI(title="KAM Virtual — Netshoes Marketplace", version="0.1.0")
    app.state.settings = settings
    # A configuração resolvida na criação é a fonte de verdade do processo;
    # sem o override, as rotas leriam o cache global do ambiente.
    app.dependency_overrides[obter_settings] = lambda: settings
    app.include_router(router)

    @app.exception_handler(DomainError)
    async def _erro_dominio(request: Request, exc: DomainError) -> JSONResponse:
        correlation_id = _correlation_id(request)
        logger.info("Erro de domínio (correlation_id=%s): %s", correlation_id, exc)
        return JSONResponse(
            status_code=422,
            content={"erro": str(exc), "correlation_id": correlation_id},
        )

    @app.exception_handler(Exception)
    async def _erro_inesperado(request: Request, exc: Exception) -> JSONResponse:
        correlation_id = getattr(exc, "correlation_id", None) or _correlation_id(request)
        logger.exception("Erro inesperado (correlation_id=%s)", correlation_id)
        return JSONResponse(
            status_code=500,
            content={"erro": _MENSAGEM_GENERICA, "correlation_id": correlation_id},
        )

    return app


app = create_app()
