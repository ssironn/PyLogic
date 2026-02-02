from apiflask import Schema
from apiflask.fields import String, Integer, Boolean, List, Nested, Raw
from apiflask.validators import OneOf


class ProveRequestSchema(Schema):
    """Schema para requisicao de prova de equivalencia."""
    proposition1 = String(
        required=True,
        metadata={
            'description': 'Primeira proposicao logica (ex: "p ^ q", "~(p v q)")',
            'example': 'p ^ q'
        }
    )
    proposition2 = String(
        required=True,
        metadata={
            'description': 'Segunda proposicao logica',
            'example': 'q ^ p'
        }
    )
    method = String(
        load_default='automatic',
        validate=OneOf(['automatic', 'direct', 'contrapositive', 'absurd', 'bidirectional']),
        metadata={
            'description': 'Metodo de demonstracao a ser utilizado',
            'example': 'automatic'
        }
    )
    max_iterations = Integer(
        load_default=50,
        validate=OneOf([50, 100, 150, 300, 500]),
        metadata={
            'description': 'Quantidade maxima de iteracoes para a prova (valores: 50, 100, 150, 300, 500)',
            'example': 50
        }
    )
    allow_bidirectional = Boolean(
        load_default=False,
        metadata={
            'description': 'Permitir prova bidirecional (P1 -> P2 e P2 -> P1)',
            'example': False
        }
    )
    verbose = Boolean(
        load_default=False,
        metadata={
            'description': 'Retornar informacoes detalhadas sobre os passos',
            'example': False
        }
    )


class TransformationSchema(Schema):
    """Schema para um passo de transformacao."""
    iteration = Integer(metadata={'description': 'Numero da iteracao'})
    proposition = Integer(metadata={'description': 'Qual proposicao foi transformada (1 ou 2)'})
    law = String(metadata={'description': 'Lei logica aplicada'})
    result = String(metadata={'description': 'Resultado da transformacao'})
    guided_by_nn = Boolean(metadata={'description': 'Se a transformacao foi guiada pela NN'})
    subexpression = String(metadata={'description': 'Subexpressao onde a lei foi aplicada'})
    p1 = String(metadata={'description': 'Estado da proposicao 1 apos este passo'})
    p2 = String(metadata={'description': 'Estado da proposicao 2 apos este passo'})


class TruthTableRowSchema(Schema):
    """Schema para uma linha da tabela verdade."""
    values = Raw(metadata={'description': 'Valores das variaveis (dicionario)'})
    subvalues_p1 = Raw(metadata={'description': 'Valores das subexpressoes de P1'})
    subvalues_p2 = Raw(metadata={'description': 'Valores das subexpressoes de P2'})
    p1 = Boolean(metadata={'description': 'Valor de P1 para esta combinacao'})
    p2 = Boolean(metadata={'description': 'Valor de P2 para esta combinacao'})


class TruthTableSchema(Schema):
    """Schema para a tabela verdade."""
    variables = List(String(), metadata={'description': 'Lista de variaveis'})
    subexpressions_p1 = List(String(), metadata={'description': 'Subexpressoes de P1'})
    subexpressions_p2 = List(String(), metadata={'description': 'Subexpressoes de P2'})
    rows = List(Nested(TruthTableRowSchema), metadata={'description': 'Linhas da tabela'})


class ProveResponseSchema(Schema):
    """Schema para resposta da prova."""
    success = Boolean(metadata={'description': 'Se a prova foi bem-sucedida'})
    equivalent = Boolean(metadata={'description': 'Se as proposicoes sao equivalentes'})
    method_used = String(metadata={'description': 'Metodo de prova utilizado'})
    iterations = Integer(metadata={'description': 'Numero de iteracoes realizadas'})
    nn_predictions = Integer(metadata={'description': 'Numero de predicoes NN utilizadas'})
    proposition1_initial = String(metadata={'description': 'Estado inicial da proposicao 1'})
    proposition2_initial = String(metadata={'description': 'Estado inicial da proposicao 2'})
    proposition1_final = String(metadata={'description': 'Estado final da proposicao 1'})
    proposition2_final = String(metadata={'description': 'Estado final da proposicao 2'})
    transformations = List(Nested(TransformationSchema), metadata={'description': 'Lista de transformacoes aplicadas'})
    truth_table = Nested(TruthTableSchema, metadata={'description': 'Tabela verdade das proposicoes'})
    message = String(metadata={'description': 'Mensagem explicativa do resultado'})
