"""Day 4, RQ4: rank a live repository's current TODOs by their risk of rotting.

Usage (from the project folder):
    python3 -m todofate.rank_todos python/mypy
    python3 -m todofate.rank_todos python/mypy --all --show 15

This is the tool a team would actually use. It:
    1. clones the repo if needed (into data/repos/, like the other scripts);
    2. takes the TODOs on the main branch today that were added in the last
       year, the same "young TODO" population the model was trained on
       (--all ranks every TODO instead);
    3. computes the same features as Day 2, at today's commit;
    4. trains the Day 3 model on ALL of data/dataset.csv (every cohort; the
       evaluation is done, so the final tool uses all the data it has);
    5. writes results/rankings/<owner>__<name>.csv: every TODO, most at risk first, with a
       GitHub link, and prints the top and bottom of the list.

This is the demo of the tool. Its accuracy is measured by replay.py, which
runs the same procedure at past dates where the outcome is already known.
Pick a repo that is NOT in data/dataset.csv, e.g. python/mypy.
"""

import argparse
import csv
from collections import Counter
from datetime import date

import numpy as np

from todofate import config
from todofate.experiments.train import FeatureBuilder, display_path, load
from todofate.features.build_features import build_row
from todofate.mining.check_repos import clone, commit_at, git
from todofate.mining.mine_todos import churn, file_sizes, grep_todos, is_test_path
from todofate.model.logreg import LogisticRegression


def one_year_ago(today):
    try:
        return today.replace(year=today.year - 1)
    except ValueError:                     # 29 February
        return today.replace(year=today.year - 1, day=28)


def current_todos(slug, repo_dir, young_only):
    today = date.today()
    start = one_year_ago(today)
    c_now = git(repo_dir, "rev-parse", "HEAD").strip()
    c_start = commit_at(repo_dir, start.isoformat())

    now = grep_todos(repo_dir, c_now)
    older = Counter(t[2] for t in grep_todos(repo_dir, c_start)) if c_start else Counter()
    per_file = Counter(t[0] for t in now)
    sizes = file_sizes(repo_dir, c_now)
    commits_last_year = churn(repo_dir, c_now, start.isoformat(), today.isoformat())

    rows = []
    for path, lineno, key, marker, owner, body, is_inline in now:
        if young_only and older[key] > 0:
            continue
        rows.append({
            "repo": slug, "snapshot": today.isoformat(), "commit_t1": c_now,
            "path": path, "line": lineno, "marker": marker, "owner": owner, "text": body,
            "body_words": len(body.split()), "is_inline": int(is_inline),
            "is_test": int(is_test_path(path)), "file_size_bytes": sizes.get(path, 0),
            "todos_in_file": per_file[path],
            "file_commits_prev_year": commits_last_year[path],
            "label": 0,                    # unknown; build_row needs the field
        })
    return rows, len(now)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="owner/name on GitHub, e.g. aio-libs/aiohttp")
    ap.add_argument("--data", default=config.DATASET_CSV)
    ap.add_argument("--all", action="store_true", help="rank every TODO, not only last year's")
    ap.add_argument("--show", type=int, default=10, help="TODOs printed at each end of the ranking")
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--lr", type=float, default=0.5)
    ap.add_argument("--lam", type=float, default=1e-3)
    args = ap.parse_args()

    training = load(args.data)
    if any(r["repo"] == args.slug for r in training):
        print(f"WARNING: {args.slug} is in {display_path(args.data)}; the model has seen this project.")

    repo_dir = clone(args.slug)
    raw, total = current_todos(args.slug, repo_dir, young_only=not args.all)
    print(f"{args.slug}: {total} TODOs on main today, {len(raw)} ranked"
          + ("" if args.all else " (added in the last year)"))
    if not raw:
        print("  Nothing to rank. Try --all or another repo.")
        return
    rows = [build_row(r) for r in raw]

    builder = FeatureBuilder(min_df=5, max_features=2000).fit(training)
    y = np.array([r["label"] for r in training])
    model = LogisticRegression(lr=args.lr, n_iter=args.iters, lam=args.lam, verbose=False)
    model.fit(builder.transform(training), y)
    risk = 1 - model.predict_proba(builder.transform(rows))

    order = np.argsort(-risk, kind="mergesort")
    out = config.RANKINGS_DIR / f"{args.slug.replace('/', '__')}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    link = lambda r: f"https://github.com/{args.slug}/blob/{r['commit_t1']}/{r['path']}#L{r['line']}"

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "risk_of_rotting", "marker", "text", "path", "line", "link"])
        for rank, i in enumerate(order, 1):
            r = rows[i]
            w.writerow([rank, f"{risk[i]:.3f}", r["marker"], r["text"], r["path"], r["line"], link(r)])

    n = min(args.show, len(rows))
    print(f"\nMost at risk of rotting:")
    for i in order[:n]:
        print(f"  {risk[i]:.2f}  {rows[i]['marker']}: {rows[i]['text'][:80]}")
    print(f"\nLeast at risk:")
    for i in order[::-1][:n]:
        print(f"  {risk[i]:.2f}  {rows[i]['marker']}: {rows[i]['text'][:80]}")
    print(f"\nWrote {display_path(out)} ({len(rows)} TODOs)")


if __name__ == "__main__":
    main()
