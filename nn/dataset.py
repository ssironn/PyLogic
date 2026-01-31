"""
Dataset generation for training the neural network.

Generates high-quality training samples that prioritize:
1. Simplification operations (double negation, absorption, idempotence)
2. Structure-preserving operations (De Morgan forward, commutativity)
3. Avoiding complexity-increasing operations
"""
import random
import numpy as np
import sys
sys.path.insert(0, '..')

from proposition import Proposition, CompoundProposition, AtomicNode, TRUE, FALSE
from equivalence import Equivalence
from nn.features import extract_pair_features, extract_single_features


# Mapping from class index to (which_prop, transformation_name)
# Organized by priority: simplification first, then structure changes
CLASS_MAPPING = {
    # High priority: Simplification operations
    0: (1, 'double_negation'),      # ~~p -> p (simplifies)
    1: (1, 'idempotence'),          # p ^ p -> p (simplifies)
    2: (1, 'absorption'),           # p ^ (p v q) -> p (simplifies)
    3: (1, 'implication_elimination'),  # p -> q => ~p v q (useful for proofs)
    # Medium priority: Structure transformations
    4: (1, 'de_morgan'),            # ~(p ^ q) -> ~p v ~q (useful structure change)
    5: (1, 'commutativity'),        # p ^ q -> q ^ p (reorder)
    # Same for prop 2
    6: (2, 'double_negation'),
    7: (2, 'idempotence'),
    8: (2, 'absorption'),
    9: (2, 'implication_elimination'),
    10: (2, 'de_morgan'),
    11: (2, 'commutativity'),
    # Lower priority
    12: (1, 'implication_introduction'),  # ~p v q => p -> q
    13: (2, 'implication_introduction'),
    14: (1, 'contraposition'),      # p -> q => ~q -> ~p
    15: (2, 'contraposition'),
    # Low priority: Complexity increasing (rarely use)
    16: (1, 'de_morgan_reverse'),
    17: (2, 'de_morgan_reverse'),
    # Distributivity (can go either way)
    18: (1, 'distributivity'),
    19: (2, 'distributivity'),
    # Truth constant laws (high priority - simplification)
    20: (1, 'complement'),          # p v ~p -> T, p ^ ~p -> F
    21: (2, 'complement'),
    22: (1, 'identity'),            # p v F -> p, p ^ T -> p
    23: (2, 'identity'),
    24: (1, 'domination'),          # p v T -> T, p ^ F -> F
    25: (2, 'domination'),
    26: (1, 'negation_constant'),   # ~T -> F, ~F -> T
    27: (2, 'negation_constant'),
    28: (1, 'implication_constant'), # T -> p = p, F -> p = T, etc.
    29: (2, 'implication_constant'),
    # Factoring (reverse distributivity - simplifies!)
    30: (1, 'factoring'),           # (p^q)v(p^r) -> p^(qvr)
    31: (2, 'factoring'),
    # Associativity (structure change - useful for exposing patterns)
    32: (1, 'associativity'),       # (p v q) v r -> p v (q v r)
    33: (2, 'associativity'),
}

REVERSE_CLASS_MAPPING = {v: k for k, v in CLASS_MAPPING.items()}


# Mapping for SimplificationPredictor (single proposition, absurdity proofs)
# Classes ordered by priority for simplification to constant (F or T)
SIMPLIFICATION_CLASS_MAPPING = {
    # CRITICAL: Transformations that directly simplify to constants
    0: 'complement',            # p ∧ ~p → F, p ∨ ~p → T (HIGHEST PRIORITY)
    1: 'domination',            # p ∧ F → F, p ∨ T → T (propagate constants)
    2: 'identity',              # p ∧ T → p, p ∨ F → p (remove constants)
    3: 'negation_constant',     # ~T → F, ~F → T
    # HIGH: Transformations that expose complement patterns
    4: 'distributivity',        # Expose p ∧ ~p patterns
    5: 'factoring',             # Reverse distributivity
    6: 'associativity',         # Regroup to expose complement
    # MEDIUM: Standard simplifications
    7: 'double_negation',       # ~~p → p
    8: 'de_morgan',             # ~(p ∧ q) → ~p ∨ ~q
    9: 'idempotence',           # p ∧ p → p
    10: 'absorption',           # p ∧ (p ∨ q) → p
    11: 'implication_elimination',  # p → q => ~p ∨ q
    12: 'implication_constant', # T → p = p, F → p = T
    # LOW: Structure changes (less useful for simplification)
    13: 'commutativity',        # p ∧ q → q ∧ p
    14: 'contraposition',       # p → q => ~q → ~p
    15: 'implication_introduction',  # ~p ∨ q => p → q
    16: 'de_morgan_reverse',    # ~p ∨ ~q → ~(p ∧ q)
}

REVERSE_SIMPLIFICATION_CLASS_MAPPING = {v: k for k, v in SIMPLIFICATION_CLASS_MAPPING.items()}


def decode_prediction(class_idx: int) -> tuple:
    """Convert class index to (which_prop, transformation_name)."""
    return CLASS_MAPPING.get(class_idx, (1, 'double_negation'))


def decode_simplification_prediction(class_idx: int) -> str:
    """Convert class index to transformation_name for SimplificationPredictor."""
    return SIMPLIFICATION_CLASS_MAPPING.get(class_idx, 'complement')


def encode_action(which_prop: int, transformation_name: str) -> int:
    """Convert (which_prop, transformation_name) to class index."""
    return REVERSE_CLASS_MAPPING.get((which_prop, transformation_name), 0)


def encode_simplification_action(transformation_name: str) -> int:
    """Convert transformation_name to class index for SimplificationPredictor."""
    return REVERSE_SIMPLIFICATION_CLASS_MAPPING.get(transformation_name, 0)


def _make_compound(prop):
    """Ensure prop is a CompoundProposition."""
    if isinstance(prop, CompoundProposition):
        return prop
    if isinstance(prop, Proposition):
        cp = CompoundProposition()
        cp.root = AtomicNode(prop)
        cp.components = {prop}
        return cp
    return prop


def _get_propositions():
    """Get a set of propositions with different names."""
    return {
        'p': Proposition(text='p', value=True),
        'q': Proposition(text='q', value=False),
        'r': Proposition(text='r', value=True),
        's': Proposition(text='s', value=False),
    }


def generate_double_negation_samples():
    """
    Generate MANY double negation samples - this is a key simplification.
    ~~p -> p (always simplify!)
    """
    props = _get_propositions()
    samples = []

    for name, p in props.items():
        # Simple: ~~p = p (MANY samples to reinforce)
        not_p = CompoundProposition(Proposition.__invert__, p)
        not_not_p = CompoundProposition(Proposition.__invert__, not_p)
        p_comp = _make_compound(p)

        # Add many samples: always simplify ~~p to p
        for _ in range(20):
            samples.append((not_not_p, p_comp, 1, 'double_negation'))
            samples.append((p_comp, not_not_p, 2, 'double_negation'))

        # Triple negation: ~~~p = ~p
        not_not_not_p = CompoundProposition(Proposition.__invert__, not_not_p)
        for _ in range(10):
            samples.append((not_not_not_p, not_p, 1, 'double_negation'))
            samples.append((not_p, not_not_not_p, 2, 'double_negation'))

        # Nested in binary: ~~p ^ q -> p ^ q
        for name2, q in props.items():
            if name != name2:
                for op in [Proposition.__mul__, Proposition.__add__]:
                    complex_expr = CompoundProposition(op, not_not_p, q)
                    simple_expr = CompoundProposition(op, p, q)
                    for _ in range(5):
                        samples.append((complex_expr, simple_expr, 1, 'double_negation'))

                    # Also: q ^ ~~p -> q ^ p
                    complex_expr2 = CompoundProposition(op, q, not_not_p)
                    simple_expr2 = CompoundProposition(op, q, p)
                    for _ in range(5):
                        samples.append((complex_expr2, simple_expr2, 1, 'double_negation'))

        # ~~(p ^ q) -> p ^ q
        for name2, q in props.items():
            if name != name2:
                for op in [Proposition.__mul__, Proposition.__add__]:
                    inner = CompoundProposition(op, p, q)
                    not_inner = CompoundProposition(Proposition.__invert__, inner)
                    not_not_inner = CompoundProposition(Proposition.__invert__, not_inner)
                    for _ in range(5):
                        samples.append((not_not_inner, inner, 1, 'double_negation'))

    return samples


def generate_absorption_samples():
    """
    Generate MANY absorption samples - this is a powerful simplification.
    p ^ (p v q) -> p
    p v (p ^ q) -> p
    """
    props = _get_propositions()
    samples = []

    for name1, p in props.items():
        for name2, q in props.items():
            if name1 != name2:
                # p ^ (p v q) -> p
                p_or_q = CompoundProposition(Proposition.__add__, p, q)
                absorption_and = CompoundProposition(Proposition.__mul__, p, p_or_q)
                p_comp = _make_compound(p)

                for _ in range(15):
                    samples.append((absorption_and, p_comp, 1, 'absorption'))
                    samples.append((p_comp, absorption_and, 2, 'absorption'))

                # p v (p ^ q) -> p
                p_and_q = CompoundProposition(Proposition.__mul__, p, q)
                absorption_or = CompoundProposition(Proposition.__add__, p, p_and_q)

                for _ in range(15):
                    samples.append((absorption_or, p_comp, 1, 'absorption'))
                    samples.append((p_comp, absorption_or, 2, 'absorption'))

                # Also with reversed inner: p ^ (q v p) -> p
                q_or_p = CompoundProposition(Proposition.__add__, q, p)
                absorption_and2 = CompoundProposition(Proposition.__mul__, p, q_or_p)

                for _ in range(10):
                    samples.append((absorption_and2, p_comp, 1, 'absorption'))

                # (p v q) ^ p -> p (swapped order)
                absorption_and3 = CompoundProposition(Proposition.__mul__, p_or_q, p)
                for _ in range(10):
                    samples.append((absorption_and3, p_comp, 1, 'absorption'))

                # Nested: (p ^ (p v q)) v r -> should simplify inner first
                for name3, r in props.items():
                    if name3 not in (name1, name2):
                        nested = CompoundProposition(Proposition.__add__, absorption_and, r)
                        simple = CompoundProposition(Proposition.__add__, p, r)
                        for _ in range(5):
                            samples.append((nested, simple, 1, 'absorption'))

    return samples


def generate_idempotence_samples():
    """
    Generate MANY idempotence samples - another key simplification.
    p ^ p -> p
    p v p -> p
    """
    props = _get_propositions()
    samples = []

    for name, p in props.items():
        p_comp = _make_compound(p)

        # p ^ p -> p
        p_and_p = CompoundProposition(Proposition.__mul__, p, p)
        for _ in range(20):
            samples.append((p_and_p, p_comp, 1, 'idempotence'))
            samples.append((p_comp, p_and_p, 2, 'idempotence'))

        # p v p -> p
        p_or_p = CompoundProposition(Proposition.__add__, p, p)
        for _ in range(20):
            samples.append((p_or_p, p_comp, 1, 'idempotence'))
            samples.append((p_comp, p_or_p, 2, 'idempotence'))

        # Nested: (p ^ p) v q -> p v q
        for name2, q in props.items():
            if name != name2:
                nested_and = CompoundProposition(Proposition.__add__, p_and_p, q)
                simple = CompoundProposition(Proposition.__add__, p, q)
                for _ in range(5):
                    samples.append((nested_and, simple, 1, 'idempotence'))

                # (p v p) ^ q -> p ^ q
                nested_or = CompoundProposition(Proposition.__mul__, p_or_p, q)
                simple2 = CompoundProposition(Proposition.__mul__, p, q)
                for _ in range(5):
                    samples.append((nested_or, simple2, 1, 'idempotence'))

    return samples


