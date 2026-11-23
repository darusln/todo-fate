# Day 3 results (2026-11-20)

Data: `dataset.csv`, 4523 TODOs.
Settings: learning rate 0.5, 1000 iterations, L2 lambda 0.001,
TF-IDF min_df 5, max 2000 words (732 kept),
class-weighted log-loss, decision threshold 0.5.

## Cohorts

| Cohort | TODOs | Resolved | Rate |
|---|---|---|---|
| 2019 | 694 | 220 | 31.7% |
| 2020 | 808 | 241 | 29.8% |
| 2021 | 961 | 398 | 41.4% |
| 2022 | 826 | 258 | 31.2% |
| 2023 | 727 | 196 | 27.0% |
| 2024 | 507 | 158 | 31.2% |

Split: train = cohorts before 2022 (2463), validation = 2022 (826),
test = after 2022 (1234).

## Test results (model fit on train + validation)

| | ROC-AUC | PR-AUC | Precision | Recall | F1 | Rot precision@50 |
|---|---|---|---|---|---|---|
| Always predict rotting | 0.500 | 0.298 | 0.000 | 0.000 | 0.000 | 0.680 |
| Rule: deadline OR removal | 0.732 | 0.554 | 0.645 | 0.596 | 0.620 | 0.840 |
| **Logistic regression** | 0.832 | 0.646 | 0.671 | 0.658 | 0.665 | 1.000 |
| Logistic regression, untagged TODOs only | 0.740 | 0.362 | 0.463 | 0.348 | 0.397 | 1.000 |

Rot precision@k: of the k TODOs the model rates least likely to be resolved,
the share that really were still there a year later.

## Validation results (model fit on train only)

| | ROC-AUC | PR-AUC | Precision | Recall | F1 | Rot precision@50 |
|---|---|---|---|---|---|---|
| Always predict rotting | 0.500 | 0.332 | 0.000 | 0.000 | 0.000 | 0.680 |
| Rule: deadline OR removal | 0.695 | 0.522 | 0.623 | 0.539 | 0.578 | 0.760 |
| **Logistic regression** | 0.775 | 0.633 | 0.613 | 0.570 | 0.590 | 0.900 |
| Logistic regression, untagged TODOs only | 0.696 | 0.398 | 0.461 | 0.240 | 0.315 | 0.900 |

## Largest weights toward "resolved"

| Feature | Weight |
|---|---|
| is_deadline_tagged | +1.671 |
| word:<ver> | +1.475 |
| word:in | +1.011 |
| has_owner_tag | +0.983 |
| word:removed | +0.927 |
| asks_removal | +0.873 |
| mentions_defect | +0.571 |
| word:kludge | +0.548 |
| word:can | +0.486 |
| word:raise | +0.428 |
| word:when | +0.389 |
| word:filterwarnings | +0.386 |
| word:mark | +0.345 |
| word:on | +0.330 |
| word:deprecation | +0.330 |

## Largest weights toward "rotting"

| Feature | Weight |
|---|---|
| word:airflow | -0.713 |
| marker_XXX | -0.620 |
| word:test | -0.521 |
| word:check | -0.495 |
| word:one | -0.466 |
| word:other | -0.446 |
| is_docs_or_example | -0.431 |
| word:if | -0.430 |
| word:<num> | -0.425 |
| word:set | -0.347 |
| word:not | -0.325 |
| word:day | -0.325 |
| word:so | -0.275 |
| word:needs | -0.271 |
| word:assert | -0.261 |

Weights of correlated features (e.g. deadline-tagged and asks-removal) share
credit, so read them as directions, not exact importances.

## Training loss (final model)

| Iteration | Loss |
|---|---|
| 0 | 0.69315 |
| 100 | 0.52951 |
| 200 | 0.51802 |
| 300 | 0.51273 |
| 400 | 0.50910 |
| 500 | 0.50624 |
| 600 | 0.50389 |
| 700 | 0.50192 |
| 800 | 0.50025 |
| 900 | 0.49883 |
| 1000 | 0.49763 |
