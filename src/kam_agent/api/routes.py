"""Rotas HTTP do copiloto."""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Header, Request

from kam_agent.adapters.bigquery_seller_data import BigQuerySellerAdapter
from kam_agent.agents.graph import executar
from kam_agent.api.dependencies import (
    obter_porta_dados,
    obter_porta_memoria,
    obter_settings,
)
from kam_agent.api.schemas import RequisicaoChat, RespostaChat, RespostaHealth
from kam_agent.config import Settings
from kam_agent.domain.exceptions import SellerNaoEncontrado
from kam_agent.ports.seller_data import SellerDataPort
from kam_agent.ports.session_memory import SessionMemoryPort


class FalhaInterna(RuntimeError):
    """Falha não recuperável de uma etapa, sinalizada à camada HTTP."""

    def __init__(self, detalhe: str, correlation_id: str) -> None:
        self.detalhe = detalhe
        self.correlation_id = correlation_id
        super().__init__(detalhe)


router = APIRouter()

CHAVE_SELLER = "id_seller"


def _resolver_sessao(
    memoria: SessionMemoryPort,
    chave_sessao: str | None,
    id_seller_sessao: str | None,
) -> tuple[str, str]:
    """Devolve ``(chave_sessao, id_seller)``, criando sessão se necessário.

    O seller vem da sessão (ou do header autenticado), nunca do corpo.
    """
    chave = chave_sessao or str(uuid.uuid4())
    estado = memoria.ler(chave) or {}
    id_seller = estado.get(CHAVE_SELLER) or id_seller_sessao
    if not id_seller:
        raise SellerNaoEncontrado("(sessão sem seller)")
    if estado.get(CHAVE_SELLER) != id_seller:
        memoria.gravar(chave, {**estado, CHAVE_SELLER: id_seller})
    return chave, id_seller


@router.get("/health", response_model=RespostaHealth)
def health(
    settings: Settings = Depends(obter_settings),
    porta_dados: SellerDataPort = Depends(obter_porta_dados),
) -> RespostaHealth:
    """Reporta os backends em uso e dependências indisponíveis."""
    indisponiveis: list[str] = []
    if isinstance(porta_dados, BigQuerySellerAdapter):
        indisponiveis.append("dw_backend=bigquery (BigQuerySellerAdapter não implementado)")

    return RespostaHealth(
        status="degradado" if indisponiveis else "ok",
        dw_backend=settings.dw_backend,
        memory_backend=settings.memory_backend,
        dependencias_indisponiveis=indisponiveis,
    )


@router.post("/chat", response_model=RespostaChat)
def chat(
    requisicao: RequisicaoChat,
    request: Request,
    porta_dados: SellerDataPort = Depends(obter_porta_dados),
    memoria: SessionMemoryPort = Depends(obter_porta_memoria),
    x_sessao: str | None = Header(default=None, alias="X-Sessao"),
    x_seller: str | None = Header(default=None, alias="X-Seller-Id"),
) -> RespostaChat:
    """Executa o grafo para o seller da sessão."""
    correlation_id = requisicao.correlation_id or request.headers.get(
        "X-Correlation-Id", str(uuid.uuid4())
    )
    _, id_seller = _resolver_sessao(memoria, x_sessao, x_seller)

    estado = executar(
        porta=porta_dados,
        id_seller=id_seller,
        mensagem=requisicao.mensagem,
        correlation_id=correlation_id,
        data_referencia=date.today(),
    )

    if estado.get("erro"):
        # O grafo registra a falha no estado sem propagar a exceção bruta
        # (task 8.4); a rota converte isso em erro interno para o handler
        # global, que responde 500 sem vazar detalhe (D11).
        raise FalhaInterna(estado["erro"], correlation_id)

    return RespostaChat(
        resposta=estado.get("resposta") or "",
        correlation_id=correlation_id,
        id_seller=id_seller,
        especialista=estado.get("especialista"),
        total_recomendacoes=len(estado.get("recomendacoes") or ()),
    )
