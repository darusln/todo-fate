"""Day 4, RQ2: does the model work on a project it has never seen?

Usage (from the project folder):
    python3 -m todofate.experiments.cross_project
        # data/dataset.csv -> results/day4_cross_project.md

Leave-one-repo-out: for each of the N repos, train the same model on the other
N-1 repos and predict the held-out one. Every TODO is therefore predicted by a
model that never saw its project, its file names or its contributors' habits.

Why it matters: the time-split model's strongest "rotting" word was the project
name "airflow". If the model mostly learned which projects let TODOs rot, it
will score much worse here than on the time split. If the wording patterns
(deadlines, removals, vague phrasing) carry over between projects, the score
should hold up.

Note: this split mixes years (train and test both span 2019-2024), so it
answers a different question from the time split. Report the two side by side.
"""

import argparse
from collections import defaultdict

import numpy as np

from todofate import config
from todofate.experiments.train import display_path, fit_and_score, load
from todofate.model.metrics import evaluate

MIN_PER_CLASS = 5   # per-repo AUC is only meaningful with a few of each class


def fmt(x):
    return "n/a" if x != x else f"{x:.3f}"   # x != x is True only for NaN


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=config.DATASET_CSV)
    ap.add_argument("--out", default=config.RESULTS_CROSS_PROJECT)
    ap.add_argument("--lr", type=float, default=0.5)
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--lam", type=float, default=1e-3)
    ap.add_argument("--min-df", type=int, default=5)
    ap.add_argument("--max-features", type=int, default=2000)
    ap.add_argument("--k", type=int, default=50)
    args = ap.parse_args()

    rows = load(args.data)
    by_repo = defaultdict(list)
    for r in rows:
        by_repo[r["repo"]].append(r)

    all_rows, all_scores, per_repo = [], [], []
    for repo in sorted(by_repo, key=lambda k: -len(by_repo[k])):
        held_out = by_repo[repo]
        others = [r for r in rows if r["repo"] != repo]
        _, _, scores = fit_and_score(others, held_out, args, verbose=False)
        y = np.array([r["label"] for r in held_out])
        m = evaluate(y, scores, k=args.k)
        enough = min(y.sum(), len(y) - y.sum()) >= MIN_PER_CLASS
        per_repo.append((repo, m, enough))
        all_rows += held_out
        all_scores.append(scores)
        print(f"  {repo:30} n={len(y):5}  resolved {y.mean():5.1%}  AUC {fmt(m['roc_auc'])}"
              + ("" if enough else "  (too few of one class)"))

    scores = np.concatenate(all_scores)
    y = np.array([r["label"] for r in all_rows])
    untagged = np.array([r["is_deadline_tagged"] == "0" for r in all_rows])
    rule = np.array([float(r["is_deadline_tagged"] == "1" or r["asks_removal"] == "1") for r in all_rows])

    pooled = evaluate(y, scores, k=args.k)
    pooled_rule = evaluate(y, rule, k=args.k)
    pooled_untagged = evaluate(y[untagged], scores[untagged], k=args.k)
    valid = [m["roc_auc"] for _, m, ok in per_repo if ok]
    mean_auc = float(np.mean(valid))

    lines = ["| | ROC-AUC | PR-AUC | Precision | Recall | F1 |", "|---|---|---|---|---|---|"]
    for name, m in [("Rule: deadline OR removal", pooled_rule),
                    ("**Logistic regression, unseen repos**", pooled),
                    ("Logistic regression, unseen repos, untagged only", pooled_untagged)]:
        lines.append(f"| {name} | " + " | ".join(fmt(m[c]) for c in
                     ["roc_auc", "pr_auc", "precision", "recall", "f1"]) + " |")
    pooled_table = "\n".join(lines)

    repo_lines = ["| Repo (held out) | TODOs | Resolved rate | ROC-AUC | PR-AUC | F1 |",
                  "|---|---|---|---|---|---|"]
    for repo, m, ok in sorted(per_repo, key=lambda t: -t[1]["n"]):
        note = "" if ok else " *"
        repo_lines.append(f"| {repo}{note} | {m['n']} | {m['resolved_rate']:.1%} | "
                          f"{fmt(m['roc_auc'])} | {fmt(m['pr_auc'])} | {fmt(m['f1'])} |")
    repo_table = "\n".join(repo_lines)

    report = f"""# Day 4: cross-project results

Leave-one-repo-out over {len(by_repo)} repos ({len(rows)} TODOs): each repo is
predicted by a model trained only on the other {len(by_repo) - 1}. Same model and
settings as Day 3 (learning rate {args.lr}, {args.iters} iterations, lambda {args.lam}).

## Pooled over all held-out predictions

{pooled_table}

Mean per-repo ROC-AUC (repos with at least {MIN_PER_CLASS} resolved and {MIN_PER_CLASS} rotting
TODOs, {len(valid)} of {len(by_repo)}): **{mean_auc:.3f}**

Pooled scores mix projects with different resolved rates, so the mean per-repo
AUC is the fairer summary of "how well does it rank TODOs inside a new project".

## Per repo

{repo_table}

\\* fewer than {MIN_PER_CLASS} TODOs of one class: AUC is unreliable, left out of the mean.
"""
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report)
    print("\n" + pooled_table + f"\n\nMean per-repo AUC: {mean_auc:.3f}\nWrote {display_path(args.out)}")


if __name__ == "__main__":
    main()
