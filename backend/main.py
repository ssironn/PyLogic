#!/usr/bin/env python3
"""
PyLogic - Demonstrador Interativo de Equivalências

Este programa permite inserir duas proposições lógicas e verifica se elas
são equivalentes. Se forem, demonstra os passos da prova usando uma rede
neural para guiar a seleção de transformações.

Sintaxe suportada:
    - Proposições atômicas: p, q, r, etc.
    - Negação: ~p, !p, NOT p
    - Conjunção (E): p ^ q, p & q, p AND q
    - Disjunção (OU): p v q, p | q, p OR q
    - Parênteses: (p ^ q), ~(p v q)

Exemplos:
    - p ^ q
    - ~(p v q)
    - (p ^ q) v r
    - ~~p
"""

import sys
import os

from utils.proposition import (
    Proposition, CompoundProposition,
    parse_proposition, ParseError, TRUE, FALSE
)
from utils.equivalence import Equivalence
from utils.nn import TransformationPredictor, generate_dataset
from utils.nn.model import SimplificationPredictor
from utils.nn.dataset import generate_simplification_dataset


def print_header():
    """Imprime o cabeçalho do programa."""
    print("=" * 60)
    print("  PyLogic - Demonstrador Interativo de Equivalências")
    print("=" * 60)
    print()
    print("Guia de Sintaxe:")
    print("  Negação:     ~p, !p, NOT p")
    print("  E (AND):     p ^ q, p & q, p AND q")
    print("  OU (OR):     p v q, p | q, p OR q")
    print("  Implicação:  p -> q, p => q, p IMPLIES q")
    print("  Constantes:  T (Verdadeiro), F (Falso)")
    print("  Agrupamento: (p ^ q), ~(p v q)")
    print()


def train_model(verbose=True):
    """Treina ambos os modelos de rede neural.

    Retorna:
        tuple: (modelo_convergencia, modelo_simplificacao)
            - modelo_convergencia: TransformationPredictor para provas diretas/contrapositivas
            - modelo_simplificacao: SimplificationPredictor para provas por absurdo
    """
    if verbose:
        print("Treinando modelos de rede neural...")
        print()
        print("[1/2] Modelo de Convergência (provas diretas/contrapositivas)")
        print("  Gerando conjunto de dados de treinamento...")

    X, y = generate_dataset(num_samples=2000, verbose=False)

    if verbose:
        print(f"  Tamanho do conjunto: {len(X)} amostras")
        print("  Treinando modelo...")

    convergence_model = TransformationPredictor(hidden_layers=(32, 16), max_iter=2000)
    metrics = convergence_model.train(X, y, verbose=False, balance=True)

    if verbose:
        print(f"  Acurácia de treino: {metrics['train_accuracy']:.1%}")
        print(f"  Acurácia de teste: {metrics['test_accuracy']:.1%}")
        print()

    # Treina SimplificationPredictor para provas por absurdo
    if verbose:
        print("[2/2] Modelo de Simplificação (provas por absurdo)")
        print("  Gerando conjunto de dados de simplificação...")

    X_simp, y_simp = generate_simplification_dataset(num_samples=1500, verbose=False)

    if verbose:
        print(f"  Tamanho do conjunto: {len(X_simp)} amostras")
        print("  Treinando modelo...")

    simplification_model = SimplificationPredictor(hidden_layers=(32, 16), max_iter=2000)
    simp_metrics = simplification_model.train(X_simp, y_simp, verbose=False, balance=True)

    if verbose:
        print(f"  Acurácia de treino: {simp_metrics['train_accuracy']:.1%}")
        print(f"  Acurácia de teste: {simp_metrics['test_accuracy']:.1%}")
        print()

    return convergence_model, simplification_model


def _is_true_constant(prop):
    """Check if a proposition is the True constant."""
    return prop is TRUE or (hasattr(prop, 'is_constant') and prop.is_constant() and prop.is_true())


def _is_false_constant(prop):
    """Check if a proposition is the False constant."""
    return prop is FALSE or (hasattr(prop, 'is_constant') and prop.is_constant() and prop.is_false())


