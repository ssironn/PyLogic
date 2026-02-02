"""
Feature extraction from propositions for neural network input.
"""
from utils.proposition import Proposition, CompoundProposition, OperatorNode, AtomicNode, PropositionNode


def analyze_proposition_usefulness(prop) -> dict:
    """
    Analyze which atomic propositions are "useful" (affect the truth value)
    and which are "useless" (don't affect the truth value) in a compound proposition.

    A proposition X is useless if:
    - For ALL combinations of other proposition values,
      the compound evaluates to the same value regardless of X's value.

    Examples:
    - p -> (p v q): q is useless (this is a tautology, always True)
    - p ^ q: both p and q are useful
    - p v ~p: p is useless (tautology)
    - p ^ ~p: p is useless (contradiction)
    - p v (p ^ q): q is useless (absorption: equals p)

    Args:
        prop: Proposition or CompoundProposition

    Returns:
        dict with keys:
            - 'propositions': dict mapping prop names to their Proposition objects
            - 'useful': set of proposition names that affect the result
            - 'useless': set of proposition names that don't affect the result
            - 'is_tautology': True if result is always True
            - 'is_contradiction': True if result is always False
            - 'useful_count': number of useful propositions
            - 'useless_count': number of useless propositions
            - 'total_count': total number of atomic propositions
            - 'useful_ratio': ratio of useful to total (0.0 to 1.0)
    """
    # Handle atomic propositions
    if isinstance(prop, Proposition):
        return {
            'propositions': {prop.text: prop},
            'useful': {prop.text},
            'useless': set(),
            'is_tautology': False,
            'is_contradiction': False,
            'useful_count': 1,
            'useless_count': 0,
            'total_count': 1,
            'useful_ratio': 1.0
        }

    if not isinstance(prop, CompoundProposition) or prop.root is None:
        return {
            'propositions': {},
            'useful': set(),
            'useless': set(),
            'is_tautology': False,
            'is_contradiction': False,
            'useful_count': 0,
            'useless_count': 0,
            'total_count': 0,
            'useful_ratio': 0.0
        }

    # Get all atomic propositions
    propositions = {}
    _collect_propositions(prop.root, propositions)

    if not propositions:
        return {
            'propositions': {},
            'useful': set(),
            'useless': set(),
            'is_tautology': False,
            'is_contradiction': False,
            'useful_count': 0,
            'useless_count': 0,
            'total_count': 0,
            'useful_ratio': 0.0
        }

    prop_names = sorted(propositions.keys())
    n = len(prop_names)

    useful = set()
    useless = set()

    # Check each proposition for usefulness
    for target_name in prop_names:
        is_useful = _check_proposition_useful(prop, propositions, prop_names, target_name)
        if is_useful:
            useful.add(target_name)
        else:
            useless.add(target_name)

    # Check if tautology or contradiction
    is_tautology = False
    is_contradiction = False

    if len(useless) == n:  # All propositions are useless
        # Evaluate with any assignment to check if tautology or contradiction
        for p in propositions.values():
            p.value = False
        result = prop.calculate_value()
        if result:
            is_tautology = True
        else:
            is_contradiction = True

    total = len(propositions)
    useful_count = len(useful)
    useless_count = len(useless)
    useful_ratio = useful_count / total if total > 0 else 0.0

    return {
        'propositions': propositions,
        'useful': useful,
        'useless': useless,
        'is_tautology': is_tautology,
        'is_contradiction': is_contradiction,
        'useful_count': useful_count,
        'useless_count': useless_count,
        'total_count': total,
        'useful_ratio': useful_ratio
    }


def _collect_propositions(node: PropositionNode, props: dict):
    """Collect all atomic propositions from a tree into a dict."""
    if node is None:
        return
    if isinstance(node, AtomicNode):
        props[node.proposition.text] = node.proposition
    elif isinstance(node, OperatorNode):
        _collect_propositions(node.left, props)
        if node.right:
            _collect_propositions(node.right, props)


def _check_proposition_useful(prop: CompoundProposition, propositions: dict,
                               prop_names: list, target_name: str) -> bool:
    """
    Check if a specific proposition affects the truth value of the compound.

    A proposition is useful if there exists at least one combination of
    other proposition values where changing the target's value changes the result.
    """
    other_names = [n for n in prop_names if n != target_name]
    n_others = len(other_names)

    # Try all combinations of other propositions
    for i in range(2 ** n_others):
        # Set other propositions based on binary representation
        for j, name in enumerate(other_names):
            propositions[name].value = bool((i >> j) & 1)

        # Evaluate with target = False
        propositions[target_name].value = False
        result_false = prop.calculate_value()

        # Evaluate with target = True
        propositions[target_name].value = True
        result_true = prop.calculate_value()

        # If results differ, target is useful
        if result_false != result_true:
            return True

    return False


