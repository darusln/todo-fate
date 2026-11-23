# Day 3 results (2026-11-23)

Data: `data/dataset.csv`, 4523 TODOs.
Settings: learning rate 0.5, 3000 iterations, L2 lambda 0.001,
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
| **Logistic regression** | 0.832 | 0.644 | 0.651 | 0.644 | 0.648 | 1.000 |
| Logistic regression, untagged TODOs only | 0.742 | 0.359 | 0.418 | 0.326 | 0.366 | 1.000 |

Rot precision@k: of the k TODOs the model rates least likely to be resolved,
the share that really were still there a year later.

## Validation results (model fit on train only)

| | ROC-AUC | PR-AUC | Precision | Recall | F1 | Rot precision@50 |
|---|---|---|---|---|---|---|
| Always predict rotting | 0.500 | 0.332 | 0.000 | 0.000 | 0.000 | 0.680 |
| Rule: deadline OR removal | 0.695 | 0.522 | 0.623 | 0.539 | 0.578 | 0.760 |
| **Logistic regression** | 0.774 | 0.631 | 0.595 | 0.570 | 0.582 | 0.900 |
| Logistic regression, untagged TODOs only | 0.698 | 0.399 | 0.442 | 0.260 | 0.328 | 0.900 |

## Largest weights toward "resolved"

| Feature | Weight |
|---|---|
| word:<ver> | +1.856 |
| is_deadline_tagged | +1.565 |
| word:removed | +1.222 |
| word:in | +1.137 |
| has_owner_tag | +0.964 |
| word:kludge | +0.855 |
| asks_removal | +0.854 |
| word:can | +0.677 |
| word:raise | +0.628 |
| word:filterwarnings | +0.589 |
| word:mark | +0.580 |
| mentions_defect | +0.564 |
| word:fail | +0.552 |
| word:just | +0.547 |
| word:deprecation | +0.533 |

## Largest weights toward "rotting"

| Feature | Weight |
|---|---|
| word:airflow | -1.318 |
| word:other | -0.759 |
| word:check | -0.720 |
| word:one | -0.704 |
| word:test | -0.677 |
| is_docs_or_example | -0.659 |
| word:if | -0.644 |
| word:set | -0.576 |
| marker_XXX | -0.534 |
| word:<num> | -0.534 |
| word:so | -0.476 |
| word:day | -0.474 |
| word:needs | -0.450 |
| word:not | -0.449 |
| word:avoid | -0.437 |

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
| 1100 | 0.49659 |
| 1200 | 0.49571 |
| 1300 | 0.49495 |
| 1400 | 0.49429 |
| 1500 | 0.49372 |
| 1600 | 0.49323 |
| 1700 | 0.49281 |
| 1800 | 0.49244 |
| 1900 | 0.49212 |
| 2000 | 0.49184 |
| 2100 | 0.49160 |
| 2200 | 0.49138 |
| 2300 | 0.49120 |
| 2400 | 0.49104 |
| 2500 | 0.49090 |
| 2600 | 0.49077 |
| 2700 | 0.49067 |
| 2800 | 0.49057 |
| 2900 | 0.49049 |
| 3000 | 0.49042 |
