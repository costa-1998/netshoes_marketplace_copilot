"""Porta de acesso a dados de performance do seller."""

from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

from kam_agent.domain.models import PerformanceSKU, SellerMaster


class DadosSeller:
    """DTO de resultado de uma leitura de performance."""

    __slots__ = ("seller", "registros")

    def __init__(self, seller: SellerMaster | None, registros: tuple[PerformanceSKU, ...]) -> None:
        self.seller = seller
        self.registros = registros

    def __len__(self) -> int:
        return len(self.registros)

    def __iter__(self):
        return iter(self.registros)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DadosSeller):
            return NotImplemented
        return self.seller == other.seller and self.registros == other.registros

    def __repr__(self) -> str:
        return f"DadosSeller(seller={self.seller!r}, registros=<{len(self.registros)} registros>)"


@runtime_checkable
class SellerDataPort(Protocol):
    """Contrato de leitura de performance por SKU filho.

    Toda leitura exige ``id_seller`` e uma janela inclusiva. Implementações
    devem rejeitar leitura sem seller e janela invertida antes de acessar a
    fonte.
    """

    def ler_performance(
        self,
        id_seller: str,
        data_inicio: date,
        data_fim: date,
    ) -> DadosSeller: ...

    def ler_seller(self, id_seller: str) -> SellerMaster | None: ...
