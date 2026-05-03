"""
modules/ai/rules_provider.py — Provider basado en reglas locales (sin API externa).

Este provider siempre está disponible. Es el fallback del sistema.
No requiere ninguna API key ni conexión a internet.
"""
from .base import AIProvider


class RulesProvider(AIProvider):
    """
    Provider que genera interpretaciones usando solo las reglas locales del sistema.
    Actúa como fallback cuando no hay API key configurada o cuando otros providers fallan.
    El output es equivalente al 'construir_resumen_detallado' existente en app.py.
    """

    @property
    def provider_name(self) -> str:
        return "rules"

    @property
    def is_available(self) -> bool:
        return True  # siempre disponible

    def interpret(self, context: str, prompt_template=None) -> str:
        """
        En el provider de reglas, el contexto ya viene procesado por el sistema de clasificación.
        Este método simplemente retorna el contexto formateado para mostrar al usuario.
        El procesamiento real ocurre en exam_interpreter.py.
        """
        # El provider de reglas delega a la lógica existente de clasificación.
        # Este método existe para mantener la interfaz uniforme.
        return context
