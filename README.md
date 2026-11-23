# todo-fate

Predicts, when a TODO / FIXME / XXX / HACK comment is less than a year old,
whether it will be removed within the following year ("resolved") or still be
there ("rotting"). Built on the git history of 18 open-source Python projects,
with a logistic regression and TF-IDF implemented from scratch in NumPy.

Full context, method and results so far: [docs/HANDOFF.md](docs/HANDOFF.md).

## Layout

```
todo-fate/
├── todofate/               all code (one Python package)
│   ├── config.py           every date, threshold and file path
│   ├── mining/             1. pick repos, mine and label TODOs
│   │   ├── check_repos.py
│   │   ├── mine_todos.py
│   │   └── spot_check.py
│   ├── features/           2. turn TODOs into features
│   │   ├── deadline.py
│   │   └── build_features.py
│   ├── model/              from-scratch TF-IDF, logistic regression, metrics
│   ├── experiments/        3-4. train and evaluate
│   │   ├── train.py            time split (RQ1)
│   │   ├── cross_project.py    leave-one-repo-out (RQ2)
│   │   └── replay.py           replayed deployment on a future cohort
│   └── rank_todos.py       the tool: rank a repo's TODOs by risk of rotting
├── tests/
│   └── test_model.py       correctness checks for the model code
├── data/                   inputs and intermediate tables
│   ├── candidates.txt      repos considered            (tracked)
│   ├── repos_ok.txt        repos that passed the checks (tracked)
│   ├── todos.csv           mined, labelled TODOs        (git-ignored)
│   ├── dataset.csv         TODOs + features             (git-ignored)
│   └── repos/              local clones, ~4 GB          (git-ignored)
├── results/                everything the report quotes
└── docs/
```

## Running

Python 3 and NumPy. Run everything from this folder, as modules; with no
arguments each step reads and writes the default files in `data/` and `results/`.

```bash
python3 -m todofate.mining.check_repos          # data/candidates.txt -> data/repos_ok.txt
python3 -m todofate.mining.mine_todos           # -> data/todos.csv, data/mining_log.txt
python3 -m todofate.mining.spot_check -n 30     # manual label check
python3 -m todofate.features.build_features     # -> data/dataset.csv, results/feature_report.txt
python3 -m tests.test_model                     # should end with "All checks passed."
python3 -m todofate.experiments.train           # -> results/day3_time_split.md
python3 -m todofate.experiments.cross_project   # -> results/day4_cross_project.md
python3 -m todofate.experiments.replay --repo-list data/repos_ok.txt --include-seen \
    --years 2025 --out results/day4_replay_2025.md
python3 -m todofate.rank_todos python/mypy      # -> results/rankings/python__mypy.csv
```

Each script's docstring explains what it does and why.
