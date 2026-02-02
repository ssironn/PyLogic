import random
from utils.proposition import Proposition, CompoundProposition, OperatorNode, AtomicNode, PropositionNode, TruthConstant, TRUE, FALSE
from utils.function_decorator import LogicOperator


class Equivalence:
    """
    Implements fundamental equivalence laws for propositional logic.

    Each law has two methods:
    - check_*: Returns True if the pattern can be applied
    - apply_*: Returns a new CompoundProposition with the transformation

    Supported laws:
    - Double Negation: ~~p = p
    - De Morgan's Laws (forward): ~(p ^ q) = ~p v ~q, ~(p v q) = ~p ^ ~q
    - De Morgan's Laws (reverse): p v q = ~(~p ^ ~q), p ^ q = ~(~p v ~q)
    - Commutativity: p ^ q = q ^ p, p v q = q v p
    - Idempotence: p ^ p = p, p v p = p
    - Absorption: p ^ (p v q) = p, p v (p ^ q) = p
    - Distributivity: p ^ (q v r) = (p ^ q) v (p ^ r)
    - Implication Elimination: p → q = ~p v q
    - Implication Introduction: ~p v q = p → q
    - Contraposition: p → q = ~q → ~p

    Truth constant laws:
    - Identity: p v F = p, p ^ T = p
    - Domination: p v T = T, p ^ F = F
    - Negation: ~T = F, ~F = T
    - Complement: p v ~p = T, p ^ ~p = F
    - Implication: T → p = p, F → p = T, p → T = T, p → F = ~p
    """

    # ==================== Double Negation ====================
    # ~~p = p

    def check_double_negation(self, proposition: CompoundProposition) -> bool:
        """Check if double negation can be eliminated: ~~p -> p"""
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.operator.name != '__invert__' or root.right is not None:
            return False
        inner = root.left
        if not isinstance(inner, OperatorNode):
            return False
        return inner.operator.name == '__invert__' and inner.right is None

    def apply_double_negation(self, proposition: CompoundProposition) -> CompoundProposition:
        """Apply double negation elimination: ~~p -> p"""
        if not self.check_double_negation(proposition):
            return proposition
        inner_operand = proposition.root.left.left
        return self._node_to_compound(inner_operand)

    # ==================== De Morgan's Laws ====================
    # Forward:  ~(p ^ q) = ~p v ~q,  ~(p v q) = ~p ^ ~q
    # Reverse:  p v q = ~(~p ^ ~q),  p ^ q = ~(~p v ~q)

    def check_de_morgan(self, proposition: CompoundProposition) -> bool:
        """Check if De Morgan's law (forward) can be applied: ~(p ^ q) or ~(p v q)"""
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.operator.name != '__invert__' or root.right is not None:
            return False
        inner = root.left
        if not isinstance(inner, OperatorNode):
            return False
        return inner.operator.name in ('__add__', '__mul__') and inner.right is not None

    def apply_de_morgan(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply De Morgan's law (forward):
        ~(p ^ q) -> ~p v ~q
        ~(p v q) -> ~p ^ ~q
        """
        if not self.check_de_morgan(proposition):
            return proposition

        inner = proposition.root.left
        left_operand = inner.left
        right_operand = inner.right

        not_left = CompoundProposition(Proposition.__invert__, self._node_to_compound(left_operand))
        not_right = CompoundProposition(Proposition.__invert__, self._node_to_compound(right_operand))

        if inner.operator.name == '__mul__':
            return CompoundProposition(Proposition.__add__, not_left, not_right)
        else:
            return CompoundProposition(Proposition.__mul__, not_left, not_right)

    def check_de_morgan_reverse(self, proposition: CompoundProposition) -> bool:
        """Check if De Morgan's law (reverse) can be applied: p v q or p ^ q"""
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        return root.operator.name in ('__add__', '__mul__') and root.right is not None

    def apply_de_morgan_reverse(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply De Morgan's law (reverse):
        p v q -> ~(~p ^ ~q)
        p ^ q -> ~(~p v ~q)
        """
        if not self.check_de_morgan_reverse(proposition):
            return proposition

        root = proposition.root
        left_operand = root.left
        right_operand = root.right

        not_left = CompoundProposition(Proposition.__invert__, self._node_to_compound(left_operand))
        not_right = CompoundProposition(Proposition.__invert__, self._node_to_compound(right_operand))

        if root.operator.name == '__add__':
            inner = CompoundProposition(Proposition.__mul__, not_left, not_right)
        else:
            inner = CompoundProposition(Proposition.__add__, not_left, not_right)

        return CompoundProposition(Proposition.__invert__, inner)

    # ==================== Commutativity ====================
    # p ^ q = q ^ p
    # p v q = q v p
    # NOTE: Implication is NOT commutative! (p → q ≠ q → p)

    def check_commutativity(self, proposition: CompoundProposition) -> bool:
        """Check if commutativity can be applied (only AND and OR, not implication)"""
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.right is None:
            return False
        # Only AND and OR are commutative, NOT implication
        return root.operator.name in ('__add__', '__mul__')

    def apply_commutativity(self, proposition: CompoundProposition) -> CompoundProposition:
        """Apply commutativity: p op q -> q op p"""
        if not self.check_commutativity(proposition):
            return proposition

        root = proposition.root
        left = self._node_to_compound(root.right)
        right = self._node_to_compound(root.left)
        return CompoundProposition(root.operator, left, right)

    # ==================== Associativity ====================
    # (p ^ q) ^ r = p ^ (q ^ r)
    # (p v q) v r = p v (q v r)
    # NOTE: Implication is NOT associative

    def check_associativity(self, proposition: CompoundProposition) -> bool:
        """Check if associativity can be applied: (p op q) op r -> p op (q op r)"""
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.right is None:
            return False
        # Only AND and OR are associative
        if root.operator.name not in ('__add__', '__mul__'):
            return False
        # Left child must be same operator
        left = root.left
        if not isinstance(left, OperatorNode):
            return False
        if left.right is None:
            return False
        return left.operator.name == root.operator.name

    def apply_associativity(self, proposition: CompoundProposition) -> CompoundProposition:
        """Apply associativity: (p op q) op r -> p op (q op r)"""
        if not self.check_associativity(proposition):
            return proposition

        root = proposition.root
        op = root.operator
        # (p op q) op r
        left_inner = root.left  # (p op q)
        p = left_inner.left
        q = left_inner.right
        r = root.right

        # p op (q op r)
        p_comp = self._node_to_compound(p)
        q_comp = self._node_to_compound(q)
        r_comp = self._node_to_compound(r)

        q_op_r = CompoundProposition(op, q_comp, r_comp)
        return CompoundProposition(op, p_comp, q_op_r)

    # ==================== Idempotence ====================
    # p ^ p = p
    # p v p = p
    # NOTE: p → p is a tautology (always true), NOT equal to p

    def check_idempotence(self, proposition: CompoundProposition) -> bool:
        """Check if idempotence can be applied: p op p -> p (only AND and OR)"""
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.right is None:
            return False
        # Only AND and OR have idempotence, NOT implication
        if root.operator.name not in ('__add__', '__mul__'):
            return False
        return self._nodes_equal(root.left, root.right)

    def apply_idempotence(self, proposition: CompoundProposition) -> CompoundProposition:
        """Apply idempotence: p op p -> p"""
        if not self.check_idempotence(proposition):
            return proposition
        return self._node_to_compound(proposition.root.left)

    # ==================== Absorption ====================
    # p ^ (p v q) = p
    # p v (p ^ q) = p

    def check_absorption(self, proposition: CompoundProposition) -> bool:
        """Check if absorption can be applied: p op (p op' q) -> p"""
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.right is None:
            return False

        outer_op = root.operator.name
        if outer_op not in ('__add__', '__mul__'):
            return False

        inner_op = '__mul__' if outer_op == '__add__' else '__add__'

        if isinstance(root.right, OperatorNode) and root.right.right is not None:
            if root.right.operator.name == inner_op:
                if self._nodes_equal(root.left, root.right.left):
                    return True
                if self._nodes_equal(root.left, root.right.right):
                    return True

        if isinstance(root.left, OperatorNode) and root.left.right is not None:
            if root.left.operator.name == inner_op:
                if self._nodes_equal(root.right, root.left.left):
                    return True
                if self._nodes_equal(root.right, root.left.right):
                    return True

        return False

    def apply_absorption(self, proposition: CompoundProposition) -> CompoundProposition:
        """Apply absorption: p op (p op' q) -> p"""
        if not self.check_absorption(proposition):
            return proposition

        root = proposition.root
        outer_op = root.operator.name
        inner_op = '__mul__' if outer_op == '__add__' else '__add__'

        if isinstance(root.right, OperatorNode) and root.right.right is not None:
            if root.right.operator.name == inner_op:
                if self._nodes_equal(root.left, root.right.left):
                    return self._node_to_compound(root.left)
                if self._nodes_equal(root.left, root.right.right):
                    return self._node_to_compound(root.left)

        if isinstance(root.left, OperatorNode) and root.left.right is not None:
            if root.left.operator.name == inner_op:
                if self._nodes_equal(root.right, root.left.left):
                    return self._node_to_compound(root.right)
                if self._nodes_equal(root.right, root.left.right):
                    return self._node_to_compound(root.right)

        return proposition

    # ==================== Distributivity ====================
    # p ^ (q v r) = (p ^ q) v (p ^ r)
    # p v (q ^ r) = (p v q) ^ (p v r)
    # NOTE: Distributivity only applies to AND/OR, not implication

    def check_distributivity(self, proposition: CompoundProposition) -> bool:
        """
        Check if distributive property can be applied.
        Example: p v (p ^ q) can be distributed because outer (v) != inner (^)
        Only applies to AND and OR operators.
        """
        root = proposition.root
        if not isinstance(root, OperatorNode) or root.right is None:
            return False

        outer_op = root.operator.name
        # Only AND and OR can be distributed
        if outer_op not in ('__add__', '__mul__'):
            return False

        return (self._can_distribute_child(root.left, outer_op) or
                self._can_distribute_child(root.right, outer_op))

    def _can_distribute_child(self, node, outer_op: str) -> bool:
        """Check if a child node can be distributed over (only AND/OR)."""
        if not isinstance(node, OperatorNode):
            return False
        if node.right is None:
            return False
        # Only AND and OR can be distributed over
        if node.operator.name not in ('__add__', '__mul__'):
            return False
        return node.operator.name != outer_op

    def apply_distributivity(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply distributivity:
        p ^ (q v r) -> (p ^ q) v (p ^ r)
        p v (q ^ r) -> (p v q) ^ (p v r)
        """
        if not self.check_distributivity(proposition):
            return proposition

        root = proposition.root
        outer_op = root.operator

        if self._can_distribute_child(root.right, outer_op.name):
            p = root.left
            inner = root.right
            q = inner.left
            r = inner.right
            inner_op = inner.operator
        else:
            p = root.right
            inner = root.left
            q = inner.left
            r = inner.right
            inner_op = inner.operator

        p_compound = self._node_to_compound(p)
        q_compound = self._node_to_compound(q)
        r_compound = self._node_to_compound(r)

        left_result = CompoundProposition(outer_op, p_compound, q_compound)
        right_result = CompoundProposition(outer_op, p_compound, r_compound)

        return CompoundProposition(inner_op, left_result, right_result)

    # ==================== Factoring (Reverse Distributivity) ====================
    # (p ^ q) v (p ^ r) = p ^ (q v r)
    # (p v q) ^ (p v r) = p v (q ^ r)
    # This is the SIMPLIFYING direction (reduces complexity)

    def check_factoring(self, proposition: CompoundProposition) -> bool:
        """
        Check if factoring (reverse distributivity) can be applied.
        Pattern: (p op q) op' (p op r) -> p op (q op' r)
        Where op and op' are different (one AND, one OR).

        Example: (p ^ q) v (p ^ r) -> p ^ (q v r)
        """
        root = proposition.root
        if not isinstance(root, OperatorNode) or root.right is None:
            return False

        outer_op = root.operator.name
        if outer_op not in ('__add__', '__mul__'):
            return False

        # Both children must be binary operations with the opposite operator
        left = root.left
        right = root.right

        if not isinstance(left, OperatorNode) or left.right is None:
            return False
        if not isinstance(right, OperatorNode) or right.right is None:
            return False

        # Inner operations must be the same and different from outer
        inner_op = '__mul__' if outer_op == '__add__' else '__add__'
        if left.operator.name != inner_op or right.operator.name != inner_op:
            return False

        # Check if there's a common factor
        # (p ^ q) v (p ^ r) - common factor p on left of both
        # (q ^ p) v (r ^ p) - common factor p on right of both
        # (p ^ q) v (r ^ p) - common factor p (left of first, right of second)
        # (q ^ p) v (p ^ r) - common factor p (right of first, left of second)

        left_left = left.left
        left_right = left.right
        right_left = right.left
        right_right = right.right

        # Check all four combinations for common factor
        if self._nodes_equal(left_left, right_left):
            return True  # p in both left positions
        if self._nodes_equal(left_left, right_right):
            return True  # p in left.left and right.right
        if self._nodes_equal(left_right, right_left):
            return True  # p in left.right and right.left
        if self._nodes_equal(left_right, right_right):
            return True  # p in both right positions

        return False

    def apply_factoring(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply factoring (reverse distributivity):
        (p ^ q) v (p ^ r) -> p ^ (q v r)
        (p v q) ^ (p v r) -> p v (q ^ r)
        """
        if not self.check_factoring(proposition):
            return proposition

        root = proposition.root
        outer_op = root.operator  # v in (p^q) v (p^r)
        inner_op_name = '__mul__' if outer_op.name == '__add__' else '__add__'
        inner_op = Proposition.__mul__ if inner_op_name == '__mul__' else Proposition.__add__

        left = root.left   # (p ^ q)
        right = root.right  # (p ^ r)

        left_left = left.left
        left_right = left.right
        right_left = right.left
        right_right = right.right

        # Find the common factor and the remainders
        common = None
        remainder1 = None
        remainder2 = None

        if self._nodes_equal(left_left, right_left):
            common = left_left
            remainder1 = left_right
            remainder2 = right_right
        elif self._nodes_equal(left_left, right_right):
            common = left_left
            remainder1 = left_right
            remainder2 = right_left
        elif self._nodes_equal(left_right, right_left):
            common = left_right
            remainder1 = left_left
            remainder2 = right_right
        elif self._nodes_equal(left_right, right_right):
            common = left_right
            remainder1 = left_left
            remainder2 = right_left

        if common is None:
            return proposition

        common_comp = self._node_to_compound(common)
        rem1_comp = self._node_to_compound(remainder1)
        rem2_comp = self._node_to_compound(remainder2)

        # Build: common inner_op (remainder1 outer_op remainder2)
        # e.g., p ^ (q v r)
        inner_result = CompoundProposition(outer_op, rem1_comp, rem2_comp)
        return CompoundProposition(inner_op, common_comp, inner_result)

    # ==================== Implication Laws ====================
    # Implication Elimination: p → q = ~p v q
    # Contraposition: p → q = ~q → ~p

    def check_implication_elimination(self, proposition: CompoundProposition) -> bool:
        """Check if implication elimination can be applied: p → q -> ~p v q"""
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        return root.operator.name == '__rshift__' and root.right is not None

    def apply_implication_elimination(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply implication elimination: p → q -> ~p v q

        This converts an implication to its equivalent disjunction form.
        """
        if not self.check_implication_elimination(proposition):
            return proposition

        root = proposition.root
        left_operand = root.left
        right_operand = root.right

        # ~p
        not_left = CompoundProposition(Proposition.__invert__, self._node_to_compound(left_operand))
        # ~p v q
        return CompoundProposition(Proposition.__add__, not_left, self._node_to_compound(right_operand))

    def check_implication_introduction(self, proposition: CompoundProposition) -> bool:
        """
        Check if implication introduction can be applied: ~p v q -> p → q

        Pattern: The left operand must be a negation.
        """
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.operator.name != '__add__' or root.right is None:
            return False
        # Check if left is a negation
        left = root.left
        if not isinstance(left, OperatorNode):
            return False
        return left.operator.name == '__invert__' and left.right is None

    def apply_implication_introduction(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply implication introduction: ~p v q -> p → q

        This converts a disjunction with a negated left operand to an implication.
        """
        if not self.check_implication_introduction(proposition):
            return proposition

        root = proposition.root
        # Get p from ~p (the inner operand of the negation)
        p = root.left.left
        q = root.right

        return CompoundProposition(Proposition.__rshift__, self._node_to_compound(p), self._node_to_compound(q))

    def check_contraposition(self, proposition: CompoundProposition) -> bool:
        """Check if contraposition can be applied: p → q -> ~q → ~p"""
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        return root.operator.name == '__rshift__' and root.right is not None

    def apply_contraposition(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply contraposition: p → q -> ~q → ~p

        This transforms an implication to its contrapositive form.
        """
        if not self.check_contraposition(proposition):
            return proposition

        root = proposition.root
        p = root.left
        q = root.right

        # ~q
        not_q = CompoundProposition(Proposition.__invert__, self._node_to_compound(q))
        # ~p
        not_p = CompoundProposition(Proposition.__invert__, self._node_to_compound(p))
        # ~q → ~p
        return CompoundProposition(Proposition.__rshift__, not_q, not_p)

    # ==================== Truth Constant Laws ====================
    # Identity: p v F = p, p ^ T = p
    # Domination: p v T = T, p ^ F = F
    # Negation: ~T = F, ~F = T
    # Complement: p v ~p = T, p ^ ~p = F

    def _is_true_constant(self, node) -> bool:
        """Check if node represents the True constant."""
        if isinstance(node, AtomicNode):
            prop = node.proposition
            return hasattr(prop, 'is_constant') and prop.is_constant() and prop.is_true()
        if hasattr(node, 'is_constant') and node.is_constant():
            return node.is_true()
        return False

    def _is_false_constant(self, node) -> bool:
        """Check if node represents the False constant."""
        if isinstance(node, AtomicNode):
            prop = node.proposition
            return hasattr(prop, 'is_constant') and prop.is_constant() and prop.is_false()
        if hasattr(node, 'is_constant') and node.is_constant():
            return node.is_false()
        return False

    def _is_constant(self, node) -> bool:
        """Check if node is a truth constant (T or F)."""
        if isinstance(node, AtomicNode):
            prop = node.proposition
            return hasattr(prop, 'is_constant') and prop.is_constant()
        return hasattr(node, 'is_constant') and node.is_constant()

    def check_identity(self, proposition: CompoundProposition) -> bool:
        """
        Check if identity law can be applied:
        - p v F = p
        - p ^ T = p
        """
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.right is None:
            return False

        # p v F
        if root.operator.name == '__add__':
            return self._is_false_constant(root.left) or self._is_false_constant(root.right)

        # p ^ T
        if root.operator.name == '__mul__':
            return self._is_true_constant(root.left) or self._is_true_constant(root.right)

        return False

    def apply_identity(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply identity law:
        - p v F -> p
        - p ^ T -> p
        """
        if not self.check_identity(proposition):
            return proposition

        root = proposition.root

        if root.operator.name == '__add__':
            # p v F -> p
            if self._is_false_constant(root.right):
                return self._node_to_compound(root.left)
            if self._is_false_constant(root.left):
                return self._node_to_compound(root.right)

        if root.operator.name == '__mul__':
            # p ^ T -> p
            if self._is_true_constant(root.right):
                return self._node_to_compound(root.left)
            if self._is_true_constant(root.left):
                return self._node_to_compound(root.right)

        return proposition

    def check_domination(self, proposition: CompoundProposition) -> bool:
        """
        Check if domination law can be applied:
        - p v T = T
        - p ^ F = F
        """
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.right is None:
            return False

        # p v T
        if root.operator.name == '__add__':
            return self._is_true_constant(root.left) or self._is_true_constant(root.right)

        # p ^ F
        if root.operator.name == '__mul__':
            return self._is_false_constant(root.left) or self._is_false_constant(root.right)

        return False

    def apply_domination(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply domination law:
        - p v T -> T
        - p ^ F -> F
        """
        if not self.check_domination(proposition):
            return proposition

        root = proposition.root

        if root.operator.name == '__add__':
            # p v T -> T
            return TRUE

        if root.operator.name == '__mul__':
            # p ^ F -> F
            return FALSE

        return proposition

    def check_negation_constant(self, proposition: CompoundProposition) -> bool:
        """
        Check if negation of constant can be simplified:
        - ~T = F
        - ~F = T
        """
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.operator.name != '__invert__' or root.right is not None:
            return False

        return self._is_constant(root.left)

    def apply_negation_constant(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply negation of constant:
        - ~T -> F
        - ~F -> T
        """
        if not self.check_negation_constant(proposition):
            return proposition

        inner = proposition.root.left

        if self._is_true_constant(inner):
            return FALSE
        if self._is_false_constant(inner):
            return TRUE

        return proposition

    def check_complement(self, proposition: CompoundProposition) -> bool:
        """
        Check if complement law can be applied:
        - p v ~p = T
        - p ^ ~p = F
        """
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.right is None:
            return False
        if root.operator.name not in ('__add__', '__mul__'):
            return False

        # Check if one side is the negation of the other
        # Case: p op ~p
        if isinstance(root.right, OperatorNode):
            if root.right.operator.name == '__invert__' and root.right.right is None:
                if self._nodes_equal(root.left, root.right.left):
                    return True

        # Case: ~p op p
        if isinstance(root.left, OperatorNode):
            if root.left.operator.name == '__invert__' and root.left.right is None:
                if self._nodes_equal(root.left.left, root.right):
                    return True

        return False

    def apply_complement(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply complement law:
        - p v ~p -> T
        - p ^ ~p -> F
        """
        if not self.check_complement(proposition):
            return proposition

        root = proposition.root

        if root.operator.name == '__add__':
            # p v ~p -> T
            return TRUE

        if root.operator.name == '__mul__':
            # p ^ ~p -> F
            return FALSE

        return proposition

    def check_implication_constant(self, proposition: CompoundProposition) -> bool:
        """
        Check if implication with constant can be simplified:
        - T → p = p
        - F → p = T
        - p → T = T
        - p → F = ~p
        """
        root = proposition.root
        if not isinstance(root, OperatorNode):
            return False
        if root.operator.name != '__rshift__' or root.right is None:
            return False

        return (self._is_constant(root.left) or self._is_constant(root.right))

    def apply_implication_constant(self, proposition: CompoundProposition) -> CompoundProposition:
        """
        Apply implication with constant:
        - T → p -> p
        - F → p -> T
        - p → T -> T
        - p → F -> ~p
        """
        if not self.check_implication_constant(proposition):
            return proposition

        root = proposition.root
        left = root.left
        right = root.right

        # T → p -> p
        if self._is_true_constant(left):
            return self._node_to_compound(right)

        # F → p -> T
        if self._is_false_constant(left):
            return TRUE

        # p → T -> T
        if self._is_true_constant(right):
            return TRUE

        # p → F -> ~p
        if self._is_false_constant(right):
            return CompoundProposition(Proposition.__invert__, self._node_to_compound(left))

        return proposition

    # ==================== Helper Methods ====================

    def _node_to_compound(self, node: PropositionNode):
        """Convert a node back to a CompoundProposition or Proposition."""
        if isinstance(node, AtomicNode):
            # Return the raw proposition (Proposition or TruthConstant)
            # The caller may need to wrap it in _ensure_compound if needed
            return node.proposition
        elif isinstance(node, OperatorNode):
            left = self._node_to_compound(node.left)
            right = self._node_to_compound(node.right) if node.right else None
            return CompoundProposition(node.operator, left, right)
        return node

    def _node_to_compound_safe(self, node: PropositionNode) -> CompoundProposition:
        """Convert a node to a CompoundProposition, ensuring it's always compound."""
        result = self._node_to_compound(node)
        if isinstance(result, CompoundProposition):
            return result
        # It's a Proposition or TruthConstant - wrap it
        return self._ensure_compound(result)

    def _nodes_equal(self, node1: PropositionNode, node2: PropositionNode) -> bool:
        """Check if two nodes represent the same proposition structure."""
        if type(node1) != type(node2):
            return False

        if isinstance(node1, AtomicNode):
            return node1.proposition.text == node2.proposition.text

        if isinstance(node1, OperatorNode):
            if node1.operator.name != node2.operator.name:
                return False
            if not self._nodes_equal(node1.left, node2.left):
                return False
            if node1.right is None and node2.right is None:
                return True
            if node1.right is None or node2.right is None:
                return False
            return self._nodes_equal(node1.right, node2.right)

        return False

    # ==================== Syntactic Equality ====================

    def are_equal(self, prop1, prop2) -> bool:
        """
        Check if two propositions are syntactically equal.

        Args:
            prop1: First proposition (Proposition or CompoundProposition)
            prop2: Second proposition (Proposition or CompoundProposition)

        Returns:
            True if both propositions have the same structure and symbols
        """
        node1 = self._to_node(prop1)
        node2 = self._to_node(prop2)
        return self._nodes_equal(node1, node2)

    def _to_node(self, prop) -> PropositionNode:
        """Convert a Proposition or CompoundProposition to a node."""
        if isinstance(prop, PropositionNode):
            return prop
        elif isinstance(prop, Proposition):
            return AtomicNode(prop)
        elif isinstance(prop, CompoundProposition):
            return prop.root
        raise TypeError(f"Cannot convert {type(prop)} to node")

    # ==================== Brute Force Equivalence Prover ====================

    def prove_equivalence(self, prop1: CompoundProposition, prop2: CompoundProposition,
                          max_iterations: int = 100, verbose: bool = False) -> dict:
        """
        Try to prove that two propositions are equivalent by randomly applying
        equivalence laws until they become syntactically equal.

        Args:
            prop1: First compound proposition
            prop2: Second compound proposition
            max_iterations: Maximum number of transformation attempts (default: 100)
            verbose: If True, print each transformation step

        Returns:
            dict with keys:
                - 'success': bool - True if equivalence was proven
                - 'iterations': int - Number of iterations performed
                - 'prop1_final': The final form of prop1
                - 'prop2_final': The final form of prop2
                - 'transformations': List of transformations applied
        """
        transformations = [
            # High priority: Simplification operations
            ('double_negation', self.check_double_negation, self.apply_double_negation),
            ('idempotence', self.check_idempotence, self.apply_idempotence),
            ('absorption', self.check_absorption, self.apply_absorption),
            ('factoring', self.check_factoring, self.apply_factoring),  # Reverse distributivity (simplifies)
            # Truth constant laws (simplification)
            ('identity', self.check_identity, self.apply_identity),
            ('domination', self.check_domination, self.apply_domination),
            ('negation_constant', self.check_negation_constant, self.apply_negation_constant),
            ('complement', self.check_complement, self.apply_complement),
            ('implication_constant', self.check_implication_constant, self.apply_implication_constant),
            # Structure transformations
            ('de_morgan', self.check_de_morgan, self.apply_de_morgan),
            ('commutativity', self.check_commutativity, self.apply_commutativity),
            ('implication_elimination', self.check_implication_elimination, self.apply_implication_elimination),
            ('implication_introduction', self.check_implication_introduction, self.apply_implication_introduction),
            ('contraposition', self.check_contraposition, self.apply_contraposition),
            # Lower priority (can increase complexity)
            ('de_morgan_reverse', self.check_de_morgan_reverse, self.apply_de_morgan_reverse),
            ('distributivity', self.check_distributivity, self.apply_distributivity),
        ]

        current1 = self._ensure_compound(prop1)
        current2 = self._ensure_compound(prop2)
        applied_transformations = []

        if verbose:
            print(f"Iniciando prova:")
            print(f"  Prop 1: {current1}")
            print(f"  Prop 2: {current2}")
            print()

        # Separate transformations by priority
        simplification_transforms = self._get_simplification_transformations()
        structure_transforms = self._get_structure_transformations()
        expansion_transforms = self._get_expansion_transformations()

        for iteration in range(max_iterations):
            if self.are_equal(current1, current2):
                if verbose:
                    print(f"\nProposições são iguais após {iteration} iterações!")
                return {
                    'success': True,
                    'iterations': iteration,
                    'prop1_final': current1,
                    'prop2_final': current2,
                    'transformations': applied_transformations
                }

            which_prop = random.choice([1, 2])
            current_prop = current1 if which_prop == 1 else current2

            # Priority 1: Try simplification transformations first (in order)
            applied = False
            matched_subexpr = None
            for name, check_fn, apply_fn in simplification_transforms:
                if self._can_apply_anywhere(current_prop, check_fn):
                    new_prop, matched_subexpr = self._apply_random_transformation_with_location(current_prop, check_fn, apply_fn)
                    applied = True
                    break

            # Priority 2: If no simplification, try structure transformations (random)
            if not applied:
                applicable_structure = [
                    (name, check_fn, apply_fn)
                    for name, check_fn, apply_fn in structure_transforms
                    if self._can_apply_anywhere(current_prop, check_fn)
                ]
                if applicable_structure:
                    name, check_fn, apply_fn = random.choice(applicable_structure)
                    new_prop, matched_subexpr = self._apply_random_transformation_with_location(current_prop, check_fn, apply_fn)
                    applied = True

            # Priority 3: Only use expansion if nothing else works (10% chance)
            if not applied and random.random() < 0.1:
                applicable_expansion = [
                    (name, check_fn, apply_fn)
                    for name, check_fn, apply_fn in expansion_transforms
                    if self._can_apply_anywhere(current_prop, check_fn)
                ]
                if applicable_expansion:
                    name, check_fn, apply_fn = random.choice(applicable_expansion)
                    new_prop, matched_subexpr = self._apply_random_transformation_with_location(current_prop, check_fn, apply_fn)
                    applied = True

            if not applied:
                continue

            if which_prop == 1:
                current1 = new_prop
            else:
                current2 = new_prop

            applied_transformations.append({
                'iteration': iteration,
                'proposition': which_prop,
                'law': name,
                'result': str(new_prop),
                'matched_subexpr': matched_subexpr,
                'p1': str(current1),
                'p2': str(current2)
            })

            if verbose:
                print(f"[{iteration}] Aplicado {name} em prop{which_prop}: {new_prop}")

        if self.are_equal(current1, current2):
            return {
                'success': True,
                'iterations': max_iterations,
                'prop1_final': current1,
                'prop2_final': current2,
                'transformations': applied_transformations
            }

        if verbose:
            print(f"\nFalha ao provar equivalência após {max_iterations} iterações.")
            print(f"  Prop 1 final: {current1}")
            print(f"  Prop 2 final: {current2}")

        return {
            'success': False,
            'iterations': max_iterations,
            'prop1_final': current1,
            'prop2_final': current2,
            'transformations': applied_transformations
        }

    def _ensure_compound(self, prop) -> CompoundProposition:
        """Ensure the proposition is a CompoundProposition."""
        if isinstance(prop, CompoundProposition):
            return prop
        elif isinstance(prop, Proposition):
            cp = CompoundProposition()
            cp.root = AtomicNode(prop)
            # Constants don't count as regular components
            cp.components = set() if prop.is_constant() else {prop}
            return cp
        raise TypeError(f"Expected Proposition or CompoundProposition, got {type(prop)}")

    def _can_apply_anywhere(self, prop, check_fn) -> bool:
        """Check if a transformation can be applied anywhere in the tree."""
        # Handle non-CompoundProposition inputs
        if not isinstance(prop, CompoundProposition):
            return False

        if check_fn(prop):
            return True

        if prop.root is None:
            return False

        return self._can_apply_to_subtree(prop.root, check_fn)

    def _can_apply_to_subtree(self, node: PropositionNode, check_fn) -> bool:
        """Recursively check if transformation can be applied to any subtree."""
        if isinstance(node, AtomicNode):
            return False

        if isinstance(node, OperatorNode):
            sub_prop = self._node_to_compound(node)
            if isinstance(sub_prop, CompoundProposition) and check_fn(sub_prop):
                return True

            if self._can_apply_to_subtree(node.left, check_fn):
                return True
            if node.right and self._can_apply_to_subtree(node.right, check_fn):
                return True

        return False

    def _apply_random_transformation(self, prop: CompoundProposition, check_fn, apply_fn) -> CompoundProposition:
        """Apply transformation at a random applicable location in the tree."""
        result, _ = self._apply_random_transformation_with_location(prop, check_fn, apply_fn)
        return result

    def _apply_random_transformation_with_location(self, prop: CompoundProposition, check_fn, apply_fn) -> tuple:
        """
        Apply transformation at a random applicable location in the tree.
        Returns: (new_proposition, matched_subexpression_string)
        """
        applicable_locations = []

        if check_fn(prop):
            applicable_locations.append('root')

        self._find_applicable_locations(prop.root, check_fn, [], applicable_locations)

        if not applicable_locations:
            return prop, None

        location = random.choice(applicable_locations)

        if location == 'root':
            # Don't show subexpression when applied to entire proposition
            result = apply_fn(prop)
            # Ensure result is always a CompoundProposition
            if not isinstance(result, CompoundProposition):
                result = self._ensure_compound(result)
            return result, None

        # Get the matched subexpression before applying
        matched_subexpr = self._get_subexpr_at_path(prop, location)
        result = self._apply_at_path(prop, location, apply_fn)
        return result, matched_subexpr

    def _get_subexpr_at_path(self, prop: CompoundProposition, path: list) -> str:
        """Get the string representation of the subexpression at the given path."""
        node = prop.root
        for direction in path:
            if isinstance(node, OperatorNode):
                if direction == 'left':
                    node = node.left
                elif direction == 'right':
                    node = node.right
            else:
                break
        sub_prop = self._node_to_compound(node)
        return str(sub_prop) if sub_prop else None

    def _get_simplification_transformations(self):
        """Return transformations that simplify (reduce complexity)."""
        return [
            ('double_negation', self.check_double_negation, self.apply_double_negation),
            ('idempotence', self.check_idempotence, self.apply_idempotence),
            ('absorption', self.check_absorption, self.apply_absorption),
            ('factoring', self.check_factoring, self.apply_factoring),
            ('identity', self.check_identity, self.apply_identity),
            ('domination', self.check_domination, self.apply_domination),
            ('negation_constant', self.check_negation_constant, self.apply_negation_constant),
            ('complement', self.check_complement, self.apply_complement),
            ('implication_constant', self.check_implication_constant, self.apply_implication_constant),
            ('implication_elimination', self.check_implication_elimination, self.apply_implication_elimination),
        ]

    def _get_structure_transformations(self):
        """Return transformations that change structure without increasing complexity much."""
        return [
            ('de_morgan', self.check_de_morgan, self.apply_de_morgan),
            ('commutativity', self.check_commutativity, self.apply_commutativity),
            ('associativity', self.check_associativity, self.apply_associativity),
            ('contraposition', self.check_contraposition, self.apply_contraposition),
        ]

    def _get_expansion_transformations(self):
        """Return transformations that increase complexity (use sparingly)."""
        return [
            ('de_morgan_reverse', self.check_de_morgan_reverse, self.apply_de_morgan_reverse),
            ('distributivity', self.check_distributivity, self.apply_distributivity),
            ('implication_introduction', self.check_implication_introduction, self.apply_implication_introduction),
        ]

    def _find_applicable_locations(self, node: PropositionNode, check_fn, path: list, locations: list):
        """Find all paths where the transformation can be applied."""
        if isinstance(node, AtomicNode):
            return

        if isinstance(node, OperatorNode):
            if node.left:
                sub_prop = self._node_to_compound(node.left)
                if isinstance(sub_prop, CompoundProposition) and check_fn(sub_prop):
                    locations.append(path + ['left'])
                self._find_applicable_locations(node.left, check_fn, path + ['left'], locations)

            if node.right:
                sub_prop = self._node_to_compound(node.right)
                if isinstance(sub_prop, CompoundProposition) and check_fn(sub_prop):
                    locations.append(path + ['right'])
                self._find_applicable_locations(node.right, check_fn, path + ['right'], locations)

    def _apply_at_path(self, prop: CompoundProposition, path: list, apply_fn) -> CompoundProposition:
        """Apply transformation at a specific path in the tree."""
        new_root = self._apply_at_path_recursive(prop.root, path, apply_fn)
        result = CompoundProposition()
        result.root = new_root
        result.components = new_root.get_components() if new_root else set()
        return result

    def _apply_at_path_recursive(self, node: PropositionNode, path: list, apply_fn) -> PropositionNode:
        """Recursively navigate to path and apply transformation."""
        if not path:
            sub_prop = self._node_to_compound(node)
            if isinstance(sub_prop, CompoundProposition):
                result = apply_fn(sub_prop)
                if isinstance(result, CompoundProposition):
                    return result.root
                elif isinstance(result, Proposition):
                    return AtomicNode(result)
            return node

        if isinstance(node, OperatorNode):
            direction = path[0]
            remaining_path = path[1:]

            if direction == 'left':
                new_left = self._apply_at_path_recursive(node.left, remaining_path, apply_fn)
                return OperatorNode(node.operator, new_left, node.right)
            elif direction == 'right':
                new_right = self._apply_at_path_recursive(node.right, remaining_path, apply_fn)
                return OperatorNode(node.operator, node.left, new_right)

        return node

    # ==================== Neural Network Guided Prover ====================

    def prove_equivalence_nn(self, prop1: CompoundProposition, prop2: CompoundProposition,
                              predictor, max_iterations: int = 100,
                              verbose: bool = False) -> dict:
        """
        Prove equivalence using neural network to guide transformations.

        The neural network predicts which proposition to transform and which
        transformation to apply. Falls back to random if prediction is not applicable.

        Args:
            prop1: First compound proposition
            prop2: Second compound proposition
            predictor: Trained TransformationPredictor instance
            max_iterations: Maximum number of transformation attempts
            verbose: If True, print each transformation step

        Returns:
            dict with keys:
                - 'success': bool - True if equivalence was proven
                - 'iterations': int - Number of iterations performed
                - 'prop1_final': The final form of prop1
                - 'prop2_final': The final form of prop2
                - 'transformations': List of transformations applied
                - 'nn_predictions_used': Number of times NN prediction was used
        """
        transformations = {
            # Simplification operations
            'double_negation': (self.check_double_negation, self.apply_double_negation),
            'idempotence': (self.check_idempotence, self.apply_idempotence),
            'absorption': (self.check_absorption, self.apply_absorption),
            'factoring': (self.check_factoring, self.apply_factoring),  # Reverse distributivity
            # Truth constant laws
            'identity': (self.check_identity, self.apply_identity),
            'domination': (self.check_domination, self.apply_domination),
            'negation_constant': (self.check_negation_constant, self.apply_negation_constant),
            'complement': (self.check_complement, self.apply_complement),
            'implication_constant': (self.check_implication_constant, self.apply_implication_constant),
            # Structure transformations
            'de_morgan': (self.check_de_morgan, self.apply_de_morgan),
            'commutativity': (self.check_commutativity, self.apply_commutativity),
            'associativity': (self.check_associativity, self.apply_associativity),
            'implication_elimination': (self.check_implication_elimination, self.apply_implication_elimination),
            'implication_introduction': (self.check_implication_introduction, self.apply_implication_introduction),
            'contraposition': (self.check_contraposition, self.apply_contraposition),
            # Lower priority
            'de_morgan_reverse': (self.check_de_morgan_reverse, self.apply_de_morgan_reverse),
            'distributivity': (self.check_distributivity, self.apply_distributivity),
        }

        current1 = self._ensure_compound(prop1)
        current2 = self._ensure_compound(prop2)
        applied_transformations = []
        nn_predictions_used = 0

        if verbose:
            print(f"Iniciando prova guiada por NN:")
            print(f"  Prop 1: {current1}")
            print(f"  Prop 2: {current2}")
            print()

        for iteration in range(max_iterations):
            if self.are_equal(current1, current2):
                if verbose:
                    print(f"\nProposições são iguais após {iteration} iterações!")
                    print(f"Predições NN usadas: {nn_predictions_used}")
                return {
                    'success': True,
                    'iterations': iteration,
                    'prop1_final': current1,
                    'prop2_final': current2,
                    'transformations': applied_transformations,
                    'nn_predictions_used': nn_predictions_used
                }

            # Get NN prediction
            which_prop, transform_name = predictor.predict(current1, current2)
            current_prop = current1 if which_prop == 1 else current2

            # Check if prediction is applicable
            used_nn = False
            matched_subexpr = None
            if transform_name in transformations:
                check_fn, apply_fn = transformations[transform_name]
                if self._can_apply_anywhere(current_prop, check_fn):
                    new_prop, matched_subexpr = self._apply_random_transformation_with_location(current_prop, check_fn, apply_fn)
                    used_nn = True
                    nn_predictions_used += 1

            # Fall back to PRIORITIZED selection if NN prediction not applicable
            # Use same priority as regular prover: simplification > structure > expansion
            if not used_nn:
                applied = False

                # Priority 1: Try simplification transformations (in order)
                simplification_transforms = self._get_simplification_transformations()
                for t_name, check_fn, apply_fn in simplification_transforms:
                    for prop_idx, prop in [(1, current1), (2, current2)]:
                        if self._can_apply_anywhere(prop, check_fn):
                            new_prop, matched_subexpr = self._apply_random_transformation_with_location(prop, check_fn, apply_fn)
                            which_prop = prop_idx
                            transform_name = t_name
                            applied = True
                            break
                    if applied:
                        break

                # Priority 2: Try structure transformations (random among applicable)
                if not applied:
                    structure_transforms = self._get_structure_transformations()
                    applicable_structure = []
                    for t_name, check_fn, apply_fn in structure_transforms:
                        for prop_idx, prop in [(1, current1), (2, current2)]:
                            if self._can_apply_anywhere(prop, check_fn):
                                applicable_structure.append((t_name, check_fn, apply_fn, prop_idx, prop))

                    if applicable_structure:
                        t_name, check_fn, apply_fn, which_prop, prop = random.choice(applicable_structure)
                        new_prop, matched_subexpr = self._apply_random_transformation_with_location(prop, check_fn, apply_fn)
                        transform_name = t_name
                        applied = True

                # Priority 3: Expansion only with 10% chance
                if not applied and random.random() < 0.1:
                    expansion_transforms = self._get_expansion_transformations()
                    applicable_expansion = []
                    for t_name, check_fn, apply_fn in expansion_transforms:
                        for prop_idx, prop in [(1, current1), (2, current2)]:
                            if self._can_apply_anywhere(prop, check_fn):
                                applicable_expansion.append((t_name, check_fn, apply_fn, prop_idx, prop))

                    if applicable_expansion:
                        t_name, check_fn, apply_fn, which_prop, prop = random.choice(applicable_expansion)
                        new_prop, matched_subexpr = self._apply_random_transformation_with_location(prop, check_fn, apply_fn)
                        transform_name = t_name
                        applied = True

                if not applied:
                    continue

            if which_prop == 1:
                current1 = new_prop
            else:
                current2 = new_prop

            applied_transformations.append({
                'iteration': iteration,
                'proposition': which_prop,
                'law': transform_name,
                'result': str(new_prop),
                'used_nn': used_nn,
                'matched_subexpr': matched_subexpr,
                'p1': str(current1),
                'p2': str(current2)
            })

            if verbose:
                nn_marker = "[NN]" if used_nn else "[RND]"
                print(f"[{iteration}] {nn_marker} Aplicado {transform_name} em prop{which_prop}: {new_prop}")

        # Final check
        if self.are_equal(current1, current2):
            return {
                'success': True,
                'iterations': max_iterations,
                'prop1_final': current1,
                'prop2_final': current2,
                'transformations': applied_transformations,
                'nn_predictions_used': nn_predictions_used
            }

        if verbose:
            print(f"\nFalha ao provar equivalência após {max_iterations} iterações.")
            print(f"Predições NN usadas: {nn_predictions_used}")
            print(f"  Prop 1 final: {current1}")
            print(f"  Prop 2 final: {current2}")

        return {
            'success': False,
            'iterations': max_iterations,
            'prop1_final': current1,
            'prop2_final': current2,
            'transformations': applied_transformations,
            'nn_predictions_used': nn_predictions_used
        }

    def prove_equivalence_bidirectional(self, prop1: CompoundProposition, prop2: CompoundProposition,
                                         predictor, max_iterations: int = 50,
                                         verbose: bool = False) -> dict:
        """
        Prove equivalence by showing both implications hold:
        P1 ≡ P2 if and only if (P1 → P2) = T and (P2 → P1) = T

        This is a fallback strategy when direct transformation fails.
        Some equivalences are easier to prove by showing both directions.

        Args:
            prop1: First compound proposition
            prop2: Second compound proposition
            predictor: Trained TransformationPredictor instance
            max_iterations: Maximum iterations per direction
            verbose: If True, print proof steps

        Returns:
            dict with keys:
                - 'success': bool - True if equivalence was proven
                - 'method': 'bidirectional' if successful
                - 'forward_proof': Result of proving P1 → P2 = T
                - 'backward_proof': Result of proving P2 → P1 = T
                - 'iterations': Total iterations used
        """
        from utils.proposition import TRUE

        current1 = self._ensure_compound(prop1)
        current2 = self._ensure_compound(prop2)

        # Create T as target
        t_prop = CompoundProposition()
        t_prop.root = AtomicNode(TRUE)
        t_prop.components = {TRUE}

        if verbose:
            print("\n" + "="*50)
            print("ESTRATÉGIA DE PROVA BIDIRECIONAL")
            print("="*50)
            print(f"Provar: {current1} ≡ {current2}")
            print(f"Estratégia: Mostrar (P1 → P2) = T E (P2 → P1) = T")
            print()

        # Constrói P1 → P2
        forward_impl = CompoundProposition(Proposition.__rshift__, current1, current2)

        if verbose:
            print("-"*50)
            print(f"PASSO 1: Provar ({current1}) → ({current2}) = T")
            print("-"*50)

        # Prove P1 → P2 = T
        forward_result = self.prove_equivalence_nn(
            forward_impl, t_prop, predictor,
            max_iterations=max_iterations, verbose=verbose
        )

        if not forward_result['success']:
            if verbose:
                print(f"\n[FALHA] Não foi possível provar P1 → P2 = T")
            return {
                'success': False,
                'method': 'bidirectional',
                'forward_proof': forward_result,
                'backward_proof': None,
                'iterations': forward_result['iterations'],
                'reason': 'forward_implication_failed'
            }

        if verbose:
            print(f"\n[SUCESSO] P1 → P2 = T provado em {forward_result['iterations']} passos")

        # Constrói P2 → P1
        backward_impl = CompoundProposition(Proposition.__rshift__, current2, current1)

        if verbose:
            print()
            print("-"*50)
            print(f"PASSO 2: Provar ({current2}) → ({current1}) = T")
            print("-"*50)

        # Prove P2 → P1 = T
        backward_result = self.prove_equivalence_nn(
            backward_impl, t_prop, predictor,
            max_iterations=max_iterations, verbose=verbose
        )

        if not backward_result['success']:
            if verbose:
                print(f"\n[FALHA] Não foi possível provar P2 → P1 = T")
            return {
                'success': False,
                'method': 'bidirectional',
                'forward_proof': forward_result,
                'backward_proof': backward_result,
                'iterations': forward_result['iterations'] + backward_result['iterations'],
                'reason': 'backward_implication_failed'
            }

        if verbose:
            print(f"\n[SUCESSO] P2 → P1 = T provado em {backward_result['iterations']} passos")
            print()
            print("="*50)
            print("PROVA BIDIRECIONAL COMPLETA!")
            print(f"Como (P1 → P2) = T e (P2 → P1) = T,")
            print(f"concluímos P1 ≡ P2")
            print("="*50)

        total_iterations = forward_result['iterations'] + backward_result['iterations']
        total_nn = forward_result['nn_predictions_used'] + backward_result['nn_predictions_used']

        return {
            'success': True,
            'method': 'bidirectional',
            'forward_proof': forward_result,
            'backward_proof': backward_result,
            'iterations': total_iterations,
            'nn_predictions_used': total_nn
        }

    def prove_by_contrapositive(self, prop1: CompoundProposition, prop2: CompoundProposition,
                                  predictor, max_iterations: int = 50,
                                  verbose: bool = False) -> dict:
        """
        Prove equivalence by contrapositive: P1 ≡ P2 iff ~P1 ≡ ~P2

        Sometimes proving the negations are equivalent is easier than
        proving the original propositions are equivalent.

        Args:
            prop1: First compound proposition
            prop2: Second compound proposition
            predictor: Trained TransformationPredictor instance
            max_iterations: Maximum iterations
            verbose: If True, print proof steps

        Returns:
            dict with proof result
        """
        current1 = self._ensure_compound(prop1)
        current2 = self._ensure_compound(prop2)

        if verbose:
            print("\n" + "="*50)
            print("ESTRATÉGIA DE PROVA POR CONTRAPOSITIVA")
            print("="*50)
            print(f"Provar: {current1} ≡ {current2}")
            print(f"Estratégia: Provar ~P1 ≡ ~P2")
            print()

        # Cria ~P1 e ~P2
        neg_p1 = CompoundProposition(Proposition.__invert__, current1)
        neg_p2 = CompoundProposition(Proposition.__invert__, current2)

        if verbose:
            print(f"Provando: {neg_p1} ≡ {neg_p2}")
            print("-"*50)

        # Prove ~P1 ≡ ~P2
        result = self.prove_equivalence_nn(
            neg_p1, neg_p2, predictor,
            max_iterations=max_iterations, verbose=verbose
        )

        if result['success']:
            if verbose:
                print(f"\n[SUCESSO] Prova por contrapositiva bem-sucedida!")
                print(f"Como ~P1 ≡ ~P2, concluímos P1 ≡ P2")

            return {
                'success': True,
                'method': 'contrapositive',
                'iterations': result['iterations'],
                'nn_predictions_used': result['nn_predictions_used'],
                'transformations': result['transformations'],
                'prop1_final': result['prop1_final'],
                'prop2_final': result['prop2_final']
            }

        return {
            'success': False,
            'method': 'contrapositive',
            'iterations': result['iterations'],
            'transformations': result.get('transformations', []),
            'prop1_final': result.get('prop1_final'),
            'prop2_final': result.get('prop2_final'),
            'reason': 'contrapositive_failed'
        }

    def prove_by_absurdity(self, prop1: CompoundProposition, prop2: CompoundProposition,
                           predictor, simplification_predictor=None, max_iterations: int = 50,
                           verbose: bool = False) -> dict:
        """
        Prova equivalência por redução ao absurdo (prova por contradição):
        P1 ≡ P2 sse (P1 ^ ~P2) = F (contradição)

        Se assumir P1 e ~P2 leva a uma contradição (F),
        então P1 implica P2. Combinado com a verificação semântica que
        já verificou que têm a mesma tabela verdade, isso prova equivalência.

        Args:
            prop1: Primeira proposição composta
            prop2: Segunda proposição composta
            predictor: Instância treinada de TransformationPredictor (fallback)
            simplification_predictor: Instância treinada de SimplificationPredictor (preferido)
            max_iterations: Máximo de iterações
            verbose: Se True, imprime passos da prova

        Returns:
            dict com resultado da prova
        """
        from utils.proposition import FALSE

        current1 = self._ensure_compound(prop1)
        current2 = self._ensure_compound(prop2)

        if verbose:
            print("\n" + "="*50)
            print("PROVA POR ABSURDO (Reductio ad Absurdum)")
            print("="*50)
            print(f"Provar: {current1} ≡ {current2}")
            print(f"Estratégia: Mostrar (P1 ^ ~P2) = F (contradição)")
            if simplification_predictor:
                print(f"Usando: SimplificationPredictor (especializado para absurdo)")
            print()

        # Create P1 ^ ~P2
        neg_p2 = CompoundProposition(Proposition.__invert__, current2)
        assumption = CompoundProposition(Proposition.__mul__, current1, neg_p2)

        # Create F as target
        f_prop = CompoundProposition()
        f_prop.root = AtomicNode(FALSE)
        f_prop.components = {FALSE}

        if verbose:
            print(f"Provando: {assumption} = F")
            print("-"*50)

        # Usa SimplificationPredictor se disponível (especializado para absurdo)
        if simplification_predictor:
            result = self.prove_simplification_nn(
                assumption, goal='F', predictor=simplification_predictor,
                fallback_predictor=predictor,
                max_iterations=max_iterations, verbose=verbose
            )
        else:
            # Fallback para predictor de convergência
            result = self.prove_equivalence_nn(
                assumption, f_prop, predictor,
                max_iterations=max_iterations, verbose=verbose
            )

        if result['success']:
            if verbose:
                print(f"\n[SUCESSO] Prova por absurdo bem-sucedida!")
                print(f"(P1 ^ ~P2) = F significa que P1 implica P2")
                print(f"Combinado com equivalência semântica, P1 ≡ P2")

            return {
                'success': True,
                'method': 'absurdity',
                'iterations': result['iterations'],
                'nn_predictions_used': result.get('nn_predictions_used', 0),
                'transformations': result['transformations'],
                'prop1_final': result.get('prop1_final', result.get('final_prop')),
                'prop2_final': result.get('prop2_final', f_prop)
            }

        return {
            'success': False,
            'method': 'absurdity',
            'iterations': result['iterations'],
            'transformations': result.get('transformations', []),
            'prop1_final': result.get('prop1_final', result.get('final_prop')),
            'prop2_final': result.get('prop2_final', f_prop),
            'reason': 'absurdity_failed'
        }

    def prove_simplification_nn(self, prop: CompoundProposition, goal: str,
                                 predictor, fallback_predictor=None,
                                 max_iterations: int = 50,
                                 verbose: bool = False) -> dict:
        """
        Simplify a single expression to a constant (F or T) using SimplificationPredictor.

        This is the core method for absurdity proofs. Unlike prove_equivalence_nn which
        tries to make two expressions converge, this simplifies a single expression
        towards a target constant.

        Args:
            prop: The proposition to simplify
            goal: Target constant - 'F' for absurdity, 'T' for tautology
            predictor: SimplificationPredictor instance
            fallback_predictor: TransformationPredictor for fallback (optional)
            max_iterations: Maximum transformation attempts
            verbose: If True, print each step

        Returns:
            dict with:
                - 'success': bool - True if reached the goal constant
                - 'iterations': Number of iterations
                - 'transformations': List of transformations applied
                - 'final_prop': Final form of the proposition
                - 'nn_predictions_used': Count of successful NN predictions
        """
        from utils.proposition import TRUE, FALSE

        transformations_map = {
            'double_negation': (self.check_double_negation, self.apply_double_negation),
            'idempotence': (self.check_idempotence, self.apply_idempotence),
            'absorption': (self.check_absorption, self.apply_absorption),
            'factoring': (self.check_factoring, self.apply_factoring),
            'identity': (self.check_identity, self.apply_identity),
            'domination': (self.check_domination, self.apply_domination),
            'negation_constant': (self.check_negation_constant, self.apply_negation_constant),
            'complement': (self.check_complement, self.apply_complement),
            'implication_constant': (self.check_implication_constant, self.apply_implication_constant),
            'de_morgan': (self.check_de_morgan, self.apply_de_morgan),
            'commutativity': (self.check_commutativity, self.apply_commutativity),
            'associativity': (self.check_associativity, self.apply_associativity),
            'implication_elimination': (self.check_implication_elimination, self.apply_implication_elimination),
            'implication_introduction': (self.check_implication_introduction, self.apply_implication_introduction),
            'contraposition': (self.check_contraposition, self.apply_contraposition),
            'de_morgan_reverse': (self.check_de_morgan_reverse, self.apply_de_morgan_reverse),
            'distributivity': (self.check_distributivity, self.apply_distributivity),
        }

        current = self._ensure_compound(prop)
        applied_transformations = []
        nn_predictions_used = 0

        target_constant = FALSE if goal.upper() == 'F' else TRUE

        if verbose:
            print(f"[SimplificationPredictor] Simplificando para {goal}:")
            print(f"  Inicial: {current}")
            print()

        for iteration in range(max_iterations):
            # Check if we've reached the goal
            if self._is_constant(current.root if hasattr(current, 'root') else current):
                is_target = (goal.upper() == 'F' and self._is_false_constant(current.root if hasattr(current, 'root') else current)) or \
                           (goal.upper() == 'T' and self._is_true_constant(current.root if hasattr(current, 'root') else current))
                if is_target:
                    if verbose:
                        print(f"\n[SUCESSO] Alcançou {goal} após {iteration} iterações!")
                    return {
                        'success': True,
                        'iterations': iteration,
                        'transformations': applied_transformations,
                        'final_prop': current,
                        'nn_predictions_used': nn_predictions_used
                    }

            # Get NN prediction
            transform_name = predictor.predict(current, goal=goal)
            used_nn = False
            matched_subexpr = None

            # Check if prediction is applicable
            if transform_name in transformations_map:
                check_fn, apply_fn = transformations_map[transform_name]
                if self._can_apply_anywhere(current, check_fn):
                    new_prop, matched_subexpr = self._apply_random_transformation_with_location(current, check_fn, apply_fn)
                    used_nn = True
                    nn_predictions_used += 1

            # Fallback: try simplification transformations in priority order
            if not used_nn:
                applied = False

                # Priority 1: Simplification ops (complement, domination, identity are key)
                simplification_priority = [
                    'complement',      # p ∧ ~p → F (MOST IMPORTANT)
                    'domination',      # p ∧ F → F
                    'identity',        # p ∧ T → p
                    'negation_constant',
                    'double_negation',
                    'idempotence',
                    'absorption',
                    'factoring',
                ]

                for t_name in simplification_priority:
                    if t_name in transformations_map:
                        check_fn, apply_fn = transformations_map[t_name]
                        if self._can_apply_anywhere(current, check_fn):
                            new_prop, matched_subexpr = self._apply_random_transformation_with_location(current, check_fn, apply_fn)
                            transform_name = t_name
                            applied = True
                            break

                # Priority 2: Structure ops that expose complement
                if not applied:
                    structure_priority = [
                        'distributivity',   # Expose p ∧ ~p patterns
                        'associativity',    # Regroup terms
                        'de_morgan',
                        'implication_elimination',
                        'commutativity',
                    ]
                    for t_name in structure_priority:
                        if t_name in transformations_map:
                            check_fn, apply_fn = transformations_map[t_name]
                            if self._can_apply_anywhere(current, check_fn):
                                new_prop, matched_subexpr = self._apply_random_transformation_with_location(current, check_fn, apply_fn)
                                transform_name = t_name
                                applied = True
                                break

                if not applied:
                    continue

            current = new_prop

            applied_transformations.append({
                'iteration': iteration,
                'proposition': 1,
                'law': transform_name,
                'result': str(new_prop),
                'used_nn': used_nn,
                'matched_subexpr': matched_subexpr,
                'p1': str(current),
                'p2': goal
            })

            if verbose:
                nn_marker = "[NN]" if used_nn else "[RND]"
                print(f"[{iteration}] {nn_marker} {transform_name}: {new_prop}")

        # Final check
        if self._is_constant(current.root if hasattr(current, 'root') else current):
            is_target = (goal.upper() == 'F' and self._is_false_constant(current.root if hasattr(current, 'root') else current)) or \
                       (goal.upper() == 'T' and self._is_true_constant(current.root if hasattr(current, 'root') else current))
            if is_target:
                return {
                    'success': True,
                    'iterations': max_iterations,
                    'transformations': applied_transformations,
                    'final_prop': current,
                    'nn_predictions_used': nn_predictions_used
                }

        if verbose:
            print(f"\n[FALHA] Não foi possível alcançar {goal} após {max_iterations} iterações")
            print(f"  Final: {current}")

        return {
            'success': False,
            'iterations': max_iterations,
            'transformations': applied_transformations,
            'final_prop': current,
            'nn_predictions_used': nn_predictions_used
        }

    def prove_with_fallback(self, prop1: CompoundProposition, prop2: CompoundProposition,
                            predictor, simplification_predictor=None, max_iterations: int = 50,
                            verbose: bool = False) -> dict:
        """
        Try to prove equivalence using multiple strategies in order:
        1. Direct proof (transform P1 to match P2)
        2. Contrapositive proof (prove ~P1 ≡ ~P2)
        3. Proof by absurdity (prove P1 ^ ~P2 = F)

        Args:
            prop1: First compound proposition
            prop2: Second compound proposition
            predictor: Trained TransformationPredictor instance (convergence)
            simplification_predictor: Trained SimplificationPredictor instance (for absurdity)
            max_iterations: Maximum iterations per strategy
            verbose: If True, print proof steps

        Returns:
            dict with proof result and method used
        """
        total_iterations = 0

        if verbose:
            print("\n" + "="*60)
            print("  PROVA MULTI-ESTRATÉGIA")
            print("="*60)
            print(f"\nTentando provar: {prop1} ≡ {prop2}")

        # Estratégia 1: Prova direta
        if verbose:
            print("\n" + "-"*60)
            print("[Estratégia 1] Prova por transformação direta")
            print("-"*60)

        direct_result = self.prove_equivalence_nn(
            prop1, prop2, predictor,
            max_iterations=max_iterations, verbose=verbose
        )
        total_iterations += direct_result['iterations']

        if direct_result['success']:
            if verbose:
                print(f"\n✓ Prova direta bem-sucedida em {direct_result['iterations']} passos")
            return {
                **direct_result,
                'method': 'direct',
                'total_iterations': total_iterations
            }

        if verbose:
            print(f"\n✗ Prova direta falhou após {direct_result['iterations']} iterações")

        # Estratégia 2: Prova por contrapositiva
        if verbose:
            print("\n" + "-"*60)
            print("[Estratégia 2] Prova por contrapositiva (~P1 ≡ ~P2)")
            print("-"*60)

        contra_result = self.prove_by_contrapositive(
            prop1, prop2, predictor,
            max_iterations=max_iterations, verbose=verbose
        )
        total_iterations += contra_result['iterations']

        if contra_result['success']:
            if verbose:
                print(f"\n✓ Prova por contrapositiva bem-sucedida em {contra_result['iterations']} passos")
            return {
                **contra_result,
                'total_iterations': total_iterations
            }

        if verbose:
            print(f"\n✗ Prova por contrapositiva falhou após {contra_result['iterations']} iterações")

        # Estratégia 3: Prova por absurdo
        if verbose:
            print("\n" + "-"*60)
            print("[Estratégia 3] Prova por absurdo (P1 ^ ~P2 = F)")
            print("-"*60)

        absurd_result = self.prove_by_absurdity(
            prop1, prop2, predictor,
            simplification_predictor=simplification_predictor,
            max_iterations=max_iterations, verbose=verbose
        )
        total_iterations += absurd_result['iterations']

        if absurd_result['success']:
            if verbose:
                print(f"\n✓ Prova por absurdo bem-sucedida em {absurd_result['iterations']} passos")
            return {
                **absurd_result,
                'total_iterations': total_iterations
            }

        if verbose:
            print(f"\n✗ Prova por absurdo falhou após {absurd_result['iterations']} iterações")
            print("\n" + "="*60)
            print("Todas as estratégias de prova esgotadas.")
            print("="*60)

        # All strategies failed
        return {
            'success': False,
            'method': 'all_failed',
            'direct_result': direct_result,
            'contrapositive_result': contra_result,
            'absurdity_result': absurd_result,
            'total_iterations': total_iterations
        }

    def optimize_proof(self, original_proof: dict, prop1: CompoundProposition,
                       prop2: CompoundProposition, predictor,
                       max_iterations: int = 20, verbose: bool = False) -> dict:
        """
        Try to find a shorter proof by checking if P1 can directly reach
        intermediate stages of the original proof.

        Given a proof: P1 → S1 → S2 → S3 → ... → Sn → P2
        This method tries:
        - Can P1 reach S2 directly? (skip S1)
        - Can P1 reach S3 directly? (skip S1, S2)
        - etc.

        If successful, returns a shorter proof path.

        Args:
            original_proof: The original proof result with 'transformations'
            prop1: Original first proposition
            prop2: Original second proposition (target)
            predictor: Trained TransformationPredictor instance
            max_iterations: Max iterations for each shortcut attempt
            verbose: If True, print optimization progress

        Returns:
            dict with:
                - 'optimized': bool - True if a shorter proof was found
                - 'original_steps': Number of steps in original proof
                - 'optimized_steps': Number of steps in optimized proof
                - 'savings': Number of steps saved
                - 'optimized_proof': The shorter proof if found
                - 'shortcuts_found': List of shortcuts discovered
        """
        if not original_proof.get('success') or not original_proof.get('transformations'):
            return {
                'optimized': False,
                'reason': 'no_valid_proof_to_optimize'
            }

        transformations = original_proof['transformations']
        original_steps = len(transformations)

        if original_steps <= 2:
            return {
                'optimized': False,
                'original_steps': original_steps,
                'reason': 'proof_already_minimal'
            }

        if verbose:
            print("\n" + "="*60)
            print("  OTIMIZAÇÃO DA PROVA")
            print("="*60)
            print(f"Prova original tem {original_steps} passos")
            print("Procurando atalhos...")
            print()

        # Collect intermediate states from the proof
        # We need to reconstruct them from the transformation results
        intermediate_states = []
        for t in transformations:
            # Parse the result string back to a proposition
            result_str = t.get('result', '')
            if result_str:
                try:
                    from main import parse_proposition
                    parsed, _ = parse_proposition(result_str)
                    if isinstance(parsed, CompoundProposition):
                        intermediate_states.append({
                            'step': t['iteration'],
                            'prop': parsed,
                            'law': t['law'],
                            'result_str': result_str
                        })
                except:
                    pass

        if not intermediate_states:
            return {
                'optimized': False,
                'original_steps': original_steps,
                'reason': 'could_not_parse_intermediate_states'
            }

        shortcuts_found = []
        best_shortcut = None
        best_savings = 0

        current1 = self._ensure_compound(prop1)

        # Try to reach later stages directly from P1
        # Start from the end (most savings) and work backwards
        for i in range(len(intermediate_states) - 1, 0, -1):
            target_state = intermediate_states[i]
            target_prop = target_state['prop']
            steps_to_skip = target_state['step']

            if steps_to_skip < 2:
                continue  # Not worth optimizing

            if verbose:
                print(f"Tentando alcançar passo {target_state['step']} diretamente...")
                print(f"  Alvo: {target_state['result_str'][:60]}{'...' if len(target_state['result_str']) > 60 else ''}")

            # Try direct proof from P1 to this intermediate state
            shortcut_result = self.prove_equivalence_nn(
                current1, target_prop, predictor,
                max_iterations=max_iterations, verbose=False
            )

            if shortcut_result['success']:
                shortcut_steps = shortcut_result['iterations']
                remaining_steps = original_steps - target_state['step'] - 1

                # Calculate total steps with this shortcut
                total_with_shortcut = shortcut_steps + remaining_steps
                savings = original_steps - total_with_shortcut

                if verbose:
                    print(f"  ✓ Atalho encontrado! {shortcut_steps} passos para alcançar passo {target_state['step']}")
                    print(f"    Original: {original_steps} passos")
                    print(f"    Com atalho: {total_with_shortcut} passos (economia de {savings})")

                if savings > best_savings:
                    best_savings = savings
                    best_shortcut = {
                        'target_step': target_state['step'],
                        'shortcut_result': shortcut_result,
                        'total_steps': total_with_shortcut,
                        'savings': savings
                    }

                shortcuts_found.append({
                    'target_step': target_state['step'],
                    'shortcut_steps': shortcut_steps,
                    'savings': savings
                })
            else:
                if verbose:
                    print(f"  ✗ Não foi possível encontrar caminho direto")

        # Também tenta encontrar atalhos diretos entre estados intermediários
        if verbose and len(intermediate_states) > 3:
            print()
            print("Verificando atalhos entre estados intermediários...")

        for i in range(len(intermediate_states) - 2):
            for j in range(i + 3, len(intermediate_states)):  # Skip at least 2 steps
                source_state = intermediate_states[i]
                target_state = intermediate_states[j]

                steps_between = target_state['step'] - source_state['step']
                if steps_between < 3:
                    continue

                source_prop = source_state['prop']
                target_prop = target_state['prop']

                shortcut_result = self.prove_equivalence_nn(
                    source_prop, target_prop, predictor,
                    max_iterations=min(max_iterations, steps_between - 1),
                    verbose=False
                )

                if shortcut_result['success']:
                    shortcut_steps = shortcut_result['iterations']
                    savings = steps_between - shortcut_steps - 1

                    if savings > 0:
                        shortcuts_found.append({
                            'from_step': source_state['step'],
                            'to_step': target_state['step'],
                            'shortcut_steps': shortcut_steps,
                            'savings': savings
                        })

                        if verbose:
                            print(f"  ✓ Atalho: passo {source_state['step']} → passo {target_state['step']} em {shortcut_steps} passos (economia de {savings})")

        if not shortcuts_found:
            if verbose:
                print()
                print("Nenhum atalho encontrado. Prova original já é ótima.")

            return {
                'optimized': False,
                'original_steps': original_steps,
                'shortcuts_found': [],
                'reason': 'no_shortcuts_found'
            }

        # Constrói prova otimizada usando melhor atalho
        if best_shortcut and best_shortcut['savings'] > 0:
            if verbose:
                print()
                print("-"*60)
                print(f"RESULTADO DA OTIMIZAÇÃO: Economia de {best_shortcut['savings']} passos!")
                print(f"  Original: {original_steps} passos")
                print(f"  Otimizada: {best_shortcut['total_steps']} passos")
                print("-"*60)

            return {
                'optimized': True,
                'original_steps': original_steps,
                'optimized_steps': best_shortcut['total_steps'],
                'savings': best_shortcut['savings'],
                'best_shortcut': best_shortcut,
                'shortcuts_found': shortcuts_found,
                'optimized_proof': best_shortcut['shortcut_result']
            }

        return {
            'optimized': False,
            'original_steps': original_steps,
            'shortcuts_found': shortcuts_found,
            'reason': 'no_beneficial_shortcuts'
        }

    def prove_and_optimize(self, prop1: CompoundProposition, prop2: CompoundProposition,
                           predictor, max_iterations: int = 50,
                           optimize_iterations: int = 15,
                           verbose: bool = False) -> dict:
        """
        Prove equivalence and then try to find a shorter proof.

        This is the main entry point for optimized proofs:
        1. First finds any valid proof
        2. Then attempts to optimize it by finding shortcuts

        Args:
            prop1: First compound proposition
            prop2: Second compound proposition
            predictor: Trained TransformationPredictor instance
            max_iterations: Maximum iterations for initial proof
            optimize_iterations: Max iterations for optimization attempts
            verbose: If True, print all steps

        Returns:
            dict with proof result and optimization info
        """
        if verbose:
            print("\n" + "="*60)
            print("  PROVAR E OTIMIZAR")
            print("="*60)
            print(f"\nProvando: {prop1} ≡ {prop2}")
            print()

        # First, get a valid proof
        initial_result = self.prove_equivalence_nn(
            prop1, prop2, predictor,
            max_iterations=max_iterations, verbose=verbose
        )

        if not initial_result['success']:
            # Try fallback strategies
            initial_result = self.prove_with_fallback(
                prop1, prop2, predictor,
                max_iterations=max_iterations, verbose=verbose
            )

        if not initial_result['success']:
            return {
                'success': False,
                'optimized': False,
                'reason': 'could_not_find_initial_proof'
            }

        original_steps = len(initial_result.get('transformations', []))

        if verbose:
            print()
            print(f"Prova inicial encontrada com {original_steps} passos")
            print("Tentando otimização...")

        # Try to optimize
        optimization = self.optimize_proof(
            initial_result, prop1, prop2, predictor,
            max_iterations=optimize_iterations, verbose=verbose
        )

        return {
            'success': True,
            'initial_proof': initial_result,
            'optimization': optimization,
            'original_steps': original_steps,
            'final_steps': optimization.get('optimized_steps', original_steps),
            'was_optimized': optimization.get('optimized', False)
        }
