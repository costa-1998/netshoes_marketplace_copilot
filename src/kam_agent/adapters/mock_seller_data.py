"""Adapter de dados local, determinístico, lendo as fixtures CSV (D7).

Lê com ``csv.DictReader``, cacheia em memória no primeiro acesso, filtra por
seller e janela inclusiva e descarta registros contaminados de outro seller
(guarda multi-tenant).
"""

from __future__ import annotations

import csv
import logging
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

from kam_agent.adapters.schema_mapping import converter_registro
from kam_agent.domain.models import PerformanceSKU, SellerMaster
from kam_agent.ports.seller_data import DadosSeller

logger = logging.getLogger(__name__)

_CAMPOS_MASTER = (
    "id_seller",
    "nome_seller",
    "nota_reputacao",
    "contato_nome",
    "contato_telefone",
    "contato_email",
    "rentabilidade",
    "taxa_conversao",
    "percentual_de_comissao",
)


class SellerInvalido(ValueError):
    """Leitura solicitada sem seller ou com janela invertida."""


def _ler_csv(caminho: Path) -> list[dict[str, str]]:
    with caminho.open("r", encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


class CsvMockSellerAdapter:
    """Implementação de ``SellerDataPort`` sobre as fixtures CSV."""

    def __init__(self, caminho_dados: Path, caminho_master: Path) -> None:
        self._caminho_dados = Path(caminho_dados)
        self._caminho_master = Path(caminho_master)
        self._cache_dados: list[dict[str, str]] | None = None
        self._cache_master: list[dict[str, str]] | None = None
        self.inconsistencias: list[str] = []

    def _dados(self) -> list[dict[str, str]]:
        if self._cache_dados is None:
            self._cache_dados = _ler_csv(self._caminho_dados)
        return self._cache_dados

    def _master(self) -> list[dict[str, str]]:
        if self._cache_master is None:
            self._cache_master = _ler_csv(self._caminho_master)
        return self._cache_master

    def _validar_leitura(self, id_seller: str, data_inicio: date, data_fim: date) -> None:
        if not id_seller or not id_seller.strip():
            raise SellerInvalido("Leitura exige id_seller não vazio.")
        if data_inicio > data_fim:
            raise SellerInvalido(
                f"Janela invertida: data_inicio {data_inicio} > data_fim {data_fim}."
            )

    def ler_performance(self, id_seller: str, data_inicio: date, data_fim: date) -> DadosSeller:
        self._validar_leitura(id_seller, data_inicio, data_fim)

        linhas = self._dados()
        chaves_do_seller = {
            (linha.get("data"), linha.get("sku_filho"))
            for linha in linhas
            if (linha.get("id_seller") or "").strip() == id_seller
        }

        registros: list[PerformanceSKU] = []
        for linha in linhas:
            seller_da_linha = (linha.get("id_seller") or "").strip()
            if seller_da_linha != id_seller:
                chave = (linha.get("data"), linha.get("sku_filho"))
                if chave in chaves_do_seller:
                    self._registrar_inconsistencia(
                        f"Registro '{chave[1]}' em {chave[0]} de '{seller_da_linha}' "
                        f"duplica SKU filho já pertencente a '{id_seller}'."
                    )
                continue

            campos = converter_registro(linha, "fixture")
            try:
                data_registro = _parse_data(campos.get("data"))
            except ValueError:
                self._registrar_inconsistencia(
                    f"Data inválida '{campos.get('data')}' para seller '{id_seller}'."
                )
                continue
            if data_registro is None or not (data_inicio <= data_registro <= data_fim):
                continue

            campos["data"] = data_registro
            campos["id_seller"] = id_seller
            if campos.get("sku_filho"):
                campos["granularidade"] = "sku_filho"
            else:
                campos["granularidade"] = "sku_pai"
            registros.append(PerformanceSKU(**campos))

        return DadosSeller(seller=self.ler_seller(id_seller), registros=tuple(registros))

    def ler_seller(self, id_seller: str) -> SellerMaster | None:
        for linha in self._master():
            if (linha.get("id_seller") or "").strip() == id_seller:
                return SellerMaster(**_campos_master(linha))
        return None

    def _registrar_inconsistencia(self, mensagem: str) -> None:
        self.inconsistencias.append(mensagem)
        logger.warning("Contaminação multi-tenant descartada: %s", mensagem)


def _parse_data(valor: Any) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, date):
        return valor
    texto = str(valor).strip()
    if not texto:
        return None
    return date.fromisoformat(texto)


def _campos_master(linha: Mapping[str, str]) -> dict[str, Any]:
    from kam_agent.adapters.schema_mapping import normalizar_numero, normalizar_texto

    campos: dict[str, Any] = {}
    for nome in _CAMPOS_MASTER:
        valor = linha.get(nome)
        if nome in {"nota_reputacao", "rentabilidade", "taxa_conversao", "percentual_de_comissao"}:
            campos[nome] = normalizar_numero(valor)
        else:
            campos[nome] = normalizar_texto(valor)
    return campos
