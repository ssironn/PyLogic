import unittest
from proposition import Proposition, CompoundProposition, parse_proposition, ParseError, TRUE, FALSE, TruthConstant
from equivalence import Equivalence


class TestCalculusOfTruthValue(unittest.TestCase):
    def test_keep_the_truth_value(self):
        p = Proposition(text='p', value=True)
        self.assertEqual(p.value, True)

    def test_tautologies(self):
        truth_values = [True, False]

        for truth_value in truth_values:
            p = Proposition(text='p', value=truth_value)
            not_p = CompoundProposition(Proposition.__invert__, p)
            proposition = CompoundProposition(Proposition.__add__, p, not_p)
            self.assertEqual(proposition.calculate_value(), True)

    def test_contradictions(self):
        truth_values = [True, False]

        for truth_value in truth_values:
            p = Proposition(text='p', value=truth_value)
            not_p = CompoundProposition(Proposition.__invert__, p)
            proposition = CompoundProposition(Proposition.__mul__, p, not_p)
            self.assertEqual(proposition.calculate_value(), False)


class TestDoubleNegation(unittest.TestCase):
    def setUp(self):
        self.eq = Equivalence()
        self.p = Proposition(text='p', value=True)

    def test_check_double_negation(self):
        # ~~p
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        not_not_p = CompoundProposition(Proposition.__invert__, not_p)
        self.assertTrue(self.eq.check_double_negation(not_not_p))

    def test_check_double_negation_false(self):
        # ~p (single negation)
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        self.assertFalse(self.eq.check_double_negation(not_p))

    def test_apply_double_negation(self):
        # ~~p -> p
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        not_not_p = CompoundProposition(Proposition.__invert__, not_p)
        result = self.eq.apply_double_negation(not_not_p)
        self.assertEqual(result.text, 'p')


class TestDeMorgan(unittest.TestCase):
    def setUp(self):
        self.eq = Equivalence()
        self.p = Proposition(text='p', value=True)
        self.q = Proposition(text='q', value=False)

    def test_check_de_morgan_and(self):
        # ~(p ^ q)
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        not_p_and_q = CompoundProposition(Proposition.__invert__, p_and_q)
        self.assertTrue(self.eq.check_de_morgan(not_p_and_q))

    def test_check_de_morgan_or(self):
        # ~(p v q)
        p_or_q = CompoundProposition(Proposition.__add__, self.p, self.q)
        not_p_or_q = CompoundProposition(Proposition.__invert__, p_or_q)
        self.assertTrue(self.eq.check_de_morgan(not_p_or_q))

    def test_apply_de_morgan_and(self):
        # ~(p ^ q) -> ~p v ~q
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        not_p_and_q = CompoundProposition(Proposition.__invert__, p_and_q)
        result = self.eq.apply_de_morgan(not_p_and_q)
        # Result should be (~p v ~q)
        self.assertEqual(str(result), '((¬p) v (¬q))')

    def test_apply_de_morgan_or(self):
        # ~(p v q) -> ~p ^ ~q
        p_or_q = CompoundProposition(Proposition.__add__, self.p, self.q)
        not_p_or_q = CompoundProposition(Proposition.__invert__, p_or_q)
        result = self.eq.apply_de_morgan(not_p_or_q)
        # Result should be (~p ^ ~q)
        self.assertEqual(str(result), '((¬p) ^ (¬q))')

    def test_de_morgan_preserves_truth_value(self):
        # ~(p ^ q) should have same truth value as ~p v ~q
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        not_p_and_q = CompoundProposition(Proposition.__invert__, p_and_q)
        result = self.eq.apply_de_morgan(not_p_and_q)
        self.assertEqual(not_p_and_q.calculate_value(), result.calculate_value())

    def test_check_de_morgan_reverse_or(self):
        # p v q
        p_or_q = CompoundProposition(Proposition.__add__, self.p, self.q)
        self.assertTrue(self.eq.check_de_morgan_reverse(p_or_q))

    def test_check_de_morgan_reverse_and(self):
        # p ^ q
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        self.assertTrue(self.eq.check_de_morgan_reverse(p_and_q))

    def test_apply_de_morgan_reverse_or(self):
        # p v q -> ~(~p ^ ~q)
        p_or_q = CompoundProposition(Proposition.__add__, self.p, self.q)
        result = self.eq.apply_de_morgan_reverse(p_or_q)
        self.assertEqual(str(result), '(¬((¬p) ^ (¬q)))')

    def test_apply_de_morgan_reverse_and(self):
        # p ^ q -> ~(~p v ~q)
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        result = self.eq.apply_de_morgan_reverse(p_and_q)
        self.assertEqual(str(result), '(¬((¬p) v (¬q)))')

    def test_de_morgan_reverse_preserves_truth_value(self):
        # p v q should have same truth value as ~(~p ^ ~q)
        p_or_q = CompoundProposition(Proposition.__add__, self.p, self.q)
        result = self.eq.apply_de_morgan_reverse(p_or_q)
        self.assertEqual(p_or_q.calculate_value(), result.calculate_value())