def generate_de_morgan_samples():
    """
    Generate De Morgan (forward) samples - useful for structure changes.
    ~(p ^ q) -> ~p v ~q
    ~(p v q) -> ~p ^ ~q

    CRITICAL: Also generates "nested negation" patterns that lead to simplification:
    ~(~p v ~q) -> ~~p ^ ~~q -> p ^ q
    ~(~p ^ ~q) -> ~~p v ~~q -> p v q

    Note: We generate MANY MORE forward than reverse samples
    to teach the NN that forward is preferred (it often leads to simplification).
    """
    props = _get_propositions()
    samples = []

    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)

                # ~(p ^ q) = ~p v ~q
                p_and_q = CompoundProposition(Proposition.__mul__, p, q)
                not_p_and_q = CompoundProposition(Proposition.__invert__, p_and_q)
                not_p_or_not_q = CompoundProposition(Proposition.__add__, not_p, not_q)

                # Forward De Morgan: MANY samples
                for _ in range(10):
                    samples.append((not_p_and_q, not_p_or_not_q, 1, 'de_morgan'))
                    samples.append((not_p_or_not_q, not_p_and_q, 2, 'de_morgan'))

                # Reverse De Morgan: FEW samples (we want to discourage this)
                samples.append((not_p_or_not_q, not_p_and_q, 1, 'de_morgan_reverse'))

                # ~(p v q) = ~p ^ ~q
                p_or_q = CompoundProposition(Proposition.__add__, p, q)
                not_p_or_q = CompoundProposition(Proposition.__invert__, p_or_q)
                not_p_and_not_q = CompoundProposition(Proposition.__mul__, not_p, not_q)

                # Forward: MANY
                for _ in range(10):
                    samples.append((not_p_or_q, not_p_and_not_q, 1, 'de_morgan'))
                    samples.append((not_p_and_not_q, not_p_or_q, 2, 'de_morgan'))

                # Reverse: FEW
                samples.append((not_p_and_not_q, not_p_or_q, 1, 'de_morgan_reverse'))

    # CRITICAL: Nested negation De Morgan patterns
    # These patterns lead to double negation elimination and full simplification!
    # ~(~p v ~q) -> ~~p ^ ~~q -> p ^ q
    # ~(~p ^ ~q) -> ~~p v ~~q -> p v q
    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)
        not_not_p = CompoundProposition(Proposition.__invert__, not_p)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)
                not_not_q = CompoundProposition(Proposition.__invert__, not_q)

                # ~(~p v ~q) -> ~~p ^ ~~q -> p ^ q
                not_p_or_not_q = CompoundProposition(Proposition.__add__, not_p, not_q)
                neg_pattern_or = CompoundProposition(Proposition.__invert__, not_p_or_not_q)
                # After De Morgan: ~~p ^ ~~q
                not_not_p_and_not_not_q = CompoundProposition(Proposition.__mul__, not_not_p, not_not_q)
                # Final result: p ^ q
                p_and_q = CompoundProposition(Proposition.__mul__, p, q)

                # MANY samples - De Morgan is the key first step!
                for _ in range(25):
                    samples.append((neg_pattern_or, p_and_q, 1, 'de_morgan'))
                    samples.append((p_and_q, neg_pattern_or, 2, 'de_morgan'))
                    samples.append((neg_pattern_or, not_not_p_and_not_not_q, 1, 'de_morgan'))

                # Intermediate steps
                not_not_p_and_q = CompoundProposition(Proposition.__mul__, not_not_p, q)
                for _ in range(15):
                    samples.append((not_not_p_and_not_not_q, p_and_q, 1, 'double_negation'))
                    samples.append((not_not_p_and_not_not_q, not_not_p_and_q, 1, 'double_negation'))
                    samples.append((not_not_p_and_q, p_and_q, 1, 'double_negation'))

                # ~(~p ^ ~q) -> ~~p v ~~q -> p v q
                not_p_and_not_q = CompoundProposition(Proposition.__mul__, not_p, not_q)
                neg_pattern_and = CompoundProposition(Proposition.__invert__, not_p_and_not_q)
                # After De Morgan: ~~p v ~~q
                not_not_p_or_not_not_q = CompoundProposition(Proposition.__add__, not_not_p, not_not_q)
                # Final result: p v q
                p_or_q = CompoundProposition(Proposition.__add__, p, q)

                for _ in range(25):
                    samples.append((neg_pattern_and, p_or_q, 1, 'de_morgan'))
                    samples.append((p_or_q, neg_pattern_and, 2, 'de_morgan'))
                    samples.append((neg_pattern_and, not_not_p_or_not_not_q, 1, 'de_morgan'))

                # Intermediate steps
                not_not_p_or_q = CompoundProposition(Proposition.__add__, not_not_p, q)
                for _ in range(15):
                    samples.append((not_not_p_or_not_not_q, p_or_q, 1, 'double_negation'))
                    samples.append((not_not_p_or_not_not_q, not_not_p_or_q, 1, 'double_negation'))
                    samples.append((not_not_p_or_q, p_or_q, 1, 'double_negation'))

    return samples


def generate_commutativity_samples():
    """Generate commutativity samples - useful for matching."""
    props = _get_propositions()
    samples = []

    for op in [Proposition.__mul__, Proposition.__add__]:
        for name1, p1 in props.items():
            for name2, p2 in props.items():
                if name1 != name2:
                    left = CompoundProposition(op, p1, p2)
                    right = CompoundProposition(op, p2, p1)
                    for _ in range(3):
                        samples.append((left, right, 1, 'commutativity'))
                        samples.append((left, right, 2, 'commutativity'))
                        samples.append((right, left, 1, 'commutativity'))
                        samples.append((right, left, 2, 'commutativity'))

    return samples


