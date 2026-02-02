"""Servico de prova de equivalencia logica."""
import re
from typing import Any

from utils.proposition import (
    Proposition, CompoundProposition,
    parse_proposition, ParseError
)
from utils.proposition import OperatorNode, AtomicNode
from utils.equivalence import Equivalence
from utils.nn import TransformationPredictor, generate_dataset
from utils.nn.model import SimplificationPredictor
from utils.nn.dataset import generate_simplification_dataset
from utils.response import Result


# Global model instances (loaded once)
_convergence_model = None
_simplification_model = None
_equivalence = None


def _load_models():
    """Carrega os modelos de rede neural se ainda nao estiverem carregados."""
    global _convergence_model, _simplification_model, _equivalence

    if _convergence_model is None:
        print("Carregando modelos de rede neural...")

        # Train convergence model
        X, y = generate_dataset(num_samples=2000, verbose=False)
        _convergence_model = TransformationPredictor(hidden_layers=(32, 16), max_iter=2000)
        _convergence_model.train(X, y, verbose=False, balance=True)

        # Train simplification model
        X_simp, y_simp = generate_simplification_dataset(num_samples=1500, verbose=False)
        _simplification_model = SimplificationPredictor(hidden_layers=(32, 16), max_iter=2000)
        _simplification_model.train(X_simp, y_simp, verbose=False, balance=True)

        _equivalence = Equivalence()

        print("Modelos carregados com sucesso!")

    return _convergence_model, _simplification_model, _equivalence


def _evaluate_proposition(prop):
    """Avalia uma proposicao."""
    if hasattr(prop, 'is_constant') and prop.is_constant():
        return prop.is_true()
    if isinstance(prop, Proposition):
        return prop.value
    elif isinstance(prop, CompoundProposition):
        return prop.calculate_value()
    return prop.value


def _verify_semantic_equivalence(prop1, props1, prop2, props2):
    """Verifica se duas proposicoes sao semanticamente equivalentes."""
    all_names = set(props1.keys()) | set(props2.keys())
    all_names.discard('T')
    all_names.discard('F')
    n = len(all_names)
    names = sorted(all_names)

    if n == 0:
        return _evaluate_proposition(prop1) == _evaluate_proposition(prop2)

    for i in range(2 ** n):
        for j, name in enumerate(names):
            value = bool((i >> j) & 1)
            if name in props1:
                props1[name].value = value
            if name in props2:
                props2[name].value = value

        val1 = _evaluate_proposition(prop1)
        val2 = _evaluate_proposition(prop2)

        if val1 != val2:
            return False

    return True


def _detect_negations(prop_str, variables):
    """Detecta quais variaveis aparecem negadas na proposicao."""
    negated = set()
    for var in variables:
        if re.search(rf'[~!¬]\s*{re.escape(var)}(?![a-zA-Z0-9])', prop_str):
            negated.add(var)
    return negated


def _extract_subexpressions(prop):
    """Extrai todas as subexpressoes de uma proposicao composta."""
    subexpressions = []
    visited = set()

    def _node_to_compound(node):
        if node is None:
            return None
        cp = CompoundProposition()
        cp.root = node
        cp.components = node.get_components() if hasattr(node, 'get_components') else set()
        return cp

    def _traverse(node, depth=0):
        if node is None:
            return

        if isinstance(node, AtomicNode):
            return

        if isinstance(node, OperatorNode):
            if node.left:
                _traverse(node.left, depth + 1)
            if node.right:
                _traverse(node.right, depth + 1)

            sub_prop = _node_to_compound(node)
            sub_str = str(sub_prop)

            if sub_str not in visited:
                op_count = (
                    sub_str.count('∧') + sub_str.count('^') +
                    sub_str.count('∨') + sub_str.count('v') +
                    sub_str.count('→') +
                    sub_str.count('¬')
                )
                if op_count >= 1 and node.right is not None:
                    visited.add(sub_str)
                    subexpressions.append((sub_prop, sub_str, depth))

    if isinstance(prop, CompoundProposition) and prop.root:
        _traverse(prop.root)

    subexpressions.sort(key=lambda x: -x[2])

    prop_str = str(prop)
    subexpressions = [(sp, ss, d) for sp, ss, d in subexpressions if ss != prop_str]

    return subexpressions