class TestCommutativity(unittest.TestCase):
    def setUp(self):
        self.eq = Equivalence()
        self.p = Proposition(text='p', value=True)
        self.q = Proposition(text='q', value=False)

    def test_check_commutativity(self):
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        self.assertTrue(self.eq.check_commutativity(p_and_q))

    def test_check_commutativity_unary_false(self):
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        self.assertFalse(self.eq.check_commutativity(not_p))

    def test_apply_commutativity(self):
        # p ^ q -> q ^ p
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        result = self.eq.apply_commutativity(p_and_q)
        self.assertEqual(str(result), '(q ^ p)')

    def test_commutativity_preserves_truth_value(self):
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        result = self.eq.apply_commutativity(p_and_q)
        self.assertEqual(p_and_q.calculate_value(), result.calculate_value())

    def test_commutativity_not_applicable_to_implication(self):
        """Implication is NOT commutative: p → q ≠ q → p"""
        impl = CompoundProposition(Proposition.__rshift__, self.p, self.q)
        self.assertFalse(self.eq.check_commutativity(impl))


class TestIdempotence(unittest.TestCase):
    def setUp(self):
        self.eq = Equivalence()
        self.p = Proposition(text='p', value=True)
        self.q = Proposition(text='q', value=False)

    def test_check_idempotence_and(self):
        # p ^ p
        p_and_p = CompoundProposition(Proposition.__mul__, self.p, self.p)
        self.assertTrue(self.eq.check_idempotence(p_and_p))

    def test_check_idempotence_or(self):
        # p v p
        p_or_p = CompoundProposition(Proposition.__add__, self.p, self.p)
        self.assertTrue(self.eq.check_idempotence(p_or_p))

    def test_check_idempotence_false(self):
        # p ^ q (different propositions)
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        self.assertFalse(self.eq.check_idempotence(p_and_q))

    def test_apply_idempotence(self):
        # p ^ p -> p
        p_and_p = CompoundProposition(Proposition.__mul__, self.p, self.p)
        result = self.eq.apply_idempotence(p_and_p)
        self.assertEqual(result.text, 'p')

    def test_idempotence_not_applicable_to_implication(self):
        """p → p is a tautology, NOT equal to p"""
        impl = CompoundProposition(Proposition.__rshift__, self.p, self.p)
        self.assertFalse(self.eq.check_idempotence(impl))


class TestAbsorption(unittest.TestCase):
    def setUp(self):
        self.eq = Equivalence()
        self.p = Proposition(text='p', value=True)
        self.q = Proposition(text='q', value=False)

    def test_check_absorption_and_or(self):
        # p ^ (p v q)
        p_or_q = CompoundProposition(Proposition.__add__, self.p, self.q)
        proposition = CompoundProposition(Proposition.__mul__, self.p, p_or_q)
        self.assertTrue(self.eq.check_absorption(proposition))

    def test_check_absorption_or_and(self):
        # p v (p ^ q)
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        proposition = CompoundProposition(Proposition.__add__, self.p, p_and_q)
        self.assertTrue(self.eq.check_absorption(proposition))

    def test_check_absorption_false(self):
        # p ^ (q v r) - p not in inner
        r = Proposition(text='r')
        q_or_r = CompoundProposition(Proposition.__add__, self.q, r)
        proposition = CompoundProposition(Proposition.__mul__, self.p, q_or_r)
        self.assertFalse(self.eq.check_absorption(proposition))

    def test_apply_absorption(self):
        # p ^ (p v q) -> p
        p_or_q = CompoundProposition(Proposition.__add__, self.p, self.q)
        proposition = CompoundProposition(Proposition.__mul__, self.p, p_or_q)
        result = self.eq.apply_absorption(proposition)
        self.assertEqual(result.text, 'p')


class TestDistributivity(unittest.TestCase):
    def setUp(self):
        self.eq = Equivalence()
        self.p = Proposition(text='p')
        self.q = Proposition(text='q')
        self.r = Proposition(text='r')

    def test_check_distributivity_exists(self):
        # p v (p ^ q)
        inner = CompoundProposition(Proposition.__mul__, self.p, self.q)
        proposition = CompoundProposition(Proposition.__add__, self.p, inner)
        self.assertTrue(self.eq.check_distributivity(proposition))

    def test_check_distributivity_not_exists(self):
        # p ^ q (no nested compound with different op)
        proposition = CompoundProposition(Proposition.__mul__, self.p, self.q)
        self.assertFalse(self.eq.check_distributivity(proposition))

    def test_apply_distributivity(self):
        # p ^ (q v r) -> (p ^ q) v (p ^ r)
        q_or_r = CompoundProposition(Proposition.__add__, self.q, self.r)
        proposition = CompoundProposition(Proposition.__mul__, self.p, q_or_r)
        result = self.eq.apply_distributivity(proposition)
        self.assertEqual(str(result), '((p ^ q) v (p ^ r))')

    def test_distributivity_preserves_truth_value(self):
        # Test with actual truth values
        p = Proposition(text='p', value=True)
        q = Proposition(text='q', value=False)
        r = Proposition(text='r', value=True)

        q_or_r = CompoundProposition(Proposition.__add__, q, r)
        original = CompoundProposition(Proposition.__mul__, p, q_or_r)
        result = self.eq.apply_distributivity(original)

        self.assertEqual(original.calculate_value(), result.calculate_value())


