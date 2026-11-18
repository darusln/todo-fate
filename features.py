"""Day 2: turn todos.csv into the modelling table dataset.csv.

Usage:
    python3 features.py                      # todos.csv -> dataset.csv + feature_report.txt
    python3 features.py --in test.csv --out test_dataset.csv

Every feature is computed from the TODO's own text, its path, or the numbers
mine_todos.py already measured at T1. Nothing looks at T2 or later, so no
feature can leak the label.

The script also prints a feature report: for each yes/no feature, how many
TODOs have it and how often those are resolved compared with the rest. That
report is your first exploratory analysis (Day 2) and a sanity check that
each feature carries some signal.
"""

import argparse
import csv
import math
import re

from deadline import is_deadline_tagged, is_version_tag

# --- Text patterns -----------------------------------------------------------
# A link to a tracked issue: "#1234", "gh-1234", "issue 1234", "bpo-1234",
# a JIRA-style key like "AIRFLOW-1234", or a GitHub issue/PR URL.
ISSUE_RE = re.compile(
    r"(?<![\w&])#\d{2,}\b"
    r"|\b(gh|bpo|pr)-?\s?\d{2,}\b"
    r"|\bissues?\s*#?\d{2,}\b"
    r"|\b[A-Z][A-Z0-9]+-\d{2,}\b"
    r"|github\.com/[^\s]+/(issues|pull)/\d+",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://\S+")

# Hedged, open-ended wording: the writer isn't committing to anything.
VAGUE_RE = re.compile(
    r"\b(maybe|perhaps|possibly|probably|someday|eventually|ideally|"
    r"at some point|in the future|nice to have|would be nice|could|might|"
    r"consider|think about|investigate|figure out|not sure)\b",
    re.IGNORECASE,
)
# Wording that signals something is actually wrong.
DEFECT_RE = re.compile(
    r"\b(bug|broken|breaks?|crash\w*|wrong|incorrect|fails?|failing|"
    r"error|leak\w*|race|hack\w*|workaround|kludge|ugly)\b",
    re.IGNORECASE,
)
# The TODO asks for something to be taken out rather than built.
REMOVAL_RE = re.compile(
    r"\b(remove|delete|drop|revert|deprecat\w*|get rid of|clean ?up)\b",
    re.IGNORECASE,
)
# Starts with an imperative verb: "Add caching", "Fix the edge case".
ACTION_VERBS = {
    "add", "fix", "handle", "implement", "support", "use", "make", "move",
    "replace", "check", "test", "refactor", "rename", "update", "allow",
    "raise", "return", "remove", "delete", "drop", "revert", "document",
    "change", "convert", "simplify", "validate",
}
DOC_DIRS = ("doc", "docs", "examples", "example", "benchmarks", "bench", "tutorials")

BINARY_FEATURES = [
    "is_deadline_tagged", "has_issue_ref", "has_url", "has_owner_tag",
    "is_vague", "mentions_defect", "asks_removal", "starts_with_verb",
    "is_question", "is_inline", "is_test", "is_docs_or_example",
    "marker_TODO", "marker_FIXME", "marker_XXX", "marker_HACK",
]
NUMERIC_FEATURES = [
    "body_words", "body_chars", "path_depth",
    "log_file_size", "log_todos_in_file", "log_file_commits_prev_year",
]
ID_COLUMNS = ["repo", "snapshot", "commit_t1", "path", "line", "marker", "owner", "text"]


def build_row(r):
    text, owner, path = r["text"], r["owner"].strip(), r["path"]
    first_word = re.sub(r"[^a-z]", "", text.split()[0].lower()) if text.split() else ""
    parts = path.lower().split("/")

    f = {c: r[c] for c in ID_COLUMNS}
    f.update({
        # text
        "is_deadline_tagged": is_deadline_tagged(owner, text),
        "has_issue_ref": int(bool(ISSUE_RE.search(text) or ISSUE_RE.search(owner))),
        "has_url": int(bool(URL_RE.search(text))),
        # TODO(alice) / TODO(typing): a tag that isn't a version. Usually a
        # person, sometimes a topic; both mean somebody filed it under a name.
        "has_owner_tag": int(bool(owner) and not is_version_tag(owner)),
        "is_vague": int(bool(VAGUE_RE.search(text))),
        "mentions_defect": int(bool(DEFECT_RE.search(text)) or r["marker"] in ("FIXME", "HACK")),
        "asks_removal": int(bool(REMOVAL_RE.search(text))),
        "starts_with_verb": int(first_word in ACTION_VERBS),
        "is_question": int("?" in text),
        # location
        "is_inline": int(r["is_inline"]),
        "is_test": int(r["is_test"]),
        "is_docs_or_example": int(any(p in DOC_DIRS for p in parts[:-1])),
        # marker, one-hot
        **{f"marker_{m}": int(r["marker"] == m) for m in ("TODO", "FIXME", "XXX", "HACK")},
        # numeric; log1p tames the long tails (a few huge or very busy files)
        "body_words": int(r["body_words"]),
        "body_chars": len(text),
        "path_depth": len(parts) - 1,
        "log_file_size": round(math.log1p(int(r["file_size_bytes"])), 4),
        "log_todos_in_file": round(math.log1p(int(r["todos_in_file"])), 4),
        "log_file_commits_prev_year": round(math.log1p(int(r["file_commits_prev_year"])), 4),
        "label": int(r["label"]),
    })
    return f


def report(rows):
    n = len(rows)
    base = sum(r["label"] for r in rows) / n
    lines = [f"{n} TODOs, base resolved rate {base:.1%}", "",
             f"{'feature':28} {'has it':>7} {'share':>6} {'resolved if 1':>14} {'if 0':>6} {'lift':>5}"]
    for name in BINARY_FEATURES:
        on = [r["label"] for r in rows if r[name]]
        off = [r["label"] for r in rows if not r[name]]
        if not on or not off:
            lines.append(f"{name:28} {len(on):7}   (constant, no information)")
            continue
        p1, p0 = sum(on) / len(on), sum(off) / len(off)
        lines.append(f"{name:28} {len(on):7} {len(on) / n:6.1%} {p1:14.1%} {p0:6.1%} "
                     f"{(p1 / p0 if p0 else float('inf')):5.1f}")
    lines += ["", f"{'numeric feature':28} {'mean if resolved':>17} {'mean if rotting':>16}"]
    for name in NUMERIC_FEATURES:
        res = [r[name] for r in rows if r["label"] == 1]
        rot = [r[name] for r in rows if r["label"] == 0]
        lines.append(f"{name:28} {sum(res) / max(len(res), 1):17.2f} {sum(rot) / max(len(rot), 1):16.2f}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="todos.csv")
    ap.add_argument("--out", default="dataset.csv")
    args = ap.parse_args()

    with open(args.inp, encoding="utf-8") as f:
        rows = [build_row(r) for r in csv.DictReader(f)]

    columns = ID_COLUMNS + BINARY_FEATURES + NUMERIC_FEATURES + ["label"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)

    text = report(rows)
    print(text)
    with open("feature_report.txt", "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"\n{len(rows)} rows, {len(BINARY_FEATURES) + len(NUMERIC_FEATURES)} features -> {args.out}")


if __name__ == "__main__":
    main()