def generate_implication_samples():
    """
    Generate implication samples.
    - Implication elimination: p → q ≡ ~p v q (high priority - simplifies proofs)
    - Implication introduction: ~p v q ≡ p → q
    - Contraposition: p → q ≡ ~q → ~p

    CRITICAL: Also generates negated implication patterns:
    ~(p → q) -> ~(~p v q) -> ~~p ^ ~q -> p ^ ~q
    """
    props = _get_propositions()
    samples = []

    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)
        not_not_p = CompoundProposition(Proposition.__invert__, not_p)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)

                # p → q
                impl = CompoundProposition(Proposition.__rshift__, p, q)
                # ~p v q (equivalent form)
                disj = CompoundProposition(Proposition.__add__, not_p, q)
                # ~q → ~p (contrapositive)
                contrapos = CompoundProposition(Proposition.__rshift__, not_q, not_p)

                # Implication elimination: p → q -> ~p v q (MANY samples - useful!)
                for _ in range(15):
                    samples.append((impl, disj, 1, 'implication_elimination'))
                    samples.append((disj, impl, 2, 'implication_elimination'))

                # Implication introduction: ~p v q -> p → q (fewer samples)
                for _ in range(5):
                    samples.append((disj, impl, 1, 'implication_introduction'))
                    samples.append((impl, disj, 2, 'implication_introduction'))

                # Contraposition: p → q -> ~q → ~p
                for _ in range(8):
                    samples.append((impl, contrapos, 1, 'contraposition'))
                    samples.append((contrapos, impl, 2, 'contraposition'))

                # CRITICAL: Negated implication pattern
                # ~(p → q) -> ~(~p v q) -> ~~p ^ ~q -> p ^ ~q
                neg_impl = CompoundProposition(Proposition.__invert__, impl)
                # After implication_elimination (deep): ~(~p v q)
                neg_disj = CompoundProposition(Proposition.__invert__, disj)
                # After de_morgan: ~~p ^ ~q
                not_not_p_and_not_q = CompoundProposition(Proposition.__mul__, not_not_p, not_q)
                # Final result: p ^ ~q
                p_and_not_q = CompoundProposition(Proposition.__mul__, p, not_q)

                # MANY samples - this is a key multi-step pattern!
                for _ in range(25):
                    # First step: implication_elimination (deep apply)
                    samples.append((neg_impl, p_and_not_q, 1, 'implication_elimination'))
                    samples.append((p_and_not_q, neg_impl, 2, 'implication_elimination'))
                    samples.append((neg_impl, neg_disj, 1, 'implication_elimination'))

                # Subsequent steps
                for _ in range(20):
                    # After implication_elimination: ~(~p v q) -> de_morgan
                    samples.append((neg_disj, p_and_not_q, 1, 'de_morgan'))
                    samples.append((neg_disj, not_not_p_and_not_q, 1, 'de_morgan'))
                    # After de_morgan: ~~p ^ ~q -> double_negation
                    samples.append((not_not_p_and_not_q, p_and_not_q, 1, 'double_negation'))

                # Nested implications: (p → q) → r, p → (q → r)
                for name3, r in props.items():
                    if name3 not in (name1, name2):
                        not_r = CompoundProposition(Proposition.__invert__, r)

                        # p → (q → r)
                        inner_impl = CompoundProposition(Proposition.__rshift__, q, r)
                        chained = CompoundProposition(Proposition.__rshift__, p, inner_impl)

                        # Equivalent: ~p v (~q v r)
                        not_q_or_r = CompoundProposition(Proposition.__add__, not_q, r)
                        equiv = CompoundProposition(Proposition.__add__, not_p, not_q_or_r)

                        for _ in range(10):
                            samples.append((chained, equiv, 1, 'implication_elimination'))

                        # (p → q) → r - outer implication first
                        impl_pq = CompoundProposition(Proposition.__rshift__, p, q)
                        outer_impl = CompoundProposition(Proposition.__rshift__, impl_pq, r)
                        # Equivalent: ~(p → q) v r = ~(~p v q) v r
                        neg_impl_pq = CompoundProposition(Proposition.__invert__, impl_pq)
                        equiv2 = CompoundProposition(Proposition.__add__, neg_impl_pq, r)

                        for _ in range(10):
                            samples.append((outer_impl, equiv2, 1, 'implication_elimination'))

    # CRITICAL: Complex tautology patterns
    # These help the NN recognize when to apply implication_elimination on complex expressions
    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)
        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)
                for name3, r in props.items():
                    if name3 not in (name1, name2):
                        not_r = CompoundProposition(Proposition.__invert__, r)
                        t_comp = _make_compound(TRUE)

                        # Distribution axiom: (p → (q → r)) → ((p → q) → (p → r))
                        # This is a tautology - always true
                        q_impl_r = CompoundProposition(Proposition.__rshift__, q, r)
                        p_impl_qr = CompoundProposition(Proposition.__rshift__, p, q_impl_r)
                        p_impl_q = CompoundProposition(Proposition.__rshift__, p, q)
                        p_impl_r = CompoundProposition(Proposition.__rshift__, p, r)
                        pq_impl_pr = CompoundProposition(Proposition.__rshift__, p_impl_q, p_impl_r)
                        distribution_axiom = CompoundProposition(Proposition.__rshift__, p_impl_qr, pq_impl_pr)

                        # For complex tautologies, apply implication_elimination to simplify
                        for _ in range(20):
                            samples.append((distribution_axiom, t_comp, 1, 'implication_elimination'))

                        # Modus ponens as tautology: ((p → q) ^ p) → q
                        impl_pq = CompoundProposition(Proposition.__rshift__, p, q)
                        impl_and_p = CompoundProposition(Proposition.__mul__, impl_pq, p)
                        modus_ponens = CompoundProposition(Proposition.__rshift__, impl_and_p, q)

                        for _ in range(20):
                            samples.append((modus_ponens, t_comp, 1, 'implication_elimination'))

                        # Modus tollens as tautology: ((p → q) ^ ~q) → ~p
                        impl_and_not_q = CompoundProposition(Proposition.__mul__, impl_pq, not_q)
                        modus_tollens = CompoundProposition(Proposition.__rshift__, impl_and_not_q, not_p)

                        for _ in range(20):
                            samples.append((modus_tollens, t_comp, 1, 'implication_elimination'))

                        # Hypothetical syllogism: ((p → q) ^ (q → r)) → (p → r)
                        q_impl_r = CompoundProposition(Proposition.__rshift__, q, r)
                        both_impl = CompoundProposition(Proposition.__mul__, impl_pq, q_impl_r)
                        hyp_syllogism = CompoundProposition(Proposition.__rshift__, both_impl, p_impl_r)

                        for _ in range(20):
                            samples.append((hyp_syllogism, t_comp, 1, 'implication_elimination'))

                        # Any implication A → B where the whole thing equals T
                        # should start with implication_elimination
                        # p → p is a tautology
                        p_impl_p = CompoundProposition(Proposition.__rshift__, p, p)
                        for _ in range(15):
                            samples.append((p_impl_p, t_comp, 1, 'implication_elimination'))

                        # p → (p v q) is a tautology
                        p_or_q = CompoundProposition(Proposition.__add__, p, q)
                        p_impl_p_or_q = CompoundProposition(Proposition.__rshift__, p, p_or_q)
                        for _ in range(15):
                            samples.append((p_impl_p_or_q, t_comp, 1, 'implication_elimination'))

                        # (p ^ q) → p is a tautology
                        p_and_q = CompoundProposition(Proposition.__mul__, p, q)
                        pq_impl_p = CompoundProposition(Proposition.__rshift__, p_and_q, p)
                        for _ in range(15):
                            samples.append((pq_impl_p, t_comp, 1, 'implication_elimination'))

    # CRITICAL: Distributivity patterns that lead to tautology simplification
    # q v (p ^ ~q) -> (q v p) ^ (q v ~q) -> (q v p) ^ T -> q v p
    # These patterns need distributivity to expose complement
    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)
        p_comp = _make_compound(p)
        t_comp = _make_compound(TRUE)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)
                q_comp = _make_compound(q)

                # q v (p ^ ~q) -> uses distributivity to simplify
                p_and_not_q = CompoundProposition(Proposition.__mul__, p, not_q)
                q_or_p_and_not_q = CompoundProposition(Proposition.__add__, q, p_and_not_q)
                # After distributivity: (q v p) ^ (q v ~q)
                q_or_p = CompoundProposition(Proposition.__add__, q, p)
                q_or_not_q = CompoundProposition(Proposition.__add__, q, not_q)
                distributed = CompoundProposition(Proposition.__mul__, q_or_p, q_or_not_q)

                for _ in range(20):
                    samples.append((q_or_p_and_not_q, q_or_p, 1, 'distributivity'))
                    samples.append((q_or_p_and_not_q, distributed, 1, 'distributivity'))
                    samples.append((distributed, q_or_p, 1, 'complement'))

                # (p ^ ~q) v q - same pattern, different order
                p_and_not_q_or_q = CompoundProposition(Proposition.__add__, p_and_not_q, q)
                for _ in range(20):
                    samples.append((p_and_not_q_or_q, q_or_p, 1, 'distributivity'))

                # p v (~p ^ q) -> (p v ~p) ^ (p v q) -> T ^ (p v q) -> p v q
                not_p_and_q = CompoundProposition(Proposition.__mul__, not_p, q)
                p_or_not_p_and_q = CompoundProposition(Proposition.__add__, p, not_p_and_q)
                p_or_q = CompoundProposition(Proposition.__add__, p, q)

                for _ in range(20):
                    samples.append((p_or_not_p_and_q, p_or_q, 1, 'distributivity'))

                # (~p ^ q) v p -> same pattern
                not_p_and_q_or_p = CompoundProposition(Proposition.__add__, not_p_and_q, p)
                for _ in range(20):
                    samples.append((not_p_and_q_or_p, p_or_q, 1, 'distributivity'))

                # Full tautology pattern: (p ^ ~q) v ~p v q = T
                # First: (p ^ ~q) v ~p = (~q v ~p) using factoring-like pattern
                p_and_not_q_or_not_p = CompoundProposition(Proposition.__add__, p_and_not_q, not_p)
                not_q_or_not_p = CompoundProposition(Proposition.__add__, not_q, not_p)

                for _ in range(15):
                    samples.append((p_and_not_q_or_not_p, not_q_or_not_p, 1, 'distributivity'))

                # The intermediate form from Modus Ponens proof:
                # ((p ^ ~q) v ~p) v q = T
                full_expr = CompoundProposition(Proposition.__add__, p_and_not_q_or_not_p, q)
                for _ in range(25):
                    samples.append((full_expr, t_comp, 1, 'distributivity'))

                # ~p v q v (p ^ ~q) = T - another arrangement
                not_p_or_q = CompoundProposition(Proposition.__add__, not_p, q)
                rearranged = CompoundProposition(Proposition.__add__, not_p_or_q, p_and_not_q)
                for _ in range(25):
                    samples.append((rearranged, t_comp, 1, 'distributivity'))

    # CRITICAL: Modus Ponens proof path
    # ((p → q) ^ p) → q = T
    # Step by step:
    # 1. ~((p → q) ^ p) v q  (implication_elimination)
    # 2. (~(p → q) v ~p) v q  (de_morgan)
    # 3. ((~~p ^ ~q) v ~p) v q  (de_morgan/implication_elimination on ~(p → q))
    # 4. ((p ^ ~q) v ~p) v q  (double_negation) <- CRITICAL: do this before distributivity!
    # 5. (~q v ~p) v q  (distributivity: (p ^ ~q) v ~p = (p v ~p) ^ (~q v ~p) = T ^ (~q v ~p))
    # 6. ~p v (~q v q) = ~p v T = T
    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)
        not_not_p = CompoundProposition(Proposition.__invert__, not_p)
        t_comp = _make_compound(TRUE)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)

                # Modus Ponens: ((p → q) ^ p) → q
                impl_pq = CompoundProposition(Proposition.__rshift__, p, q)
                impl_and_p = CompoundProposition(Proposition.__mul__, impl_pq, p)
                modus_ponens = CompoundProposition(Proposition.__rshift__, impl_and_p, q)

                # After first implication_elimination: ~((p → q) ^ p) v q
                neg_impl_and_p = CompoundProposition(Proposition.__invert__, impl_and_p)
                step1 = CompoundProposition(Proposition.__add__, neg_impl_and_p, q)

                # After de_morgan on ~((p → q) ^ p): (~(p → q) v ~p) v q
                neg_impl_pq = CompoundProposition(Proposition.__invert__, impl_pq)
                neg_impl_or_neg_p = CompoundProposition(Proposition.__add__, neg_impl_pq, not_p)
                step2 = CompoundProposition(Proposition.__add__, neg_impl_or_neg_p, q)

                # Train: step1 should use de_morgan
                for _ in range(30):
                    samples.append((step1, t_comp, 1, 'de_morgan'))
                    samples.append((step1, step2, 1, 'de_morgan'))

                # ~(p → q) = ~(~p v q)
                not_p_or_q = CompoundProposition(Proposition.__add__, not_p, q)
                neg_not_p_or_q = CompoundProposition(Proposition.__invert__, not_p_or_q)

                # After de_morgan on ~(~p v q): ~~p ^ ~q
                not_not_p_and_not_q = CompoundProposition(Proposition.__mul__, not_not_p, not_q)

                # After double_negation: p ^ ~q
                p_and_not_q = CompoundProposition(Proposition.__mul__, p, not_q)

                # Step 3: ((~~p ^ ~q) v ~p) v q
                step3 = CompoundProposition(Proposition.__add__,
                    CompoundProposition(Proposition.__add__, not_not_p_and_not_q, not_p), q)

                # Step 4: ((p ^ ~q) v ~p) v q  <- after double_negation
                step4 = CompoundProposition(Proposition.__add__,
                    CompoundProposition(Proposition.__add__, p_and_not_q, not_p), q)

                # CRITICAL: At step 3, apply double_negation first, NOT distributivity!
                for _ in range(40):
                    samples.append((step3, t_comp, 1, 'double_negation'))
                    samples.append((step3, step4, 1, 'double_negation'))
                    samples.append((not_not_p_and_not_q, p_and_not_q, 1, 'double_negation'))

                # After step 4: ((p ^ ~q) v ~p) v q
                # Now distributivity makes sense: (p ^ ~q) v ~p = (~q v ~p)
                not_q_or_not_p = CompoundProposition(Proposition.__add__, not_q, not_p)
                step5 = CompoundProposition(Proposition.__add__, not_q_or_not_p, q)

                for _ in range(30):
                    samples.append((step4, t_comp, 1, 'distributivity'))
                    samples.append((step4, step5, 1, 'distributivity'))

                # step5: (~q v ~p) v q = ~p v (~q v q) = ~p v T = T
                not_p_or_t = CompoundProposition(Proposition.__add__, not_p, TRUE)
                for _ in range(25):
                    samples.append((step5, t_comp, 1, 'complement'))
                    samples.append((not_p_or_t, t_comp, 1, 'domination'))

                # Also train intermediate steps
                for _ in range(25):
                    samples.append((neg_impl_pq, p_and_not_q, 1, 'implication_elimination'))
                    samples.append((neg_not_p_or_q, not_not_p_and_not_q, 1, 'de_morgan'))
                    samples.append((neg_not_p_or_q, p_and_not_q, 1, 'de_morgan'))
                    samples.append((step2, t_comp, 1, 'implication_elimination'))

                # CRITICAL: After implication_elimination, we get ~(~p v q) inside
                # This is step 2: (((¬((¬p) v q)) v (¬p)) v q)
                # The inner ~(~p v q) should trigger de_morgan to get (~~p ^ ~q)
                step2_actual = CompoundProposition(Proposition.__add__,
                    CompoundProposition(Proposition.__add__, neg_not_p_or_q, not_p), q)
                step2_after_dm = CompoundProposition(Proposition.__add__,
                    CompoundProposition(Proposition.__add__, not_not_p_and_not_q, not_p), q)

                for _ in range(40):
                    samples.append((step2_actual, t_comp, 1, 'de_morgan'))
                    samples.append((step2_actual, step2_after_dm, 1, 'de_morgan'))

                # CRITICAL: Final step patterns
                # ((~p v ~q) v q) = (~p v (~q v q)) = ~p v T = T
                # This needs complement on (~q v q)
                not_p_or_not_q = CompoundProposition(Proposition.__add__, not_p, not_q)
                final_form = CompoundProposition(Proposition.__add__, not_p_or_not_q, q)
                # Also with different arrangements
                not_q_or_q = CompoundProposition(Proposition.__add__, not_q, q)
                not_p_or_not_q_or_q = CompoundProposition(Proposition.__add__, not_p, not_q_or_q)

                for _ in range(40):
                    samples.append((final_form, t_comp, 1, 'complement'))
                    samples.append((not_p_or_not_q_or_q, t_comp, 1, 'complement'))

                # (q v (~p v ~q)) - same thing, different order
                q_or_rest = CompoundProposition(Proposition.__add__, q, not_p_or_not_q)
                for _ in range(40):
                    samples.append((q_or_rest, t_comp, 1, 'complement'))

                # (~q v ~p) v q - another arrangement
                not_q_or_not_p = CompoundProposition(Proposition.__add__, not_q, not_p)
                alt_form = CompoundProposition(Proposition.__add__, not_q_or_not_p, q)
                for _ in range(40):
                    samples.append((alt_form, t_comp, 1, 'complement'))

                # q v (~q v ~p) - yet another
                q_or_not_q_or_not_p = CompoundProposition(Proposition.__add__, q,
                    CompoundProposition(Proposition.__add__, not_q, not_p))
                for _ in range(40):
                    samples.append((q_or_not_q_or_not_p, t_comp, 1, 'complement'))

    # CRITICAL: Associativity samples to expose complement patterns
    # ((~p v ~q) v q) -> (~p v (~q v q)) -> ~p v T -> T
    # This is the key transformation to complete Modus Ponens proof
    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)
        t_comp = _make_compound(TRUE)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)

                # ((~p v ~q) v q) - left-associative, needs to become (~p v (~q v q))
                not_p_or_not_q = CompoundProposition(Proposition.__add__, not_p, not_q)
                left_assoc = CompoundProposition(Proposition.__add__, not_p_or_not_q, q)

                # (~p v (~q v q)) - right-associative, complement can be applied
                not_q_or_q = CompoundProposition(Proposition.__add__, not_q, q)
                right_assoc = CompoundProposition(Proposition.__add__, not_p, not_q_or_q)

                # Train: use associativity to expose complement
                for _ in range(40):
                    samples.append((left_assoc, t_comp, 1, 'associativity'))
                    samples.append((left_assoc, right_assoc, 1, 'associativity'))

                # After associativity: (~p v (~q v q)) -> use complement
                for _ in range(30):
                    samples.append((right_assoc, t_comp, 1, 'complement'))

                # Also ((~q v ~p) v q) -> (~q v (~p v q)) - same pattern different order
                not_q_or_not_p = CompoundProposition(Proposition.__add__, not_q, not_p)
                left_assoc2 = CompoundProposition(Proposition.__add__, not_q_or_not_p, q)
                not_p_or_q = CompoundProposition(Proposition.__add__, not_p, q)
                right_assoc2 = CompoundProposition(Proposition.__add__, not_q, not_p_or_q)

                for _ in range(40):
                    samples.append((left_assoc2, t_comp, 1, 'associativity'))

                # (q v (~p v ~q)) - already right-associative but ~q is on right
                # Use commutativity inside: (~p v ~q) -> (~q v ~p), then associativity
                q_or_rest = CompoundProposition(Proposition.__add__, q, not_p_or_not_q)
                for _ in range(30):
                    samples.append((q_or_rest, t_comp, 1, 'commutativity'))

                # AND versions: ((p ^ q) ^ r) -> (p ^ (q ^ r))
                for name3, r in props.items():
                    if name3 not in (name1, name2):
                        # ((p ^ q) ^ r)
                        p_and_q = CompoundProposition(Proposition.__mul__, p, q)
                        left_and = CompoundProposition(Proposition.__mul__, p_and_q, r)
                        # (p ^ (q ^ r))
                        q_and_r = CompoundProposition(Proposition.__mul__, q, r)
                        right_and = CompoundProposition(Proposition.__mul__, p, q_and_r)

                        for _ in range(15):
                            samples.append((left_and, right_and, 1, 'associativity'))
                            samples.append((right_and, left_and, 2, 'associativity'))

                        # ((p v q) v r)
                        p_or_q = CompoundProposition(Proposition.__add__, p, q)
                        left_or = CompoundProposition(Proposition.__add__, p_or_q, r)
                        # (p v (q v r))
                        q_or_r = CompoundProposition(Proposition.__add__, q, r)
                        right_or = CompoundProposition(Proposition.__add__, p, q_or_r)

                        for _ in range(15):
                            samples.append((left_or, right_or, 1, 'associativity'))
                            samples.append((right_or, left_or, 2, 'associativity'))

    return samples