def check_semantic_equivalence(prop1, props1, prop2, props2):
    """
    Check if two propositions are semantically equivalent by checking
    all possible truth value combinations.
    """
    # Handle truth constants directly
    if _is_true_constant(prop1):
        if _is_true_constant(prop2):
            return True
        # prop1 is T, prop2 is something else - check if prop2 is always True
        all_names = set(props2.keys())
        n = len(all_names)
        names = sorted(all_names)
        for i in range(2 ** n):
            for j, name in enumerate(names):
                props2[name].value = bool((i >> j) & 1)
            if not evaluate_prop(prop2):
                return False
        return True

    if _is_false_constant(prop1):
        if _is_false_constant(prop2):
            return True
        # prop1 is F, prop2 is something else - check if prop2 is always False
        all_names = set(props2.keys())
        n = len(all_names)
        names = sorted(all_names)
        for i in range(2 ** n):
            for j, name in enumerate(names):
                props2[name].value = bool((i >> j) & 1)
            if evaluate_prop(prop2):
                return False
        return True

    # Get all unique proposition names (excluding T and F from the name set)
    all_names = set(props1.keys()) | set(props2.keys())
    # Remove T and F if they somehow got in there
    all_names.discard('T')
    all_names.discard('F')
    n = len(all_names)
    names = sorted(all_names)

    # If no variables, just evaluate once
    if n == 0:
        return evaluate_prop(prop1) == evaluate_prop(prop2)

    # Check all 2^n combinations
    for i in range(2 ** n):
        # Set truth values based on binary representation
        for j, name in enumerate(names):
            value = bool((i >> j) & 1)
            if name in props1:
                props1[name].value = value
            if name in props2:
                props2[name].value = value

        # Evaluate both propositions
        val1 = evaluate_prop(prop1)
        val2 = evaluate_prop(prop2)

        if val1 != val2:
            return False

    return True


def evaluate_prop(prop):
    """Evaluate a proposition (handles both Proposition and CompoundProposition)."""
    if hasattr(prop, 'is_constant') and prop.is_constant():
        return prop.is_true()
    if isinstance(prop, Proposition):
        return prop.value
    elif isinstance(prop, CompoundProposition):
        return prop.calculate_value()
    return prop.value


def format_transformation(t, iteration_width=3):
    """Formata um passo de transformação para exibição."""
    idx = t['iteration']
    which = t['proposition']
    law = t['law']
    result = t['result']
    used_nn = t.get('used_nn', False)

    marker = "[NN]" if used_nn else "[RND]"
    return f"  {idx:>{iteration_width}}. {marker} Aplicar {law} em P{which}: {result}"


