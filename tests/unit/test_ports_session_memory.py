"""Contrato de ``SessionMemoryPort`` (task 4.2)."""

from __future__ import annotations

from kam_agent.ports.session_memory import SessionMemoryPort


class _StubConforme:
    def ler(self, chave_sessao: str):
        return None

    def gravar(self, chave_sessao: str, estado: dict) -> None:
        return None

    def apagar(self, chave_sessao: str) -> None:
        return None


class _StubIncompleto:
    def ler(self, chave_sessao: str):
        return None


def test_stub_conforme_satisfaz_protocolo() -> None:
    assert isinstance(_StubConforme(), SessionMemoryPort)


def test_stub_incompleto_nao_satisfaz() -> None:
    assert not isinstance(_StubIncompleto(), SessionMemoryPort)


def test_protocolo_cobre_tres_metodos() -> None:
    for metodo in ("ler", "gravar", "apagar"):
        assert hasattr(SessionMemoryPort, metodo)
