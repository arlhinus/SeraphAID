"""
modules/ai/base.py — Interfaz base para providers de IA en SeraphAID.

Cualquier proveedor (OpenAI, Anthropic, local, RAG, etc.) debe implementar esta interfaz.
Esto garantiza que el sistema no quede amarrado a ningún proveedor específico.
"""
from abc import ABC, abstractmethod
from typing import Optional


class AIProvider(ABC):
    """
    Interfaz abstracta para proveedores de interpretación IA.

    Un provider recibe un contexto clínico estructurado y retorna
    una interpretación en lenguaje simple para el paciente.
    """

    @abstractmethod
    def interpret(self, context: str, prompt_template: Optional[str] = None) -> str:
        """
        Interpreta un contexto clínico y retorna una explicación para el paciente.

        Args:
            context: Texto estructurado con valores, rangos y estados de los analitos.
            prompt_template: Plantilla de prompt opcional. Si None, usa el default del provider.

        Returns:
            Texto de interpretación en lenguaje simple. Nunca debe emitir diagnósticos.

        Raises:
            AIProviderError: Si la llamada falla y no hay fallback disponible.
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nombre legible del proveedor, ej: 'openai', 'anthropic', 'rules'."""
        ...

    @property
    def is_available(self) -> bool:
        """
        True si el provider puede operar (ej: tiene API key configurada).
        Los providers que no requieren API key siempre retornan True.
        """
        return True


class AIProviderError(Exception):
    """Error al invocar un provider de IA."""
    pass