class TestFactoring(unittest.TestCase):
    """Test factoring (reverse distributivity)."""

    def setUp(self):
        self.eq = Equivalence()
        self.p = Proposition(text='p')
        self.q = Proposition(text='q')
        self.r = Proposition(text='r')

    def test_check_factoring_or_pattern(self):
        """(p ^ q) v (p ^ r) should be factorable."""
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        p_and_r = CompoundProposition(Proposition.__mul__, self.p, self.r)
        proposition = CompoundProposition(Proposition.__add__, p_and_q, p_and_r)
        self.assertTrue(self.eq.check_factoring(proposition))

    def test_check_factoring_and_pattern(self):
        """(p v q) ^ (p v r) should be factorable."""
        p_or_q = CompoundProposition(Proposition.__add__, self.p, self.q)
        p_or_r = CompoundProposition(Proposition.__add__, self.p, self.r)
        proposition = CompoundProposition(Proposition.__mul__, p_or_q, p_or_r)
        self.assertTrue(self.eq.check_factoring(proposition))

    def test_check_factoring_no_common_factor(self):
        """(p ^ q) v (r ^ s) should NOT be factorable (no common factor)."""
        s = Proposition(text='s')
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        r_and_s = CompoundProposition(Proposition.__mul__, self.r, s)
        proposition = CompoundProposition(Proposition.__add__, p_and_q, r_and_s)
        self.assertFalse(self.eq.check_factoring(proposition))

    def test_apply_factoring_or(self):
        """(p ^ q) v (p ^ r) -> p ^ (q v r)"""
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        p_and_r = CompoundProposition(Proposition.__mul__, self.p, self.r)
        proposition = CompoundProposition(Proposition.__add__, p_and_q, p_and_r)
        result = self.eq.apply_factoring(proposition)
        self.assertEqual(str(result), '(p ^ (q v r))')

    def test_apply_factoring_and(self):
        """(p v q) ^ (p v r) -> p v (q ^ r)"""
        p_or_q = CompoundProposition(Proposition.__add__, self.p, self.q)
        p_or_r = CompoundProposition(Proposition.__add__, self.p, self.r)
        proposition = CompoundProposition(Proposition.__mul__, p_or_q, p_or_r)
        result = self.eq.apply_factoring(proposition)
        self.assertEqual(str(result), '(p v (q ^ r))')

    def test_factoring_preserves_truth_value(self):
        """Factoring should preserve truth value."""
        p = Proposition(text='p', value=True)
        q = Proposition(text='q', value=False)
        r = Proposition(text='r', value=True)

        p_and_q = CompoundProposition(Proposition.__mul__, p, q)
        p_and_r = CompoundProposition(Proposition.__mul__, p, r)
        original = CompoundProposition(Proposition.__add__, p_and_q, p_and_r)
        result = self.eq.apply_factoring(original)

        self.assertEqual(original.calculate_value(), result.calculate_value())

    def test_factoring_common_on_right(self):
        """(q ^ p) v (r ^ p) -> p ^ (q v r) - common factor on right."""
        q_and_p = CompoundProposition(Proposition.__mul__, self.q, self.p)
        r_and_p = CompoundProposition(Proposition.__mul__, self.r, self.p)
        proposition = CompoundProposition(Proposition.__add__, q_and_p, r_and_p)
        self.assertTrue(self.eq.check_factoring(proposition))
        result = self.eq.apply_factoring(proposition)
        # Should factor out p
        self.assertIn('p', str(result))


class TestSyntacticEquality(unittest.TestCase):
    def setUp(self):
        self.eq = Equivalence()
        self.p = Proposition(text='p', value=True)
        self.q = Proposition(text='q', value=False)

    def test_equal_atomic_propositions(self):
        p1 = Proposition(text='p')
        p2 = Proposition(text='p')
        self.assertTrue(self.eq.are_equal(p1, p2))

    def test_different_atomic_propositions(self):
        self.assertFalse(self.eq.are_equal(self.p, self.q))

    def test_equal_compound_propositions(self):
        prop1 = CompoundProposition(Proposition.__mul__, self.p, self.q)
        prop2 = CompoundProposition(Proposition.__mul__, self.p, self.q)
        self.assertTrue(self.eq.are_equal(prop1, prop2))

    def test_different_compound_propositions(self):
        prop1 = CompoundProposition(Proposition.__mul__, self.p, self.q)
        prop2 = CompoundProposition(Proposition.__add__, self.p, self.q)
        self.assertFalse(self.eq.are_equal(prop1, prop2))

    def test_equal_nested_propositions(self):
        inner1 = CompoundProposition(Proposition.__add__, self.p, self.q)
        outer1 = CompoundProposition(Proposition.__mul__, self.p, inner1)

        inner2 = CompoundProposition(Proposition.__add__, self.p, self.q)
        outer2 = CompoundProposition(Proposition.__mul__, self.p, inner2)

        self.assertTrue(self.eq.are_equal(outer1, outer2))


