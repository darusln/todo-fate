"""Step 2: extract every TODO at T1 and label it by whether it survives to T2.

Usage:
    python mine_todos.py repos_ok.txt              # all repos -> todos.csv
    python mine_todos.py repos_ok.txt --only psf/requests --out test.csv

For every snapshot year (see config.py) only TODOs added in the year
before T1 are kept. Label rule (per such TODO):
    resolved (1)  its text appears nowhere in the repo at T2, and its file still exists
    rotting  (0)  its text still appears at T2 (possibly in another file)
    excluded      its file was deleted, or duplicates make the outcome unclear
"""

import argparse
import csv
import random
import re
from collections import Counter

import config
from check_repos import commit_at, git

MARKER_RE = re.compile(r"\b(" + "|".join(config.MARKERS) + r")\b")
# "TODO(alice): fix this"  ->  marker=TODO, owner=alice, body="fix this"
HEAD_RE = re.compile(
    r"^(?P<marker>" + "|".join(config.MARKERS) + r")"
    r"(?:\((?P<owner>[^)]*)\))?[\s:\-]*(?P<body>.*)$"
)


def pathspecs():
    """Limit git to Python files outside vendored / generated folders."""
    specs = [config.FILE_GLOB]
    for d in config.EXCLUDED_DIRS:
        specs.append(f":(exclude,glob)**/{d}/**")
    return specs


def parse_comment(content):
    """Turn a source line into (key, marker, owner, body, is_inline) or None.

    key is the TODO's identity across snapshots: the comment text from the
    marker onward, lowercased, whitespace collapsed. Indentation and code
    around the comment are deliberately ignored, so re-indenting or running
    a formatter does not make a TODO look "resolved".
    """
    m = MARKER_RE.search(content)
    if not m:
        return None
    hash_pos = content.rfind("#", 0, m.start())
    if hash_pos == -1:  # marker is not inside a comment
        return None
    comment = content[hash_pos:].lstrip("#").strip()
    head = HEAD_RE.match(comment[comment.find(m.group(1)):])
    if not head:
        return None
    body = head.group("body").strip()
    if len(body.split()) < config.MIN_BODY_WORDS:
        return None
    key = " ".join(comment[comment.find(m.group(1)):].lower().split())
    is_inline = content[:hash_pos].strip() != ""
    return key, head.group("marker"), (head.group("owner") or "").strip(), body, is_inline


def grep_todos(repo_dir, commit):
    """All TODO comments at a commit, read straight from git history."""
    out = git(repo_dir, "grep", "-n", "-I", "-E", config.GREP_PATTERN,
              commit, "--", *pathspecs())
    todos = []
    for line in out.splitlines():
        # format: <commit>:<path>:<line number>:<source line>
        _, path, lineno, content = line.split(":", 3)
        parsed = parse_comment(content)
        if parsed:
            todos.append((path, int(lineno), *parsed))
    return todos


def file_sizes(repo_dir, commit):
    """{path: size in bytes} for every file at a commit, in one git call."""
    sizes = {}
    for line in git(repo_dir, "ls-tree", "-r", "-l", commit).splitlines():
        meta, path = line.split("\t", 1)
        size = meta.split()[3]
        sizes[path] = int(size) if size.isdigit() else 0
    return sizes


def churn(repo_dir, commit, since, until):
    """{path: commits touching it between since and until}, in one git call."""
    out = git(repo_dir, "log", "--format=", "--name-only",
              f"--since={since}", f"--until={until}", commit)
    return Counter(p for p in out.splitlines() if p)


def is_test_path(path):
    """True for test code: a tests/ or testing/ folder, or test_*.py / *_test.py.

    A plain substring check ("test" in path) is wrong: it flags
    src/_pytest/... and src/pytest_plugin.py as tests.
    """
    parts = path.lower().split("/")
    name, folders = parts[-1], parts[:-1]
    return (any(f in ("test", "tests", "testing") for f in folders)
            or name.startswith("test_") or name.endswith("_test.py")
            or name == "conftest.py")


