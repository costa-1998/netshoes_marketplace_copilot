"""Configuração tipada da aplicação, espelhando ``.env.example``."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BackendDados = Literal["mock", "bigquery"]
BackendMemoria = Literal["memory"]


class Settings(BaseSettings):
    """Configuração resolvida de variáveis de ambiente.

    Backends são validados de forma fechada: um valor fora do conjunto aceito
    derruba a inicialização com mensagem que lista as opções válidas.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    llm_provider: str = "vertexai"
    google_genai_use_vertexai: int = 1
    google_cloud_project: str = "pdia0024"
    gcp_location: str = "us-central1"
    llm_model_orchestrator: str = "gemini-2.5-pro"
    llm_model_specialists: str = "gemini-2.5-flash"

    dw_backend: BackendDados = "bigquery"
    bq_project_id: str = "pdia0024"
    bq_dataset: str = "netshoes_kam_analytics"
    bq_view_child_sku: str = "vw_seller_performance_child_sku"
    bq_location: str = "US"

    memory_backend: BackendMemoria = "memory"
    session_ttl_seconds: int = Field(default=86400, gt=0)

    mock_data_path: Path = Path("tests/fixtures/seller_sku_sales.csv")
    mock_seller_master_path: Path = Path("tests/fixtures/seller_master.csv")


def carregar_settings() -> Settings:
    """Constrói ``Settings`` a partir do ambiente, falhando alto se inválido."""
    return Settings()
