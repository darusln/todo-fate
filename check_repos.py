"""Step 1: clone candidate repos and keep only the ones fit for the study.

Usage:
    python check_repos.py candidates.txt

candidates.txt holds one GitHub "owner/name" per line (# starts a comment).
Writes repos_ok.txt with the repos that pass every check, and prints a
table explaining why each rejected repo failed.
"""

import os
import subprocess
import sys

import config


def git(repo_dir, *args):
    """Run a git command inside repo_dir and return its stdout as text."""
    result = subprocess.run(
        ["git", "-C", repo_dir, *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode not in (0, 1):  # grep returns 1 for "no matches"
        raise RuntimeError(f"git {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout


def clone(slug):
    """Clone owner/name into repos/owner__name unless it is already there.

    --no-checkout: we never need a working copy. Every later step reads
    files straight out of git's history (git grep <commit>, git ls-tree),
    which is faster and avoids switching branches back and forth.
    """
    target = os.path.join(config.REPOS_DIR, slug.replace("/", "__"))
    if not os.path.isdir(target):
        print(f"  cloning {slug} ...", flush=True)
        subprocess.run(
            ["git", "clone", "--quiet", "--no-checkout",
             f"https://github.com/{slug}.git", target],
            check=True,
        )
    return target


def commit_at(repo_dir, date):
    """Last commit on the main line made before `date` ('' if none).

    --first-parent follows the default branch's own history and ignores
    commits that only lived on merged feature branches, so the snapshot is
    what the main branch actually looked like on that date.
    """
    return git(repo_dir, "rev-list", "-1", "--first-parent",
               f"--before={date}", "HEAD").strip()


def count_todos(repo_dir, commit):
    out = git(repo_dir, "grep", "-I", "-E", "-c", config.GREP_PATTERN,
              commit, "--", config.FILE_GLOB)
    # -c prints "<commit>:<path>:<count>" per file
    return sum(int(line.rsplit(":", 1)[1]) for line in out.splitlines() if line)


def check(slug):
    repo_dir = clone(slug)
    first = git(repo_dir, "log", "--reverse", "--format=%cs", "HEAD").split("\n", 1)[0]
    last = git(repo_dir, "log", "-1", "--format=%cs", "HEAD").strip()
    authors = len(set(git(repo_dir, "log", "--format=%ae", "HEAD").split()))
    c1 = commit_at(repo_dir, config.T1)
    todos = count_todos(repo_dir, c1) if c1 else 0

    problems = []
    # ISO dates (YYYY-MM-DD) compare correctly as plain strings.
    if first > config.MAX_FIRST_COMMIT:
        problems.append(f"history starts {first}")
    if last < config.MIN_LAST_COMMIT:
        problems.append(f"inactive since {last}")
    if authors < config.MIN_CONTRIBUTORS:
        problems.append(f"only {authors} authors")
    if todos < config.MIN_TODOS_AT_T1:
        problems.append(f"only {todos} TODOs at T1")
    return first, last, authors, todos, problems


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python check_repos.py candidates.txt")
    with open(sys.argv[1], encoding="utf-8") as f:
        slugs = [l.split("#")[0].strip() for l in f]
    slugs = [s for s in slugs if s]

    os.makedirs(config.REPOS_DIR, exist_ok=True)
    passed = []
    print(f"{'repo':35} {'first':10} {'last':10} {'authors':>7} {'TODOs@T1':>8}  verdict")
    for slug in slugs:
        try:
            first, last, authors, todos, problems = check(slug)
        except Exception as e:  # a bad slug shouldn't kill the whole run
            print(f"{slug:35} ERROR: {e}")
            continue
        verdict = "OK" if not problems else "REJECT: " + "; ".join(problems)
        print(f"{slug:35} {first:10} {last:10} {authors:7} {todos:8}  {verdict}")
        if not problems:
            passed.append(slug)

    with open("repos_ok.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(passed) + "\n")
    print(f"\n{len(passed)}/{len(slugs)} repos passed -> repos_ok.txt")


if __name__ == "__main__":
    main()
