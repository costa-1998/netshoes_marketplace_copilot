"""Porta de memória de sessão conversacional."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SessionMemoryPort(Protocol):
    """Contrato de estado de sessão com expiração.

    Uma leitura de sessão inexistente ou expirada devolve ``None`` — ausência
    explícita, distinguível de um estado vazio armazenado.
    """

    def ler(self, chave_sessao: str) -> dict[str, Any] | None: ...

    def gravar(self, chave_sessao: str, estado: dict[str, Any]) -> None: ...

    def apagar(self, chave_sessao: str) -> None: ...