def prove_and_display(prop1, prop2, model, eq, simplification_model=None,
                      max_iterations=50, use_fallback=True):
    """Executa o demonstrador e exibe resultados usando abordagem multi-estratégia.

    Args:
        prop1: Primeira proposição
        prop2: Segunda proposição
        model: TransformationPredictor (modelo de convergência)
        eq: Instância de Equivalence
        simplification_model: SimplificationPredictor para provas por absurdo (opcional)
        max_iterations: Máximo de iterações por estratégia
        use_fallback: Se deve tentar estratégias contrapositiva e por absurdo

    Returns:
        tuple: (sucesso: bool, resultado: dict) - O dict resultado para potencial otimização
    """
    print("\nIniciando demonstração guiada por NN...")
    print("-" * 40)

    # Estratégia 1: Prova direta
    print("\n[Estratégia 1] Transformação direta")
    result = eq.prove_equivalence_nn(
        prop1, prop2, model,
        max_iterations=max_iterations,
        verbose=False
    )

    if result['transformations']:
        print("\nPassos de transformação:")
        for t in result['transformations']:
            print(format_transformation(t))

    print()
    print("-" * 40)

    if result['success']:
        print("RESULTADO: EQUIVALENTES! (prova direta)")
        print(f"  Iterações: {result['iterations']}")
        print(f"  Predições NN usadas: {result['nn_predictions_used']}")
        nn_count = sum(1 for t in result['transformations'] if t.get('used_nn', False))
        rnd_count = len(result['transformations']) - nn_count
        print(f"  Detalhamento: {nn_count} guiadas por NN, {rnd_count} aleatórias")
        return True, result

    if not use_fallback:
        print("RESULTADO: Não foi possível provar equivalência sintaticamente.")
        print(f"  Máximo de iterações atingido: {result['iterations']}")
        print(f"  P1 final: {result['prop1_final']}")
        print(f"  P2 final: {result['prop2_final']}")
        return False, result

    # Estratégia 2: Prova por contrapositiva
    print("Prova direta falhou. Tentando contrapositiva...")
    print()
    print("="*50)
    print("  [Estratégia 2] CONTRAPOSITIVA: ~P1 ≡ ~P2")
    print("="*50)

    # Constrói ~P1 e ~P2 para mostrar o que estamos provando
    from utils.proposition import CompoundProposition, Proposition
    neg_p1 = CompoundProposition(Proposition.__invert__, prop1)
    neg_p2 = CompoundProposition(Proposition.__invert__, prop2)
    print(f"\nProvando: ~P1 ≡ ~P2")
    print(f"  ~P1 = {neg_p1}")
    print(f"  ~P2 = {neg_p2}")
    print()

    contra_result = eq.prove_by_contrapositive(
        prop1, prop2, model,
        max_iterations=max_iterations,
        verbose=False
    )

    if contra_result['success']:
        if contra_result.get('transformations'):
            print("Passos de transformação:")
            for t in contra_result['transformations']:
                print(format_transformation(t))
        print()
        print("-"*50)
        print("RESULTADO: EQUIVALENTES! (via contrapositiva)")
        print(f"  Como ~P1 ≡ ~P2, concluímos que P1 ≡ P2")
        print(f"  Iterações: {contra_result['iterations']}")
        print(f"  Predições NN usadas: {contra_result['nn_predictions_used']}")
        print("="*50)
        return True, contra_result

    # Mostra passos mesmo em falha
    if contra_result.get('transformations'):
        print("Passos de transformação (incompleto):")
        for t in contra_result['transformations'][-20:]:  # Mostra últimos 20 passos
            print(format_transformation(t))
        if len(contra_result.get('transformations', [])) > 20:
            print(f"  ... ({len(contra_result['transformations']) - 20} passos anteriores omitidos)")
    print()
    print(f"  Não foi possível provar em {contra_result['iterations']} iterações")
    print(f"  Estado final: {contra_result.get('prop1_final', 'N/A')}")

    # Estratégia 3: Prova por absurdo
    print()
    print("Contrapositiva falhou. Tentando prova por absurdo...")
    print()
    print("="*50)
    print("  [Estratégia 3] ABSURDO: (P1 ^ ~P2) = F")
    print("="*50)

    # Constrói (P1 ^ ~P2) para mostrar o que estamos provando
    assumption = CompoundProposition(Proposition.__mul__, prop1, neg_p2)
    print(f"\nProvando: (P1 ^ ~P2) = F")
    print(f"  P1 ^ ~P2 = {assumption}")
    print(f"  Alvo: F")
    print()

    absurd_result = eq.prove_by_absurdity(
        prop1, prop2, model,
        simplification_predictor=simplification_model,
        max_iterations=max_iterations,
        verbose=False
    )

    if absurd_result['success']:
        if absurd_result.get('transformations'):
            print("Passos de transformação:")
            for t in absurd_result['transformations']:
                print(format_transformation(t))
        print()
        print("-"*50)
        print("RESULTADO: EQUIVALENTES! (via prova por absurdo)")
        print(f"  (P1 ^ ~P2) = F prova que P1 implica P2")
        print(f"  Combinado com verificação semântica, P1 ≡ P2")
        print(f"  Iterações: {absurd_result['iterations']}")
        print(f"  Predições NN usadas: {absurd_result['nn_predictions_used']}")
        print("="*50)
        return True, absurd_result

    # Mostra passos mesmo em falha
    if absurd_result.get('transformations'):
        print("Passos de transformação (incompleto):")
        for t in absurd_result['transformations'][-20:]:  # Mostra últimos 20 passos
            print(format_transformation(t))
        if len(absurd_result.get('transformations', [])) > 20:
            print(f"  ... ({len(absurd_result['transformations']) - 20} passos anteriores omitidos)")
    print()
    print(f"  Não foi possível provar em {absurd_result['iterations']} iterações")
    print(f"  Estado final: {absurd_result.get('prop1_final', 'N/A')}")

    # Todas as estratégias falharam
    print()
    print("Todas as estratégias de prova esgotadas.")
    print("RESULTADO: Não foi possível provar equivalência sintaticamente.")
    print(f"  Direta: {result['iterations']} iterações")
    print(f"  Contrapositiva: {contra_result['iterations']} iterações")
    print(f"  Absurdo: {absurd_result['iterations']} iterações")
    print(f"  P1 final: {result['prop1_final']}")
    print(f"  P2 final: {result['prop2_final']}")

    return False, result


