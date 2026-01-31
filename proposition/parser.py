"""
Parser for propositional logic expressions.

Converts string representations like "p ^ q" or "p -> q" into
CompoundProposition objects.

Supported syntax:
    - Atomic propositions: single letters (p, q, r, etc.)
    - Truth constants: T (True), F (False)
    - Negation: ~, !, ¬ (prefix)
    - Conjunction (AND): ^, &, *, AND
    - Disjunction (OR): v, |, +, OR
    - Implication: ->, =>, →, IMPLIES
    - Parentheses for grouping: ()

Operator precedence (highest to lowest):
    1. Parentheses
    2. Negation (~)
    3. Conjunction (^)
    4. Disjunction (v)
    5. Implication (->) - lowest precedence, right-associative

Examples:
    "p ^ q"           -> p AND q
    "~p v q"          -> (NOT p) OR q
    "p -> q"          -> p IMPLIES q
    "p -> q -> r"     -> p IMPLIES (q IMPLIES r)  (right-associative)
    "p ^ q -> r"      -> (p AND q) IMPLIES r
    "p v ~p"          -> Tautology (can be simplified to T)
    "p ^ ~p"          -> Contradiction (can be simplified to F)
"""

import re
from proposition import Proposition, CompoundProposition, TRUE, FALSE


class ParseError(Exception):
    """Exception raised for parsing errors."""
    pass


