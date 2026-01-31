#!/usr/bin/env python3
"""
PyLogic API - API REST para demonstração de equivalências lógicas.

Este módulo fornece uma API REST usando APIFlask para verificar
equivalência entre proposições lógicas usando redes neurais.
"""

from apiflask import APIFlask, Schema, abort
from apiflask.fields import String, Integer, Boolean, List, Nested
from apiflask.validators import OneOf, Range

from proposition import (
    Proposition, CompoundProposition,
    parse_proposition, ParseError, TRUE, FALSE
)
from equivalence import Equivalence
from nn import TransformationPredictor, generate_dataset
from nn.model import SimplificationPredictor
from nn.dataset import generate_simplification_dataset


# ============================================================
# Schemas para validação de entrada/saída
# ============================================================

class ProvaRequestSchema(Schema):
    """Schema para requisição de prova de equivalência."""
    proposicao1 = String(
        required=True,
        metadata={
            'description': 'Primeira proposição lógica (ex: "p ^ q", "~(p v q)")',
            'example': 'p ^ q'
        }
    )
    proposicao2 = String(
        required=True,
        metadata={
            'description': 'Segunda proposição lógica',
            'example': 'q ^ p'
        }
    )
    metodo = String(
        load_default='automatico',
        validate=OneOf(['automatico', 'direto', 'contrapositiva', 'absurdo', 'bidirecional']),
        metadata={
            'description': 'Método de demonstração a ser utilizado',
            'example': 'automatico'
        }
    )
    max_iteracoes = Integer(
        load_default=50,
        validate=Range(min=1, max=500),
        metadata={
            'description': 'Quantidade máxima de iterações para a prova',
            'example': 50
        }
    )
    permitir_bidirecional = Boolean(
        load_default=False,
        metadata={
            'description': 'Permitir prova bidirecional (P1 → P2 e P2 → P1)',
            'example': False
        }
    )
    verbose = Boolean(
        load_default=False,
        metadata={
            'description': 'Retornar informações detalhadas sobre os passos',
            'example': False
        }
    )


class TransformacaoSchema(Schema):
    """Schema para um passo de transformação."""
    iteracao = Integer(metadata={'description': 'Número da iteração'})
    proposicao = Integer(metadata={'description': 'Qual proposição foi transformada (1 ou 2)'})
    lei = String(metadata={'description': 'Lei lógica aplicada'})
    resultado = String(metadata={'description': 'Resultado da transformação'})
    guiado_por_nn = Boolean(metadata={'description': 'Se a transformação foi guiada pela NN'})


class ProvaResponseSchema(Schema):
    """Schema para resposta da prova."""
    sucesso = Boolean(metadata={'description': 'Se a prova foi bem-sucedida'})
    equivalentes = Boolean(metadata={'description': 'Se as proposições são equivalentes'})
    metodo_utilizado = String(metadata={'description': 'Método de prova utilizado'})
    iteracoes = Integer(metadata={'description': 'Número de iterações realizadas'})
    predicoes_nn = Integer(metadata={'description': 'Número de predições NN utilizadas'})
    proposicao1_final = String(metadata={'description': 'Estado final da proposição 1'})
    proposicao2_final = String(metadata={'description': 'Estado final da proposição 2'})
    transformacoes = List(Nested(TransformacaoSchema), metadata={'description': 'Lista de transformações aplicadas'})
    mensagem = String(metadata={'description': 'Mensagem explicativa do resultado'})


class ErroSchema(Schema):
    """Schema para resposta de erro."""
    erro = String(metadata={'description': 'Tipo do erro'})
    mensagem = String(metadata={'description': 'Descrição do erro'})
    detalhe = String(metadata={'description': 'Detalhes adicionais'})


class StatusSchema(Schema):
    """Schema para status da API."""
    status = String(metadata={'description': 'Status da API'})
    modelos_carregados = Boolean(metadata={'description': 'Se os modelos estão carregados'})
    versao = String(metadata={'description': 'Versão da API'})


# ============================================================
# Aplicação Flask
# ============================================================

app = APIFlask(
    __name__,
    title='PyLogic API',
    version='1.0.0',
    spec_path='/openapi.json',
    docs_ui='swagger-ui',
    docs_path='/docs'
)

app.config['SPEC_FORMAT'] = 'json'
app.config['AUTO_VALIDATION'] = True

# Variáveis globais para os modelos (carregados uma única vez)
_modelo_convergencia = None
_modelo_simplificacao = None
_equivalence = None