def interactive_mode(model, eq, simplification_model=None):
    """Executa o modo interativo onde usuários inserem proposições."""
    while True:
        print("-" * 60)
        print()

        # Obtém primeira proposição
        try:
            input1 = input("Digite a primeira proposição (ou 'sair' para encerrar): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")
            break

        if input1.lower() in ('quit', 'exit', 'q', 'sair', 's'):
            print("\nAté logo!")
            break

        if not input1:
            print("Por favor, digite uma proposição.")
            continue

        try:
            prop1, props1 = parse_proposition(input1)
            print(f"  Interpretado como: {prop1}")
        except ParseError as e:
            print(f"  Erro ao interpretar primeira proposição: {e}")
            continue

        # Obtém segunda proposição
        try:
            input2 = input("Digite a segunda proposição: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")
            break

        if input2.lower() in ('quit', 'exit', 'q', 'sair', 's'):
            print("\nAté logo!")
            break

        if not input2:
            print("Por favor, digite uma proposição.")
            continue

        try:
            prop2, props2 = parse_proposition(input2)
            print(f"  Interpretado como: {prop2}")
        except ParseError as e:
            print(f"  Erro ao interpretar segunda proposição: {e}")
            continue

        print()

        # Primeiro verifica equivalência semântica
        if not check_semantic_equivalence(prop1, props1, prop2, props2):
            print("Estas proposições NÃO são equivalentes.")
            print("(Elas têm valores de verdade diferentes para algumas atribuições)")
            continue

        print("Verificação semântica: Proposições têm a mesma tabela verdade.")

        # Verifica se já são sintaticamente iguais
        if eq.are_equal(prop1, prop2):
            print("\nAs proposições já são sintaticamente iguais!")
            continue

        # Converte para CompoundProposition se necessário para o demonstrador
        if isinstance(prop1, Proposition):
            prop1_compound = eq._ensure_compound(prop1)
        else:
            prop1_compound = prop1

        if isinstance(prop2, Proposition):
            prop2_compound = eq._ensure_compound(prop2)
        else:
            prop2_compound = prop2

        # Tenta provar equivalência com NN (com opção de repetir)
        last_result = None
        while True:
            success, last_result = prove_and_display(prop1_compound, prop2_compound, model, eq,
                                                      simplification_model=simplification_model)

            print()
            if success and last_result and len(last_result.get('transformations', [])) > 2:
                print("Opções: [o]timizar | [r]epetir | [n]ovas proposições | [s]air")
                prompt = "Escolha (o/r/n/s): "
            else:
                print("Opções: [r]epetir | [n]ovas proposições | [s]air")
                prompt = "Escolha (r/n/s): "

            try:
                choice = input(prompt).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nAté logo!")
                return

            if choice in ('q', 'quit', 'exit', 's', 'sair'):
                print("\nAté logo!")
                return
            elif choice in ('n', 'new', 'nova', ''):
                break  # Sai do loop interno, continua loop externo para novas proposições
            elif choice in ('r', 'retry', 'rerun', 'repetir'):
                print("\n" + "=" * 40)
                print("Repetindo com as mesmas proposições...")
                print("=" * 40)
                continue  # Continua loop interno para repetir
            elif choice in ('o', 'optimize', 'otimizar') and success and last_result:
                print("\n" + "=" * 60)
                print("  OTIMIZAÇÃO DA PROVA")
                print("=" * 60)
                print("Buscando uma prova mais curta...")
                print()

                optimization = eq.optimize_proof(
                    last_result, prop1_compound, prop2_compound, model,
                    max_iterations=15, verbose=True
                )

                if optimization.get('optimized'):
                    print()
                    print("="*60)
                    print(f"✓ PROVA OTIMIZADA ENCONTRADA!")
                    print(f"  Original: {optimization['original_steps']} passos")
                    print(f"  Otimizada: {optimization['optimized_steps']} passos")
                    print(f"  Economia: {optimization['savings']} passos")
                    print("="*60)

                    # Mostra a prova otimizada
                    opt_proof = optimization.get('optimized_proof')
                    if opt_proof and opt_proof.get('transformations'):
                        print()
                        print("Passos de transformação otimizados:")
                        for t in opt_proof['transformations']:
                            print(format_transformation(t))
                else:
                    print()
                    print("="*60)
                    print("Nenhuma prova mais curta encontrada. A original já é ótima.")
                    print("="*60)

                continue  # Permanece no loop para permitir mais opções
            else:
                break  # Padrão para novas proposições


