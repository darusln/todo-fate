"""Day 4, real-world validation without other people: replay a past deployment.

Usage (from the project folder):
    python3 -m todofate.experiments.replay             # unseen repos, 2022-2024
    python3 -m todofate.experiments.replay --repo-list data/repos_ok.txt --include-seen \
        --years 2025 --out results/day4_replay_2025.md # the dataset's repos, new 2025 cohort
    python3 -m todofate.experiments.replay python/mypy matplotlib/matplotlib --years 2023 2024

The question: if the tool had been run on these projects on 1 November of a
given year, would its warnings have been right a year later?

Two ways to use it:
    - repos NOT in dataset.csv, any years up to 2025 (a new project);
    - the dataset's own repos with --include-seen, only for years after the
      dataset's newest cohort (2025): a cohort of TODOs the model has never
      seen, written after everything it was trained on.

For each repo:
    1. clone it if needed;
    2. at each replay date, take the TODOs on main that were added in the year
       before (exactly the population the tool targets), with features as of
       that day;
    3. score them with a model trained only on cohorts BEFORE that year, i.e.
       only labels already known on that date, so no future information is used;
    4. look up what really happened a year later, using the same labelling rule
       as the dataset.

This is a live-style test on real projects the model never saw, with known
outcomes. It writes results/day4_replay.md (or --out) with per-repo and pooled scores,
and the ten most and least at-risk TODOs per repo for your own qualitative
review in the report.
"""

import argparse
from collections import Counter

import numpy as np

from todofate import config
from todofate.experiments.train import FeatureBuilder, display_path, load
from todofate.features.build_features import build_row
from todofate.mining.check_repos import clone
from todofate.mining.mine_todos import mine_snapshot
from todofate.model.logreg import LogisticRegression
from todofate.model.metrics import evaluate

# Unseen by the model: aiohttp and poetry were rejected only for having under
# 30 TODOs; mypy and matplotlib were never candidates.
DEFAULT_REPOS = ["python/mypy", "matplotlib/matplotlib", "aio-libs/aiohttp", "python-poetry/poetry"]


