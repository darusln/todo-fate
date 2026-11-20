"""Day 3: train the TODO-fate model and evaluate it on a time-based split.

Usage:
    python3 train.py                         # dataset.csv -> results_day3.md
    python3 train.py --data test_dataset.csv --lam 0.01

Split (by the year the TODO was observed, i.e. its cohort):
    train       cohorts up to 2021
    validation  cohort 2022     a sanity check of the settings, never the test set
    test        cohorts 2023+   touched once, for the final numbers

Two phases:
    1. fit on train, score on validation   (are the settings sensible?)
    2. fit on train + validation, score on test   (the reported result)
Every statistic the features need (vocabulary, idf, means, standard
deviations) is learned from the fitting rows only, so nothing leaks from the
rows being scored.
"""

import argparse
import csv
from collections import defaultdict
from datetime import date

import numpy as np

from features import BINARY_FEATURES, NUMERIC_FEATURES
from model.logreg import LogisticRegression
from model.metrics import evaluate
from model.tfidf import TfidfVectorizer

METRICS = ["roc_auc", "pr_auc", "precision", "recall", "f1"]


def load(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["year"] = int(r["snapshot"][:4])
        r["label"] = int(r["label"])
    return rows


def cohort_table(rows):
    counts = defaultdict(lambda: [0, 0])
    for r in rows:
        counts[r["year"]][0] += 1
        counts[r["year"]][1] += r["label"]
    lines = ["| Cohort | TODOs | Resolved | Rate |", "|---|---|---|---|"]
    for year in sorted(counts):
        n, res = counts[year]
        lines.append(f"| {year} | {n} | {res} | {res / n:.1%} |")
    return "\n".join(lines)


class FeatureBuilder:
    """TF-IDF of the text + binary features + standardised numeric features."""

    def __init__(self, min_df, max_features):
        self.tfidf = TfidfVectorizer(min_df=min_df, max_features=max_features)

    def fit(self, rows):
        self.tfidf.fit([r["text"] for r in rows])
        numeric = self._numeric(rows)
        self.mean = numeric.mean(axis=0)
        self.std = numeric.std(axis=0)
        self.std[self.std == 0] = 1
        return self

    def transform(self, rows):
        text = self.tfidf.transform([r["text"] for r in rows])
        binary = np.array([[float(r[c]) for c in BINARY_FEATURES] for r in rows])
        numeric = (self._numeric(rows) - self.mean) / self.std
        return np.hstack([text, binary, numeric])

    def names(self):
        return self.tfidf.feature_names() + BINARY_FEATURES + NUMERIC_FEATURES

    @staticmethod
    def _numeric(rows):
        return np.array([[float(r[c]) for c in NUMERIC_FEATURES] for r in rows])


def fit_and_score(fit_rows, score_rows, args, verbose):
    builder = FeatureBuilder(args.min_df, args.max_features).fit(fit_rows)
    X_fit, y_fit = builder.transform(fit_rows), np.array([r["label"] for r in fit_rows])
    model = LogisticRegression(lr=args.lr, n_iter=args.iters, lam=args.lam, verbose=verbose)
    model.fit(X_fit, y_fit)
    scores = model.predict_proba(builder.transform(score_rows))
    return model, builder, scores


def metric_row(name, y, scores, k):
    m = evaluate(y, scores, k=k)
    cells = " | ".join(f"{m[key]:.3f}" for key in METRICS)
    return f"| {name} | {cells} | {m[f'rot_precision@{min(k, len(y))}']:.3f} |", m


def results_table(rows, scores, k):
    y = np.array([r["label"] for r in rows])
    rule = np.array([float(r["is_deadline_tagged"] == "1" or r["asks_removal"] == "1") for r in rows])
    untagged = np.array([r["is_deadline_tagged"] == "0" for r in rows])
    kk = min(k, len(y))
    lines = [f"| | ROC-AUC | PR-AUC | Precision | Recall | F1 | Rot precision@{kk} |",
             "|---|---|---|---|---|---|---|"]
    lines.append(metric_row("Always predict rotting", y, np.zeros(len(y)), k)[0])
    lines.append(metric_row("Rule: deadline OR removal", y, rule, k)[0])
    model_line, model_metrics = metric_row("**Logistic regression**", y, scores, k)
    lines.append(model_line)
    if untagged.sum() and 0 < y[untagged].sum() < untagged.sum():
        lines.append(metric_row("Logistic regression, untagged TODOs only",
                                y[untagged], scores[untagged], k)[0])
    return "\n".join(lines), model_metrics


def top_weights(model, builder, n=15):
    names = builder.names()
    order = np.argsort(model.w)
    fmt = lambda i: f"| {names[i]} | {model.w[i]:+.3f} |"
    toward_resolved = "\n".join(fmt(i) for i in order[::-1][:n])
    toward_rotting = "\n".join(fmt(i) for i in order[:n])
    header = "| Feature | Weight |\n|---|---|\n"
    return header + toward_resolved, header + toward_rotting


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="dataset.csv")
    ap.add_argument("--out", default="results_day3.md")
    ap.add_argument("--val-year", type=int, default=2022)
    ap.add_argument("--lr", type=float, default=0.5)
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--lam", type=float, default=1e-3)
    ap.add_argument("--min-df", type=int, default=5)
    ap.add_argument("--max-features", type=int, default=2000)
    ap.add_argument("--k", type=int, default=50)
    args = ap.parse_args()

    rows = load(args.data)
    train = [r for r in rows if r["year"] < args.val_year]
    val = [r for r in rows if r["year"] == args.val_year]
    test = [r for r in rows if r["year"] > args.val_year]
    print(cohort_table(rows))
    print(f"\ntrain {len(train)}   validation {len(val)}   test {len(test)}")

    print("\nPhase 1: fit on train, score validation")
    _, _, val_scores = fit_and_score(train, val, args, verbose=True)
    val_table, _ = results_table(val, val_scores, args.k)
    print(val_table)

    print("\nPhase 2: fit on train + validation, score test")
    model, builder, test_scores = fit_and_score(train + val, test, args, verbose=True)
    test_table, _ = results_table(test, test_scores, args.k)
    print(test_table)
    resolved_w, rotting_w = top_weights(model, builder)

    curve = "\n".join(f"| {it} | {loss:.5f} |" for it, loss in model.loss_history)
    report = f"""# Day 3 results ({date.today()})

Data: `{args.data}`, {len(rows)} TODOs.
Settings: learning rate {args.lr}, {args.iters} iterations, L2 lambda {args.lam},
TF-IDF min_df {args.min_df}, max {args.max_features} words ({len(builder.tfidf.vocab)} kept),
class-weighted log-loss, decision threshold 0.5.

## Cohorts

{cohort_table(rows)}

Split: train = cohorts before {args.val_year} ({len(train)}), validation = {args.val_year} ({len(val)}),
test = after {args.val_year} ({len(test)}).

## Test results (model fit on train + validation)

{test_table}

Rot precision@k: of the k TODOs the model rates least likely to be resolved,
the share that really were still there a year later.

## Validation results (model fit on train only)

{val_table}

## Largest weights toward "resolved"

{resolved_w}

## Largest weights toward "rotting"

{rotting_w}

Weights of correlated features (e.g. deadline-tagged and asks-removal) share
credit, so read them as directions, not exact importances.

## Training loss (final model)

| Iteration | Loss |
|---|---|
{curve}
"""
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