def demo_mode(model, eq, simplification_model=None):
    """Executa uma demonstração com exemplos de múltiplos passos."""
    print("Executando demonstração com exemplos de múltiplos passos...\n")

    examples = [
        # === Básicos de passo único ===
        ("~~p", "p", "Dupla Negação (1 passo)"),
        ("p v ~p", "T", "Complemento - Tautologia (1-2 passos)"),
        ("p ^ ~p", "F", "Complemento - Contradição (1-2 passos)"),

        # === Provas de 2-3 passos ===
        ("~(p ^ q)", "~p v ~q", "Lei de De Morgan (1-2 passos)"),
        ("p -> q", "~p v q", "Eliminação da Implicação (1-2 passos)"),
        ("~~p ^ q", "p ^ q", "Dupla Negação em contexto (2 passos)"),

        # === Provas de 3-4 passos ===
        ("~(~p v ~q)", "p ^ q", "De Morgan + Dupla Negação (3-4 passos)"),
        ("~~p v ~~q", "p v q", "Dupla Negação em ambos lados (2-3 passos)"),
        ("(p v ~p) ^ q", "q", "Simplificação de tautologia (2-3 passos)"),

        # === Provas de 4+ passos ===
        ("~~(p ^ q) v r", "(p ^ q) v r", "Dupla negação aninhada (2-3 passos)"),
        ("~(p -> q)", "p ^ ~q", "Negação da implicação (3-4 passos)"),
        ("(p ^ q) v (p ^ ~q)", "p", "Fatoração (3-5 passos)"),
    ]

    run_examples(examples, model, eq, simplification_model=simplification_model, max_iterations=100)