def _generate_truth_table(prop1, props1, prop2, props2):
    """Gera a tabela verdade para ambas as proposicoes."""
    all_names = set(props1.keys()) | set(props2.keys())
    all_names.discard('T')
    all_names.discard('F')
    names = sorted(all_names)
    n = len(names)

    if n == 0:
        val1 = _evaluate_proposition(prop1)
        val2 = _evaluate_proposition(prop2)
        return {
            'variables': [],
            'subexpressions_p1': [],
            'subexpressions_p2': [],
            'rows': [{
                'values': {},
                'subvalues_p1': {},
                'subvalues_p2': {},
                'p1': val1,
                'p2': val2
            }]
        }

    prop1_str = str(prop1)
    prop2_str = str(prop2)
    negated = _detect_negations(prop1_str, names) | _detect_negations(prop2_str, names)

    columns = []
    for name in names:
        columns.append(name)
        if name in negated:
            columns.append(f'~{name}')

    subexpr_p1 = _extract_subexpressions(prop1)
    subexpr_p2 = _extract_subexpressions(prop2)

    subexpr_p1_strs = [ss for _, ss, _ in subexpr_p1]
    subexpr_p2_strs = [ss for _, ss, _ in subexpr_p2]

    rows = []
    for i in range(2 ** n):
        values = {}
        for j, name in enumerate(names):
            value = bool((i >> j) & 1)
            values[name] = value
            if name in negated:
                values[f'~{name}'] = not value
            if name in props1:
                props1[name].value = value
            if name in props2:
                props2[name].value = value

        subvalues_p1 = {}
        for sp, ss, _ in subexpr_p1:
            try:
                subvalues_p1[ss] = _evaluate_proposition(sp)
            except:
                subvalues_p1[ss] = None

        subvalues_p2 = {}
        for sp, ss, _ in subexpr_p2:
            try:
                subvalues_p2[ss] = _evaluate_proposition(sp)
            except:
                subvalues_p2[ss] = None

        val1 = _evaluate_proposition(prop1)
        val2 = _evaluate_proposition(prop2)

        rows.append({
            'values': values,
            'subvalues_p1': subvalues_p1,
            'subvalues_p2': subvalues_p2,
            'p1': val1,
            'p2': val2
        })

    return {
        'variables': columns,
        'subexpressions_p1': subexpr_p1_strs,
        'subexpressions_p2': subexpr_p2_strs,
        'rows': rows
    }


def _format_transformations(transformations):
    """Formata a lista de transformacoes para a resposta da API."""
    result = []
    for t in transformations:
        result.append({
            'iteration': t.get('iteration', 0),
            'proposition': t.get('proposition', 1),
            'law': t.get('law', ''),
            'result': t.get('result', ''),
            'guided_by_nn': t.get('used_nn', False),
            'subexpression': t.get('matched_subexpr', ''),
            'p1': t.get('p1', ''),
            'p2': t.get('p2', '')
        })
    return result


