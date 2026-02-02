"""Controller para endpoints do prover."""
from http import HTTPStatus

from apiflask import APIBlueprint

from resources.platform.prover.prove.service import ProveService
from resources.platform.prover.prove.schemas import ProveRequestSchema, ProveResponseSchema
from resources.platform.prover.status.service import StatusService
from resources.platform.prover.status.schemas import StatusResponseSchema
from resources.platform.prover.syntax.service import SyntaxService
from resources.platform.prover.methods.service import MethodsService
from utils.response import ApiResponse


prover_bp = APIBlueprint('prover', __name__, url_prefix='')


@prover_bp.get('/status')
@prover_bp.output(StatusResponseSchema)
@prover_bp.doc(tags=['System'], summary='Check API status')
def status():
    """Retorna o status atual da API e se os modelos estao carregados."""
    return StatusService.get_status()


@prover_bp.post('/prove')
@prover_bp.input(ProveRequestSchema)
@prover_bp.output(ProveResponseSchema)
@prover_bp.doc(tags=['Equivalence'], summary='Prove equivalence between two propositions')
def prove(json_data):
    """
    Verifica e prova a equivalencia entre duas proposicoes logicas.

    Metodos disponiveis:
    - **automatic**: Tenta multiplas estrategias automaticamente
    - **direct**: Prova por transformacao direta
    - **contrapositive**: Prova que ~P1 ≡ ~P2
    - **absurd**: Prova que (P1 ∧ ~P2) = F
    - **bidirectional**: Prova que (P1 -> P2) = T e (P2 -> P1) = T
    """
    result = ProveService.prove(json_data)

    if result.is_failure:
        return ApiResponse.bad_request(
            message=result.message,
            errors=[result.error] if result.error else None
        ).to_tuple()

    # Return the prove data directly (matches ProveResponseSchema)
    return result.value


@prover_bp.get('/syntax')
@prover_bp.doc(tags=['Help'], summary='Show supported syntax')
def syntax():
    """Retorna informacoes sobre a sintaxe suportada para proposicoes."""
    return SyntaxService.get_syntax()


@prover_bp.get('/methods')
@prover_bp.doc(tags=['Help'], summary='List available proof methods')
def methods():
    """Retorna informacoes sobre os metodos de prova disponiveis."""
    return MethodsService.get_methods()
