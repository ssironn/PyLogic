"""Servico de sintaxe suportada."""


class SyntaxService:
    """Servico para retornar informacoes sobre a sintaxe suportada."""

    @staticmethod
    def get_syntax():
        """Retorna informacoes sobre a sintaxe suportada para proposicoes."""
        return {
            'operators': {
                'negation': ['~p', '!p', 'NOT p'],
                'conjunction': ['p ^ q', 'p & q', 'p AND q'],
                'disjunction': ['p v q', 'p | q', 'p OR q'],
                'implication': ['p -> q', 'p => q', 'p IMPLIES q']
            },
            'constants': {
                'true': 'T',
                'false': 'F'
            },
            'grouping': '(p ^ q)',
            'examples': [
                'p ^ q',
                '~(p v q)',
                '(p ^ q) v r',
                '~~p',
                'p -> q',
                '(p -> q) ^ (q -> r)'
            ]
        }
