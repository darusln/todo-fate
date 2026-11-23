"""Evaluation metrics, written from scratch with NumPy.

y_true holds 1 (resolved) / 0 (rotting); scores are the model's predicted
probability of "resolved". Higher score = more likely resolved.
"""

import numpy as np

_TIE_SEED = 0


def _rank_order(scores):
    """Indices from highest to lowest score. Ties are broken randomly (fixed
    seed), so a constant or yes/no scorer is judged like a random ranking
    instead of by whatever order the rows happen to be in."""
    scores = np.asarray(scores, dtype=float)
    tiebreak = np.random.default_rng(_TIE_SEED).random(len(scores))
    return np.lexsort((tiebreak, -scores))


def confusion(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))
    tn = int(np.sum((y_pred == 0) & (y_true == 0)))
    return tp, fp, fn, tn


def precision_recall_f1(y_true, y_pred):
    tp, fp, fn, _ = confusion(y_true, y_pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def average_ranks(scores):
    """Rank 1 = lowest score; tied scores share the average of their ranks."""
    scores = np.asarray(scores, dtype=float)
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(len(scores))
    sorted_scores = scores[order]
    i = 0
    while i < len(scores):
        j = i
        while j + 1 < len(scores) and sorted_scores[j + 1] == sorted_scores[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1    # average of ranks i+1 .. j+1
        i = j + 1
    return ranks


def roc_auc(y_true, scores):
    """Probability that a random resolved TODO scores above a random rotting one.

    Rank formula (Mann-Whitney U): exact, and needs no ROC curve.
    """
    y_true = np.asarray(y_true)
    n_pos, n_neg = int(y_true.sum()), int(len(y_true) - y_true.sum())
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    ranks = average_ranks(scores)
    return (ranks[y_true == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def average_precision(y_true, scores):
    """PR-AUC: mean precision at each rank where a resolved TODO appears."""
    y_true = np.asarray(y_true)
    hits = y_true[_rank_order(scores)]
    if hits.sum() == 0:
        return float("nan")
    precision_at_i = np.cumsum(hits) / np.arange(1, len(hits) + 1)
    return float(precision_at_i[hits == 1].mean())


def precision_at_k(y_true, scores, k, positive=1):
    """Of the k highest-scoring items, the share whose label is `positive`."""
    y_true = np.asarray(y_true)
    order = _rank_order(scores)[:k]
    return float(np.mean(y_true[order] == positive))


def evaluate(y_true, scores, threshold=0.5, k=50):
    """All metrics in one dict. Precision@k ranks by RISK OF ROTTING (1 - score)."""
    y_pred = (np.asarray(scores) >= threshold).astype(int)
    precision, recall, f1 = precision_recall_f1(y_true, y_pred)
    k = min(k, len(y_true))
    return {
        "n": len(y_true),
        "resolved_rate": float(np.mean(y_true)),
        "roc_auc": roc_auc(y_true, scores),
        "pr_auc": average_precision(y_true, scores),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        f"rot_precision@{k}": precision_at_k(y_true, -np.asarray(scores), k, positive=0),
    }