def generate_multi_step_simplification_proofs():
    """
    Generate samples from multi-step proofs that SIMPLIFY.
    These teach the NN the path to simpler forms.
    """
    props = _get_propositions()
    p, q, r = props['p'], props['q'], props['r']
    samples = []

    # Proof 1: ~(~p ^ ~q) = p v q
    # This is a classic: De Morgan then double negation
    not_p = CompoundProposition(Proposition.__invert__, p)
    not_q = CompoundProposition(Proposition.__invert__, q)
    not_p_and_not_q = CompoundProposition(Proposition.__mul__, not_p, not_q)
    start1 = CompoundProposition(Proposition.__invert__, not_p_and_not_q)

    # After De Morgan: ~~p v ~~q
    not_not_p = CompoundProposition(Proposition.__invert__, not_p)
    not_not_q = CompoundProposition(Proposition.__invert__, not_q)
    step1 = CompoundProposition(Proposition.__add__, not_not_p, not_not_q)

    # After first double_negation: p v ~~q
    step2 = CompoundProposition(Proposition.__add__, p, not_not_q)

    # Final: p v q
    end1 = CompoundProposition(Proposition.__add__, p, q)

    # Each step should lead towards simplification
    for _ in range(15):
        samples.append((start1, end1, 1, 'de_morgan'))
        samples.append((step1, end1, 1, 'double_negation'))
        samples.append((step2, end1, 1, 'double_negation'))

    # Proof 2: ~~p ^ ~~q = p ^ q
    start2 = CompoundProposition(Proposition.__mul__, not_not_p, not_not_q)
    step2a = CompoundProposition(Proposition.__mul__, p, not_not_q)
    end2 = CompoundProposition(Proposition.__mul__, p, q)

    for _ in range(15):
        samples.append((start2, end2, 1, 'double_negation'))
        samples.append((step2a, end2, 1, 'double_negation'))

    # Proof 3: p ^ (p v q) = p (absorption directly!)
    p_or_q = CompoundProposition(Proposition.__add__, p, q)
    start3 = CompoundProposition(Proposition.__mul__, p, p_or_q)
    p_comp = _make_compound(p)

    for _ in range(20):
        samples.append((start3, p_comp, 1, 'absorption'))

    # Proof 4: (p ^ p) v q = p v q then potentially more
    p_and_p = CompoundProposition(Proposition.__mul__, p, p)
    start4 = CompoundProposition(Proposition.__add__, p_and_p, q)
    end4 = CompoundProposition(Proposition.__add__, p, q)

    for _ in range(15):
        samples.append((start4, end4, 1, 'idempotence'))

    # Proof 5: ~~(p ^ q) = p ^ q
    p_and_q = CompoundProposition(Proposition.__mul__, p, q)
    not_p_and_q = CompoundProposition(Proposition.__invert__, p_and_q)
    not_not_p_and_q = CompoundProposition(Proposition.__invert__, not_p_and_q)

    for _ in range(15):
        samples.append((not_not_p_and_q, p_and_q, 1, 'double_negation'))

    return samples


def generate_factoring_samples():
    """
    Generate factoring (reverse distributivity) samples.
    This is a KEY simplification operation.

    (p ^ q) v (p ^ r) -> p ^ (q v r)
    (p v q) ^ (p v r) -> p v (q ^ r)

    CRITICAL: Also generates complement factoring patterns like:
    (p ^ q) v (p ^ ~q) -> p ^ (q v ~q) -> p ^ T -> p
    """
    props = _get_propositions()
    samples = []

    for name1, p in props.items():
        for name2, q in props.items():
            for name3, r in props.items():
                if len({name1, name2, name3}) == 3:  # All different
                    # (p ^ q) v (p ^ r) -> p ^ (q v r)
                    p_and_q = CompoundProposition(Proposition.__mul__, p, q)
                    p_and_r = CompoundProposition(Proposition.__mul__, p, r)
                    expanded_or = CompoundProposition(Proposition.__add__, p_and_q, p_and_r)

                    q_or_r = CompoundProposition(Proposition.__add__, q, r)
                    factored_and = CompoundProposition(Proposition.__mul__, p, q_or_r)

                    # MANY samples - factoring simplifies!
                    for _ in range(15):
                        samples.append((expanded_or, factored_and, 1, 'factoring'))
                        samples.append((factored_and, expanded_or, 2, 'factoring'))

                    # (p v q) ^ (p v r) -> p v (q ^ r)
                    p_or_q = CompoundProposition(Proposition.__add__, p, q)
                    p_or_r = CompoundProposition(Proposition.__add__, p, r)
                    expanded_and = CompoundProposition(Proposition.__mul__, p_or_q, p_or_r)

                    q_and_r = CompoundProposition(Proposition.__mul__, q, r)
                    factored_or = CompoundProposition(Proposition.__add__, p, q_and_r)

                    for _ in range(15):
                        samples.append((expanded_and, factored_or, 1, 'factoring'))
                        samples.append((factored_or, expanded_and, 2, 'factoring'))

                    # Also with different positions of common factor
                    # (q ^ p) v (r ^ p) -> p ^ (q v r)
                    q_and_p = CompoundProposition(Proposition.__mul__, q, p)
                    r_and_p = CompoundProposition(Proposition.__mul__, r, p)
                    expanded_or2 = CompoundProposition(Proposition.__add__, q_and_p, r_and_p)

                    for _ in range(10):
                        samples.append((expanded_or2, factored_and, 1, 'factoring'))

    # CRITICAL: Complement factoring patterns - these are the most important!
    # (p ^ q) v (p ^ ~q) -> p ^ (q v ~q) -> p ^ T -> p
    # These patterns lead to complete simplification!
    for name1, p in props.items():
        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)
                p_comp = _make_compound(p)

                # (p ^ q) v (p ^ ~q) -> p (via factoring -> complement -> identity)
                p_and_q = CompoundProposition(Proposition.__mul__, p, q)
                p_and_not_q = CompoundProposition(Proposition.__mul__, p, not_q)
                complement_pattern_or = CompoundProposition(Proposition.__add__, p_and_q, p_and_not_q)

                # Factored form: p ^ (q v ~q)
                q_or_not_q = CompoundProposition(Proposition.__add__, q, not_q)
                factored_complement = CompoundProposition(Proposition.__mul__, p, q_or_not_q)

                # After complement: p ^ T
                p_and_t = CompoundProposition(Proposition.__mul__, p, TRUE)

                # MANY samples for this critical pattern
                for _ in range(30):
                    # First step: factoring
                    samples.append((complement_pattern_or, p_comp, 1, 'factoring'))
                    samples.append((p_comp, complement_pattern_or, 2, 'factoring'))
                    # Also train on intermediate steps
                    samples.append((complement_pattern_or, factored_complement, 1, 'factoring'))
                    samples.append((factored_complement, p_and_t, 1, 'complement'))
                    samples.append((p_and_t, p_comp, 1, 'identity'))

                # Reversed order: (p ^ ~q) v (p ^ q)
                complement_pattern_or_rev = CompoundProposition(Proposition.__add__, p_and_not_q, p_and_q)
                for _ in range(20):
                    samples.append((complement_pattern_or_rev, p_comp, 1, 'factoring'))
                    samples.append((complement_pattern_or_rev, factored_complement, 1, 'factoring'))

                # (p v q) ^ (p v ~q) -> p v (q ^ ~q) -> p v F -> p
                p_or_q = CompoundProposition(Proposition.__add__, p, q)
                p_or_not_q = CompoundProposition(Proposition.__add__, p, not_q)
                complement_pattern_and = CompoundProposition(Proposition.__mul__, p_or_q, p_or_not_q)

                # Factored form: p v (q ^ ~q)
                q_and_not_q = CompoundProposition(Proposition.__mul__, q, not_q)
                factored_complement_and = CompoundProposition(Proposition.__add__, p, q_and_not_q)

                # After complement: p v F
                p_or_f = CompoundProposition(Proposition.__add__, p, FALSE)

                for _ in range(30):
                    samples.append((complement_pattern_and, p_comp, 1, 'factoring'))
                    samples.append((p_comp, complement_pattern_and, 2, 'factoring'))
                    samples.append((complement_pattern_and, factored_complement_and, 1, 'factoring'))
                    samples.append((factored_complement_and, p_or_f, 1, 'complement'))
                    samples.append((p_or_f, p_comp, 1, 'identity'))

                # Also with common factor on right side
                # (q ^ p) v (~q ^ p) -> p
                q_and_p = CompoundProposition(Proposition.__mul__, q, p)
                not_q_and_p = CompoundProposition(Proposition.__mul__, not_q, p)
                complement_pattern_right = CompoundProposition(Proposition.__add__, q_and_p, not_q_and_p)

                for _ in range(20):
                    samples.append((complement_pattern_right, p_comp, 1, 'factoring'))

    return samples