class Token:
    """Represents a token from the lexer."""

    # Token types
    ATOM = 'ATOM'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    NOT = 'NOT'
    AND = 'AND'
    OR = 'OR'
    IMPLIES = 'IMPLIES'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    EOF = 'EOF'

    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class Lexer:
    """Tokenizes a propositional logic expression."""

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None

    def advance(self):
        """Move to the next character."""
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def peek(self):
        """Peek at the next character without advancing."""
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None

    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char and self.current_char.isspace():
            self.advance()

    def peek_word(self):
        """Peek ahead to see if there's a keyword."""
        if not self.current_char or not self.current_char.isalpha():
            return None

        start = self.pos
        end = start
        while end < len(self.text) and self.text[end].isalpha():
            end += 1
        return self.text[start:end].upper()

    def get_next_token(self):
        """Return the next token from the input."""
        while self.current_char:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # Implication operators: ->, =>
            if self.current_char == '-' and self.peek() == '>':
                self.advance()  # consume '-'
                self.advance()  # consume '>'
                return Token(Token.IMPLIES, '→')

            if self.current_char == '=' and self.peek() == '>':
                self.advance()  # consume '='
                self.advance()  # consume '>'
                return Token(Token.IMPLIES, '→')

            # Unicode implication arrow
            if self.current_char == '→':
                self.advance()
                return Token(Token.IMPLIES, '→')

            # Negation operators
            if self.current_char in '~!¬':
                self.advance()
                return Token(Token.NOT, '~')

            # AND operators
            if self.current_char in '^&*':
                self.advance()
                return Token(Token.AND, '^')

            # OR operators
            if self.current_char in 'v|+':
                self.advance()
                return Token(Token.OR, 'v')

            # Parentheses
            if self.current_char == '(':
                self.advance()
                return Token(Token.LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(Token.RPAREN, ')')

            # Keywords (AND, OR, NOT, IMPLIES, TRUE, FALSE)
            word = self.peek_word()
            if word == 'AND':
                for _ in range(3):
                    self.advance()
                return Token(Token.AND, '^')
            if word == 'OR':
                for _ in range(2):
                    self.advance()
                return Token(Token.OR, 'v')
            if word == 'NOT':
                for _ in range(3):
                    self.advance()
                return Token(Token.NOT, '~')
            if word == 'IMPLIES':
                for _ in range(7):
                    self.advance()
                return Token(Token.IMPLIES, '→')
            if word == 'TRUE':
                for _ in range(4):
                    self.advance()
                return Token(Token.TRUE, 'T')
            if word == 'FALSE':
                for _ in range(5):
                    self.advance()
                return Token(Token.FALSE, 'F')
            if word == 'T':
                self.advance()
                return Token(Token.TRUE, 'T')
            if word == 'F':
                self.advance()
                return Token(Token.FALSE, 'F')

            # Atomic proposition (single letter or identifier)
            if self.current_char.isalpha():
                name = ''
                while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
                    name += self.current_char
                    self.advance()
                return Token(Token.ATOM, name)

            raise ParseError(f"Unexpected character: '{self.current_char}' at position {self.pos}")

        return Token(Token.EOF)


class Parser:
    """
    Recursive descent parser for propositional logic.

    Grammar (precedence from lowest to highest):
        expression   -> implication
        implication  -> disjunction (IMPLIES implication)?  (right-associative)
        disjunction  -> conjunction (OR conjunction)*
        conjunction  -> unary (AND unary)*
        unary        -> NOT unary | primary
        primary      -> ATOM | LPAREN expression RPAREN
    """

    def __init__(self, text):
        self.lexer = Lexer(text)
        self.current_token = self.lexer.get_next_token()
        self._propositions = {}  # Cache propositions by name

    def error(self, msg="Invalid syntax"):
        raise ParseError(f"{msg} at token {self.current_token}")

    def eat(self, token_type):
        """Consume a token of the expected type."""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")

    def get_proposition(self, name):
        """Get or create a proposition by name."""
        if name not in self._propositions:
            self._propositions[name] = Proposition(text=name, value=False)
        return self._propositions[name]

    def parse(self):
        """Parse the expression and return a CompoundProposition."""
        result = self.expression()
        if self.current_token.type != Token.EOF:
            self.error("Unexpected token after expression")
        return result, self._propositions

    def expression(self):
        """Parse an expression (top level)."""
        return self.implication()

    def implication(self):
        """Parse implication: disjunction (IMPLIES implication)?

        Implication is right-associative: p -> q -> r = p -> (q -> r)
        """
        left = self.disjunction()

        if self.current_token.type == Token.IMPLIES:
            self.eat(Token.IMPLIES)
            # Right-associative: recursively parse the right side
            right = self.implication()
            left = CompoundProposition(Proposition.__rshift__, left, right)

        return left

    def disjunction(self):
        """Parse disjunction: conjunction (OR conjunction)*"""
        left = self.conjunction()

        while self.current_token.type == Token.OR:
            self.eat(Token.OR)
            right = self.conjunction()
            left = CompoundProposition(Proposition.__add__, left, right)

        return left

    def conjunction(self):
        """Parse conjunction: unary (AND unary)*"""
        left = self.unary()

        while self.current_token.type == Token.AND:
            self.eat(Token.AND)
            right = self.unary()
            left = CompoundProposition(Proposition.__mul__, left, right)

        return left

    def unary(self):
        """Parse unary: NOT unary | primary"""
        if self.current_token.type == Token.NOT:
            self.eat(Token.NOT)
            operand = self.unary()
            return CompoundProposition(Proposition.__invert__, operand)

        return self.primary()

    def primary(self):
        """Parse primary: ATOM | TRUE | FALSE | LPAREN expression RPAREN"""
        token = self.current_token

        if token.type == Token.ATOM:
            self.eat(Token.ATOM)
            return self.get_proposition(token.value)

        if token.type == Token.TRUE:
            self.eat(Token.TRUE)
            return TRUE

        if token.type == Token.FALSE:
            self.eat(Token.FALSE)
            return FALSE

        if token.type == Token.LPAREN:
            self.eat(Token.LPAREN)
            result = self.expression()
            self.eat(Token.RPAREN)
            return result

        self.error(f"Unexpected token: {token}")


def parse_proposition(text):
    """
    Parse a propositional logic expression from a string.

    Args:
        text: The expression to parse (e.g., "p ^ q", "p -> q")

    Returns:
        tuple: (proposition, propositions_dict)
            - proposition: CompoundProposition or Proposition object
            - propositions_dict: dict mapping names to Proposition objects

    Raises:
        ParseError: If the expression cannot be parsed

    Examples:
        >>> prop, props = parse_proposition("p ^ q")
        >>> print(prop)  # (p ^ q)

        >>> prop, props = parse_proposition("p -> q")
        >>> print(prop)  # (p → q)

        >>> prop, props = parse_proposition("~(p v q)")
        >>> print(prop)  # (~(p v q))
    """
    if not text or not text.strip():
        raise ParseError("Empty expression")

    parser = Parser(text.strip())
    return parser.parse()


def set_proposition_values(propositions, values):
    """
    Set truth values for propositions.

    Args:
        propositions: dict mapping names to Proposition objects
        values: dict mapping names to boolean values

    Example:
        >>> prop, props = parse_proposition("p ^ q")
        >>> set_proposition_values(props, {'p': True, 'q': False})
    """
    for name, value in values.items():
        if name in propositions:
            propositions[name].value = value