def fmt(x):
    return "n/a" if x != x else f"{x:.3f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repos", nargs="*", default=None)
    ap.add_argument("--repo-list", help="read repos from a file instead, e.g. data/repos_ok.txt")
    ap.add_argument("--include-seen", action="store_true",
                    help="allow repos that are in the dataset (for a new, later cohort)")
    ap.add_argument("--years", type=int, nargs="+", default=[2022, 2023, 2024],
                    help="replay dates = 1 November of each of these years")
    ap.add_argument("--data", default=config.DATASET_CSV)
    ap.add_argument("--out", default=config.RESULTS_REPLAY)
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--lr", type=float, default=0.5)
    ap.add_argument("--lam", type=float, default=1e-3)
    ap.add_argument("--k", type=int, default=20)
    ap.add_argument("--show", type=int, default=10, help="TODOs listed per end of each ranking")
    args = ap.parse_args()

    data = load(args.data)
    seen = {r["repo"] for r in data}
    if args.repo_list:
        with open(args.repo_list, encoding="utf-8") as f:
            args.repos = [l.strip() for l in f if l.strip()]
    args.repos = args.repos or DEFAULT_REPOS
    newest_cohort = max(r["year"] for r in data)
    if args.include_seen and min(args.years) <= newest_cohort:
        raise SystemExit(f"--include-seen needs replay years after {newest_cohort}: earlier cohorts "
                         f"of these repos are already in {display_path(args.data)}, so they'd be scored twice.")
    slugs = []
    for slug in args.repos:
        if slug in seen and not args.include_seen:
            print(f"  skipping {slug}: it is in {display_path(args.data)}, so it isn't unseen")
        else:
            slugs.append(slug)

    # One model per replay date, trained only on labels known on that date.
    models = {}
    for year in args.years:
        training = [r for r in data if r["year"] < year]
        builder = FeatureBuilder(min_df=5, max_features=2000).fit(training)
        model = LogisticRegression(lr=args.lr, n_iter=args.iters, lam=args.lam, verbose=False)
        model.fit(builder.transform(training), np.array([r["label"] for r in training]))
        models[year] = (builder, model, len(training))
        print(f"Replay {config.snapshot_dates(year)[1]}: model trained on cohorts before {year} "
              f"({len(training)} TODOs)")

    pooled_y, pooled_scores, pooled_rule = [], [], []
    repo_lines = ["| Repo | Young TODOs | Resolved within a year | ROC-AUC | PR-AUC | F1 | Rot precision@k |",
                  "|---|---|---|---|---|---|---|"]
    review = []
    for slug in slugs:
        repo_dir = clone(slug)
        rows, scores, cache = [], [], {}
        stats = Counter()
        for year in args.years:
            raw = mine_snapshot(slug, repo_dir, year, cache, stats)
            if not raw:
                continue
            year_rows = [build_row({k: str(v) for k, v in r.items()}) for r in raw]
            builder, model, _ = models[year]
            rows += year_rows
            scores.append(model.predict_proba(builder.transform(year_rows)))
        if not rows:
            print(f"  {slug}: no young TODOs at any replay date {dict(stats)}")
            continue
        scores = np.concatenate(scores)
        y = np.array([r["label"] for r in rows])
        rule = np.array([float(r["is_deadline_tagged"] or r["asks_removal"]) for r in rows])
        pooled_y.append(y); pooled_scores.append(scores); pooled_rule.append(rule)

        k = min(args.k, len(y))
        m = evaluate(y, scores, k=k)
        repo_lines.append(f"| {slug} | {len(y)} | {int(y.sum())} ({y.mean():.0%}) | {fmt(m['roc_auc'])} | "
                          f"{fmt(m['pr_auc'])} | {fmt(m['f1'])} | {m[f'rot_precision@{k}']:.0%} (k={k}) |")
        print(f"  {slug:28} {len(y):4} young TODOs, {y.mean():5.1%} resolved, AUC {fmt(m['roc_auc'])}")

        order = np.argsort(scores, kind="mergesort")          # lowest P(resolved) first
        outcome = lambda i: "still there" if y[i] == 0 else "**resolved**"
        link = lambda r: f"https://github.com/{slug}/blob/{r['commit_t1']}/{r['path']}#L{r['line']}"
        row_md = lambda i: (f"| {rows[i]['snapshot'][:4]} | {1 - scores[i]:.2f} | "
                            f"[{rows[i]['text'][:90].replace('|', '/')}]({link(rows[i])}) | {outcome(i)} |")
        n = min(args.show, len(rows) // 2)
        head = ["| Replayed in | Risk | TODO | What happened |", "|---|---|---|---|"]
        block = [f"### {slug}", "", "Most at risk of rotting (the model's top warnings):", ""] + head
        block += [row_md(i) for i in order[:n]]
        block += ["", "Least at risk:", ""] + head + [row_md(i) for i in order[::-1][:n]]
        review.append("\n".join(block))

    if not pooled_y:
        raise SystemExit("No repo produced young TODOs to evaluate.")
    y, s, rule = (np.concatenate(x) for x in (pooled_y, pooled_scores, pooled_rule))
    k = min(args.k, len(y))
    lines = [f"| | ROC-AUC | PR-AUC | Precision | Recall | F1 | Rot precision@{k} |",
             "|---|---|---|---|---|---|---|"]
    for name, sc in [("Always predict rotting", np.zeros(len(y))),
                     ("Rule: deadline OR removal", rule),
                     ("**Logistic regression**", s)]:
        m = evaluate(y, sc, k=k)
        lines.append(f"| {name} | " + " | ".join(fmt(m[c]) for c in
                     ["roc_auc", "pr_auc", "precision", "recall", "f1"]) + f" | {m[f'rot_precision@{k}']:.0%} |")
    pooled_table = "\n".join(lines)

    report = f"""# Day 4: replayed deployment

As if the tool had been run on 1 November of {", ".join(map(str, args.years))}. At each
date the model was trained only on cohorts before that year (labels already known on
that date), then ranked the TODOs each project had added in the year before.
Outcomes are what really happened one year later, using the dataset's labelling rule.

## Pooled over all replayed repos ({len(y)} TODOs, {y.mean():.0%} resolved)

{pooled_table}

## Per repo

{chr(10).join(repo_lines)}

Rot precision@k: of the k TODOs the model flagged as most at risk, the share
still there a year later. Compare with each repo's own rotting rate.

## The rankings, for qualitative review

{chr(10).join(review)}
"""
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report)
    print("\n" + pooled_table + f"\n\nWrote {display_path(args.out)}")


if __name__ == "__main__":
    main()