def test_mode(model, eq, simplification_model=None):
    """Executa testes abrangentes com equivalências complexas."""
    print("=" * 60)
    print("  TESTES ABRANGENTES DE EQUIVALÊNCIA (MÚLTIPLOS PASSOS)")
    print("=" * 60)
    print()

    # Equivalências complexas que DEVEM ser provadas
    # Organizadas por número esperado de passos
    equivalent_tests = [
        # ========================================
        # NÍVEL 1: Constantes de Verdade (1-2 passos)
        # ========================================
        ("p v ~p", "T", "Lei do Complemento - Tautologia"),
        ("p ^ ~p", "F", "Lei do Complemento - Contradição"),
        ("p v T", "T", "Dominação (OU)"),
        ("p ^ F", "F", "Dominação (E)"),
        ("p v F", "p", "Identidade (OU)"),
        ("p ^ T", "p", "Identidade (E)"),
        ("~T", "F", "Negação de Verdadeiro"),
        ("~F", "T", "Negação de Falso"),
        ("T -> p", "p", "Implicação: T -> p = p"),
        ("F -> p", "T", "Implicação: F -> p = T"),
        ("p -> T", "T", "Implicação: p -> T = T"),

        # ========================================
        # NÍVEL 2: Leis Básicas (1-2 passos)
        # ========================================
        ("~~p", "p", "Dupla Negação"),
        ("p ^ p", "p", "Idempotência (E)"),
        ("p v p", "p", "Idempotência (OU)"),
        ("p ^ q", "q ^ p", "Comutatividade (E)"),
        ("p v q", "q v p", "Comutatividade (OU)"),
        ("~(p ^ q)", "~p v ~q", "De Morgan (E)"),
        ("~(p v q)", "~p ^ ~q", "De Morgan (OU)"),
        ("p -> q", "~p v q", "Definição da Implicação"),

        # ========================================
        # NÍVEL 3: Provas de Dois Passos (2-3 passos)
        # ========================================
        ("~~p ^ q", "p ^ q", "Dupla Negação em E"),
        ("p v ~~q", "p v q", "Dupla Negação em OU"),
        ("~~(p ^ q)", "p ^ q", "Dupla Negação de composto"),
        ("p ^ (p v q)", "p", "Absorção (E-OU)"),
        ("p v (p ^ q)", "p", "Absorção (OU-E)"),
        ("(p v q) ^ p", "p", "Absorção (invertida)"),
        ("p -> q", "~q -> ~p", "Contraposição"),
        ("(p v ~p) ^ q", "T ^ q", "Tautologia em E (passo 1)"),

        # ========================================
        # NÍVEL 4: Provas de Três Passos (3-4 passos)
        # ========================================
        ("~~p ^ ~~q", "p ^ q", "Dupla Negação ambos lados"),
        ("~~p v ~~q", "p v q", "Dupla Negação ambos lados (OU)"),
        ("~(~p ^ ~q)", "p v q", "De Morgan depois Dupla Neg"),
        ("~(~p v ~q)", "p ^ q", "De Morgan depois Dupla Neg (E)"),
        ("~(p -> q)", "p ^ ~q", "Negação da Implicação"),
        ("(p v ~p) ^ q", "q", "Simplificação de tautologia"),
        ("p v (q ^ ~q)", "p", "Simplificação de contradição"),
        ("T ^ (p v q)", "p v q", "Identidade com composto"),
        ("F v (p ^ q)", "p ^ q", "Identidade com composto (OU)"),

        # ========================================
        # NÍVEL 5: Provas de 4+ Passos (4-6 passos)
        # ========================================
        ("~~(p v q) ^ r", "(p v q) ^ r", "Dupla negação aninhada em E"),
        ("~(p ^ q) v r", "(~p v ~q) v r", "De Morgan dentro de OU"),
        ("(~~p ^ q) v r", "(p ^ q) v r", "Dupla neg em expr complexa"),
        ("(p ^ q) v (p ^ ~q)", "p", "Fatoração de p"),
        ("(p v q) ^ (p v ~q)", "p", "Fatoração de p (forma OU)"),
        ("~(p -> q) v r", "(p ^ ~q) v r", "Neg implicação dentro de OU"),
        ("(p -> q) ^ (q -> r)", "(~p v q) ^ (~q v r)", "Duas implicações"),

        # ========================================
        # NÍVEL 6: Multi-passos Complexos (5+ passos)
        # ========================================
        ("~~p -> ~~q", "p -> q", "Dupla negação em implicação"),
        ("~(~p -> ~q)", "~p ^ q", "Neg da forma contrapositiva"),
        ("(p v ~p) -> q", "q", "Antecedente tautologia"),
        ("p -> (q v ~q)", "T", "Consequente tautologia"),
        ("(p ^ ~p) -> q", "T", "Antecedente contradição (ex falso)"),
        ("~~(p -> q)", "p -> q", "Dupla neg de implicação"),
        ("~(p ^ q) ^ ~(~p v ~q)", "F", "Contradição via De Morgan"),
        ("(p ^ q) v (~p ^ q) v (p ^ ~q) v (~p ^ ~q)", "T", "Tabela verdade completa"),

        # ========================================
        # NÍVEL 7: Muito Complexos (7+ passos)
        # ========================================
        ("~(~~p ^ ~~q)", "~p v ~q", "Processamento triplo"),
        ("((p -> q) ^ p) -> q", "T", "Modus Ponens é tautologia"),
        ("(p -> q) ^ (~q) -> ~p", "T", "Modus Tollens é tautologia"),
        ("(p -> (q -> r)) -> ((p -> q) -> (p -> r))", "T", "Axioma da distribuição"),
    ]

    # Testes que devem FALHAR (NÃO equivalentes)
    non_equivalent_tests = [
        ("p -> q", "q -> p", "Implicação NÃO é Comutativa"),
        ("p ^ q", "p v q", "E vs OU"),
        ("p -> q", "p ^ q", "Implicação vs Conjunção"),
        ("p -> q", "~p ^ q", "Implicação vs Forma Incorreta"),
        ("(p -> q) -> r", "p -> (q -> r)", "Implicação NÃO é Associativa"),
        ("p", "T", "Variável vs Verdadeiro"),
        ("p", "F", "Variável vs Falso"),
        ("p ^ q", "T", "Conjunção vs Verdadeiro"),
        ("p v q", "F", "Disjunção vs Falso"),
    ]

    print("PARTE 1: Testando proposições EQUIVALENTES (provas de múltiplos passos)")
    print("-" * 60)
    print()

    passed = 0
    failed = 0
    warnings = 0

    for prop1_str, prop2_str, description in equivalent_tests:
        result = run_single_test(prop1_str, prop2_str, description, model, eq,
                                 simplification_model=simplification_model,
                                 expected_equivalent=True, max_iterations=150)
        if result == 'pass':
            passed += 1
        elif result == 'warn':
            warnings += 1
        else:
            failed += 1

    print()
    print("PARTE 2: Testando proposições NÃO EQUIVALENTES")
    print("-" * 60)
    print()

    for prop1_str, prop2_str, description in non_equivalent_tests:
        result = run_single_test(prop1_str, prop2_str, description, model, eq,
                                 simplification_model=simplification_model,
                                 expected_equivalent=False, max_iterations=150)
        if result == 'pass':
            passed += 1
        elif result == 'warn':
            warnings += 1
        else:
            failed += 1

    # Resumo
    total = len(equivalent_tests) + len(non_equivalent_tests)
    print()
    print("=" * 60)
    print(f"  RESUMO DOS TESTES")
    print(f"  Total de testes: {total}")
    print(f"  Aprovados:       {passed}")
    print(f"  Avisos:          {warnings} (semanticamente equivalentes mas prova não encontrada)")
    print(f"  Reprovados:      {failed}")
    print("=" * 60)