class TestBruteForceProver(unittest.TestCase):
    def setUp(self):
        self.eq = Equivalence()
        self.p = Proposition(text='p', value=True)
        self.q = Proposition(text='q', value=False)

    def test_prove_identical_propositions(self):
        """Identical propositions should match in 0 iterations (deterministic)."""
        prop1 = CompoundProposition(Proposition.__mul__, self.p, self.q)
        prop2 = CompoundProposition(Proposition.__mul__, self.p, self.q)
        result = self.eq.prove_equivalence(prop1, prop2)
        self.assertTrue(result['success'])
        self.assertEqual(result['iterations'], 0)

    def test_prover_preserves_semantic_equivalence(self):
        """Transformations should preserve truth values regardless of success."""
        prop1 = CompoundProposition(Proposition.__mul__, self.p, self.q)
        prop2 = CompoundProposition(Proposition.__mul__, self.q, self.p)

        original_value1 = prop1.calculate_value()
        original_value2 = prop2.calculate_value()

        result = self.eq.prove_equivalence(prop1, prop2, max_iterations=50)

        # Final propositions should have same truth value as originals
        final1 = result['prop1_final']
        final2 = result['prop2_final']

        self.assertEqual(final1.calculate_value(), original_value1)
        self.assertEqual(final2.calculate_value(), original_value2)

    def test_prover_applies_transformations(self):
        """Prover should apply transformations when propositions differ."""
        prop1 = CompoundProposition(Proposition.__mul__, self.p, self.q)
        prop2 = CompoundProposition(Proposition.__mul__, self.q, self.p)

        result = self.eq.prove_equivalence(prop1, prop2, max_iterations=50)

        # Should have attempted some transformations
        if not result['success'] or result['iterations'] > 0:
            self.assertIsInstance(result['transformations'], list)

    def test_prover_tracks_transformation_history(self):
        """Each transformation should be recorded with proper structure."""
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        not_not_p = CompoundProposition(Proposition.__invert__, not_p)

        p_compound = CompoundProposition()
        from proposition import AtomicNode
        p_compound.root = AtomicNode(self.p)
        p_compound.components = {self.p}

        result = self.eq.prove_equivalence(not_not_p, p_compound, max_iterations=50)

        for t in result['transformations']:
            self.assertIn('iteration', t)
            self.assertIn('proposition', t)
            self.assertIn('law', t)
            self.assertIn('result', t)

    def test_returns_correct_structure(self):
        """Result dictionary should have all required keys."""
        prop1 = CompoundProposition(Proposition.__mul__, self.p, self.q)
        prop2 = CompoundProposition(Proposition.__mul__, self.p, self.q)
        result = self.eq.prove_equivalence(prop1, prop2)

        self.assertIn('success', result)
        self.assertIn('iterations', result)
        self.assertIn('prop1_final', result)
        self.assertIn('prop2_final', result)
        self.assertIn('transformations', result)

    def test_respects_max_iterations(self):
        """Prover should stop at max_iterations if not successful."""
        # Use propositions that are unlikely to match quickly
        p_or_q = CompoundProposition(Proposition.__add__, self.p, self.q)
        r = Proposition(text='r', value=True)
        p_or_r = CompoundProposition(Proposition.__add__, self.p, r)

        result = self.eq.prove_equivalence(p_or_q, p_or_r, max_iterations=10)

        self.assertLessEqual(result['iterations'], 10)


class TestNeuralNetworkFeatures(unittest.TestCase):
    """Test feature extraction for neural network."""

    def setUp(self):
        self.p = Proposition(text='p', value=True)
        self.q = Proposition(text='q', value=False)

    def test_extract_features_atomic(self):
        """Atomic proposition should have specific features."""
        from nn.features import extract_features
        features = extract_features(self.p)
        self.assertEqual(len(features), 17)  # 12 structure + 5 usefulness features
        self.assertEqual(features[11], 1)  # is_atomic

    def test_extract_features_compound(self):
        """Compound proposition should have correct feature count."""
        from nn.features import extract_features
        prop = CompoundProposition(Proposition.__mul__, self.p, self.q)
        features = extract_features(prop)
        self.assertEqual(len(features), 17)  # 12 structure + 5 usefulness features
        self.assertEqual(features[10], 1)  # has_binary_root

    def test_extract_features_negation(self):
        """Negation should be counted."""
        from nn.features import extract_features
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        features = extract_features(not_p)
        self.assertEqual(features[3], 1)  # num_negations

    def test_extract_features_double_negation(self):
        """Double negation pattern should be detected."""
        from nn.features import extract_features
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        not_not_p = CompoundProposition(Proposition.__invert__, not_p)
        features = extract_features(not_not_p)
        self.assertEqual(features[7], 1)  # has_double_negation

    def test_extract_features_implication(self):
        """Implication should be detected."""
        from nn.features import extract_features
        impl = CompoundProposition(Proposition.__rshift__, self.p, self.q)
        features = extract_features(impl)
        self.assertEqual(features[6], 1)  # num_implications
        self.assertEqual(features[9], 1)  # has_implication

    def test_extract_pair_features(self):
        """Pair features should concatenate both proposition features plus applicability."""
        from nn.features import extract_pair_features
        prop1 = CompoundProposition(Proposition.__mul__, self.p, self.q)
        prop2 = CompoundProposition(Proposition.__add__, self.p, self.q)
        features = extract_pair_features(prop1, prop2)
        # 17 structural features per proposition (34) + 17 applicability features per proposition (34) = 68
        self.assertEqual(len(features), 68)

    def test_applicability_features(self):
        """Applicability features should correctly indicate which transformations can be applied."""
        from nn.features import get_applicability_features
        # Double negation should be applicable
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        not_not_p = CompoundProposition(Proposition.__invert__, not_p)
        features = get_applicability_features(not_not_p)
        self.assertEqual(len(features), 17)  # 17 transformations
        self.assertEqual(features[0], 1)  # can_apply_double_negation

        # Commutativity should be applicable to p ^ q
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        features = get_applicability_features(p_and_q)
        self.assertEqual(features[10], 1)  # can_apply_commutativity

        # Atomic propositions should have no applicable transformations
        features = get_applicability_features(self.p)
        self.assertEqual(sum(features), 0)  # No transformations applicable


