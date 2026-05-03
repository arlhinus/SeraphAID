"""
modules/ai/registry.py — Registro central de providers de IA.

Carga el provider activo desde la variable de entorno AI_PROVIDER.
Valores válidos: "openai" | "anthropic" | "rules" (default).

Ejemplo en .env:
    AI_PROVIDER=openai
    OPENAI_API_KEY=sk-...

Si el provider configurado no está disponible (ej: falta API key),
cae automáticamente al provider de reglas (RulesProvider).
"""
import os
import logging
from .base import AIProvider
from .rules_provider import RulesProvider

logger = logging.getLogger(__name__)

_PROVIDER_MAP = {
    "openai": "modules.ai.openai_provider.OpenAIProvider",
    "anthropic": "modules.ai.anthropic_provider.AnthropicProvider",
    "rules": "modules.ai.rules_provider.RulesProvider",
}


def get_provider(provider_name: str = None) -> AIProvider:
    """
    Retorna el provider de IA activo.

    Args:
        provider_name: Nombre del provider. Si None, lee AI_PROVIDER del entorno.

    Returns:
        Instancia de AIProvider lista para usar.
        Si el provider configurado no está disponible, retorna RulesProvider.
    """
    name = (provider_name or os.getenv("AI_PROVIDER", "rules")).lower().strip()

    if name not in _PROVIDER_MAP:
        logger.warning(f"Provider '{name}' desconocido. Usando 'rules'.")
        return RulesProvider()

    try:
        module_path, class_name = _PROVIDER_MAP[name].rsplit(".", 1)
        import importlib
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        instance = cls()

        if not instance.is_available:
            logger.warning(
                f"Provider '{name}' no disponible (falta configuración). Usando 'rules'."
            )
            return RulesProvider()

        logger.info(f"Provider de IA activo: {name}")
        return instance

    except Exception as e:
        logger.error(f"Error al cargar provider '{name}': {e}. Usando 'rules'.")
        return RulesProvider()


def list_available_providers() -> list[str]:
    """Retorna los nombres de providers que tienen su configuración disponible."""
    available = ["rules"]  # siempre disponible
    for name, path in _PROVIDER_MAP.items():
        if name == "rules":
            continue
        try:
            module_path, class_name = path.rsplit(".", 1)
            import importlib
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            if cls().is_available:
                available.append(name)
        except Exception:
            pass
    return available
