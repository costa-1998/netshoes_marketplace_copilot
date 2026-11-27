"""Adapter de memória de sessão em processo, com TTL desde a última escrita."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

Estado = dict[str, Any]


class InMemorySessionAdapter:
    """Implementação de ``SessionMemoryPort`` com relógio injetável."""

    def __init__(
        self,
        ttl_segundos: int = 86400,
        relogio: Callable[[], float] = time.monotonic,
    ) -> None:
        self._ttl = ttl_segundos
        self._relogio = relogio
        self._estados: dict[str, tuple[float, Estado]] = {}

    def ler(self, chave_sessao: str) -> Estado | None:
        entrada = self._estados.get(chave_sessao)
        if entrada is None:
            return None
        gravado_em, estado = entrada
        if self._relogio() - gravado_em >= self._ttl:
            self._estados.pop(chave_sessao, None)
            return None
        return dict(estado)

    def gravar(self, chave_sessao: str, estado: Estado) -> None:
        self._estados[chave_sessao] = (self._relogio(), dict(estado))

    def apagar(self, chave_sessao: str) -> None:
        self._estados.pop(chave_sessao, None)