def generate_nested_complement_samples():
    """
    Generate samples for complement patterns NESTED inside larger expressions.

    CRITICAL: The NN must learn to apply complement when (p v ~p) or (p ^ ~p)
    appears ANYWHERE in the expression, not just at the root.

    These patterns are essential for completing proofs like Modus Ponens where
    the complement pattern only appears after several transformations.
    """
    props = _get_propositions()
    samples = []

    t_comp = _make_compound(TRUE)
    f_comp = _make_compound(FALSE)

    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)
        p_comp = _make_compound(p)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)
                q_comp = _make_compound(q)

                # Pattern 1: ((p v ~p) ^ X) v Y -> should apply complement to get (T ^ X) v Y
                p_or_not_p = CompoundProposition(Proposition.__add__, p, not_p)
                inner1 = CompoundProposition(Proposition.__mul__, p_or_not_p, q)  # (p v ~p) ^ q
                outer1 = CompoundProposition(Proposition.__add__, inner1, not_q)  # ((p v ~p) ^ q) v ~q
                # After complement: (T ^ q) v ~q
                t_and_q = CompoundProposition(Proposition.__mul__, TRUE, q)
                step1 = CompoundProposition(Proposition.__add__, t_and_q, not_q)

                for _ in range(40):
                    samples.append((outer1, t_comp, 1, 'complement'))
                    samples.append((outer1, step1, 1, 'complement'))
                    # After identity: q v ~q = T
                    q_or_not_q = CompoundProposition(Proposition.__add__, q, not_q)
                    samples.append((step1, q_or_not_q, 1, 'identity'))
                    samples.append((q_or_not_q, t_comp, 1, 'complement'))

                # Pattern 2: (X ^ (p v ~p)) v Y -> complement on inner
                inner2 = CompoundProposition(Proposition.__mul__, q, p_or_not_p)  # q ^ (p v ~p)
                outer2 = CompoundProposition(Proposition.__add__, inner2, not_q)

                for _ in range(40):
                    samples.append((outer2, t_comp, 1, 'complement'))

                # Pattern 3: X v ((p v ~p) ^ Y) -> complement on inner
                inner3 = CompoundProposition(Proposition.__mul__, p_or_not_p, not_q)  # (p v ~p) ^ ~q
                outer3 = CompoundProposition(Proposition.__add__, q, inner3)  # q v ((p v ~p) ^ ~q)

                for _ in range(40):
                    samples.append((outer3, t_comp, 1, 'complement'))

                # Pattern 4: After distributivity result like ((~p v p) ^ (~p v ~q)) v q
                # This is EXACTLY what appears in Modus Ponens proof!
                not_p_or_p = CompoundProposition(Proposition.__add__, not_p, p)
                not_p_or_not_q = CompoundProposition(Proposition.__add__, not_p, not_q)
                dist_result = CompoundProposition(Proposition.__mul__, not_p_or_p, not_p_or_not_q)
                full_expr = CompoundProposition(Proposition.__add__, dist_result, q)
                # After complement on (not_p_or_p): (T ^ (~p v ~q)) v q
                t_and_rest = CompoundProposition(Proposition.__mul__, TRUE, not_p_or_not_q)
                after_comp = CompoundProposition(Proposition.__add__, t_and_rest, q)
                # After identity: (~p v ~q) v q
                rest_or_q = CompoundProposition(Proposition.__add__, not_p_or_not_q, q)

                for _ in range(50):
                    samples.append((full_expr, t_comp, 1, 'complement'))
                    samples.append((full_expr, after_comp, 1, 'complement'))
                    samples.append((after_comp, rest_or_q, 1, 'identity'))
                    samples.append((after_comp, t_comp, 1, 'identity'))

                # Same with different order: ((p v ~p) ^ (~p v ~q)) v q
                p_or_not_p_inner = CompoundProposition(Proposition.__mul__, p_or_not_p, not_p_or_not_q)
                full_expr2 = CompoundProposition(Proposition.__add__, p_or_not_p_inner, q)

                for _ in range(50):
                    samples.append((full_expr2, t_comp, 1, 'complement'))

                # Pattern 5: (p ^ ~p) nested - contradiction
                p_and_not_p = CompoundProposition(Proposition.__mul__, p, not_p)
                # (p ^ ~p) v X = F v X = X
                contr_or_q = CompoundProposition(Proposition.__add__, p_and_not_p, q)

                for _ in range(40):
                    samples.append((contr_or_q, q_comp, 1, 'complement'))

                # X v (p ^ ~p) = X v F = X
                q_or_contr = CompoundProposition(Proposition.__add__, q, p_and_not_p)
                for _ in range(40):
                    samples.append((q_or_contr, q_comp, 1, 'complement'))

                # (p ^ ~p) ^ X = F ^ X = F
                contr_and_q = CompoundProposition(Proposition.__mul__, p_and_not_p, q)
                for _ in range(40):
                    samples.append((contr_and_q, f_comp, 1, 'complement'))

                # X ^ (p ^ ~p) = X ^ F = F
                q_and_contr = CompoundProposition(Proposition.__mul__, q, p_and_not_p)
                for _ in range(40):
                    samples.append((q_and_contr, f_comp, 1, 'complement'))

                # Pattern 6: X v (p v ~p) = X v T = T (domination after complement)
                q_or_taut = CompoundProposition(Proposition.__add__, q, p_or_not_p)
                for _ in range(40):
                    samples.append((q_or_taut, t_comp, 1, 'complement'))

                # (p v ~p) v X = T v X = T
                taut_or_q = CompoundProposition(Proposition.__add__, p_or_not_p, q)
                for _ in range(40):
                    samples.append((taut_or_q, t_comp, 1, 'complement'))

                # Pattern 7: More complex - ((~p v p) ^ X) where result is T
                # This is what the Modus Ponens proof reaches
                for name3, r in props.items():
                    if name3 not in (name1, name2):
                        not_r = CompoundProposition(Proposition.__invert__, r)

                        # ((~p v p) ^ (~q v r)) v q
                        inner_and = CompoundProposition(Proposition.__mul__, not_p_or_p,
                            CompoundProposition(Proposition.__add__, not_q, r))
                        complex1 = CompoundProposition(Proposition.__add__, inner_and, q)

                        for _ in range(30):
                            samples.append((complex1, t_comp, 1, 'complement'))

    return samples


def generate_truth_constant_samples():
    """
    Generate samples involving truth constants T and F.

    Laws:
    - Complement: p v ~p = T, p ^ ~p = F
    - Identity: p v F = p, p ^ T = p
    - Domination: p v T = T, p ^ F = F
    - Negation: ~T = F, ~F = T
    - Implication: T -> p = p, F -> p = T, p -> T = T, p -> F = ~p
    """
    props = _get_propositions()
    samples = []

    t_comp = _make_compound(TRUE)
    f_comp = _make_compound(FALSE)

    for name, p in props.items():
        p_comp = _make_compound(p)
        not_p = CompoundProposition(Proposition.__invert__, p)

        # Complement: p v ~p = T (MANY samples - key simplification)
        p_or_not_p = CompoundProposition(Proposition.__add__, p, not_p)
        for _ in range(25):
            samples.append((p_or_not_p, t_comp, 1, 'complement'))
            samples.append((t_comp, p_or_not_p, 2, 'complement'))

        # Complement: ~p v p = T (reversed)
        not_p_or_p = CompoundProposition(Proposition.__add__, not_p, p)
        for _ in range(25):
            samples.append((not_p_or_p, t_comp, 1, 'complement'))

        # Complement: p ^ ~p = F
        p_and_not_p = CompoundProposition(Proposition.__mul__, p, not_p)
        for _ in range(25):
            samples.append((p_and_not_p, f_comp, 1, 'complement'))
            samples.append((f_comp, p_and_not_p, 2, 'complement'))

        # Complement: ~p ^ p = F (reversed)
        not_p_and_p = CompoundProposition(Proposition.__mul__, not_p, p)
        for _ in range(25):
            samples.append((not_p_and_p, f_comp, 1, 'complement'))

        # Identity: p v F = p
        p_or_f = CompoundProposition(Proposition.__add__, p, FALSE)
        for _ in range(20):
            samples.append((p_or_f, p_comp, 1, 'identity'))
            samples.append((p_comp, p_or_f, 2, 'identity'))

        # Identity: F v p = p
        f_or_p = CompoundProposition(Proposition.__add__, FALSE, p)
        for _ in range(20):
            samples.append((f_or_p, p_comp, 1, 'identity'))

        # Identity: p ^ T = p
        p_and_t = CompoundProposition(Proposition.__mul__, p, TRUE)
        for _ in range(20):
            samples.append((p_and_t, p_comp, 1, 'identity'))
            samples.append((p_comp, p_and_t, 2, 'identity'))

        # Identity: T ^ p = p
        t_and_p = CompoundProposition(Proposition.__mul__, TRUE, p)
        for _ in range(20):
            samples.append((t_and_p, p_comp, 1, 'identity'))

        # Domination: p v T = T
        p_or_t = CompoundProposition(Proposition.__add__, p, TRUE)
        for _ in range(20):
            samples.append((p_or_t, t_comp, 1, 'domination'))
            samples.append((t_comp, p_or_t, 2, 'domination'))

        # Domination: T v p = T
        t_or_p = CompoundProposition(Proposition.__add__, TRUE, p)
        for _ in range(20):
            samples.append((t_or_p, t_comp, 1, 'domination'))

        # Domination: p ^ F = F
        p_and_f = CompoundProposition(Proposition.__mul__, p, FALSE)
        for _ in range(20):
            samples.append((p_and_f, f_comp, 1, 'domination'))
            samples.append((f_comp, p_and_f, 2, 'domination'))

        # Domination: F ^ p = F
        f_and_p = CompoundProposition(Proposition.__mul__, FALSE, p)
        for _ in range(20):
            samples.append((f_and_p, f_comp, 1, 'domination'))

        # Implication constants
        # T -> p = p
        t_impl_p = CompoundProposition(Proposition.__rshift__, TRUE, p)
        for _ in range(15):
            samples.append((t_impl_p, p_comp, 1, 'implication_constant'))
            samples.append((p_comp, t_impl_p, 2, 'implication_constant'))

        # F -> p = T
        f_impl_p = CompoundProposition(Proposition.__rshift__, FALSE, p)
        for _ in range(15):
            samples.append((f_impl_p, t_comp, 1, 'implication_constant'))

        # p -> T = T
        p_impl_t = CompoundProposition(Proposition.__rshift__, p, TRUE)
        for _ in range(15):
            samples.append((p_impl_t, t_comp, 1, 'implication_constant'))

        # p -> F = ~p
        p_impl_f = CompoundProposition(Proposition.__rshift__, p, FALSE)
        not_p_comp = CompoundProposition(Proposition.__invert__, p)
        for _ in range(15):
            samples.append((p_impl_f, not_p_comp, 1, 'implication_constant'))

    # Negation of constants
    # ~T = F
    not_t = CompoundProposition(Proposition.__invert__, TRUE)
    for _ in range(15):
        samples.append((not_t, f_comp, 1, 'negation_constant'))
        samples.append((f_comp, not_t, 2, 'negation_constant'))

    # ~F = T
    not_f = CompoundProposition(Proposition.__invert__, FALSE)
    for _ in range(15):
        samples.append((not_f, t_comp, 1, 'negation_constant'))
        samples.append((t_comp, not_f, 2, 'negation_constant'))

    # ~~T = T
    not_not_t = CompoundProposition(Proposition.__invert__, not_t)
    for _ in range(10):
        samples.append((not_not_t, t_comp, 1, 'double_negation'))

    # ~~F = F
    not_not_f = CompoundProposition(Proposition.__invert__, not_f)
    for _ in range(10):
        samples.append((not_not_f, f_comp, 1, 'double_negation'))

    return samples