def get_usefulness_features(prop) -> list:
    """
    Extract usefulness-related features from a proposition.

    Returns:
        List of 5 features:
        - useful_count: number of useful propositions
        - useless_count: number of useless propositions
        - useful_ratio: ratio of useful to total (0.0 to 1.0)
        - is_tautology: 1 if always True, 0 otherwise
        - is_contradiction: 1 if always False, 0 otherwise
    """
    analysis = analyze_proposition_usefulness(prop)
    return [
        analysis['useful_count'],
        analysis['useless_count'],
        analysis['useful_ratio'],
        1 if analysis['is_tautology'] else 0,
        1 if analysis['is_contradiction'] else 0
    ]


def extract_features(prop) -> list:
    """
    Extract 17 numerical features from a proposition.

    Features:
    - depth: Tree depth
    - num_nodes: Total number of nodes
    - num_atomic: Number of atomic propositions
    - num_negations: Count of NOT operators
    - num_conjunctions: Count of AND operators
    - num_disjunctions: Count of OR operators
    - num_implications: Count of IMPLIES operators
    - has_double_negation: 1 if ~~p pattern exists
    - has_de_morgan_pattern: 1 if ~(p op q) pattern exists
    - has_implication: 1 if p → q pattern exists at root
    - has_binary_at_root: 1 if root is binary operator
    - is_atomic: 1 if just atomic proposition
    - useful_count: number of useful propositions
    - useless_count: number of useless propositions
    - useful_ratio: ratio of useful to total (0.0 to 1.0)
    - is_tautology: 1 if always True
    - is_contradiction: 1 if always False

    Args:
        prop: Proposition or CompoundProposition

    Returns:
        List of 17 float features
    """
    if isinstance(prop, Proposition):
        # Atomic: depth=1, nodes=1, atomic=1, all ops=0, patterns=0,
        # not binary root, is atomic, 1 useful, 0 useless, ratio=1.0, not taut/contr
        return [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1.0, 0, 0]

    if not isinstance(prop, CompoundProposition) or prop.root is None:
        return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0]

    root = prop.root

    # Structure features
    depth = _calculate_depth(root)
    num_nodes = _count_nodes(root)
    num_atomic = _count_atomic(root)
    num_negations = _count_operator(root, '__invert__')
    num_conjunctions = _count_operator(root, '__mul__')
    num_disjunctions = _count_operator(root, '__add__')
    num_implications = _count_operator(root, '__rshift__')
    has_double_neg = 1 if _has_double_negation(root) else 0
    has_de_morgan = 1 if _has_de_morgan_pattern(root) else 0
    has_implication = 1 if _has_implication_at_root(root) else 0
    has_binary_root = 1 if (isinstance(root, OperatorNode) and root.right is not None) else 0
    is_atomic = 1 if isinstance(root, AtomicNode) else 0

    # Usefulness features
    usefulness = get_usefulness_features(prop)

    return [
        depth,
        num_nodes,
        num_atomic,
        num_negations,
        num_conjunctions,
        num_disjunctions,
        num_implications,
        has_double_neg,
        has_de_morgan,
        has_implication,
        has_binary_root,
        is_atomic,
    ] + usefulness


def _calculate_depth(node: PropositionNode) -> int:
    """Calculate the depth of the tree."""
    if node is None:
        return 0
    if isinstance(node, AtomicNode):
        return 1
    if isinstance(node, OperatorNode):
        left_depth = _calculate_depth(node.left)
        right_depth = _calculate_depth(node.right) if node.right else 0
        return 1 + max(left_depth, right_depth)
    return 0


def _count_nodes(node: PropositionNode) -> int:
    """Count total number of nodes in the tree."""
    if node is None:
        return 0
    if isinstance(node, AtomicNode):
        return 1
    if isinstance(node, OperatorNode):
        left_count = _count_nodes(node.left)
        right_count = _count_nodes(node.right) if node.right else 0
        return 1 + left_count + right_count
    return 0


def _count_atomic(node: PropositionNode) -> int:
    """Count number of atomic propositions."""
    if node is None:
        return 0
    if isinstance(node, AtomicNode):
        return 1
    if isinstance(node, OperatorNode):
        left_count = _count_atomic(node.left)
        right_count = _count_atomic(node.right) if node.right else 0
        return left_count + right_count
    return 0


def _count_operator(node: PropositionNode, op_name: str) -> int:
    """Count occurrences of a specific operator."""
    if node is None:
        return 0
    if isinstance(node, AtomicNode):
        return 0
    if isinstance(node, OperatorNode):
        count = 1 if node.operator.name == op_name else 0
        count += _count_operator(node.left, op_name)
        if node.right:
            count += _count_operator(node.right, op_name)
        return count
    return 0