def run_single_test(prop1_str, prop2_str, description, model, eq,
                    simplification_model=None, expected_equivalent=True,
                    max_iterations=150, show_steps=False):
    """Executa um único teste e retorna 'pass', 'warn' ou 'fail'."""
    print(f"Teste: {description}")
    print(f"  P1: {prop1_str}")
    print(f"  P2: {prop2_str}")

    try:
        prop1, props1 = parse_proposition(prop1_str)
        prop2, props2 = parse_proposition(prop2_str)

        # Verifica equivalência semântica primeiro
        is_semantically_equivalent = check_semantic_equivalence(prop1, props1, prop2, props2)

        if expected_equivalent:
            if not is_semantically_equivalent:
                print(f"  [FALHA] Esperado equivalente mas tabelas verdade diferem!")
                print()
                return 'fail'

            # Converte para CompoundProposition se necessário
            if isinstance(prop1, Proposition):
                prop1 = eq._ensure_compound(prop1)
            if isinstance(prop2, Proposition):
                prop2 = eq._ensure_compound(prop2)

            # Estratégia 1: Prova direta
            result = eq.prove_equivalence_nn(prop1, prop2, model,
                                              max_iterations=max_iterations, verbose=False)

            if result['success']:
                steps = result['iterations']
                nn_used = result['nn_predictions_used']
                total_transforms = len(result['transformations'])

                # Mostra detalhamento dos passos
                if steps == 0:
                    print(f"  [OK] Já são iguais (0 passos)")
                elif steps <= 2:
                    print(f"  [OK] {steps} passo(s), {total_transforms} transformação(ões) (NN: {nn_used})")
                else:
                    print(f"  [OK] {steps} passos, {total_transforms} transformação(ões) (NN: {nn_used})")

                # Opcionalmente mostra passos de transformação para provas multi-passo
                if show_steps and total_transforms > 0:
                    print(f"  Passos:")
                    for t in result['transformations'][:10]:  # Mostra primeiros 10 passos
                        marker = "[NN]" if t.get('used_nn', False) else "[RND]"
                        print(f"    {t['iteration']}. {marker} {t['law']} em P{t['proposition']}")
                    if total_transforms > 10:
                        print(f"    ... e mais {total_transforms - 10}")

                print()
                return 'pass'

            # Estratégia 2: Prova por contrapositiva
            contra_result = eq.prove_by_contrapositive(prop1, prop2, model,
                                                        max_iterations=max_iterations, verbose=False)

            if contra_result['success']:
                steps = contra_result['iterations']
                nn_used = contra_result['nn_predictions_used']
                print(f"  [OK] Contrapositiva: ~P1≡~P2 ({steps} passos), NN: {nn_used}")
                print()
                return 'pass'

            # Estratégia 3: Prova por absurdo
            absurd_result = eq.prove_by_absurdity(prop1, prop2, model,
                                                   simplification_predictor=simplification_model,
                                                   max_iterations=max_iterations, verbose=False)

            if absurd_result['success']:
                steps = absurd_result['iterations']
                nn_used = absurd_result['nn_predictions_used']
                print(f"  [OK] Absurdo: (P1^~P2)=F ({steps} passos), NN: {nn_used}")
                print()
                return 'pass'

            # Todos os métodos falharam
            total_iters = result['iterations'] + contra_result['iterations'] + absurd_result['iterations']
            print(f"  [AVISO] Semanticamente equivalente mas prova não encontrada")
            print(f"          Direta: {result['iterations']}, Contrapositiva: {contra_result['iterations']}, Absurdo: {absurd_result['iterations']} iterações")
            print(f"          P1 final: {result['prop1_final']}")
            print(f"          P2 final: {result['prop2_final']}")
            print()
            return 'warn'
        else:
            if is_semantically_equivalent:
                print(f"  [INESPERADO] Estas SÃO semanticamente equivalentes!")
                print()
                return 'fail'
            else:
                print(f"  [OK] Corretamente identificado como NÃO equivalente")
                print()
                return 'pass'

    except ParseError as e:
        print(f"  [ERRO] Erro de análise: {e}")
        print()
        return 'fail'


