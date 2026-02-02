"""
Neural network model for predicting the best transformation.
"""
import pickle
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from utils.nn.features import extract_pair_features, extract_single_features
from utils.nn.dataset import (decode_prediction, CLASS_MAPPING,
                              decode_simplification_prediction, SIMPLIFICATION_CLASS_MAPPING)


class TransformationPredictor:
    """
    Neural network that predicts which transformation to apply.

    Architecture:
    - Input: 66 features (33 per proposition)
      - 17 structural/semantic features per proposition
      - 16 applicability features per proposition (which transformations can be applied)
    - Hidden layers: configurable (default 64, 32)
    - Output: 32 classes (16 transformations x 2 propositions)

    Structural features (17 per proposition):
    - depth, num_nodes, num_atomic
    - num_negations, num_conjunctions, num_disjunctions, num_implications
    - has_double_negation, has_de_morgan_pattern, has_implication
    - has_binary_root, is_atomic
    - useful_count, useless_count, useful_ratio
    - is_tautology, is_contradiction

    Applicability features (16 per proposition):
    - Indicates which transformations can actually be applied
    - Eliminates randomness when NN predicts valid transformations

    Prioritizes simplification operations:
    - double_negation (~~p -> p)
    - idempotence (p ^ p -> p)
    - absorption (p ^ (p v q) -> p)
    - factoring ((p^q)v(p^r) -> p^(qvr)) - reverse distributivity
    - complement (p v ~p -> T, p ^ ~p -> F)
    - identity (p v F -> p, p ^ T -> p)
    - domination (p v T -> T, p ^ F -> F)
    """

    def __init__(self, hidden_layers: tuple = (64, 32), max_iter: int = 1000):
        """
        Initialize the predictor.

        Args:
            hidden_layers: Tuple of hidden layer sizes
            max_iter: Maximum training iterations
        """
        self.model = MLPClassifier(
            hidden_layer_sizes=hidden_layers,
            activation='relu',
            solver='adam',
            max_iter=max_iter,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        )
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray, verbose: bool = False,
              balance: bool = True) -> dict:
        """
        Train the neural network.

        Args:
            X: Feature matrix (n_samples, 20)
            y: Class labels (n_samples,)
            verbose: Print training info
            balance: Balance classes before training

        Returns:
            Dict with training metrics
        """
        if balance:
            from utils.nn.dataset import balance_dataset
            X, y = balance_dataset(X, y)
            if verbose:
                print(f"Balanced dataset: {len(X)} samples")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        if verbose:
            print(f"Training accuracy: {train_score:.2%}")
            print(f"Test accuracy: {test_score:.2%}")
            print(f"Training iterations: {self.model.n_iter_}")

            y_pred = self.model.predict(X_test)
            print("\nClassification Report:")
            print(classification_report(y_test, y_pred, zero_division=0))

        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'iterations': self.model.n_iter_
        }

    def predict(self, prop1, prop2) -> tuple:
        """
        Predict which transformation to apply.

        Args:
            prop1: First proposition
            prop2: Second proposition

        Returns:
            (which_prop, transformation_name)
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        features = extract_pair_features(prop1, prop2)
        features = np.array(features).reshape(1, -1)

        prediction = self.model.predict(features)[0]
        return decode_prediction(prediction)

    def predict_proba(self, prop1, prop2) -> dict:
        """
        Get probability distribution over all transformations.

        Args:
            prop1: First proposition
            prop2: Second proposition

        Returns:
            Dict mapping (which_prop, transform_name) to probability
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        features = extract_pair_features(prop1, prop2)
        features = np.array(features).reshape(1, -1)

        probas = self.model.predict_proba(features)[0]

        result = {}
        for class_idx, proba in enumerate(probas):
            if class_idx in CLASS_MAPPING:
                which_prop, transform_name = CLASS_MAPPING[class_idx]
                result[(which_prop, transform_name)] = proba

        return result

    def save(self, path: str):
        """Save the model to a file."""
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

    def load(self, path: str):
        """Load the model from a file."""
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
        self.is_trained = True

    def get_architecture(self) -> dict:
        """Get information about the model architecture."""
        return {
            'input_size': 68,  # 34 features per proposition (17 structural + 17 applicability)
            'hidden_layers': self.model.hidden_layer_sizes,
            'output_size': len(CLASS_MAPPING),
            'activation': self.model.activation,
            'classes': list(CLASS_MAPPING.values())
        }