class TestNeuralNetworkDataset(unittest.TestCase):
    """Test dataset generation."""

    def test_generate_small_dataset(self):
        """Should generate dataset with correct shape."""
        from nn.dataset import generate_dataset
        X, y = generate_dataset(num_samples=10)
        # 68 features: 34 structural (17 per prop) + 34 applicability (17 per prop)
        self.assertEqual(X.shape[1], 68)
        self.assertEqual(len(X), len(y))

    def test_decode_prediction(self):
        """Should decode class index to action tuple."""
        from nn.dataset import decode_prediction
        which_prop, transform = decode_prediction(0)
        self.assertEqual(which_prop, 1)
        self.assertEqual(transform, 'double_negation')

    def test_encode_action(self):
        """Should encode action tuple to class index."""
        from nn.dataset import encode_action
        class_idx = encode_action(1, 'double_negation')
        self.assertEqual(class_idx, 0)


class TestNeuralNetworkModel(unittest.TestCase):
    """Test neural network model."""

    def test_model_architecture(self):
        """Model should have correct architecture."""
        from nn.model import TransformationPredictor
        model = TransformationPredictor()
        arch = model.get_architecture()
        # 68 features: 34 structural (17 per prop) + 34 applicability (17 per prop)
        self.assertEqual(arch['input_size'], 68)
        self.assertEqual(arch['output_size'], 34)  # 17 transformations x 2 propositions
        self.assertEqual(arch['hidden_layers'], (64, 32))

    def test_model_train_and_predict(self):
        """Model should train and make predictions."""
        from nn import TransformationPredictor, generate_dataset
        import numpy as np

        # Generate small dataset
        X, y = generate_dataset(num_samples=50)

        if len(X) < 10:
            self.skipTest("Not enough training samples generated")

        model = TransformationPredictor(max_iter=100)
        model.train(X, y)

        self.assertTrue(model.is_trained)

        # Make a prediction
        p = Proposition(text='p', value=True)
        q = Proposition(text='q', value=False)
        prop1 = CompoundProposition(Proposition.__mul__, p, q)
        prop2 = CompoundProposition(Proposition.__mul__, q, p)

        which_prop, transform = model.predict(prop1, prop2)
        self.assertIn(which_prop, [1, 2])
        self.assertIsInstance(transform, str)


class TestParser(unittest.TestCase):
    """Test the proposition parser."""

    def test_parse_atomic(self):
        """Should parse atomic propositions."""
        prop, props = parse_proposition("p")
        self.assertEqual(prop.text, 'p')
        self.assertIn('p', props)

    def test_parse_negation(self):
        """Should parse negation."""
        prop, props = parse_proposition("~p")
        self.assertIsInstance(prop, CompoundProposition)
        self.assertEqual(str(prop), '(¬p)')

    def test_parse_conjunction(self):
        """Should parse conjunction with ^."""
        prop, props = parse_proposition("p ^ q")
        self.assertIsInstance(prop, CompoundProposition)
        self.assertEqual(str(prop), '(p ^ q)')

    def test_parse_disjunction(self):
        """Should parse disjunction with v."""
        prop, props = parse_proposition("p v q")
        self.assertIsInstance(prop, CompoundProposition)
        self.assertEqual(str(prop), '(p v q)')

    def test_parse_parentheses(self):
        """Should parse expressions with parentheses."""
        prop, props = parse_proposition("(p ^ q) v r")
        self.assertIsInstance(prop, CompoundProposition)

    def test_parse_complex_expression(self):
        """Should parse complex nested expressions."""
        prop, props = parse_proposition("~(p ^ q)")
        self.assertIsInstance(prop, CompoundProposition)
        # Check the structure is correct
        self.assertEqual(str(prop), '(¬(p ^ q))')

    def test_parse_double_negation(self):
        """Should parse double negation."""
        prop, props = parse_proposition("~~p")
        self.assertIsInstance(prop, CompoundProposition)
        self.assertEqual(str(prop), '(¬(¬p))')

    def test_parse_operator_precedence(self):
        """AND should have higher precedence than OR."""
        prop, props = parse_proposition("p v q ^ r")
        # Should be parsed as p v (q ^ r), not (p v q) ^ r
        self.assertIsInstance(prop, CompoundProposition)
        # The root should be OR
        self.assertEqual(prop.root.operator.name, '__add__')

    def test_parse_alternative_operators(self):
        """Should parse alternative operator symbols."""
        # AND with &
        prop, _ = parse_proposition("p & q")
        self.assertEqual(str(prop), '(p ^ q)')

        # OR with |
        prop, _ = parse_proposition("p | q")
        self.assertEqual(str(prop), '(p v q)')

        # NOT with !
        prop, _ = parse_proposition("!p")
        self.assertEqual(str(prop), '(¬p)')

    def test_parse_keywords(self):
        """Should parse keyword operators."""
        prop, _ = parse_proposition("p AND q")
        self.assertEqual(str(prop), '(p ^ q)')

        prop, _ = parse_proposition("p OR q")
        self.assertEqual(str(prop), '(p v q)')

        prop, _ = parse_proposition("NOT p")
        self.assertEqual(str(prop), '(¬p)')

    def test_parse_empty_raises_error(self):
        """Should raise ParseError for empty input."""
        with self.assertRaises(ParseError):
            parse_proposition("")

    def test_parse_invalid_raises_error(self):
        """Should raise ParseError for invalid input."""
        with self.assertRaises(ParseError):
            parse_proposition("p ^")

    def test_propositions_dict(self):
        """Should return a dict with all propositions."""
        prop, props = parse_proposition("p ^ q v r")
        self.assertIn('p', props)
        self.assertIn('q', props)
        self.assertIn('r', props)
        self.assertEqual(len(props), 3)

    def test_same_proposition_shared(self):
        """Same proposition name should refer to same object."""
        prop, props = parse_proposition("p ^ p")
        # There should be only one 'p' in the dict
        self.assertEqual(len(props), 1)

    def test_parse_implication(self):
        """Should parse implication with ->."""
        prop, props = parse_proposition("p -> q")
        self.assertIsInstance(prop, CompoundProposition)
        self.assertEqual(str(prop), '(p → q)')

    def test_parse_implication_arrow(self):
        """Should parse implication with =>."""
        prop, props = parse_proposition("p => q")
        self.assertIsInstance(prop, CompoundProposition)
        self.assertEqual(str(prop), '(p → q)')

    def test_parse_implication_keyword(self):
        """Should parse implication with IMPLIES keyword."""
        prop, props = parse_proposition("p IMPLIES q")
        self.assertIsInstance(prop, CompoundProposition)
        self.assertEqual(str(prop), '(p → q)')

    def test_implication_precedence(self):
        """Implication should have lower precedence than OR."""
        prop, props = parse_proposition("p v q -> r")
        # Should be parsed as (p v q) -> r
        self.assertIsInstance(prop, CompoundProposition)
        # Root should be implication
        self.assertEqual(prop.root.operator.name, '__rshift__')

    def test_implication_right_associative(self):
        """Implication should be right-associative."""
        prop, props = parse_proposition("p -> q -> r")
        # Should be parsed as p -> (q -> r)
        self.assertIsInstance(prop, CompoundProposition)
        # Left should be p, right should be (q -> r)
        self.assertEqual(prop.root.left.proposition.text, 'p')


