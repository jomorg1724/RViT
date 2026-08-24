"""Datasets for RViT+ training. Stage 1 = MovingMNIST; Stage 2 = KTH / UCF101."""
from .moving_mnist import MovingMNIST, generate_moving_mnist_batch

__all__ = ["MovingMNIST", "generate_moving_mnist_batch"]