def _carregar_modelos():
    """Carrega os modelos de rede neural se ainda não estiverem carregados."""
    global _modelo_convergencia, _modelo_simplificacao, _equivalence

    if _modelo_convergencia is None:
        print("Carregando modelos de rede neural...")

        # Treina modelo de convergência
        X, y = generate_dataset(num_samples=2000, verbose=False)
        _modelo_convergencia = TransformationPredictor(hidden_layers=(32, 16), max_iter=2000)
        _modelo_convergencia.train(X, y, verbose=False, balance=True)

        # Treina modelo de simplificação
        X_simp, y_simp = generate_simplification_dataset(num_samples=1500, verbose=False)
        _modelo_simplificacao = SimplificationPredictor(hidden_layers=(32, 16), max_iter=2000)
        _modelo_simplificacao.train(X_simp, y_simp, verbose=False, balance=True)

        _equivalence = Equivalence()

        print("Modelos carregados com sucesso!")

    return _modelo_convergencia, _modelo_simplificacao, _equivalence


def _verificar_equivalencia_semantica(prop1, props1, prop2, props2):
    """Verifica se duas proposições são semanticamente equivalentes."""
    # Obtém todos os nomes de proposições únicas
    all_names = set(props1.keys()) | set(props2.keys())
    all_names.discard('T')
    all_names.discard('F')
    n = len(all_names)
    names = sorted(all_names)

    if n == 0:
        return _avaliar_prop(prop1) == _avaliar_prop(prop2)

    # Verifica todas as 2^n combinações
    for i in range(2 ** n):
        for j, name in enumerate(names):
            value = bool((i >> j) & 1)
            if name in props1:
                props1[name].value = value
            if name in props2:
                props2[name].value = value

        val1 = _avaliar_prop(prop1)
        val2 = _avaliar_prop(prop2)

        if val1 != val2:
            return False

    return True


def _avaliar_prop(prop):
    """Avalia uma proposição."""
    if hasattr(prop, 'is_constant') and prop.is_constant():
        return prop.is_true()
    if isinstance(prop, Proposition):
        return prop.value
    elif isinstance(prop, CompoundProposition):
        return prop.calculate_value()
    return prop.value


def _formatar_transformacoes(transformacoes):
    """Formata a lista de transformações para a resposta da API."""
    resultado = []
    for t in transformacoes:
        resultado.append({
            'iteracao': t.get('iteration', 0),
            'proposicao': t.get('proposition', 1),
            'lei': t.get('law', ''),
            'resultado': t.get('result', ''),
            'guiado_por_nn': t.get('used_nn', False)
        })
    return resultado


# ============================================================
# Endpoints
# ============================================================

@app.get('/status')
@app.output(StatusSchema)
@app.doc(tags=['System'], summary='Check API status')
def status():
    """Retorna o status atual da API e se os modelos estão carregados."""
    return {
        'status': 'online',
        'modelos_carregados': _modelo_convergencia is not None,
        'versao': '1.0.0'
    }