def mine_snapshot(slug, repo_dir, year, cache, stats):
    """Label the TODOs that were added in the year before T1."""
    t0, t1, t2 = config.snapshot_dates(year)
    c0, c1, c2 = (commit_at(repo_dir, d) for d in (t0, t1, t2))
    if not (c0 and c1 and c2):
        stats[f"skipped_year_{year}"] += 1  # repo too young for this year
        return []

    def todos_at(c):  # each snapshot is reused by the neighbouring year
        if c not in cache:
            cache[c] = grep_todos(repo_dir, c)
        return cache[c]

    at_t1 = todos_at(c1)
    count0 = Counter(t[2] for t in todos_at(c0))
    count1 = Counter(t[2] for t in at_t1)
    count2 = Counter(t[2] for t in todos_at(c2))
    per_file = Counter(t[0] for t in at_t1)
    sizes1 = file_sizes(repo_dir, c1)
    files2 = set(file_sizes(repo_dir, c2))
    commits_prev_year = churn(repo_dir, c1, t0, t1)

    rows = []
    for path, lineno, key, marker, owner, body, is_inline in at_t1:
        if count0[key] > 0:
            stats["skipped_older_than_a_year"] += 1  # already existed at T0
            continue
        if count2[key] == 0:
            if path not in files2:
                stats["excluded_file_deleted"] += 1
                continue
            label = 1
        elif count2[key] >= count1[key]:
            label = 0
        else:  # e.g. 3 copies at T1, 1 at T2: can't tell which one was fixed
            stats["excluded_ambiguous_duplicate"] += 1
            continue
        stats["resolved" if label else "rotting"] += 1
        rows.append({
            "repo": slug,
            "snapshot": t1,
            "commit_t1": c1,
            "path": path,
            "line": lineno,
            "marker": marker,
            "owner": owner,
            "text": body,
            "body_words": len(body.split()),
            "is_inline": int(is_inline),
            "is_test": int(is_test_path(path)),
            "file_size_bytes": sizes1.get(path, 0),
            "todos_in_file": per_file[path],
            "file_commits_prev_year": commits_prev_year[path],
            "label": label,
        })
    return rows


def mine_repo(slug):
    repo_dir = f"{config.REPOS_DIR}/{slug.replace('/', '__')}"
    rows, stats, cache = [], Counter(), {}
    for year in config.SNAPSHOT_YEARS:
        rows.extend(mine_snapshot(slug, repo_dir, year, cache, stats))

    if len(rows) > config.MAX_TODOS_PER_REPO:
        stats["dropped_by_cap"] = len(rows) - config.MAX_TODOS_PER_REPO
        rows = random.Random(config.RANDOM_SEED).sample(rows, config.MAX_TODOS_PER_REPO)
    return rows, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_list")
    ap.add_argument("--only", help="mine a single owner/name from the list")
    ap.add_argument("--out", default="todos.csv")
    args = ap.parse_args()

    with open(args.repo_list, encoding="utf-8") as f:
        slugs = [l.strip() for l in f if l.strip()]
    if args.only:
        slugs = [s for s in slugs if s == args.only]

    all_rows, log_lines = [], []
    for slug in slugs:
        rows, stats = mine_repo(slug)
        all_rows.extend(rows)
        line = f"{slug:35} kept={len(rows):5}  " + "  ".join(f"{k}={v}" for k, v in sorted(stats.items()))
        print(line, flush=True)
        log_lines.append(line)

    if not all_rows:
        raise SystemExit("No TODOs mined - check the repo list and dates.")
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)

    resolved = sum(r["label"] for r in all_rows)
    summary = (f"\n{len(all_rows)} TODOs -> {args.out}  "
               f"(resolved {resolved}, {resolved / len(all_rows):.1%}; rotting {len(all_rows) - resolved})")
    print(summary)
    with open("mining_log.txt", "w", encoding="utf-8") as f:
        f.write(f"snapshot years={config.SNAPSHOT_YEARS}\n" + "\n".join(log_lines) + summary + "\n")


if __name__ == "__main__":
    main()