def run_examples(examples, model, eq, simplification_model=None, max_iterations=30):
    """Executa uma lista de exemplos com saída completa."""
    for prop1_str, prop2_str, description in examples:
        print("=" * 50)
        print(f"Exemplo: {description}")
        print(f"  P1: {prop1_str}")
        print(f"  P2: {prop2_str}")

        try:
            prop1, props1 = parse_proposition(prop1_str)
            prop2, props2 = parse_proposition(prop2_str)

            # Converte para CompoundProposition se necessário
            if isinstance(prop1, Proposition):
                prop1 = eq._ensure_compound(prop1)
            if isinstance(prop2, Proposition):
                prop2 = eq._ensure_compound(prop2)

            prove_and_display(prop1, prop2, model, eq,
                             simplification_model=simplification_model,
                             max_iterations=max_iterations)

        except ParseError as e:
            print(f"  Erro de análise: {e}")

        print()


def show_menu():
    """Exibe o menu principal e obtém a escolha do usuário."""
    print()
    print("Escolha um modo:")
    print("  [1] Modo interativo - Digite proposições manualmente")
    print("  [2] Modo demonstração - Exemplos simples com saída passo a passo")
    print("  [3] Modo teste - Testes abrangentes (equivalências complexas)")
    print("  [s] Sair")
    print()

    try:
        choice = input("Escolha (1/2/3/s): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return 'q'

    return choice


def main():
    """Ponto de entrada principal."""
    print_header()

    # Verifica argumentos de linha de comando primeiro
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("Uso: python main.py [OPÇÕES]")
            print()
            print("Opções:")
            print("  --interactive, -i  Executa modo interativo diretamente")
            print("  --demo, -d         Executa modo demonstração com exemplos simples")
            print("  --test, -t         Executa suite de testes abrangentes")
            print("  --help, -h         Exibe esta mensagem de ajuda")
            print()
            print("Sem argumentos, exibe o menu de seleção de modo.")
            return

        # Treina ambos os modelos
        model, simplification_model = train_model(verbose=True)
        eq = Equivalence()

        if sys.argv[1] in ('--demo', '-d'):
            demo_mode(model, eq, simplification_model)
            return
        elif sys.argv[1] in ('--test', '-t'):
            test_mode(model, eq, simplification_model)
            return
        elif sys.argv[1] in ('--interactive', '-i'):
            print("Digite duas proposições para verificar sua equivalência.\n")
            interactive_mode(model, eq, simplification_model)
            return

    # Treina ambos os modelos
    model, simplification_model = train_model(verbose=True)
    eq = Equivalence()

    # Exibe menu e executa modo selecionado
    while True:
        choice = show_menu()

        if choice in ('1', 'i', 'interactive', 'interativo'):
            print("\n" + "=" * 60)
            print("Digite duas proposições para verificar sua equivalência.\n")
            interactive_mode(model, eq, simplification_model)
        elif choice in ('2', 'd', 'demo', 'demonstracao'):
            print()
            demo_mode(model, eq, simplification_model)
        elif choice in ('3', 't', 'test', 'teste'):
            print()
            test_mode(model, eq, simplification_model)
        elif choice in ('q', 'quit', 'exit', 's', 'sair'):
            print("\nAté logo!")
            break
        else:
            print("Escolha inválida. Tente novamente.")


if __name__ == "__main__":
    main()