@app.post('/prove')
@app.input(ProvaRequestSchema)
@app.output(ProvaResponseSchema)
@app.doc(tags=['Equivalence'], summary='Prove equivalence between two propositions')
def provar_equivalencia(json_data):
    """
    Verifies and proves the equivalence between two logical propositions.

    Available methods:
    - **automatico**: Tries multiple strategies automatically
    - **direto**: Direct transformation proof
    - **contrapositiva**: Proves that ~P1 ≡ ~P2
    - **absurdo**: Proves that (P1 ∧ ~P2) = F
    - **bidirecional**: Proves that (P1 → P2) = T and (P2 → P1) = T
    """
    # Carrega modelos se necessário
    modelo, modelo_simp, eq = _carregar_modelos()

    # Obtém parâmetros
    prop1_str = json_data['proposicao1']
    prop2_str = json_data['proposicao2']
    metodo = json_data['metodo']
    max_iteracoes = json_data['max_iteracoes']
    permitir_bidirecional = json_data['permitir_bidirecional']

    # Faz parse das proposições
    try:
        prop1, props1 = parse_proposition(prop1_str)
    except ParseError as e:
        abort(400, message=f"Erro ao analisar proposição 1: {str(e)}")

    try:
        prop2, props2 = parse_proposition(prop2_str)
    except ParseError as e:
        abort(400, message=f"Erro ao analisar proposição 2: {str(e)}")

    # Verifica equivalência semântica
    semanticamente_equivalentes = _verificar_equivalencia_semantica(prop1, props1, prop2, props2)

    if not semanticamente_equivalentes:
        return {
            'sucesso': True,
            'equivalentes': False,
            'metodo_utilizado': 'verificacao_semantica',
            'iteracoes': 0,
            'predicoes_nn': 0,
            'proposicao1_final': str(prop1),
            'proposicao2_final': str(prop2),
            'transformacoes': [],
            'mensagem': 'As proposições NÃO são equivalentes (tabelas verdade diferentes)'
        }

    # Verifica se já são sintaticamente iguais
    if eq.are_equal(prop1, prop2):
        return {
            'sucesso': True,
            'equivalentes': True,
            'metodo_utilizado': 'igualdade_sintatica',
            'iteracoes': 0,
            'predicoes_nn': 0,
            'proposicao1_final': str(prop1),
            'proposicao2_final': str(prop2),
            'transformacoes': [],
            'mensagem': 'As proposições já são sintaticamente iguais'
        }

    # Converte para CompoundProposition se necessário
    if isinstance(prop1, Proposition):
        prop1 = eq._ensure_compound(prop1)
    if isinstance(prop2, Proposition):
        prop2 = eq._ensure_compound(prop2)

    resultado = None
    metodo_utilizado = metodo

    # Executa a prova conforme o método escolhido
    if metodo == 'automatico':
        # Tenta múltiplas estratégias
        resultado = eq.prove_with_fallback(
            prop1, prop2, modelo,
            simplification_predictor=modelo_simp,
            max_iterations=max_iteracoes,
            verbose=False
        )
        metodo_utilizado = resultado.get('method', 'automatico')

    elif metodo == 'direto':
        resultado = eq.prove_equivalence_nn(
            prop1, prop2, modelo,
            max_iterations=max_iteracoes,
            verbose=False
        )

    elif metodo == 'contrapositiva':
        resultado = eq.prove_by_contrapositive(
            prop1, prop2, modelo,
            max_iterations=max_iteracoes,
            verbose=False
        )

    elif metodo == 'absurdo':
        resultado = eq.prove_by_absurdity(
            prop1, prop2, modelo,
            simplification_predictor=modelo_simp,
            max_iterations=max_iteracoes,
            verbose=False
        )

    elif metodo == 'bidirecional':
        resultado = eq.prove_bidirectional(
            prop1, prop2, modelo,
            max_iterations=max_iteracoes,
            verbose=False
        )

    # Monta resposta
    sucesso = resultado.get('success', False)
    transformacoes = resultado.get('transformations', [])

    if sucesso:
        mensagem = f'Equivalência provada com sucesso usando método {metodo_utilizado}'
    else:
        mensagem = f'Não foi possível provar equivalência sintaticamente (semanticamente são equivalentes)'

    return {
        'sucesso': sucesso,
        'equivalentes': True,  # Já verificamos que são semanticamente equivalentes
        'metodo_utilizado': metodo_utilizado,
        'iteracoes': resultado.get('iterations', 0),
        'predicoes_nn': resultado.get('nn_predictions_used', 0),
        'proposicao1_final': str(resultado.get('prop1_final', prop1)),
        'proposicao2_final': str(resultado.get('prop2_final', prop2)),
        'transformacoes': _formatar_transformacoes(transformacoes),
        'mensagem': mensagem
    }


@app.get('/syntax')
@app.doc(tags=['Help'], summary='Show supported syntax')
def sintaxe():
    """Retorna informações sobre a sintaxe suportada para proposições."""
    return {
        'operadores': {
            'negacao': ['~p', '!p', 'NOT p'],
            'conjuncao': ['p ^ q', 'p & q', 'p AND q'],
            'disjuncao': ['p v q', 'p | q', 'p OR q'],
            'implicacao': ['p -> q', 'p => q', 'p IMPLIES q']
        },
        'constantes': {
            'verdadeiro': 'T',
            'falso': 'F'
        },
        'agrupamento': '(p ^ q)',
        'exemplos': [
            'p ^ q',
            '~(p v q)',
            '(p ^ q) v r',
            '~~p',
            'p -> q',
            '(p -> q) ^ (q -> r)'
        ]
    }


@app.get('/methods')
@app.doc(tags=['Help'], summary='List available proof methods')
def metodos():
    """Retorna informações sobre os métodos de prova disponíveis."""
    return {
        'metodos': {
            'automatico': {
                'descricao': 'Tenta múltiplas estratégias automaticamente',
                'estrategias': ['direto', 'contrapositiva', 'absurdo']
            },
            'direto': {
                'descricao': 'Prova por transformação direta',
                'objetivo': 'Transformar P1 até que seja igual a P2'
            },
            'contrapositiva': {
                'descricao': 'Prova através da contrapositiva',
                'objetivo': 'Provar que ~P1 ≡ ~P2'
            },
            'absurdo': {
                'descricao': 'Prova por redução ao absurdo',
                'objetivo': 'Provar que (P1 ∧ ~P2) = F'
            },
            'bidirecional': {
                'descricao': 'Prova através de dupla implicação',
                'objetivo': 'Provar que (P1 → P2) = T e (P2 → P1) = T'
            }
        }
    }


# ============================================================
# Ponto de entrada
# ============================================================

if __name__ == '__main__':
    # Pré-carrega os modelos ao iniciar
    print("Iniciando PyLogic API...")
    _carregar_modelos()

    # Inicia o servidor
    app.run(host='0.0.0.0', port=5000, debug=True)
