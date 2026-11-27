"""Modelos de requisição e resposta do chat.

O corpo nunca carrega ``id_seller``: o seller vem da sessão autenticada
(guardrail #7). Qualquer ``id_seller`` enviado no corpo é descartado na
construção do comando.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RequisicaoChat(BaseModel):
    """Corpo aceito por ``POST /chat``."""

    model_config = ConfigDict(extra="ignore")

    mensagem: str = Field(min_length=1, max_length=4000)
    correlation_id: str | None = None

    @field_validator("mensagem")
    @classmethod
    def _nao_vazia(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("mensagem não pode ser vazia")
        return valor.strip()


class RespostaChat(BaseModel):
    """Resposta consolidada do copiloto."""

    resposta: str
    correlation_id: str
    id_seller: str
    especialista: str | None = None
    total_recomendacoes: int = 0


class RespostaHealth(BaseModel):
    """Estado do serviço e das dependências em uso."""

    status: str
    dw_backend: str
    memory_backend: str
    dependencias_indisponiveis: list[str] = Field(default_factory=list)
