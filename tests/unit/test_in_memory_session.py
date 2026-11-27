"""Memória de sessão em processo com TTL (task 6.2)."""

from __future__ import annotations

from kam_agent.adapters.in_memory_session import InMemorySessionAdapter


class _Relogio:
    def __init__(self) -> None:
        self.agora = 0.0

    def __call__(self) -> float:
        return self.agora

    def avancar(self, segundos: float) -> None:
        self.agora += segundos


def _adapter(ttl: int = 60) -> tuple[InMemorySessionAdapter, _Relogio]:
    relogio = _Relogio()
    return InMemorySessionAdapter(ttl_segundos=ttl, relogio=relogio), relogio


def test_leitura_da_propria_sessao() -> None:
    adapter, _ = _adapter()
    adapter.gravar("s1", {"passo": 1})
    assert adapter.ler("s1") == {"passo": 1}


def test_sessao_inexistente_devolve_none() -> None:
    adapter, _ = _adapter()
    assert adapter.ler("nunca") is None


def test_leitura_cruzada_nao_vaza() -> None:
    adapter, _ = _adapter()
    adapter.gravar("s1", {"segredo": "x"})
    assert adapter.ler("s2") is None


def test_expira_apos_ttl() -> None:
    adapter, relogio = _adapter(ttl=60)
    adapter.gravar("s1", {"a": 1})
    relogio.avancar(60)
    assert adapter.ler("s1") is None


def test_escrita_renova_prazo() -> None:
    adapter, relogio = _adapter(ttl=60)
    adapter.gravar("s1", {"a": 1})
    relogio.avancar(50)
    adapter.gravar("s1", {"a": 2})
    relogio.avancar(50)
    assert adapter.ler("s1") == {"a": 2}


def test_apagar_remove() -> None:
    adapter, _ = _adapter()
    adapter.gravar("s1", {"a": 1})
    adapter.apagar("s1")
    assert adapter.ler("s1") is None


def test_apagar_inexistente_e_idempotente() -> None:
    adapter, _ = _adapter()
    adapter.gravar("s1", {"a": 1})
    adapter.apagar("nunca")
    assert adapter.ler("s1") == {"a": 1}


def test_estado_retornado_e_copia() -> None:
    adapter, _ = _adapter()
    adapter.gravar("s1", {"a": 1})
    lido = adapter.ler("s1")
    assert lido is not None
    lido["a"] = 99
    assert adapter.ler("s1") == {"a": 1}
