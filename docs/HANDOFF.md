# HANDOFF: TODO-fate prediction ("Project 2")

This file is the full context for continuing the project in Claude Code. Read it
completely before doing anything. Last updated: 2026-11-23 (after the
reorganisation and the 2025 replay).

---

## 1. The assignment

University course assignment, "Project 2: Apply a machine learning technique to a
software engineering related problem". Required parts:

1. **Problem**: pick a real software engineering activity that ML can support.
2. **Data collection**: collect data *specifically for this project*, with a
   strategy that suits the activity; data must be representative and sufficient.
3. **ML approach**: choose a technique that fits the data and problem.
4. **Implementation**: preprocessing, training, evaluation, with the process and
   the rationale for each choice documented.
5. **Validation**: validate with real-world examples (live environment or real users).

### Hard constraints set by the student (Darius)

- **The model must be implemented by him, from scratch.** NumPy is allowed; no
  scikit-learn, LightGBM, PyTorch etc. for the model. scikit-learn may be used
  only to cross-check results (it is optional and not installed by default).
- **One model only.** He explicitly does not want to compare several models.
  Reference rows (an "always predict rotting" baseline and a two-feature rule)
  are fine because they are not trained models.
- **Solo work.** No survey, no other raters, no user study. Validation must be
  done without other people.
- **No data or code from his employer.** Public open-source data only.
- **Tight time budget**: about 3 focused hours per day; originally planned as 5 days.
- He wants step-by-step instructions with the reasoning behind each step, and
  tested scripts rather than untested code.

---

## 2. The project in one paragraph

Developers leave TODO/FIXME/XXX/HACK comments as cheap deferred work, but these
have no owner, deadline or visibility, and many are never addressed
("self-admitted technical debt", SATD, an established research area). This
project predicts, **at the moment a TODO is observed (within a year of being
written), whether it will be removed within the following year** ("resolved")
or still be there ("rotting"). The intended use is a triage tool that ranks a
repo's TODOs by risk of rotting, so a team can spot the ones likely to be
forgotten, and a write-time nudge (e.g. "link an issue / set a deadline").

**Main research question:** Can we predict, when a TODO comment is young,
whether it will be resolved within a year, and can that prediction help
developers prioritise technical debt?

| RQ | Question | How it is answered |
|---|---|---|
| RQ1 | How accurately can TODO fate be predicted? | Time split (train on older cohorts, test on newer) vs baselines |
| RQ2 | Does it generalise to unseen projects? | Leave-one-repo-out |
| RQ3 | What determines whether a TODO is resolved? | Feature report (lift table) + model weights. **No ablation study** (dropped to keep one model) |
| RQ4 | Does the ranking help prioritisation? | Rot precision@k + "replayed deployment" on a new 2025 cohort (replaces the dropped survey) |

**Known limitation to state:** the model predicts *neglect*, not *importance*.
A TODO likely to rot may be harmless. "Resolved" means the comment was removed,
not that the work was verified.

---

## 3. Environment and repository

- **Machine:** Darius's work MacBook (macOS, zsh, user `ituser`). Python 3, NumPy.
- **Project folder:** `~/personal/todo-fate/`
- **Git identity:** personal, separated from work via a conditional include:
  - `~/.gitconfig` ends with `[includeIf "gitdir:~/personal/"] path = ~/.gitconfig-personal`
  - `~/.gitconfig-personal` sets his personal name/email and
    `core.sshCommand = ssh -i ~/.ssh/id_ed25519_personal -o IdentitiesOnly=yes`
  - Remote: `git@github.com:darusln/todo-fate.git` (SSH, personal account `darusln`).
    **Never switch to HTTPS**: the credential manager holds the work account.
- **`.gitignore`:** `data/repos/`, `*.csv`, `data/mining_log.txt`, `__pycache__/`, `.DS_Store`.
  So data CSVs are not committed; code, repo lists and results markdown are.
- **Clones:** `data/repos/<owner>__<name>/`, made with `git clone --no-checkout`.
  All scripts read history straight from git objects (`git grep <commit>`,
  `git ls-tree <commit>`), never a working copy.
