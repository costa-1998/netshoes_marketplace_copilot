"""Isolamento de camada do domínio (task 2.4).

O pacote ``domain`` não pode depender de GCP, FastAPI, LangGraph ou
pydantic-settings. A checagem roda em subprocesso limpo para não herdar
imports do processo de teste.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"

PROIBIDOS = ("fastapi", "langgraph", "google.cloud", "pydantic_settings")

SCRIPT = f"""
import sys
sys.path.insert(0, {str(SRC)!r})

proibidos = {PROIBIDOS!r}

def proibidos_carregados():
    return {{
        m for m in sys.modules
        if any(m == p or m.startswith(p + ".") for p in proibidos)
    }}

# Namespaces ``google.cloud`` podem ser injetados por arquivos .pth do
# ambiente antes de qualquer import nosso; medimos só o que o domínio adiciona.
antes = proibidos_carregados()

import kam_agent.domain
import kam_agent.domain.enums
import kam_agent.domain.exceptions
import kam_agent.domain.guardrails
import kam_agent.domain.models
import kam_agent.domain.price_simulation

depois = proibidos_carregados()
print(",".join(sorted(depois - antes)))
"""


def test_domain_nao_importa_camadas_externas() -> None:
    resultado = subprocess.run(
        [sys.executable, "-I", "-c", SCRIPT],
        capture_output=True,
        text=True,
        check=True,
    )
    carregados = [m for m in resultado.stdout.strip().split(",") if m]
    assert carregados == [], f"domain importou camadas externas: {carregados}"
