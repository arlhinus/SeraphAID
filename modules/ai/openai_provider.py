"""
modules/ai/openai_provider.py — Provider de IA usando OpenAI (GPT-4o, etc.).

Requiere: OPENAI_API_KEY en variables de entorno.
Modelo configurable vía OPENAI_MODEL (default: gpt-4o).
"""
import os
import logging
from typing import Optional
from .base import AIProvider, AIProviderError

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """Provider que usa la API de OpenAI para interpretar resultados clínicos."""

    DEFAULT_MODEL = "gpt-4o"

    def __init__(self):
        self._api_key = os.getenv("OPENAI_API_KEY")
        self._model = os.getenv("OPENAI_MODEL", self.DEFAULT_MODEL)

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def is_available(self) -> bool:
        return bool(self._api_key)

    def interpret(self, context: str, prompt_template: Optional[str] = None) -> str:
        if not self.is_available:
            raise AIProviderError("OPENAI_API_KEY no configurada.")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self._api_key)

            system_prompt = prompt_template or self._default_system_prompt()
            full_prompt = system_prompt.replace("{context}", context)

            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": context},
                ],
                max_tokens=600,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAIProvider error: {e}")
            raise AIProviderError(f"Error al consultar OpenAI: {e}") from e

    def _default_system_prompt(self) -> str:
        """Carga el prompt desde archivo, con fallback inline."""
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
                "Usa lenguaje orientativo y siempre recomienda consultar al médico.\n\nContexto:\n{context}"
            )