- **macOS gotcha:** macOS git's regex engine does not support `\b` (a pattern
  with it silently matches nothing). `config.GREP_PATTERN` is therefore
  `r"#.*(TODO|FIXME|XXX|HACK)"`; exact whole-word matching happens afterwards
  in Python (`mine_todos.parse_comment`). The `\b` version had crept back into
  the committed `config.py` (it caused the "no young TODOs" replay failure);
  fixed again on 2026-11-23. Do not reintroduce `\b` into anything passed to `git grep`.
- **Running scripts:** all code is in the `todofate` package. Run every script
  from the project folder as a module, e.g. `python3 -m todofate.experiments.train`.
  All file paths come from `todofate/config.py`, so defaults need no arguments.
- A companion tutorial for Day 1 exists as a Claude Doc ("Day 1 Tutorial: Mining
  TODOs") on claude.ai; it is not needed to continue.

### File map

```
todo-fate/
├── README.md               layout and how to run each step
├── docs/HANDOFF.md         this file
├── todofate/               all code (one Python package)
│   ├── config.py           every date, threshold and file path
│   ├── mining/             Day 1: check_repos, mine_todos, spot_check
│   ├── features/           Day 2: deadline, build_features
│   ├── model/              from-scratch tfidf, logreg, metrics
│   ├── experiments/        Days 3-4: train, cross_project, replay
│   └── rank_todos.py       the tool demo
├── tests/test_model.py     correctness checks for the model code
├── data/                   repo lists (tracked), CSVs + clones (git-ignored)
└── results/                everything the report quotes (tracked)
```

| File | Purpose |
|---|---|
| `todofate/config.py` | All dates, thresholds and paths: snapshot years, eligibility rules, grep pattern, excluded dirs, per-repo cap, seed, `repo_dir(slug)` |
| `data/candidates.txt` | 22 candidate GitHub repos |
| `todofate/mining/check_repos.py` | Clones candidates, applies eligibility checks, writes `data/repos_ok.txt`. Also provides `git()`, `clone()`, `commit_at()` used everywhere |
| `data/repos_ok.txt` | The 18 repos actually used (see §5) |
| `todofate/mining/mine_todos.py` | Mines and labels TODOs per yearly cohort → `data/todos.csv`, `data/mining_log.txt` (log only on full runs, not `--only`). Provides `grep_todos`, `file_sizes`, `churn`, `is_test_path`, `mine_snapshot` |
| `todofate/mining/spot_check.py` | Prints random labelled TODOs with GitHub links and the removing commit, for manual label checking |
| `data/spotcheck_sqlalchemy.csv` | Single-repo mining output (sqlalchemy, 224 rows) used for the Day 1 spot check; was `test.csv` |
| `todofate/features/deadline.py` | `is_deadline_tagged(owner, text)` and `is_version_tag(owner)`: detects TODOs tied to a release or Python version |
| `todofate/features/build_features.py` | `data/todos.csv` → `data/dataset.csv` (22 features) + `results/feature_report.txt` (lift table). Exposes `build_row`, `BINARY_FEATURES`, `NUMERIC_FEATURES`, `report`. Was `features.py` |
| `todofate/model/tfidf.py` | From-scratch TF-IDF (`tokenize`, `TfidfVectorizer`) |
| `todofate/model/logreg.py` | From-scratch logistic regression (stable sigmoid, class weights, L2, batch gradient descent) |
| `todofate/model/metrics.py` | From-scratch confusion matrix, precision/recall/F1, ROC-AUC (rank formula), average precision, precision@k, `evaluate()` |
| `tests/test_model.py` | 16 correctness checks (hand calculations, gradient check, metric edge cases, optional sklearn cross-check) |
| `todofate/experiments/train.py` | Day 3: time split, two-phase training → `results/day3_time_split.md`. Exposes `load`, `FeatureBuilder`, `fit_and_score`, `display_path` |
| `todofate/experiments/cross_project.py` | Day 4 RQ2: leave-one-repo-out → `results/day4_cross_project.md` |
| `todofate/experiments/replay.py` | Day 4 validation: "replayed deployment" at past dates → `results/day4_replay.md` (or `--out`) |
| `todofate/rank_todos.py` | The tool demo: ranks a live repo's young TODOs by risk → `results/rankings/<owner>__<name>.csv` |

---

## 4. Method (what is implemented)

### 4.1 Labelling: rolling yearly snapshots

For each cohort year Y in 2019–2024 (`config.SNAPSHOT_YEARS`), three snapshots of
the main branch (last first-parent commit before the date):

- **T0 = Y-1-11-01**: only used to decide which TODOs are new.
- **T1 = Y-11-01**: observation point. Keep TODOs present at T1 but absent at T0
  ("young": written in the past year). Features are computed at T1.
- **T2 = Y+1-11-01**: label. TODO text gone → resolved (1); still present → rotting (0).

TODO identity = comment text from the marker onward, lowercased, whitespace
collapsed; searched **repo-wide**, so moved/renamed files don't count as fixes.

| Situation at T2 | Outcome |
|---|---|
| Text still present at least as often as at T1 | rotting (0) |
| Text gone, file still exists | resolved (1) |
| Text gone, file deleted | excluded |
| Fewer copies than at T1 but not zero | excluded (ambiguous duplicate) |
| Body shorter than 2 words | excluded |
| Path in a vendored/generated dir (`vendor`, `_vendor`, `third_party`, `build`, `dist`, …) | excluded |

Each TODO appears in exactly one cohort. Per-repo cap 1,500 rows (seed 42).

**Why young TODOs only:** a single-snapshot design (all TODOs on 2024-11-01,
checked 2025-11-01) gave only **2% resolved** (26 of 1,282 in sympy, celery,
sqlalchemy): most TODOs present at any moment are years old. Restricting to
young TODOs gives a learnable signal. This is itself a finding.

### 4.2 Repo selection (`check_repos.py`)

Eligibility: first commit before 2021-11-01; last commit after 2026-02-01 (dead
projects would make every TODO look rotting); ≥10 distinct author emails; ≥30
TODOs at the latest T1. Candidates came from well-known large Python projects;
SEART GitHub Search was suggested as the citable sampling source.

### 4.3 Features (`build_features.py`, all measured at T1, no leakage)

- **Text:** `is_deadline_tagged`, `has_issue_ref`, `has_url`, `has_owner_tag`
  (a `TODO(name)` tag that is not a version), `is_vague` (maybe/perhaps/someday/
  investigate…), `mentions_defect` (bug/broken/crash/hack…, or FIXME/HACK marker),
  `asks_removal`, `starts_with_verb`, `is_question`
- **Location:** `is_inline`, `is_test` (path rule: tests/testing dir, test_*.py,
  *_test.py, conftest.py), `is_docs_or_example`
- **Marker one-hot:** `marker_TODO`, `marker_FIXME`, `marker_XXX`, `marker_HACK`
- **Numeric:** `body_words`, `body_chars`, `path_depth`, `log_file_size`,
  `log_todos_in_file`, `log_file_commits_prev_year` (log1p transforms)
- Plus the raw `text`, used for TF-IDF.

`deadline.py` matches: a removal word followed by a version ("remove in 0.23");
"in/after/before/until/once" + version; Python support conditions ("python < 3.10",
"drop support for Python 3.8"); owner tags like `TODO(1.6)` / `TODO(py38)`.
It deliberately does **not** match "multiply by 1.5" or "segfault in Python 3.9".
12/12 hand-written test cases pass.

### 4.4 Model (`model/`, `train.py`)

- **TF-IDF:** tokens lowercased; versions → `<ver>`, other numbers → `<num>`;
  vocabulary fit on training rows only; min_df 5, max 2,000 words;
  idf = log((1+N)/(1+df)) + 1; rows L2-normalised.
- **Feature matrix:** TF-IDF ‖ 16 binary features ‖ 6 numeric features
  standardised with training mean/std.
- **Logistic regression:** class-weighted log-loss (w = N / (2·N_class)),
  L2 λ = 0.001 (bias not regularised), batch gradient descent, lr 0.5,
  1,000 iterations, threshold 0.5.
- **Split:** train = cohorts 2019–2021, validation = 2022, test = 2023–2024.
  Phase 1 fits on train and scores validation (sanity check). Phase 2 fits on
  train+validation and scores test (reported numbers). The test set is used once.
- **Metrics:** ROC-AUC, PR-AUC, precision, recall, F1 for the "resolved" class,
  and **rot precision@k** (of the k TODOs rated least likely to be resolved,
  the share that really rotted). Ties are broken randomly with a fixed seed.

---

## 5. Data (final)

- 22 candidates → 20 passed eligibility (aiohttp 23 and poetry 14 TODOs rejected).
- tornado (4 rows) and twisted (12 rows) dropped after mining (too few rows).
- **18 repos, 4,523 labelled TODOs, 32.5% resolved overall.**

Repos: pytest, sympy, celery, sqlalchemy, django, pip, setuptools, ipython,
pandas, numpy, scipy, scikit-learn, networkx, astropy, dask, airflow, ansible, salt.

| Cohort | TODOs | Resolved | Rate |
|---|---|---|---|
| 2019 | 694 | 220 | 31.7% |
| 2020 | 808 | 241 | 29.8% |
| 2021 | 961 | 398 | 41.4% |
| 2022 | 826 | 258 | 31.2% |
| 2023 | 727 | 196 | 27.0% |
| 2024 | 507 | 158 | 31.2% |

Per repo (kept / resolved): scikit-learn 958 / 657 (69%), pandas 1,335 / 488
(37%), sympy 412 / 27, astropy 238 / 15, ansible 327 / 31, airflow 233 / 52,
sqlalchemy 224 / 43, salt 151 / 14, scipy 130 / 22, dask 91 / 20,
setuptools 89 / 14, numpy 89 / 13, pip 62 / 20, networkx 51 / 18,
pytest 50 / 7, celery 39 / 16, ipython 24 / 5, django 20 / 9.
Excluding scikit-learn and pandas, the resolved rate is about 15%.

**Label quality:** Darius spot-checked labels with `spot_check.py` and reported
all checked labels correct. **Record the exact sample size and repos** for the
report; with 0 errors in n labels, the 95% upper bound on the error rate is
about 3/n (rule of three).

---

## 6. Results and findings so far

### 6.1 Feature report (whole dataset, 4,523 TODOs, base rate 32.5%)

| Feature | Has it | Resolved if 1 | if 0 | Lift |
|---|---|---|---|---|
| is_deadline_tagged | 826 | 83.1% | 21.2% | 3.9 |
| asks_removal | 1,020 | 68.0% | 22.2% | 3.1 |
| starts_with_verb | 1,431 | 51.9% | 23.6% | 2.2 |
| has_owner_tag | 312 | 48.7% | 31.3% | 1.6 |
| is_test | 1,705 | 40.3% | 27.8% | 1.4 |
| marker_TODO | 3,574 | 34.5% | 25.0% | 1.4 |
| mentions_defect | 694 | 36.6% | 31.8% | 1.2 |
| has_url | 35 | 34.3% | 32.5% | 1.1 |
| has_issue_ref | 129 | 32.6% | 32.5% | 1.0 |
| is_inline | 223 | 28.3% | 32.7% | 0.9 |
| marker_HACK | 32 | 25.0% | 32.6% | 0.8 |
| is_question | 598 | 20.1% | 34.4% | 0.6 |
| is_vague | 319 | 16.0% | 33.8% | 0.5 |
| is_docs_or_example | 25 | 12.0% | 32.6% | 0.4 |
| marker_XXX | 442 | 11.1% | 34.8% | 0.3 |

Numeric (mean resolved vs rotting): body_words 13.1 vs 9.9; body_chars 112 vs 71;
file size, TODOs in file and file churn are almost identical between classes.

### 6.2 Day 3: time split (test = cohorts 2023–2024, 1,234 TODOs)

| | ROC-AUC | PR-AUC | Precision | Recall | F1 | Rot precision@50 |
|---|---|---|---|---|---|---|
| Always predict rotting | 0.500 | 0.298 | 0.000 | 0.000 | 0.000 | 0.680 |
| Rule: deadline OR removal | 0.732 | 0.554 | 0.645 | 0.596 | 0.620 | 0.840 |
| **Logistic regression** | **0.832** | 0.646 | 0.671 | 0.658 | 0.665 | **1.000** |
| LR, untagged TODOs only | 0.740 | 0.362 | 0.463 | 0.348 | 0.397 | 1.000 |

Validation (2022, model fit on 2019–2021): LR AUC 0.775, rule 0.695.
Test > validation is explained by the extra training year; the test set was used once.
732 vocabulary words kept. Loss 0.693 → 0.498 at 1,000 iterations, still falling
very slowly (≈0.001 per 100 iterations).

Top weights toward resolved: is_deadline_tagged (+1.67), word:<ver> (+1.48),
word:in (+1.01), has_owner_tag (+0.98), word:removed, asks_removal,
mentions_defect, word:deprecation, word:filterwarnings.
Toward rotting: **word:airflow (−0.71, a project name: the model partly learned
project identity)**, marker_XXX (−0.62), word:test, word:check, word:one,
is_docs_or_example, word:<num>, word:needs, word:assert, word:day.
("one" and "day" might be the phrase "one day"; unverified.)

### 6.3 Day 4: cross-project (leave-one-repo-out, 18 repos)

| | ROC-AUC | PR-AUC | Precision | Recall | F1 |
|---|---|---|---|---|---|
| Rule: deadline OR removal | 0.718 | 0.565 | 0.689 | 0.557 | 0.616 |
| **LR, unseen repos (pooled)** | 0.754 | 0.632 | 0.694 | 0.527 | 0.599 |
| LR, unseen repos, untagged only | 0.590 | 0.272 | 0.323 | 0.122 | 0.177 |

**Mean per-repo ROC-AUC: 0.646** (18 of 18 repos). Use this as the headline.
Per repo: scikit-learn 0.853, celery 0.802, networkx 0.778, django 0.768 (n=20),
ipython 0.758 (n=24), sympy 0.727, astropy 0.670, pandas 0.652, numpy 0.630,
salt 0.628, airflow 0.619, scipy 0.581, ansible 0.564, sqlalchemy 0.562,
pip 0.557, pytest 0.551, dask 0.523, **setuptools 0.398 (below chance)**.

Interpretation: deadline/removal signals generalise; finer lexical patterns are
largely project-specific (untagged AUC 0.74 → 0.59). The 0.5 threshold does not
transfer (F1 = 0 for ansible and ipython despite AUC > 0.5), so the tool should
be presented as a **ranking**, not a yes/no classifier.

### 6.4 Consolidated findings list (for the report)

1. Most TODOs present at any moment are long-lived: single-snapshot labelling
   gave 2% resolved. Motivates the young-TODO design.
2. Young TODOs: 32.5% resolved within a year overall, ≈15% excluding
   scikit-learn and pandas; per repo from ≈6% (astropy) to 69% (scikit-learn).
3. Small clean projects barely use TODOs (flask 2, httpx 1, requests 7 at the
   2024 snapshot); TODO-heavy repos are large mature projects (generalisability limit).
4. Deadline-tagged TODOs: 83% resolved vs 21% (3.9×). The effect holds without
   scikit-learn (≈63% vs ≈21%, approximate, computed with the first regex version).
5. scikit-learn's 69% is explained by its deprecation policy ("remove in 0.24");
   its untagged TODOs are resolved at ≈26%, close to other repos.
6. Concrete, action-shaped TODOs get done: removal 3.1×, action verb 2.2×, owner tag 1.6×.
7. Open-ended TODOs rot: XXX 0.3×, vague 0.5×, question 0.6×.
8. **Issue links make no difference (1.0×, n=129)**, contrary to common advice.
9. File activity (size, churn, TODO count) carries no signal: what the TODO
   says matters, not where it lives.
10. Label spot check found no errors (record n).
11. Project restructuring shows up as "file deleted" exclusions: airflow 157,
    ansible 60 (both split code into separate packages).
12. is_test (1.4×) and longer text may be scikit-learn artefacts. **Unverified**:
    run the feature report without scikit-learn (command in §8).
13. Deadline and removal overlap heavily; read their weights as directions.
14. Model beats the rule on the time split (AUC 0.83 vs 0.73) and stays useful on
    untagged TODOs (0.74). All 50 most at-risk test TODOs really rotted (vs 68% base).
15. Cross-project: mean per-repo AUC 0.65; advantage over the rule mostly
    disappears; untagged 0.59. The model leans partly on project identity.

Pipeline validation worth a paragraph: the `"test" in path` bug (flagged all of
`src/_pytest/`), the macOS `\b` bug (0 TODOs found everywhere), the deadline regex
false matches ("by 1.5", "Python 3.9"), all found and fixed; plus `test_model.py`
(gradient check agrees to ~1e-10).

---

### 6.5 Day 4: 2025 replayed deployment (`results/day4_replay_2025.md`)

The 2025 cohort (TODOs added Nov 2024–Nov 2025, outcome date 2026-11-01) is not
in the dataset and was written after everything the model trained on. Model
trained on cohorts 2019–2024, scored the 2025 cohort: **794 young TODOs, 26% resolved.**

| | ROC-AUC | PR-AUC | F1 | Rot precision@20 |
|---|---|---|---|---|
| Always predict rotting | 0.500 | 0.275 | 0.000 | 80% |
| Rule: deadline OR removal | 0.597 | 0.366 | 0.400 | 90% |
| **Logistic regression** | 0.597 | 0.438 | 0.329 | 70% |

- Mean per-repo AUC (7 repos with ≥5 of each class): **0.621**, close to the
  cross-project 0.646. Per repo: scikit-learn 0.814, setuptools 0.778, salt 0.733,
  pandas 0.549, ansible 0.536, scipy 0.499, airflow 0.439.
- The time-split 0.83 does not hold on the future cohort; honest headline is
  ≈0.60 pooled / ≈0.62 per repo, no better than the rule on AUC.
- **airflow** (235 of 794 rows) resolved 39% vs 22% in earlier cohorts (Airflow 3
  work). The model had learned `word:airflow` → rotting, so it ranked airflow's
  TODOs as risky just as they were being fixed. Labels checked: only 1 of 91
  resolved airflow TODOs survives anywhere at T2 even as its first 6 words, so
  they are real removals, not rewording. Diagnostic only (do not report as the
  main result): without airflow, LR AUC 0.710 vs rule 0.638, rot precision@20
  80% vs base 85%. Evidence for the project-identity limitation.
- celery: 0 young TODOs in 2025 (all 62 TODOs at T1 already existed at T0). Correct.
- sqlalchemy, django, ipython, dask, networkx: no resolved TODOs; pip, numpy,
  astropy: one each. Their per-repo AUC is n/a or meaningless.
- Data-quality threats seen in the rankings: `sklearn/externals/array_api_compat/`
  (vendored, `externals` not in EXCLUDED_DIRS) and setuptools' generated
  `fastjsonschema_validations.py` (TODOs inside embedded JSON-schema strings).
  Report as limitations; do not re-mine.

---

## 7. Current status: where we are right now

**Done:** Day 1 (selection, mining, spot check), Day 2 (features, feature report),
Day 3 (model, results), Day 4 cross-project results and the 2025 replay (§6.5).
Project reorganised into `todofate/`, `data/`, `results/`, `docs/`, `tests/`
(2026-11-23); every script was re-run afterwards and reproduced its earlier
output exactly (dataset.csv byte-identical; Day 3, cross-project and replay
numbers identical).

**Open checks (small), run from the project folder:**
- setuptools AUC 0.398: check whether its rows come from the vendored
  `setuptools/_distutils` copy (not in the exclusion list):
  ```bash
  python3 -c "import csv; r=[x for x in csv.DictReader(open('data/dataset.csv')) if x['repo']=='pypa/setuptools']; print(sum('_distutils' in x['path'] for x in r), 'of', len(r))"
  ```
  If large: report as a limitation (do not re-mine this late).
- Convergence: `python3 -m todofate.experiments.train --iters 3000 --out results/day3_time_split_3000.md`;
  if test AUC changes by < 0.005, keep the 1,000-iteration results and state convergence.
- Confirm `python3 -m tests.test_model` prints "All checks passed." (screenshot for report).
- Feature report without scikit-learn (finding 12):
  ```bash
  python3 -c "
  import csv
  from todofate.features.build_features import report, BINARY_FEATURES, NUMERIC_FEATURES
  rows = []
  for r in csv.DictReader(open('data/dataset.csv')):
      if r['repo'] == 'scikit-learn/scikit-learn': continue
      for k in BINARY_FEATURES + ['label']: r[k] = int(r[k])
      for k in NUMERIC_FEATURES: r[k] = float(r[k])
      rows.append(r)
  print(report(rows))
  " | tee results/feature_report_no_sklearn.txt
  ```

---

## 8. What comes next

### Finish Day 4
1. **Qualitative review by Darius himself** of the "most at risk" / "least at risk"
   lists in `results/day4_replay_2025.md`: patterns, 2–3 clear hits and misses.
   Label it in the report as the author's qualitative analysis, not a user study.
2. Optional tool demo: `python3 -m todofate.rank_todos python/mypy` (mypy is not
   in the dataset; clones it on first run). Screenshot the output.
3. Optional extra: `python3 -m todofate.experiments.replay` with no options
   replays 2022–2024 on unseen repos (mypy, matplotlib, aiohttp, poetry).
4. Commit (the reorganisation, the grep fix and the Day 4 work):
   ```bash
   git add -A
   git status          # check: no CSVs, no data/repos
   git commit -m "Reorganise into package; fix grep pattern; Day 4 results"
   ```

### Day 5: the report
Suggested structure, mapped to the assignment and RQs:

1. **Introduction and motivation**: why TODOs rot (no owner, deadline,
   visibility; context decays), SATD background, why existing approaches
   (linters, bans, cleanup sprints) don't prioritise. Research question + RQ1–RQ4.
2. **Related work**: 3–4 SATD papers (search Google Scholar for
   "self-admitted technical debt removal"). Contribution: predicting at
   introduction time, practical ranking, validation on a future cohort.
3. **Data collection**: repo selection criteria and the check_repos table
   (accepted/rejected with reasons), snapshot labelling with T0/T1/T2, label
   rules, exclusions with counts, the 2% finding, spot-check accuracy, the
   cohort table, threats (reworded TODOs count as resolved; removal ≠ verified
   fix; Python only; large projects only; vendored code such as `_distutils`).
4. **Features and exploratory analysis**: feature list, lift table, the
   deadline finding with and without scikit-learn, issue-link non-effect.
5. **ML approach and implementation**: why supervised binary classification
   (labels exist; unsupervised/RL don't fit), why logistic regression
   (interpretable, suits sparse text + tabular), TF-IDF details, class weights,
   L2, gradient descent, leakage prevention (fit on train only, time split),
   correctness checks (test_model.py, gradient check).
6. **Evaluation**: RQ1 time split table; RQ2 cross-project table; RQ3 weights +
   lift table; RQ4 rot precision@k and the 2025 replay.
7. **Validation with real-world examples**: the 2025 replayed deployment and
   the qualitative review; tool demo on mypy.
8. **Limitations and threats to validity**; neglect ≠ importance; threshold
   doesn't transfer across projects; project-identity leakage (word:airflow).
9. **Future work**: score the 2026 cohort in Nov 2027; gradient-boosted trees
   from scratch; survival analysis (Cox model) instead of a fixed 12-month
   cutoff; per-project calibration; a real user study; combining rot risk
   with a severity signal.

Numbers in the report should come straight from the files in `results/`.

---

## 9. Rules for whoever continues this

- Keep **one model** (the from-scratch logistic regression). Don't add models.
- Keep the implementation from scratch; NumPy only.
- Never tune on the test set; fit TF-IDF and standardisation on training rows only.
- Don't involve other people (no surveys) and don't use employer data.
- Don't put `\b` in patterns passed to `git grep` (macOS).
- Test scripts before handing them over; explain changes and their reasoning.
- Darius works ~3 hours per day: prefer small, concrete steps with commands
  he can copy, and say what output to expect.
- Commit with his personal identity (already automatic under `~/personal/`);
  push over SSH.