def generate_associativity_samples():
    """
    Generate comprehensive associativity samples.

    Associativity: (a op b) op c = a op (b op c) for AND and OR

    CRITICAL: Teach the NN WHEN to apply associativity:
    1. To expose complement patterns: ((~p v ~q) v q) -> (~p v (~q v q)) -> ~p v T
    2. To expose identity patterns: ((p v F) v q) -> (p v (F v q))
    3. To expose domination patterns: ((p v T) v q) -> already T
    4. To group related terms together

    The key insight is that associativity is useful when it groups complementary
    or simplifiable terms together.
    """
    props = _get_propositions()
    samples = []

    t_comp = _make_compound(TRUE)
    f_comp = _make_compound(FALSE)

    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)
        p_comp = _make_compound(p)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)
                q_comp = _make_compound(q)

                # ===========================================
                # PATTERN 1: Expose complement via associativity
                # ===========================================

                # ((~p v ~q) v q) -> (~p v (~q v q)) -> ~p v T -> T
                not_p_or_not_q = CompoundProposition(Proposition.__add__, not_p, not_q)
                left_assoc1 = CompoundProposition(Proposition.__add__, not_p_or_not_q, q)
                not_q_or_q = CompoundProposition(Proposition.__add__, not_q, q)
                right_assoc1 = CompoundProposition(Proposition.__add__, not_p, not_q_or_q)

                for _ in range(50):
                    samples.append((left_assoc1, t_comp, 1, 'associativity'))
                    samples.append((left_assoc1, right_assoc1, 1, 'associativity'))

                # ((~q v ~p) v p) -> (~q v (~p v p)) -> ~q v T -> T
                not_q_or_not_p = CompoundProposition(Proposition.__add__, not_q, not_p)
                left_assoc2 = CompoundProposition(Proposition.__add__, not_q_or_not_p, p)
                not_p_or_p = CompoundProposition(Proposition.__add__, not_p, p)
                right_assoc2 = CompoundProposition(Proposition.__add__, not_q, not_p_or_p)

                for _ in range(50):
                    samples.append((left_assoc2, t_comp, 1, 'associativity'))
                    samples.append((left_assoc2, right_assoc2, 1, 'associativity'))

                # (p v (~p v q)) -> already right-assoc, has complement
                p_or_rest = CompoundProposition(Proposition.__add__, p,
                    CompoundProposition(Proposition.__add__, not_p, q))
                for _ in range(30):
                    samples.append((p_or_rest, t_comp, 1, 'complement'))

                # ((p v ~p) v q) -> T v q -> T
                p_or_not_p = CompoundProposition(Proposition.__add__, p, not_p)
                taut_or_q = CompoundProposition(Proposition.__add__, p_or_not_p, q)
                for _ in range(40):
                    samples.append((taut_or_q, t_comp, 1, 'complement'))

                # AND version: ((p ^ ~p) ^ q) -> F ^ q -> F
                p_and_not_p = CompoundProposition(Proposition.__mul__, p, not_p)
                contr_and_q = CompoundProposition(Proposition.__mul__, p_and_not_p, q)
                for _ in range(40):
                    samples.append((contr_and_q, f_comp, 1, 'complement'))

                # ===========================================
                # PATTERN 2: Expose complement when it's not adjacent
                # ===========================================

                # (q v (~q v p)) - complement is inside, already simplifiable
                q_or_rest = CompoundProposition(Proposition.__add__, q,
                    CompoundProposition(Proposition.__add__, not_q, p))
                for _ in range(30):
                    samples.append((q_or_rest, t_comp, 1, 'complement'))

                # ((q v ~q) v p) -> T v p -> T
                q_or_not_q = CompoundProposition(Proposition.__add__, q, not_q)
                taut_or_p = CompoundProposition(Proposition.__add__, q_or_not_q, p)
                for _ in range(30):
                    samples.append((taut_or_p, t_comp, 1, 'complement'))

                # ===========================================
                # PATTERN 3: Three-variable associativity for complement
                # ===========================================

                for name3, r in props.items():
                    if name3 not in (name1, name2):
                        not_r = CompoundProposition(Proposition.__invert__, r)

                        # (((~p v q) v ~q) v r) - needs associativity to expose (q v ~q)
                        not_p_or_q = CompoundProposition(Proposition.__add__, not_p, q)
                        inner1 = CompoundProposition(Proposition.__add__, not_p_or_q, not_q)
                        outer1 = CompoundProposition(Proposition.__add__, inner1, r)

                        for _ in range(30):
                            samples.append((outer1, t_comp, 1, 'associativity'))

                        # ((p v (q v ~q)) v r) -> (p v T) v r -> T v r -> T
                        q_or_not_q = CompoundProposition(Proposition.__add__, q, not_q)
                        p_or_taut = CompoundProposition(Proposition.__add__, p, q_or_not_q)
                        full1 = CompoundProposition(Proposition.__add__, p_or_taut, r)

                        for _ in range(30):
                            samples.append((full1, t_comp, 1, 'complement'))

                        # ===========================================
                        # PATTERN 4: General associativity (structure change)
                        # ===========================================

                        # OR: ((p v q) v r) <-> (p v (q v r))
                        p_or_q = CompoundProposition(Proposition.__add__, p, q)
                        left_or = CompoundProposition(Proposition.__add__, p_or_q, r)
                        q_or_r = CompoundProposition(Proposition.__add__, q, r)
                        right_or = CompoundProposition(Proposition.__add__, p, q_or_r)

                        for _ in range(20):
                            samples.append((left_or, right_or, 1, 'associativity'))
                            samples.append((right_or, left_or, 2, 'associativity'))

                        # AND: ((p ^ q) ^ r) <-> (p ^ (q ^ r))
                        p_and_q = CompoundProposition(Proposition.__mul__, p, q)
                        left_and = CompoundProposition(Proposition.__mul__, p_and_q, r)
                        q_and_r = CompoundProposition(Proposition.__mul__, q, r)
                        right_and = CompoundProposition(Proposition.__mul__, p, q_and_r)

                        for _ in range(20):
                            samples.append((left_and, right_and, 1, 'associativity'))
                            samples.append((right_and, left_and, 2, 'associativity'))

                        # ===========================================
                        # PATTERN 5: Associativity in proof contexts
                        # ===========================================

                        # After De Morgan + elimination, we often get forms like:
                        # ((~p v ~q) v q) which needs associativity to simplify
                        # This is exactly what happens in Modus Ponens proof!

                        # (~p v (~q v q)) -> ~p v T -> T (after associativity)
                        not_q_or_q = CompoundProposition(Proposition.__add__, not_q, q)
                        after_assoc = CompoundProposition(Proposition.__add__, not_p, not_q_or_q)
                        not_p_or_t = CompoundProposition(Proposition.__add__, not_p, TRUE)

                        for _ in range(40):
                            samples.append((after_assoc, t_comp, 1, 'complement'))
                            samples.append((after_assoc, not_p_or_t, 1, 'complement'))
                            samples.append((not_p_or_t, t_comp, 1, 'domination'))

                        # ((a v b) v ~b) -> (a v (b v ~b)) -> a v T -> T
                        p_or_q = CompoundProposition(Proposition.__add__, p, q)
                        needs_assoc = CompoundProposition(Proposition.__add__, p_or_q, not_q)
                        after = CompoundProposition(Proposition.__add__, p, q_or_not_q)

                        for _ in range(40):
                            samples.append((needs_assoc, t_comp, 1, 'associativity'))
                            samples.append((needs_assoc, after, 1, 'associativity'))

    return samples