def _has_double_negation(node: PropositionNode) -> bool:
    """Check if double negation pattern exists anywhere in tree."""
    if node is None:
        return False
    if isinstance(node, AtomicNode):
        return False
    if isinstance(node, OperatorNode):
        if node.operator.name == '__invert__' and node.right is None:
            inner = node.left
            if isinstance(inner, OperatorNode):
                if inner.operator.name == '__invert__' and inner.right is None:
                    return True
        if _has_double_negation(node.left):
            return True
        if node.right and _has_double_negation(node.right):
            return True
    return False


def _has_de_morgan_pattern(node: PropositionNode) -> bool:
    """Check if De Morgan pattern ~(p op q) exists anywhere in tree."""
    if node is None:
        return False
    if isinstance(node, AtomicNode):
        return False
    if isinstance(node, OperatorNode):
        if node.operator.name == '__invert__' and node.right is None:
            inner = node.left
            if isinstance(inner, OperatorNode):
                if inner.operator.name in ('__add__', '__mul__') and inner.right is not None:
                    return True
        if _has_de_morgan_pattern(node.left):
            return True
        if node.right and _has_de_morgan_pattern(node.right):
            return True
    return False


def _has_implication_at_root(node: PropositionNode) -> bool:
    """Check if the root is an implication."""
    if node is None:
        return False
    if isinstance(node, OperatorNode):
        return node.operator.name == '__rshift__' and node.right is not None
    return False


def get_applicability_features(prop) -> list:
    """
    Extract features indicating which transformations can be applied.

    This allows the NN to make informed decisions about which
    transformations are actually valid for each proposition.

    Returns:
        List of 17 boolean features (1 if applicable, 0 if not):
        - can_apply_double_negation
        - can_apply_idempotence
        - can_apply_absorption
        - can_apply_factoring
        - can_apply_identity
        - can_apply_domination
        - can_apply_negation_constant
        - can_apply_complement
        - can_apply_implication_constant
        - can_apply_de_morgan
        - can_apply_commutativity
        - can_apply_associativity
        - can_apply_implication_elimination
        - can_apply_implication_introduction
        - can_apply_contraposition
        - can_apply_de_morgan_reverse
        - can_apply_distributivity
    """
    from utils.equivalence import Equivalence

    eq = Equivalence()

    # Handle non-compound propositions
    if isinstance(prop, Proposition) and not isinstance(prop, CompoundProposition):
        # Atomic propositions can't have any transformations applied
        return [0] * 17

    if not isinstance(prop, CompoundProposition):
        return [0] * 17

    # Check each transformation (including deep application)
    return [
        1 if eq._can_apply_anywhere(prop, eq.check_double_negation) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_idempotence) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_absorption) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_factoring) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_identity) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_domination) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_negation_constant) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_complement) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_implication_constant) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_de_morgan) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_commutativity) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_associativity) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_implication_elimination) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_implication_introduction) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_contraposition) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_de_morgan_reverse) else 0,
        1 if eq._can_apply_anywhere(prop, eq.check_distributivity) else 0,
    ]


# Mapping from applicability feature index to transformation name
APPLICABILITY_MAPPING = [
    'double_negation',
    'idempotence',
    'absorption',
    'factoring',
    'identity',
    'domination',
    'negation_constant',
    'complement',
    'implication_constant',
    'de_morgan',
    'commutativity',
    'associativity',
    'implication_elimination',
    'implication_introduction',
    'contraposition',
    'de_morgan_reverse',
    'distributivity',
]


def extract_pair_features(prop1, prop2) -> list:
    """
    Extract features from a pair of propositions.

    Returns:
        List of 68 float features:
        - 17 structural/semantic features per proposition (34 total)
        - 17 applicability features per proposition (34 total)
    """
    features1 = extract_features(prop1)
    features2 = extract_features(prop2)
    applicability1 = get_applicability_features(prop1)
    applicability2 = get_applicability_features(prop2)
    return features1 + features2 + applicability1 + applicability2


def extract_single_features(prop, goal: str = 'F') -> list:
    """
    Extract features from a single proposition for simplification tasks.

    Used by SimplificationPredictor for absurdity proofs where the goal
    is to simplify a single expression (P1 ∧ ~P2) to a constant (F or T).

    Args:
        prop: Proposition or CompoundProposition
        goal: Target constant - 'F' for absurdity proofs, 'T' for tautology proofs

    Returns:
        List of 35 float features:
        - 17 structural/semantic features
        - 17 applicability features
        - 1 goal indicator (0=reach_F, 1=reach_T)
    """
    structural = extract_features(prop)
    applicability = get_applicability_features(prop)
    goal_indicator = 1 if goal.upper() == 'T' else 0
    return structural + applicability + [goal_indicator]