class SimplificationPredictor:
    """
    Neural network for absurdity proofs - simplifies single expression to constant.

    Used for reductio ad absurdum proofs where:
    - Input: Single expression (P1 ∧ ~P2) that should simplify to F
    - Goal: Choose transformations that lead to the constant F (or T)

    Architecture:
    - Input: 35 features
      - 17 structural features (depth, nodes, operators, patterns)
      - 17 applicability features (which transformations can apply)
      - 1 goal indicator (0=reach_F for absurdity, 1=reach_T)
    - Hidden layers: (32, 16) - smaller than convergence model
    - Output: 17 classes (one for each transformation type)

    Focuses on transformations that simplify to constants:
    - complement (p ∧ ~p → F, p ∨ ~p → T) - CRITICAL
    - distributivity (expose complement patterns) - CRITICAL
    - domination (p ∧ F → F, p ∨ T → T) - CRITICAL for propagation
    - identity (p ∧ T → p, p ∨ F → p) - simplify after constants appear
    - double_negation, de_morgan (reach simplifiable forms)
    """

    def __init__(self, hidden_layers: tuple = (32, 16), max_iter: int = 1000):
        """
        Initialize the simplification predictor.

        Args:
            hidden_layers: Tuple of hidden layer sizes (smaller than convergence model)
            max_iter: Maximum training iterations
        """
        self.model = MLPClassifier(
            hidden_layer_sizes=hidden_layers,
            activation='relu',
            solver='adam',
            max_iter=max_iter,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        )
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray, verbose: bool = False,
              balance: bool = True) -> dict:
        """
        Train the neural network with simplification samples.

        Args:
            X: Feature matrix (n_samples, 35)
            y: Class labels (n_samples,) - transformation indices
            verbose: Print training info
            balance: Balance classes before training

        Returns:
            Dict with training metrics
        """
        if balance:
            from utils.nn.dataset import balance_dataset
            X, y = balance_dataset(X, y)
            if verbose:
                print(f"[SimplificationPredictor] Balanced dataset: {len(X)} samples")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        if verbose:
            print(f"[SimplificationPredictor] Training accuracy: {train_score:.2%}")
            print(f"[SimplificationPredictor] Test accuracy: {test_score:.2%}")
            print(f"[SimplificationPredictor] Training iterations: {self.model.n_iter_}")

            y_pred = self.model.predict(X_test)
            print("\n[SimplificationPredictor] Classification Report:")
            print(classification_report(y_test, y_pred, zero_division=0))

        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'iterations': self.model.n_iter_
        }

    def predict(self, prop, goal: str = 'F') -> str:
        """
        Predict which transformation to apply to simplify the expression.

        Args:
            prop: The proposition to simplify
            goal: Target constant - 'F' for absurdity, 'T' for tautology

        Returns:
            transformation_name (string)
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        features = extract_single_features(prop, goal=goal)
        features = np.array(features).reshape(1, -1)

        prediction = self.model.predict(features)[0]
        return decode_simplification_prediction(prediction)

    def predict_proba(self, prop, goal: str = 'F') -> dict:
        """
        Get probability distribution over all transformations.

        Args:
            prop: The proposition to simplify
            goal: Target constant - 'F' for absurdity, 'T' for tautology

        Returns:
            Dict mapping transformation_name to probability
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")

        features = extract_single_features(prop, goal=goal)
        features = np.array(features).reshape(1, -1)

        probas = self.model.predict_proba(features)[0]

        result = {}
        for class_idx, proba in enumerate(probas):
            if class_idx in SIMPLIFICATION_CLASS_MAPPING:
                transform_name = SIMPLIFICATION_CLASS_MAPPING[class_idx]
                result[transform_name] = proba

        return result

    def save(self, path: str):
        """Save the model to a file."""
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

    def load(self, path: str):
        """Load the model from a file."""
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
        self.is_trained = True

    def get_architecture(self) -> dict:
        """Get information about the model architecture."""
        return {
            'input_size': 35,  # 17 structural + 17 applicability + 1 goal
            'hidden_layers': self.model.hidden_layer_sizes,
            'output_size': len(SIMPLIFICATION_CLASS_MAPPING),
            'activation': self.model.activation,
            'classes': list(SIMPLIFICATION_CLASS_MAPPING.values())
        }
