"""Binary logistic regression, written from scratch with NumPy.

Model:      p = sigmoid(X·w + b)
Loss:       weighted log-loss + (lam/2)·||w||²     (the bias b is not regularised)
Training:   batch gradient descent

Class weights make a mistake on the rarer class cost more, so the model
doesn't win cheaply by predicting the majority class for everything.
"""

import numpy as np


def sigmoid(z):
    # Equivalent to 1 / (1 + exp(-z)), but never overflows: logaddexp(0, -z)
    # computes log(1 + exp(-z)) safely for very large or very small z.
    return np.exp(-np.logaddexp(0, -z))


class LogisticRegression:
    def __init__(self, lr=0.5, n_iter=1000, lam=1e-3, class_weight=True, verbose=True):
        self.lr = lr                      # gradient descent step size
        self.n_iter = n_iter
        self.lam = lam                    # L2 regularisation strength
        self.class_weight = class_weight
        self.verbose = verbose
        self.w, self.b = None, 0.0
        self.loss_history = []

    def _sample_weights(self, y):
        if not self.class_weight:
            return np.ones_like(y, dtype=float)
        n, n_pos = len(y), y.sum()
        n_neg = n - n_pos
        # Each class then contributes half of the total weight.
        return np.where(y == 1, n / (2 * n_pos), n / (2 * n_neg))

    def loss(self, X, y, w, b, c):
        p = np.clip(sigmoid(X @ w + b), 1e-12, 1 - 1e-12)
        log_loss = -np.mean(c * (y * np.log(p) + (1 - y) * np.log(1 - p)))
        return log_loss + self.lam / 2 * np.dot(w, w)

    def gradient(self, X, y, w, b, c):
        error = c * (sigmoid(X @ w + b) - y)       # weighted residuals
        grad_w = X.T @ error / len(y) + self.lam * w
        grad_b = error.mean()
        return grad_w, grad_b

    def fit(self, X, y):
        y = np.asarray(y, dtype=float)
        c = self._sample_weights(y)
        self.w, self.b = np.zeros(X.shape[1]), 0.0
        self.loss_history = []
        for it in range(self.n_iter + 1):
            if it % 100 == 0:
                current = self.loss(X, y, self.w, self.b, c)
                self.loss_history.append((it, current))
                if self.verbose:
                    print(f"    iter {it:5d}  loss {current:.5f}")
            if it == self.n_iter:
                break
            grad_w, grad_b = self.gradient(X, y, self.w, self.b, c)
            self.w -= self.lr * grad_w
            self.b -= self.lr * grad_b
        return self

    def predict_proba(self, X):
        """Probability that each TODO gets resolved."""
        return sigmoid(X @ self.w + self.b)

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)