class TestUsefulnessAnalysis(unittest.TestCase):
    """Test usefulness analysis of propositions."""

    def setUp(self):
        self.p = Proposition(text='p', value=True)
        self.q = Proposition(text='q', value=False)
        self.r = Proposition(text='r', value=True)

    def test_atomic_proposition_useful(self):
        """Atomic proposition should be useful."""
        from nn.features import analyze_proposition_usefulness
        result = analyze_proposition_usefulness(self.p)
        self.assertEqual(result['useful_count'], 1)
        self.assertEqual(result['useless_count'], 0)
        self.assertIn('p', result['useful'])

    def test_conjunction_both_useful(self):
        """In p ^ q, both p and q are useful."""
        from nn.features import analyze_proposition_usefulness
        prop = CompoundProposition(Proposition.__mul__, self.p, self.q)
        result = analyze_proposition_usefulness(prop)
        self.assertEqual(result['useful_count'], 2)
        self.assertEqual(result['useless_count'], 0)
        self.assertIn('p', result['useful'])
        self.assertIn('q', result['useful'])

    def test_tautology_detected(self):
        """p v ~p should be detected as tautology."""
        from nn.features import analyze_proposition_usefulness
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        prop = CompoundProposition(Proposition.__add__, self.p, not_p)
        result = analyze_proposition_usefulness(prop)
        self.assertTrue(result['is_tautology'])
        self.assertFalse(result['is_contradiction'])
        self.assertEqual(result['useless_count'], 1)  # p is useless in a tautology

    def test_contradiction_detected(self):
        """p ^ ~p should be detected as contradiction."""
        from nn.features import analyze_proposition_usefulness
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        prop = CompoundProposition(Proposition.__mul__, self.p, not_p)
        result = analyze_proposition_usefulness(prop)
        self.assertTrue(result['is_contradiction'])
        self.assertFalse(result['is_tautology'])
        self.assertEqual(result['useless_count'], 1)  # p is useless in a contradiction

    def test_implication_tautology(self):
        """p -> (p v q) should be a tautology with q useless."""
        from nn.features import analyze_proposition_usefulness
        p_or_q = CompoundProposition(Proposition.__add__, self.p, self.q)
        impl = CompoundProposition(Proposition.__rshift__, self.p, p_or_q)
        result = analyze_proposition_usefulness(impl)
        self.assertTrue(result['is_tautology'])
        self.assertIn('q', result['useless'])

    def test_absorption_useless_proposition(self):
        """In p v (p ^ q), q is useless (absorption)."""
        from nn.features import analyze_proposition_usefulness
        p_and_q = CompoundProposition(Proposition.__mul__, self.p, self.q)
        prop = CompoundProposition(Proposition.__add__, self.p, p_and_q)
        result = analyze_proposition_usefulness(prop)
        self.assertIn('q', result['useless'])
        self.assertIn('p', result['useful'])

    def test_usefulness_features_in_extraction(self):
        """Features should include usefulness analysis."""
        from nn.features import extract_features
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        prop = CompoundProposition(Proposition.__add__, self.p, not_p)
        features = extract_features(prop)
        # Features 12-16 are usefulness features
        # useful_count, useless_count, useful_ratio, is_tautology, is_contradiction
        self.assertEqual(features[15], 1)  # is_tautology


