"""Contratos Pydantic v2 do domínio do copiloto KAM.

Registros declaram a própria granularidade (D1): um registro ``sku_filho``
exige ``sku_filho`` preenchido; um registro ``sku_pai`` o dispensa.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator

from kam_agent.domain.enums import (
    Granularidade,
    ResultadoGuardrail,
    TipoGargalo,
    TipoRecomendacao,
)


class _ModeloBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SellerMaster(_ModeloBase):
    """Cadastro do seller (``seller_master.csv``)."""

    id_seller: str
    nome_seller: str
    nota_reputacao: float | None = None
    contato_nome: str | None = None
    contato_telefone: str | None = None
    contato_email: str | None = None
    rentabilidade: float | None = None
    taxa_conversao: float | None = None
    percentual_de_comissao: float | None = None


class PerformanceSKU(_ModeloBase):
    """Registro diário de performance no grão de SKU filho.

    Métricas são ``Optional`` porque a origem pode não as fornecer; ausência
    nunca é convertida em zero silencioso (D3).
    """

    data: date
    id_seller: str
    sku_pai: str
    sku_filho: str | None = None
    granularidade: Granularidade = Granularidade.SKU_FILHO

    nome_produto: str | None = None
    categoria_do_produto: str | None = None
    categoria_curva: str | None = None

    vmd: float | None = None
    unidades_vendidas: float | None = None
    receita_captada: float | None = None
    receita_faturada: float | None = None
    percentual_de_comissao: float | None = None
    valor_de_comissao: float | None = None
    margem: float | None = None
    rentabilidade: float | None = None

    preco_de: float | None = None
    preco_por: float | None = None
    preco_1p: float | None = None
    delta_preco: float | None = None
    prazo_medio_envio: float | None = None
    delta_prazo: float | None = None
    custo_frete: float | None = None
    tem_1p: bool | None = None
    buybox_win_rate: float | None = None
    winner_avg_price: float | None = None
    winner_avg_prazo: float | None = None

    estoque: float | None = None
    cobertura: float | None = None

    sessoes: float | None = None
    cliques: float | None = None
    adicao_ao_carrinho: float | None = None
    adicao_de_informacoes_de_envio: float | None = None
    adicao_de_pagamento: float | None = None
    compras_faturadas: float | None = None
    cancelamentos: float | None = None
    taxa_conversao: float | None = None

    @model_validator(mode="after")
    def _validar_granularidade(self) -> PerformanceSKU:
        if self.granularidade is Granularidade.SKU_FILHO and not self.sku_filho:
            raise ValueError("granularidade='sku_filho' exige 'sku_filho' preenchido")
        return self

    @property
    def exige_sku_filho(self) -> bool:
        """True quando a análise pode operar no nível de SKU filho."""
        return self.granularidade is Granularidade.SKU_FILHO and bool(self.sku_filho)


class ResultadoGuardrailDetalhado(_ModeloBase):
    """Resultado auditável de um guardrail: estado + identificador + motivo."""

    guardrail: str
    resultado: ResultadoGuardrail
    motivo: str

    @property
    def aprovado(self) -> bool:
        return self.resultado is ResultadoGuardrail.APROVADO


class Recomendacao(_ModeloBase):
    """Recomendação acionável, candidata ao Top 3."""

    tipo: TipoRecomendacao
    impacto_financeiro_estimado: float
    justificativa: str
    sku_pai: str
    sku_filho: str | None = None
    gargalo: TipoGargalo = TipoGargalo.NENHUM
    guardrails: tuple[ResultadoGuardrailDetalhado, ...] = Field(default_factory=tuple)

    @property
    def bloqueada(self) -> bool:
        """True se qualquer guardrail aplicável não aprovou a recomendação."""
        return any(g.resultado is not ResultadoGuardrail.APROVADO for g in self.guardrails)
