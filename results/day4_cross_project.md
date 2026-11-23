# Day 4: cross-project results

Leave-one-repo-out over 18 repos (4523 TODOs): each repo is
predicted by a model trained only on the other 17. Same model and
settings as Day 3 (learning rate 0.5, 1000 iterations, lambda 0.001).

## Pooled over all held-out predictions

| | ROC-AUC | PR-AUC | Precision | Recall | F1 |
|---|---|---|---|---|---|
| Rule: deadline OR removal | 0.718 | 0.565 | 0.689 | 0.557 | 0.616 |
| **Logistic regression, unseen repos** | 0.754 | 0.632 | 0.694 | 0.527 | 0.599 |
| Logistic regression, unseen repos, untagged only | 0.590 | 0.272 | 0.323 | 0.122 | 0.177 |

Mean per-repo ROC-AUC (repos with at least 5 resolved and 5 rotting
TODOs, 18 of 18): **0.646**

Pooled scores mix projects with different resolved rates, so the mean per-repo
AUC is the fairer summary of "how well does it rank TODOs inside a new project".

## Per repo

| Repo (held out) | TODOs | Resolved rate | ROC-AUC | PR-AUC | F1 |
|---|---|---|---|---|---|
| pandas-dev/pandas | 1335 | 36.6% | 0.652 | 0.526 | 0.306 |
| scikit-learn/scikit-learn | 958 | 68.6% | 0.853 | 0.912 | 0.874 |
| sympy/sympy | 412 | 6.6% | 0.727 | 0.128 | 0.185 |
| ansible/ansible | 327 | 9.5% | 0.564 | 0.109 | 0.000 |
| astropy/astropy | 238 | 6.3% | 0.670 | 0.226 | 0.158 |
| apache/airflow | 233 | 22.3% | 0.619 | 0.306 | 0.336 |
| sqlalchemy/sqlalchemy | 224 | 19.2% | 0.562 | 0.316 | 0.235 |
| saltstack/salt | 151 | 9.3% | 0.628 | 0.299 | 0.300 |
| scipy/scipy | 130 | 16.9% | 0.581 | 0.288 | 0.276 |
| dask/dask | 91 | 22.0% | 0.523 | 0.281 | 0.256 |
| pypa/setuptools | 89 | 15.7% | 0.398 | 0.189 | 0.250 |
| numpy/numpy | 89 | 14.6% | 0.630 | 0.245 | 0.118 |
| pypa/pip | 62 | 32.3% | 0.557 | 0.446 | 0.294 |
| networkx/networkx | 51 | 35.3% | 0.778 | 0.731 | 0.348 |
| pytest-dev/pytest | 50 | 14.0% | 0.551 | 0.166 | 0.111 |
| celery/celery | 39 | 41.0% | 0.802 | 0.733 | 0.727 |
| ipython/ipython | 24 | 20.8% | 0.758 | 0.373 | 0.000 |
| django/django | 20 | 45.0% | 0.768 | 0.688 | 0.167 |

\* fewer than 5 TODOs of one class: AUC is unreliable, left out of the mean.