class TestTruthConstants(unittest.TestCase):
    """Test truth constants T and F."""

    def setUp(self):
        self.eq = Equivalence()
        self.p = Proposition(text='p', value=True)
        self.q = Proposition(text='q', value=False)

    def test_true_constant_value(self):
        """T should always be True."""
        self.assertTrue(TRUE.value)
        self.assertTrue(TRUE.is_true())
        self.assertFalse(TRUE.is_false())
        self.assertTrue(TRUE.is_constant())

    def test_false_constant_value(self):
        """F should always be False."""
        self.assertFalse(FALSE.value)
        self.assertTrue(FALSE.is_false())
        self.assertFalse(FALSE.is_true())
        self.assertTrue(FALSE.is_constant())

    def test_constant_value_immutable(self):
        """Truth constants should not be mutable."""
        TRUE.value = False  # Should be ignored
        self.assertTrue(TRUE.value)
        FALSE.value = True  # Should be ignored
        self.assertFalse(FALSE.value)

    def test_parse_true(self):
        """Should parse T as True constant."""
        prop, props = parse_proposition("T")
        self.assertIsInstance(prop, TruthConstant)
        self.assertTrue(prop.is_true())

    def test_parse_false(self):
        """Should parse F as False constant."""
        prop, props = parse_proposition("F")
        self.assertIsInstance(prop, TruthConstant)
        self.assertTrue(prop.is_false())

    def test_parse_true_keyword(self):
        """Should parse TRUE as True constant."""
        prop, props = parse_proposition("TRUE")
        self.assertIsInstance(prop, TruthConstant)
        self.assertTrue(prop.is_true())

    def test_parse_false_keyword(self):
        """Should parse FALSE as False constant."""
        prop, props = parse_proposition("FALSE")
        self.assertIsInstance(prop, TruthConstant)
        self.assertTrue(prop.is_false())

    def test_parse_p_or_t(self):
        """Should parse p v T."""
        prop, props = parse_proposition("p v T")
        self.assertIsInstance(prop, CompoundProposition)
        self.assertEqual(str(prop), '(p v T)')

    def test_parse_p_and_f(self):
        """Should parse p ^ F."""
        prop, props = parse_proposition("p ^ F")
        self.assertIsInstance(prop, CompoundProposition)
        self.assertEqual(str(prop), '(p ^ F)')

    def test_check_complement_or(self):
        """p v ~p should be detectable as complement."""
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        p_or_not_p = CompoundProposition(Proposition.__add__, self.p, not_p)
        self.assertTrue(self.eq.check_complement(p_or_not_p))

    def test_apply_complement_or(self):
        """p v ~p should simplify to T."""
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        p_or_not_p = CompoundProposition(Proposition.__add__, self.p, not_p)
        result = self.eq.apply_complement(p_or_not_p)
        self.assertIsInstance(result, TruthConstant)
        self.assertTrue(result.is_true())

    def test_check_complement_and(self):
        """p ^ ~p should be detectable as complement."""
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        p_and_not_p = CompoundProposition(Proposition.__mul__, self.p, not_p)
        self.assertTrue(self.eq.check_complement(p_and_not_p))

    def test_apply_complement_and(self):
        """p ^ ~p should simplify to F."""
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        p_and_not_p = CompoundProposition(Proposition.__mul__, self.p, not_p)
        result = self.eq.apply_complement(p_and_not_p)
        self.assertIsInstance(result, TruthConstant)
        self.assertTrue(result.is_false())

    def test_check_identity_or_false(self):
        """p v F should be detectable as identity."""
        p_or_f = CompoundProposition(Proposition.__add__, self.p, FALSE)
        self.assertTrue(self.eq.check_identity(p_or_f))

    def test_apply_identity_or_false(self):
        """p v F should simplify to p."""
        p_or_f = CompoundProposition(Proposition.__add__, self.p, FALSE)
        result = self.eq.apply_identity(p_or_f)
        self.assertEqual(str(result), 'p')

    def test_check_identity_and_true(self):
        """p ^ T should be detectable as identity."""
        p_and_t = CompoundProposition(Proposition.__mul__, self.p, TRUE)
        self.assertTrue(self.eq.check_identity(p_and_t))

    def test_apply_identity_and_true(self):
        """p ^ T should simplify to p."""
        p_and_t = CompoundProposition(Proposition.__mul__, self.p, TRUE)
        result = self.eq.apply_identity(p_and_t)
        self.assertEqual(str(result), 'p')

    def test_check_domination_or_true(self):
        """p v T should be detectable as domination."""
        p_or_t = CompoundProposition(Proposition.__add__, self.p, TRUE)
        self.assertTrue(self.eq.check_domination(p_or_t))

    def test_apply_domination_or_true(self):
        """p v T should simplify to T."""
        p_or_t = CompoundProposition(Proposition.__add__, self.p, TRUE)
        result = self.eq.apply_domination(p_or_t)
        self.assertIsInstance(result, TruthConstant)
        self.assertTrue(result.is_true())

    def test_check_domination_and_false(self):
        """p ^ F should be detectable as domination."""
        p_and_f = CompoundProposition(Proposition.__mul__, self.p, FALSE)
        self.assertTrue(self.eq.check_domination(p_and_f))

    def test_apply_domination_and_false(self):
        """p ^ F should simplify to F."""
        p_and_f = CompoundProposition(Proposition.__mul__, self.p, FALSE)
        result = self.eq.apply_domination(p_and_f)
        self.assertIsInstance(result, TruthConstant)
        self.assertTrue(result.is_false())

    def test_check_negation_constant(self):
        """~T and ~F should be detectable."""
        not_t = CompoundProposition(Proposition.__invert__, TRUE)
        not_f = CompoundProposition(Proposition.__invert__, FALSE)
        self.assertTrue(self.eq.check_negation_constant(not_t))
        self.assertTrue(self.eq.check_negation_constant(not_f))

    def test_apply_negation_constant_true(self):
        """~T should simplify to F."""
        not_t = CompoundProposition(Proposition.__invert__, TRUE)
        result = self.eq.apply_negation_constant(not_t)
        self.assertIsInstance(result, TruthConstant)
        self.assertTrue(result.is_false())

    def test_apply_negation_constant_false(self):
        """~F should simplify to T."""
        not_f = CompoundProposition(Proposition.__invert__, FALSE)
        result = self.eq.apply_negation_constant(not_f)
        self.assertIsInstance(result, TruthConstant)
        self.assertTrue(result.is_true())

    def test_implication_constant_true_implies_p(self):
        """T -> p should simplify to p."""
        t_impl_p = CompoundProposition(Proposition.__rshift__, TRUE, self.p)
        self.assertTrue(self.eq.check_implication_constant(t_impl_p))
        result = self.eq.apply_implication_constant(t_impl_p)
        self.assertEqual(str(result), 'p')

    def test_implication_constant_false_implies_p(self):
        """F -> p should simplify to T."""
        f_impl_p = CompoundProposition(Proposition.__rshift__, FALSE, self.p)
        self.assertTrue(self.eq.check_implication_constant(f_impl_p))
        result = self.eq.apply_implication_constant(f_impl_p)
        self.assertIsInstance(result, TruthConstant)
        self.assertTrue(result.is_true())

    def test_implication_constant_p_implies_true(self):
        """p -> T should simplify to T."""
        p_impl_t = CompoundProposition(Proposition.__rshift__, self.p, TRUE)
        self.assertTrue(self.eq.check_implication_constant(p_impl_t))
        result = self.eq.apply_implication_constant(p_impl_t)
        self.assertIsInstance(result, TruthConstant)
        self.assertTrue(result.is_true())

    def test_implication_constant_p_implies_false(self):
        """p -> F should simplify to ~p."""
        p_impl_f = CompoundProposition(Proposition.__rshift__, self.p, FALSE)
        self.assertTrue(self.eq.check_implication_constant(p_impl_f))
        result = self.eq.apply_implication_constant(p_impl_f)
        self.assertEqual(str(result), '(¬p)')


