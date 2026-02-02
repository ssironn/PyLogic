from apiflask import Schema
from apiflask.fields import String, Boolean


class StatusResponseSchema(Schema):
    """Schema para status da API."""
    status = String(metadata={'description': 'Status da API'})
    models_loaded = Boolean(metadata={'description': 'Se os modelos estao carregados'})
    version = String(metadata={'description': 'Versao da API'})
