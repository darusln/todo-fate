"""Checks that the from-scratch components compute what they claim.

Run (from the project folder):  python3 -m tests.test_model
Each check prints OK or stops with an error. Mention these in the report:
they show the implementation was verified, not just run.
"""

import math

import numpy as np

from todofate.model.logreg import LogisticRegression, sigmoid
from todofate.model.metrics import average_precision, precision_at_k, precision_recall_f1, roc_auc
from todofate.model.tfidf import TfidfVectorizer, tokenize


def check(name, condition):
    assert condition, f"FAILED: {name}"
    print(f"OK  {name}")


# --- TF-IDF -------------------------------------------------------------------
check("tokenize replaces versions and numbers",
      tokenize("Remove in v0.23, see issue 1234") == ["remove", "in", "<ver>", "see", "issue", "<num>"])

docs = ["remove remove deprecated", "remove this", "add tests"]
vec = TfidfVectorizer(min_df=1).fit(docs)
X = vec.transform(docs)
# By hand for document 0: "remove" appears twice and in 2 of 3 docs,
# "deprecated" once and in 1 of 3 docs.
idf_remove = math.log(4 / 3) + 1
idf_deprecated = math.log(4 / 2) + 1
raw = np.array([2 * idf_remove, 1 * idf_deprecated])
expected = raw / np.linalg.norm(raw)
check("tf-idf value matches hand calculation",
      np.isclose(X[0, vec.vocab["remove"]], expected[0]) and
      np.isclose(X[0, vec.vocab["deprecated"]], expected[1]))
check("each row has length 1", np.allclose(np.linalg.norm(X, axis=1), 1))
check("unseen words are ignored", vec.transform(["completely unknown words"]).sum() == 0)

# --- Logistic regression ------------------------------------------------------
check("sigmoid is stable at extremes",
      sigmoid(np.array([-1000.0]))[0] == 0.0 and sigmoid(np.array([1000.0]))[0] == 1.0)

rng = np.random.default_rng(0)
Xs = rng.normal(size=(20, 5))
ys = (rng.random(20) > 0.6).astype(float)
model = LogisticRegression(lam=0.1)
c = model._sample_weights(ys)
w, b = rng.normal(size=5), 0.3
grad_w, grad_b = model.gradient(Xs, ys, w, b, c)
eps = 1e-6
numeric_w = np.array([
    (model.loss(Xs, ys, w + eps * e, b, c) - model.loss(Xs, ys, w - eps * e, b, c)) / (2 * eps)
    for e in np.eye(5)
])
numeric_b = (model.loss(Xs, ys, w, b + eps, c) - model.loss(Xs, ys, w, b - eps, c)) / (2 * eps)
max_diff = max(np.abs(grad_w - numeric_w).max(), abs(grad_b - numeric_b))
check(f"gradient matches numerical estimate (max difference {max_diff:.1e})", max_diff < 1e-6)

Xt = np.vstack([rng.normal(-2, 1, size=(50, 2)), rng.normal(2, 1, size=(50, 2))])
yt = np.array([0] * 50 + [1] * 50)
fitted = LogisticRegression(n_iter=500, verbose=False).fit(Xt, yt)
check("learns two separated clusters (accuracy > 95%)", (fitted.predict(Xt) == yt).mean() > 0.95)
losses = [l for _, l in fitted.loss_history]
check("training loss never increases", all(a >= b for a, b in zip(losses, losses[1:])))

# --- Metrics ------------------------------------------------------------------
y = np.array([0, 0, 1, 0, 1, 1])
check("AUC = 1 for a perfect ranking", roc_auc(y, [0.1, 0.2, 0.8, 0.3, 0.9, 0.7]) == 1.0)
check("AUC = 0 for a reversed ranking", roc_auc(y, [0.9, 0.8, 0.1, 0.7, 0.2, 0.3]) == 0.0)
check("AUC = 0.5 when every score ties", roc_auc(y, [0.5] * 6) == 0.5)
# Ranking 1,0,1,0: precision 1/1 at the first hit, 2/3 at the second.
check("average precision matches hand calculation",
      np.isclose(average_precision([1, 0, 1, 0], [0.9, 0.8, 0.7, 0.6]), (1 + 2 / 3) / 2))
check("precision@k", precision_at_k([1, 0, 1, 0], [0.9, 0.8, 0.7, 0.6], k=2) == 0.5)
p, r, f = precision_recall_f1([1, 1, 0, 0], [1, 0, 1, 0])
check("precision / recall / F1", (p, r, f) == (0.5, 0.5, 0.5))

# --- Optional: agreement with scikit-learn ------------------------------------
try:
    from sklearn.metrics import roc_auc_score, average_precision_score
except ImportError:
    print("--  scikit-learn not installed, skipping the cross-check (fine)")
else:
    ry = rng.integers(0, 2, 300)
    rs = np.round(rng.random(300), 2)          # rounding creates ties on purpose
    check("AUC agrees with scikit-learn", np.isclose(roc_auc(ry, rs), roc_auc_score(ry, rs)))
    rs = rng.random(300)                       # sklearn's AP handles ties differently
    check("average precision agrees with scikit-learn",
          np.isclose(average_precision(ry, rs), average_precision_score(ry, rs)))

print("\nAll checks passed.")