def generate_anti_oscillation_samples():
    """
    Generate samples that teach the NN to NOT undo its previous transformation.

    CRITICAL: Prevent oscillation patterns like:
    - implication_elimination followed by implication_introduction (or vice versa)
    - de_morgan followed by de_morgan_reverse (or vice versa)

    After converting p -> q to ~p v q, the next step should NOT convert it back!
    Instead, continue with the proof by working on OTHER parts or applying different transformations.
    """
    props = _get_propositions()
    samples = []

    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)

                for name3, r in props.items():
                    if name3 not in (name1, name2):
                        not_r = CompoundProposition(Proposition.__invert__, r)

                        # Pattern 1: After implication_elimination on one part,
                        # apply implication_elimination on the OTHER part, not introduction back!
                        # (p -> q) ^ (q -> r) after first elim becomes: (~p v q) ^ (q -> r)
                        # Next step should be elim on (q -> r), NOT introduction on (~p v q)!

                        impl_pq = CompoundProposition(Proposition.__rshift__, p, q)
                        impl_qr = CompoundProposition(Proposition.__rshift__, q, r)
                        both_impl = CompoundProposition(Proposition.__mul__, impl_pq, impl_qr)

                        # After first elimination: (~p v q) ^ (q -> r)
                        disj_pq = CompoundProposition(Proposition.__add__, not_p, q)
                        after_first_elim = CompoundProposition(Proposition.__mul__, disj_pq, impl_qr)

                        # Target: (~p v q) ^ (~q v r) - apply elim to second part!
                        disj_qr = CompoundProposition(Proposition.__add__, not_q, r)
                        target = CompoundProposition(Proposition.__mul__, disj_pq, disj_qr)

                        # MANY samples: after first elim, continue with elim on other part
                        for _ in range(50):
                            samples.append((after_first_elim, target, 1, 'implication_elimination'))
                            # Discourage introduction by NOT having samples for it here

                        # Also: (p -> q) ^ (~q v r) -> should apply elim to first part
                        partial_elim = CompoundProposition(Proposition.__mul__, impl_pq, disj_qr)
                        for _ in range(50):
                            samples.append((partial_elim, target, 1, 'implication_elimination'))

                        # Pattern 2: After de_morgan, don't apply de_morgan_reverse!
                        # ~(p ^ q) -> ~p v ~q, then work with the result, don't go back
                        p_and_q = CompoundProposition(Proposition.__mul__, p, q)
                        neg_p_and_q = CompoundProposition(Proposition.__invert__, p_and_q)
                        after_dm = CompoundProposition(Proposition.__add__, not_p, not_q)

                        # After de_morgan, if we have ~p v ~q in a larger context,
                        # apply other transformations, not de_morgan_reverse
                        # Example: (~p v ~q) ^ r - continue with other ops
                        dm_and_r = CompoundProposition(Proposition.__mul__, after_dm, r)
                        for _ in range(30):
                            # Could apply commutativity, but NOT de_morgan_reverse
                            samples.append((dm_and_r, dm_and_r, 1, 'commutativity'))

                        # Pattern 3: In context of proving tautologies with nested implications
                        # (p -> q) ^ (q -> r) should become (~p v q) ^ (~q v r)
                        # and stay that way (both eliminated)
                        for _ in range(40):
                            samples.append((both_impl, target, 1, 'implication_elimination'))

                        # Pattern 4: Single implication in AND context
                        # p ^ (q -> r) -> p ^ (~q v r), NOT back to implication
                        p_and_impl = CompoundProposition(Proposition.__mul__, p, impl_qr)
                        p_and_disj = CompoundProposition(Proposition.__mul__, p, disj_qr)
                        for _ in range(40):
                            samples.append((p_and_impl, p_and_disj, 1, 'implication_elimination'))
                            # After elimination, keep it as disjunction
                            samples.append((p_and_disj, p_and_disj, 1, 'commutativity'))

                        # Pattern 5: Implication in OR context
                        # p v (q -> r) -> p v (~q v r)
                        p_or_impl = CompoundProposition(Proposition.__add__, p, impl_qr)
                        p_or_disj = CompoundProposition(Proposition.__add__, p, disj_qr)
                        for _ in range(40):
                            samples.append((p_or_impl, p_or_disj, 1, 'implication_elimination'))

    return samples


def generate_prefer_simplification_samples():
    """
    Generate samples that explicitly teach: when simplification is possible, do it.
    Even if other operations are applicable, prefer simplification.
    """
    props = _get_propositions()
    p, q = props['p'], props['q']
    samples = []

    # Scenario 1: ~~p vs p
    # Both commutativity (not applicable) and double_negation work
    # Always choose double_negation
    not_p = CompoundProposition(Proposition.__invert__, p)
    not_not_p = CompoundProposition(Proposition.__invert__, not_p)
    p_comp = _make_compound(p)

    for _ in range(30):
        samples.append((not_not_p, p_comp, 1, 'double_negation'))

    # Scenario 2: p ^ p vs p
    # Idempotence simplifies
    p_and_p = CompoundProposition(Proposition.__mul__, p, p)
    for _ in range(30):
        samples.append((p_and_p, p_comp, 1, 'idempotence'))

    # Scenario 3: p ^ (p v q) vs p
    # Absorption is the best choice
    p_or_q = CompoundProposition(Proposition.__add__, p, q)
    absorption = CompoundProposition(Proposition.__mul__, p, p_or_q)
    for _ in range(30):
        samples.append((absorption, p_comp, 1, 'absorption'))

    # Scenario 4: When we have ~~p ^ q vs p ^ q
    # Should apply double_negation, not commutativity
    complex_and = CompoundProposition(Proposition.__mul__, not_not_p, q)
    simple_and = CompoundProposition(Proposition.__mul__, p, q)
    for _ in range(20):
        samples.append((complex_and, simple_and, 1, 'double_negation'))

    # Scenario 5: ~(p ^ q) vs ~p v ~q
    # De Morgan forward is good (leads to potential double neg elimination later)
    not_p = CompoundProposition(Proposition.__invert__, p)
    not_q = CompoundProposition(Proposition.__invert__, q)
    p_and_q = CompoundProposition(Proposition.__mul__, p, q)
    negated = CompoundProposition(Proposition.__invert__, p_and_q)
    expanded = CompoundProposition(Proposition.__add__, not_p, not_q)
    for _ in range(15):
        samples.append((negated, expanded, 1, 'de_morgan'))

    return samples


def generate_dataset(num_samples: int = 1000, verbose: bool = False) -> tuple:
    """
    Generate high-quality training dataset with emphasis on simplification.
    """
    all_samples = []

    if verbose:
        print("Generating double negation samples (high priority)...")
    double_neg = generate_double_negation_samples()
    all_samples.extend(double_neg)

    if verbose:
        print("Generating absorption samples (high priority)...")
    absorption = generate_absorption_samples()
    all_samples.extend(absorption)

    if verbose:
        print("Generating idempotence samples (high priority)...")
    idempotence = generate_idempotence_samples()
    all_samples.extend(idempotence)

    if verbose:
        print("Generating De Morgan samples...")
    de_morgan = generate_de_morgan_samples()
    all_samples.extend(de_morgan)

    if verbose:
        print("Generating commutativity samples...")
    commutativity = generate_commutativity_samples()
    all_samples.extend(commutativity)

    if verbose:
        print("Generating implication samples...")
    implication = generate_implication_samples()
    all_samples.extend(implication)

    if verbose:
        print("Generating multi-step simplification proofs...")
    multi_step = generate_multi_step_simplification_proofs()
    all_samples.extend(multi_step)

    if verbose:
        print("Generating associativity samples...")
    associativity = generate_associativity_samples()
    all_samples.extend(associativity)

    if verbose:
        print("Generating anti-oscillation samples...")
    anti_oscillation = generate_anti_oscillation_samples()
    all_samples.extend(anti_oscillation)

    if verbose:
        print("Generating prefer-simplification samples...")
    prefer_simple = generate_prefer_simplification_samples()
    all_samples.extend(prefer_simple)

    if verbose:
        print("Generating factoring samples (reverse distributivity)...")
    factoring = generate_factoring_samples()
    all_samples.extend(factoring)

    if verbose:
        print("Generating truth constant samples...")
    truth_constant = generate_truth_constant_samples()
    all_samples.extend(truth_constant)

    if verbose:
        print("Generating nested complement samples (critical for Modus Ponens)...")
    nested_complement = generate_nested_complement_samples()
    all_samples.extend(nested_complement)

    # Convert to features
    X = []
    y = []

    for prop1, prop2, which_prop, transform in all_samples:
        try:
            prop1 = _make_compound(prop1)
            prop2 = _make_compound(prop2)

            features = extract_pair_features(prop1, prop2)
            label = encode_action(which_prop, transform)

            X.append(features)
            y.append(label)
        except Exception:
            continue

    # Shuffle
    indices = list(range(len(X)))
    random.shuffle(indices)
    X = [X[i] for i in indices]
    y = [y[i] for i in indices]

    # Limit to num_samples
    X = X[:num_samples]
    y = y[:num_samples]

    if verbose:
        print(f"Generated {len(X)} samples")
        from collections import Counter
        dist = Counter(y)
        print("Class distribution:")
        for class_idx, count in sorted(dist.items()):
            which_prop, transform = CLASS_MAPPING[class_idx]
            print(f"  {class_idx}: prop{which_prop} {transform}: {count}")

    return np.array(X), np.array(y)


def balance_dataset(X: np.ndarray, y: np.ndarray) -> tuple:
    """Balance the dataset by oversampling minority classes."""
    from collections import Counter

    class_counts = Counter(y)
    max_count = max(class_counts.values())

    X_balanced = []
    y_balanced = []

    for class_idx in class_counts:
        class_mask = y == class_idx
        class_X = X[class_mask]
        class_y = y[class_mask]

        current_count = len(class_y)
        if current_count < max_count:
            indices = np.random.choice(current_count, max_count - current_count, replace=True)
            X_balanced.extend(class_X)
            X_balanced.extend(class_X[indices])
            y_balanced.extend(class_y)
            y_balanced.extend(class_y[indices])
        else:
            X_balanced.extend(class_X)
            y_balanced.extend(class_y)

    indices = np.random.permutation(len(y_balanced))
    return np.array(X_balanced)[indices], np.array(y_balanced)[indices]


# ============================================================================
# SIMPLIFICATION DATASET GENERATORS (for absurdity proofs)
# ============================================================================

def generate_absurdity_complement_samples():
    """
    Generate samples for direct complement patterns (p ∧ ~p → F).
    These are the CRITICAL patterns for absurdity proofs.
    """
    props = _get_propositions()
    samples = []

    f_comp = _make_compound(FALSE)

    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)

        # Direct complement: p ∧ ~p → F (MANY samples - highest priority)
        p_and_not_p = CompoundProposition(Proposition.__mul__, p, not_p)
        for _ in range(50):
            samples.append((p_and_not_p, 'complement', 'F'))

        # Reversed: ~p ∧ p → F
        not_p_and_p = CompoundProposition(Proposition.__mul__, not_p, p)
        for _ in range(50):
            samples.append((not_p_and_p, 'complement', 'F'))

        # Nested complement: (p ∧ ~p) ∧ q → F ∧ q → F
        for name2, q in props.items():
            if name1 != name2:
                nested1 = CompoundProposition(Proposition.__mul__, p_and_not_p, q)
                for _ in range(30):
                    samples.append((nested1, 'complement', 'F'))

                # q ∧ (p ∧ ~p) → q ∧ F → F
                nested2 = CompoundProposition(Proposition.__mul__, q, p_and_not_p)
                for _ in range(30):
                    samples.append((nested2, 'complement', 'F'))

                # (p ∧ ~p) ∨ q - complement first, then identity
                nested_or = CompoundProposition(Proposition.__add__, p_and_not_p, q)
                for _ in range(25):
                    samples.append((nested_or, 'complement', 'F'))

    return samples


