"""Servico de status da API."""
from resources.platform.prover.prove.service import ProveService


class StatusService:
    """Servico para verificar o status da API."""

    @staticmethod
    def get_status():
        """Retorna o status atual da API e se os modelos estao carregados."""
        return {
            'status': 'online',
            'models_loaded': ProveService.are_models_loaded(),
            'version': '1.0.0'
        }
