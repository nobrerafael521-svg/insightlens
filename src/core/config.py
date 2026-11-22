from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import os
import yaml


# Pasta base do projeto (raiz) → .../insightlens
ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT_DIR / "config"


# ----------------- Helpers internos -----------------


def _load_yaml(filename: str) -> Dict[str, Any]:
    """
    Lê um ficheiro YAML da pasta config/ e devolve um dict.
    Se o ficheiro não existir, devolve {} para não partir a app.
    """
    path = CONFIG_DIR / filename
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ----------------- AppConfig simples -----------------


class AppConfig:
    """
    Wrapper muito simples para a config de app (app.yaml),
    só para facilitar acessos como app_cfg.paths.
    """

    def __init__(self, raw: Dict[str, Any]) -> None:
        self.raw = raw or {}
        # seção "app" (nome, idioma, etc.)
        self.app: Dict[str, Any] = self.raw.get("app", {})
        # seção "paths" (logs_dir, data_dir, etc.)
        self.paths: Dict[str, Any] = self.raw.get("paths", {})

    def get(self, key: str, default: Any = None) -> Any:
        return self.raw.get(key, default)


# caches simples em memória
__APP_CONFIG_CACHE: AppConfig | None = None
__NLP_CONFIG_CACHE: Dict[str, Any] | None = None
__FEATURES_CONFIG_CACHE: Dict[str, Any] | None = None
__DASHBOARD_CONFIG_CACHE: Dict[str, Any] | None = None


# ----------------- Funções públicas usadas no projeto -----------------


def load_app_config() -> AppConfig:
    """
    Carrega config/app.yaml e devolve um AppConfig.
    Usado, por exemplo, pelo logger e pelo dashboard.
    """
    global __APP_CONFIG_CACHE
    if __APP_CONFIG_CACHE is None:
        raw = _load_yaml("app.yaml")
        __APP_CONFIG_CACHE = AppConfig(raw)
    return __APP_CONFIG_CACHE


def get_app_config() -> AppConfig:
    """
    Alias para compatibilidade com código antigo.
    Alguns módulos ainda chamam get_app_config().
    """
    return load_app_config()


def get_nlp_config() -> Dict[str, Any]:
    """
    Carrega config/nlp.yaml (modelos, thresholds, etc.).
    Usado em src/nlp/preprocess.py, sentiment, topics, etc.
    """
    global __NLP_CONFIG_CACHE
    if __NLP_CONFIG_CACHE is None:
        __NLP_CONFIG_CACHE = _load_yaml("nlp.yaml")
    return __NLP_CONFIG_CACHE


def get_features_config() -> Dict[str, Any]:
    """
    Carrega config/features.yaml (flags para tópicos, keywords, sumarização...).
    """
    global __FEATURES_CONFIG_CACHE
    if __FEATURES_CONFIG_CACHE is None:
        __FEATURES_CONFIG_CACHE = _load_yaml("features.yaml")
    return __FEATURES_CONFIG_CACHE


def get_dashboard_config() -> Dict[str, Any]:
    """
    Carrega config/dashboard.yaml (páginas, limites, etc.).
    """
    global __DASHBOARD_CONFIG_CACHE
    if __DASHBOARD_CONFIG_CACHE is None:
        __DASHBOARD_CONFIG_CACHE = _load_yaml("dashboard.yaml")
    return __DASHBOARD_CONFIG_CACHE
