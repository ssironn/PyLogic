"""
Neural Network module for the equivalence prover.

This module provides a neural network that learns to predict
which transformation to apply when proving logical equivalences.

Usage:
    from nn import TransformationPredictor, generate_dataset

    # Generate training data
    X, y = generate_dataset(num_samples=1000)

    # Train the model
    model = TransformationPredictor()
    model.train(X, y, verbose=True)

    # Make predictions
    which_prop, transform = model.predict(prop1, prop2)

    # Save/load model
    model.save('model.pkl')
    model.load('model.pkl')
"""

from nn.features import extract_features, extract_pair_features
from nn.dataset import generate_dataset, decode_prediction, encode_action, balance_dataset
from nn.model import TransformationPredictor

__all__ = [
    'extract_features',
    'extract_pair_features',
    'generate_dataset',
    'decode_prediction',
    'encode_action',
    'balance_dataset',
    'TransformationPredictor',
]