class ProveService:
    """Servico para provar equivalencia entre proposicoes logicas."""

    @staticmethod
    def are_models_loaded():
        """Verifica se os modelos estao carregados."""
        return _convergence_model is not None

    @staticmethod
    def prove(data: dict) -> Result[dict[str, Any]]:
        """
        Verifica e prova a equivalencia entre duas proposicoes logicas.

        Metodos disponiveis:
        - automatic: Tenta multiplas estrategias automaticamente
        - direct: Prova por transformacao direta
        - contrapositive: Prova que ~P1 ≡ ~P2
        - absurd: Prova que (P1 ∧ ~P2) = F
        - bidirectional: Prova que (P1 -> P2) = T e (P2 -> P1) = T

        Returns:
            Result contendo os dados da prova ou erro
        """
        model, simp_model, eq = _load_models()

        prop1_str = data['proposition1']
        prop2_str = data['proposition2']
        method = data['method']
        max_iterations = data['max_iterations']

        try:
            prop1, props1 = parse_proposition(prop1_str)
        except ParseError as e:
            return Result.fail(
                message=f"Erro ao analisar proposicao 1: {str(e)}",
                code="PARSE_ERROR",
                field="proposition1"
            )

        try:
            prop2, props2 = parse_proposition(prop2_str)
        except ParseError as e:
            return Result.fail(
                message=f"Erro ao analisar proposicao 2: {str(e)}",
                code="PARSE_ERROR",
                field="proposition2"
            )

        prop1_initial = str(prop1)
        prop2_initial = str(prop2)

        truth_table = _generate_truth_table(prop1, props1, prop2, props2)

        semantically_equivalent = _verify_semantic_equivalence(prop1, props1, prop2, props2)

        if not semantically_equivalent:
            return Result.success({
                'success': True,
                'equivalent': False,
                'method_used': 'semantic_verification',
                'iterations': 0,
                'nn_predictions': 0,
                'proposition1_initial': prop1_initial,
                'proposition2_initial': prop2_initial,
                'proposition1_final': str(prop1),
                'proposition2_final': str(prop2),
                'transformations': [],
                'truth_table': truth_table,
                'message': 'As proposicoes NAO sao equivalentes (tabelas verdade diferentes)'
            })

        if eq.are_equal(prop1, prop2):
            return Result.success({
                'success': True,
                'equivalent': True,
                'method_used': 'syntactic_equality',
                'iterations': 0,
                'nn_predictions': 0,
                'proposition1_initial': prop1_initial,
                'proposition2_initial': prop2_initial,
                'proposition1_final': str(prop1),
                'proposition2_final': str(prop2),
                'transformations': [],
                'truth_table': truth_table,
                'message': 'As proposicoes ja sao sintaticamente iguais'
            })

        if isinstance(prop1, Proposition):
            prop1 = eq._ensure_compound(prop1)
        if isinstance(prop2, Proposition):
            prop2 = eq._ensure_compound(prop2)

        result = None
        method_used = method

        if method == 'automatic':
            result = eq.prove_with_fallback(
                prop1, prop2, model,
                simplification_predictor=simp_model,
                max_iterations=max_iterations,
                verbose=False
            )
            method_used = result.get('method', 'automatic')

        elif method == 'direct':
            result = eq.prove_equivalence_nn(
                prop1, prop2, model,
                max_iterations=max_iterations,
                verbose=False
            )

        elif method == 'contrapositive':
            result = eq.prove_by_contrapositive(
                prop1, prop2, model,
                max_iterations=max_iterations,
                verbose=False
            )

        elif method == 'absurd':
            result = eq.prove_by_absurdity(
                prop1, prop2, model,
                simplification_predictor=simp_model,
                max_iterations=max_iterations,
                verbose=False
            )

        elif method == 'bidirectional':
            result = eq.prove_bidirectional(
                prop1, prop2, model,
                max_iterations=max_iterations,
                verbose=False
            )

        success = result.get('success', False)
        transformations = result.get('transformations', [])

        if success:
            message = f'Equivalencia provada com sucesso usando metodo {method_used}'
        else:
            message = 'Nao foi possivel provar equivalencia sintaticamente (semanticamente sao equivalentes)'

        return Result.success({
            'success': success,
            'equivalent': True,
            'method_used': method_used,
            'iterations': result.get('iterations', 0),
            'nn_predictions': result.get('nn_predictions_used', 0),
            'proposition1_initial': prop1_initial,
            'proposition2_initial': prop2_initial,
            'proposition1_final': str(result.get('prop1_final', prop1)),
            'proposition2_final': str(result.get('prop2_final', prop2)),
            'transformations': _format_transformations(transformations),
            'truth_table': truth_table,
            'message': message
        })