class TestImplicationEquivalence(unittest.TestCase):
    """Test implication equivalence laws."""

    def setUp(self):
        self.eq = Equivalence()
        self.p = Proposition(text='p', value=True)
        self.q = Proposition(text='q', value=False)

    def test_check_implication_elimination(self):
        """Should detect implication elimination pattern."""
        impl = CompoundProposition(Proposition.__rshift__, self.p, self.q)
        self.assertTrue(self.eq.check_implication_elimination(impl))

    def test_apply_implication_elimination(self):
        """Should convert p → q to ~p v q."""
        impl = CompoundProposition(Proposition.__rshift__, self.p, self.q)
        result = self.eq.apply_implication_elimination(impl)
        # Result should be (~p v q)
        self.assertEqual(str(result), '((¬p) v q)')

    def test_implication_elimination_preserves_truth(self):
        """Implication elimination should preserve truth value."""
        for p_val in [True, False]:
            for q_val in [True, False]:
                p = Proposition(text='p', value=p_val)
                q = Proposition(text='q', value=q_val)
                impl = CompoundProposition(Proposition.__rshift__, p, q)
                result = self.eq.apply_implication_elimination(impl)
                self.assertEqual(impl.calculate_value(), result.calculate_value())

    def test_check_implication_introduction(self):
        """Should detect implication introduction pattern."""
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        disj = CompoundProposition(Proposition.__add__, not_p, self.q)
        self.assertTrue(self.eq.check_implication_introduction(disj))

    def test_apply_implication_introduction(self):
        """Should convert ~p v q to p → q."""
        not_p = CompoundProposition(Proposition.__invert__, self.p)
        disj = CompoundProposition(Proposition.__add__, not_p, self.q)
        result = self.eq.apply_implication_introduction(disj)
        # Result should be (p → q)
        self.assertEqual(str(result), '(p → q)')

    def test_check_contraposition(self):
        """Should detect contraposition pattern."""
        impl = CompoundProposition(Proposition.__rshift__, self.p, self.q)
        self.assertTrue(self.eq.check_contraposition(impl))

    def test_apply_contraposition(self):
        """Should convert p → q to ~q → ~p."""
        impl = CompoundProposition(Proposition.__rshift__, self.p, self.q)
        result = self.eq.apply_contraposition(impl)
        # Result should be (~q → ~p)
        self.assertEqual(str(result), '((¬q) → (¬p))')

    def test_contraposition_preserves_truth(self):
        """Contraposition should preserve truth value."""
        for p_val in [True, False]:
            for q_val in [True, False]:
                p = Proposition(text='p', value=p_val)
                q = Proposition(text='q', value=q_val)
                impl = CompoundProposition(Proposition.__rshift__, p, q)
                result = self.eq.apply_contraposition(impl)
                self.assertEqual(impl.calculate_value(), result.calculate_value())


if __name__ == '__main__':
    unittest.main()
