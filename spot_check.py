"""Step 3: print a random sample of labeled TODOs so you can verify them by hand.

Usage:
    python spot_check.py test.csv            # 30 random TODOs
    python spot_check.py test.csv -n 50

For each TODO you get a GitHub link to the line as it was at T1. For the
ones labeled resolved, it also finds the commit that removed the text
(git's "pickaxe" search, -S), so you can open that commit and judge whether
the TODO was really fixed or just deleted / reworded.
"""

import argparse
import csv
import random

import config
from check_repos import commit_at, git


def removing_commit(repo_dir, c1, c2, text):
    """Commits between T1 and T2 that changed how often `text` appears."""
    out = git(repo_dir, "log", "--first-parent", "--format=%h %cs %s", f"-S{text}",
              f"{c1}..{c2}", "--", "*.py")
    return out.strip().splitlines()[:2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_file")
    ap.add_argument("-n", type=int, default=30)
    args = ap.parse_args()

    with open(args.csv_file, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    sample = random.Random(config.RANDOM_SEED).sample(rows, min(args.n, len(rows)))

    for i, r in enumerate(sample, 1):
        label = "RESOLVED" if r["label"] == "1" else "rotting"
        url = f"https://github.com/{r['repo']}/blob/{r['commit_t1']}/{r['path']}#L{r['line']}"
        print(f"[{i:2}] {label:8} ({r['snapshot'][:4]}) {r['marker']}: {r['text'][:90]}")
        print(f"     {url}")
        if r["label"] == "1":
            repo_dir = f"{config.REPOS_DIR}/{r['repo'].replace('/', '__')}"
            year = int(r["snapshot"][:4])
            c2 = commit_at(repo_dir, config.snapshot_dates(year)[2])
            for c in removing_commit(repo_dir, r["commit_t1"], c2, r["text"]) or ["(no commit found)"]:
                print(f"     removed by: {c}")
        print()


if __name__ == "__main__":
    main()
