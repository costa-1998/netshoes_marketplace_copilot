"""Roteamento determinístico por intenção — sem chamada a LLM (D9)."""

from __future__ import annotations

from kam_agent.domain.enums import TipoGargalo

#: Intenções suportadas e as palavras-chave que as disparam.
INTENCOES: dict[str, tuple[str, ...]] = {
    "diagnostico": ("diagnostico", "diagnóstico", "gargalo", "problema", "vendas"),
    "preco": ("preco", "preço", "buybox", "buy box", "concorrente"),
    "estoque": ("estoque", "ruptura", "reposicao", "reposição", "cobertura"),
    "funil": ("funil", "checkout", "carrinho", "conversao", "conversão", "cancelamento"),
}

ESPECIALISTA_PADRAO = "padrao"


def rotear(mensagem: str) -> str:
    """Seleciona o especialista pela primeira intenção que casar.

    Determinístico: a mesma mensagem sempre devolve o mesmo especialista.
    Intenção não reconhecida cai no especialista padrão, não em erro.
    """
    texto = (mensagem or "").lower()
    for especialista, palavras in INTENCOES.items():
        if any(palavra in texto for palavra in palavras):
            return especialista
    return ESPECIALISTA_PADRAO


def gargalos_por_especialista(especialista: str) -> tuple[TipoGargalo, ...]:
    """Gargalos que o especialista investiga."""
    mapa = {
        "diagnostico": (
            TipoGargalo.RUPTURA_CURVA_A,
            TipoGargalo.LOGISTICA_PRAZO_FRETE,
            TipoGargalo.PRECO_ACIMA_CONCORRENTE,
            TipoGargalo.TRAVA_1P,
        ),
        "preco": (TipoGargalo.PRECO_ACIMA_CONCORRENTE, TipoGargalo.TRAVA_1P),
        "estoque": (TipoGargalo.RUPTURA_CURVA_A,),
        "funil": (TipoGargalo.ATRITO_CHECKOUT, TipoGargalo.CANCELAMENTO_ALTO),
    }
    return mapa.get(especialista, ())
