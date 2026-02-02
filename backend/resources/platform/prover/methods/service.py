"""Servico de metodos de prova disponiveis."""


class MethodsService:
    """Servico para retornar informacoes sobre os metodos de prova."""

    @staticmethod
    def get_methods():
        """Retorna informacoes sobre os metodos de prova disponiveis."""
        return {
            'methods': {
                'automatic': {
                    'description': 'Tenta multiplas estrategias automaticamente',
                    'strategies': ['direct', 'contrapositive', 'absurd']
                },
                'direct': {
                    'description': 'Prova por transformacao direta',
                    'objective': 'Transformar P1 ate que seja igual a P2'
                },
                'contrapositive': {
                    'description': 'Prova atraves da contrapositiva',
                    'objective': 'Provar que ~P1 ≡ ~P2'
                },
                'absurd': {
                    'description': 'Prova por reducao ao absurdo',
                    'objective': 'Provar que (P1 ∧ ~P2) = F'
                },
                'bidirectional': {
                    'description': 'Prova atraves de dupla implicacao',
                    'objective': 'Provar que (P1 -> P2) = T e (P2 -> P1) = T'
                }
            }
        }