def generate_f_propagation_samples():
    """
    Generate samples for propagating F through expressions.
    p ∧ F → F (domination)
    F ∧ p → F
    These are critical AFTER complement creates F.
    """
    props = _get_propositions()
    samples = []

    f_comp = _make_compound(FALSE)

    for name, p in props.items():
        # p ∧ F → F
        p_and_f = CompoundProposition(Proposition.__mul__, p, FALSE)
        for _ in range(40):
            samples.append((p_and_f, 'domination', 'F'))

        # F ∧ p → F
        f_and_p = CompoundProposition(Proposition.__mul__, FALSE, p)
        for _ in range(40):
            samples.append((f_and_p, 'domination', 'F'))

        # Nested: (F ∧ p) ∧ q → F ∧ q → F
        for name2, q in props.items():
            if name != name2:
                inner = CompoundProposition(Proposition.__mul__, FALSE, p)
                nested = CompoundProposition(Proposition.__mul__, inner, q)
                for _ in range(20):
                    samples.append((nested, 'domination', 'F'))

                # p ∧ (F ∧ q) → p ∧ F → F
                inner2 = CompoundProposition(Proposition.__mul__, FALSE, q)
                nested2 = CompoundProposition(Proposition.__mul__, p, inner2)
                for _ in range(20):
                    samples.append((nested2, 'domination', 'F'))

        # F ∨ p → p (identity, not domination) - important distinction
        f_or_p = CompoundProposition(Proposition.__add__, FALSE, p)
        for _ in range(30):
            samples.append((f_or_p, 'identity', 'F'))

        p_or_f = CompoundProposition(Proposition.__add__, p, FALSE)
        for _ in range(30):
            samples.append((p_or_f, 'identity', 'F'))

    return samples


def generate_expose_complement_samples():
    """
    Generate samples where distributivity/associativity exposes complement.
    These are the KEY patterns that make absurdity proofs work.

    Pattern: p ∧ (~p ∨ q) → (p ∧ ~p) ∨ (p ∧ q) → F ∨ (p ∧ q) → p ∧ q
    """
    props = _get_propositions()
    samples = []

    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)

                # Pattern 1: p ∧ (~p ∨ q) → use distributivity
                # After dist: (p ∧ ~p) ∨ (p ∧ q) → complement exposes F
                not_p_or_q = CompoundProposition(Proposition.__add__, not_p, q)
                p_and_rest = CompoundProposition(Proposition.__mul__, p, not_p_or_q)
                for _ in range(40):
                    samples.append((p_and_rest, 'distributivity', 'F'))

                # Pattern 2: (~p ∨ q) ∧ p - same, different order
                rest_and_p = CompoundProposition(Proposition.__mul__, not_p_or_q, p)
                for _ in range(40):
                    samples.append((rest_and_p, 'distributivity', 'F'))

                # Pattern 3: p ∧ (q ∨ ~p) - complement on right of inner
                q_or_not_p = CompoundProposition(Proposition.__add__, q, not_p)
                p_and_rest2 = CompoundProposition(Proposition.__mul__, p, q_or_not_p)
                for _ in range(40):
                    samples.append((p_and_rest2, 'distributivity', 'F'))

                # Pattern 4: After distributivity, we get (p ∧ ~p) ∨ X
                # Use complement on the (p ∧ ~p) part
                p_and_not_p = CompoundProposition(Proposition.__mul__, p, not_p)
                p_and_q = CompoundProposition(Proposition.__mul__, p, q)
                after_dist = CompoundProposition(Proposition.__add__, p_and_not_p, p_and_q)
                for _ in range(50):
                    samples.append((after_dist, 'complement', 'F'))

                # Pattern 5: Associativity to expose complement
                # ((p ∧ ~p) ∧ q) - complement directly applicable
                contr_and_q = CompoundProposition(Proposition.__mul__, p_and_not_p, q)
                for _ in range(40):
                    samples.append((contr_and_q, 'complement', 'F'))

                # Pattern 6: Complex nested - (p ∧ q) ∧ ~p
                # Needs commutativity or associativity first
                p_and_q = CompoundProposition(Proposition.__mul__, p, q)
                pq_and_not_p = CompoundProposition(Proposition.__mul__, p_and_q, not_p)
                for _ in range(30):
                    samples.append((pq_and_not_p, 'associativity', 'F'))

                # After associativity: p ∧ (q ∧ ~p) → p ∧ (~p ∧ q) via commutativity
                q_and_not_p = CompoundProposition(Proposition.__mul__, q, not_p)
                p_and_q_not_p = CompoundProposition(Proposition.__mul__, p, q_and_not_p)
                for _ in range(30):
                    samples.append((p_and_q_not_p, 'commutativity', 'F'))

    return samples


def generate_absurdity_demorgan_samples():
    """
    Generate samples where De Morgan helps reach contradiction.
    ~(p ∨ q) ∧ p → (~p ∧ ~q) ∧ p → needs associativity to get ~p ∧ p
    """
    props = _get_propositions()
    samples = []

    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)

                # ~(p ∨ q) → ~p ∧ ~q via De Morgan
                p_or_q = CompoundProposition(Proposition.__add__, p, q)
                neg_p_or_q = CompoundProposition(Proposition.__invert__, p_or_q)
                for _ in range(25):
                    samples.append((neg_p_or_q, 'de_morgan', 'F'))

                # ~(p ∨ q) ∧ p - De Morgan first to expose ~p
                neg_p_or_q_and_p = CompoundProposition(Proposition.__mul__, neg_p_or_q, p)
                for _ in range(35):
                    samples.append((neg_p_or_q_and_p, 'de_morgan', 'F'))

                # After De Morgan: (~p ∧ ~q) ∧ p → use associativity
                not_p_and_not_q = CompoundProposition(Proposition.__mul__, not_p, not_q)
                after_dm = CompoundProposition(Proposition.__mul__, not_p_and_not_q, p)
                for _ in range(35):
                    samples.append((after_dm, 'associativity', 'F'))

                # After associativity: ~p ∧ (~q ∧ p) → commutativity inside
                not_q_and_p = CompoundProposition(Proposition.__mul__, not_q, p)
                after_assoc = CompoundProposition(Proposition.__mul__, not_p, not_q_and_p)
                for _ in range(30):
                    samples.append((after_assoc, 'commutativity', 'F'))

                # p ∧ ~(p ∧ q) - another pattern
                p_and_q = CompoundProposition(Proposition.__mul__, p, q)
                neg_p_and_q = CompoundProposition(Proposition.__invert__, p_and_q)
                p_and_neg_pq = CompoundProposition(Proposition.__mul__, p, neg_p_and_q)
                for _ in range(30):
                    samples.append((p_and_neg_pq, 'de_morgan', 'F'))

    return samples


def generate_double_negation_simplification_samples():
    """
    Generate samples for double negation in simplification context.
    ~~p → p is important to reach simplifiable forms.
    """
    props = _get_propositions()
    samples = []

    for name, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)
        not_not_p = CompoundProposition(Proposition.__invert__, not_p)

        # Direct: ~~p → p
        for _ in range(30):
            samples.append((not_not_p, 'double_negation', 'F'))

        # Nested: ~~p ∧ ~p → p ∧ ~p → F
        # First step should be double_negation
        not_not_p_and_not_p = CompoundProposition(Proposition.__mul__, not_not_p, not_p)
        for _ in range(40):
            samples.append((not_not_p_and_not_p, 'double_negation', 'F'))

        # ~~p ∧ q → p ∧ q (simplify first)
        for name2, q in props.items():
            if name != name2:
                not_not_p_and_q = CompoundProposition(Proposition.__mul__, not_not_p, q)
                for _ in range(25):
                    samples.append((not_not_p_and_q, 'double_negation', 'F'))

    return samples


def generate_implication_absurdity_samples():
    """
    Generate samples for implications in absurdity context.
    (p → q) ∧ p ∧ ~q should lead to F via:
    (~p ∨ q) ∧ p ∧ ~q → many steps → F
    """
    props = _get_propositions()
    samples = []

    for name1, p in props.items():
        not_p = CompoundProposition(Proposition.__invert__, p)

        for name2, q in props.items():
            if name1 != name2:
                not_q = CompoundProposition(Proposition.__invert__, q)

                # (p → q) ∧ p ∧ ~q - classic Modus Tollens contradiction
                impl = CompoundProposition(Proposition.__rshift__, p, q)
                impl_and_p = CompoundProposition(Proposition.__mul__, impl, p)
                full = CompoundProposition(Proposition.__mul__, impl_and_p, not_q)

                # First step: implication_elimination on p → q
                for _ in range(40):
                    samples.append((full, 'implication_elimination', 'F'))

                # After elimination: (~p ∨ q) ∧ p ∧ ~q
                disj = CompoundProposition(Proposition.__add__, not_p, q)
                disj_and_p = CompoundProposition(Proposition.__mul__, disj, p)
                after_elim = CompoundProposition(Proposition.__mul__, disj_and_p, not_q)

                # Use distributivity to progress
                for _ in range(35):
                    samples.append((after_elim, 'distributivity', 'F'))

                # p ∧ (p → q) ∧ ~q - same pattern, different arrangement
                p_and_impl = CompoundProposition(Proposition.__mul__, p, impl)
                alt_full = CompoundProposition(Proposition.__mul__, p_and_impl, not_q)
                for _ in range(30):
                    samples.append((alt_full, 'implication_elimination', 'F'))

    return samples


def generate_simplification_dataset(num_samples: int = 2000, verbose: bool = False) -> tuple:
    """
    Generate training dataset for SimplificationPredictor.
    Focuses on patterns that simplify expressions to constants (F or T).

    Args:
        num_samples: Maximum number of samples to generate
        verbose: Print generation info

    Returns:
        (X, y) tuple where X is feature matrix and y is class labels
    """
    all_samples = []

    if verbose:
        print("[SimplificationPredictor] Generating complement samples...")
    complement = generate_absurdity_complement_samples()
    all_samples.extend(complement)

    if verbose:
        print("[SimplificationPredictor] Generating F propagation samples...")
    f_prop = generate_f_propagation_samples()
    all_samples.extend(f_prop)

    if verbose:
        print("[SimplificationPredictor] Generating expose complement samples...")
    expose = generate_expose_complement_samples()
    all_samples.extend(expose)

    if verbose:
        print("[SimplificationPredictor] Generating De Morgan samples...")
    demorgan = generate_absurdity_demorgan_samples()
    all_samples.extend(demorgan)

    if verbose:
        print("[SimplificationPredictor] Generating double negation samples...")
    double_neg = generate_double_negation_simplification_samples()
    all_samples.extend(double_neg)

    if verbose:
        print("[SimplificationPredictor] Generating implication samples...")
    implication = generate_implication_absurdity_samples()
    all_samples.extend(implication)

    # Convert to features
    X = []
    y = []

    for prop, transform, goal in all_samples:
        try:
            prop = _make_compound(prop)
            features = extract_single_features(prop, goal=goal)
            label = encode_simplification_action(transform)

            X.append(features)
            y.append(label)
        except Exception:
            continue

    # Shuffle
    indices = list(range(len(X)))
    random.shuffle(indices)
    X = [X[i] for i in indices]
    y = [y[i] for i in indices]

    # Limit to num_samples
    X = X[:num_samples]
    y = y[:num_samples]

    if verbose:
        print(f"[SimplificationPredictor] Generated {len(X)} samples")
        from collections import Counter
        dist = Counter(y)
        print("[SimplificationPredictor] Class distribution:")
        for class_idx, count in sorted(dist.items()):
            transform = SIMPLIFICATION_CLASS_MAPPING[class_idx]
            print(f"  {class_idx}: {transform}: {count}")

    return np.array(X), np.array(y)
