from utils.function_decorator import LogicOperator


class TruthValue:
    def __init__(self, value) -> None:
        self.value = value

    def __repr__(self) -> str:
        return str(self.value)


class Proposition:
    def __init__(self, text, value=False) -> None:
        self.text = text
        self.value = value

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return str(self)

    def is_constant(self) -> bool:
        """Check if this is a truth constant (T or F)."""
        return False

    @staticmethod
    @LogicOperator
    def __add__(left_proposition, right_proposition) -> 'TruthValue':
        return TruthValue(left_proposition.value or right_proposition.value)

    @staticmethod
    @LogicOperator
    def __mul__(left_proposition, right_proposition) -> 'TruthValue':
        return TruthValue(left_proposition.value and right_proposition.value)

    @staticmethod
    @LogicOperator
    def __invert__(proposition) -> 'TruthValue':
        return TruthValue(not proposition.value)

    @staticmethod
    @LogicOperator
    def __rshift__(left_proposition, right_proposition) -> 'TruthValue':
        """Material implication: p → q ≡ ~p v q"""
        return TruthValue(not left_proposition.value or right_proposition.value)


class TruthConstant(Proposition):
    """
    A truth constant representing True (T) or False (F).

    Unlike regular propositions, truth constants have a fixed value
    that cannot be changed.
    """

    def __init__(self, value: bool) -> None:
        text = 'T' if value else 'F'
        super().__init__(text, value)
        self._fixed_value = value

    @property
    def value(self):
        return self._fixed_value

    @value.setter
    def value(self, _):
        # Truth constants cannot be changed
        pass

    def is_constant(self) -> bool:
        """Check if this is a truth constant (T or F)."""
        return True

    def is_true(self) -> bool:
        """Check if this is the True constant."""
        return self._fixed_value

    def is_false(self) -> bool:
        """Check if this is the False constant."""
        return not self._fixed_value


# Singleton instances for T and F
TRUE = TruthConstant(True)
FALSE = TruthConstant(False)


class PropositionNode:
    """Base class for tree nodes."""

    def evaluate(self) -> bool:
        raise NotImplementedError

    def get_components(self) -> set:
        raise NotImplementedError


class AtomicNode(PropositionNode):
    """Leaf node wrapping an atomic Proposition."""

    def __init__(self, proposition: Proposition):
        self.proposition = proposition

    def evaluate(self) -> bool:
        return self.proposition.value

    def get_components(self) -> set:
        return {self.proposition}

    def __str__(self) -> str:
        return str(self.proposition)

    def __repr__(self) -> str:
        return str(self)


class OperatorNode(PropositionNode):
    """Node representing an operator with operands."""

    def __init__(self, operator, left, right=None):
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self) -> bool:
        left_val = Proposition("", self.left.evaluate())
        if self.right is None:
            return self.operator(left_val).value
        right_val = Proposition("", self.right.evaluate())
        return self.operator(left_val, right_val).value

    def get_components(self) -> set:
        result = self.left.get_components()
        if self.right:
            result |= self.right.get_components()
        return result

    def __str__(self) -> str:
        if self.right is None:
            return f"({self.operator}{self.left})"
        return f"({self.left} {self.operator} {self.right})"

    def __repr__(self) -> str:
        return str(self)


class CompoundProposition:
    """A compound proposition represented as a tree structure."""

    def __init__(self, operator=None, left=None, right=None):
        """
        Create a compound proposition as a tree.

        For binary: CompoundProposition(Proposition.__add__, p, q)  # p v q
        For unary:  CompoundProposition(Proposition.__invert__, p)   # ~p
        """
        if operator is None:
            self.root = None
            self.components = set()
            return

        left_node = self._to_node(left)
        right_node = self._to_node(right) if right is not None else None

        self.root = OperatorNode(operator, left_node, right_node)
        self.components = self.root.get_components()

    @staticmethod
    def _to_node(value):
        if isinstance(value, PropositionNode):
            return value
        elif isinstance(value, Proposition):
            return AtomicNode(value)
        elif isinstance(value, CompoundProposition):
            return value.root
        raise TypeError(f"Cannot convert {type(value)} to node")

    def prepare_calculus(self, **kwargs):
        if kwargs.get('debug'):
            for elem in self.components:
                print(f"{elem} is {elem.value}")
            print(f"\n{self}\n")
            print("\nSolving the proposition...\n")

    def calculate_value(self, **kwargs) -> bool:
        if self.root is None:
            return None
        return self.root.evaluate()

    def __str__(self):
        if self.root is None:
            return "()"
        return str(self.root)

    def __repr__(self):
        return str(self)

    def is_constant(self) -> bool:
        """Check if this compound proposition is a truth constant (T or F)."""
        if self.root is None:
            return False
        if isinstance(self.root, AtomicNode):
            return isinstance(self.root.proposition, TruthConstant)
        return False

    def is_true(self) -> bool:
        """Check if this is the True constant."""
        if self.is_constant():
            return self.root.proposition.is_true()
        return False

    def is_false(self) -> bool:
        """Check if this is the False constant."""
        if self.is_constant():
            return self.root.proposition.is_false()
        return False

    def __iter__(self):
        """Pre-order traversal yielding operators and propositions."""
        yield from self._traverse(self.root)

    def _traverse(self, node):
        if node is None:
            return
        if isinstance(node, AtomicNode):
            yield node.proposition
        elif isinstance(node, OperatorNode):
            yield node.operator
            yield from self._traverse(node.left)
            if node.right:
                yield from self._traverse(node.right)


# Import parser functions after class definitions to avoid circular imports
from proposition.parser import parse_proposition, set_proposition_values, ParseError

__all__ = [
    'Proposition',
    'TruthConstant',
    'TRUE',
    'FALSE',
    'PropositionNode',
    'AtomicNode',
    'OperatorNode',
    'CompoundProposition',
    'TruthValue',
    'parse_proposition',
    'set_proposition_values',
    'ParseError',
]
