"""
modules/ai/anthropic_provider.py — Provider de IA usando Anthropic (Claude).

Requiere: ANTHROPIC_API_KEY en variables de entorno.
Modelo configurable vía ANTHROPIC_MODEL (default: claude-sonnet-4-6).
"""
import os
import logging
from typing import Optional
from .base import AIProvider, AIProviderError

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    """Provider que usa la API de Anthropic (Claude) para interpretar resultados clínicos."""

    DEFAULT_MODEL = "claude-sonnet-4-6"

    def __init__(self):
        self._api_key = os.getenv("ANTHROPIC_API_KEY")
        self._model = os.getenv("ANTHROPIC_MODEL", self.DEFAULT_MODEL)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def is_available(self) -> bool:
        return bool(self._api_key)

    def interpret(self, context: str, prompt_template: Optional[str] = None) -> str:
        if not self.is_available:
            raise AIProviderError("ANTHROPIC_API_KEY no configurada.")
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self._api_key)

            system_prompt = prompt_template or self._default_system_prompt()
            # El {context} ya está incluido en el mensaje del usuario
            system_clean = system_prompt.replace("{context}", "").strip()

            message = client.messages.create(
                model=self._model,
                max_tokens=600,
                system=system_clean,
                messages=[{"role": "user", "content": context}],
            )
            return message.content[0].text.strip()
        except Exception as e:
            logger.error(f"AnthropicProvider error: {e}")
            raise AIProviderError(f"Error al consultar Anthropic: {e}") from e

    def _default_system_prompt(self) -> str:
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "prompts", "interpret_prompt.txt"
        )
        try:
            with open(prompt_path, encoding="utf-8") as f:
                return f.read()
        except Exception:
            return (
                "Eres un profesional de la salud que interpreta resultados de laboratorio "
                "en español para pacientes. No emitas diagnósticos definitivos. "
                "Usa lenguaje orientativo y siempre recomienda consultar al médico."
            )
