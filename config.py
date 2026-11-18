"""Shared settings for the TODO mining pipeline.

Every date and threshold the study depends on lives here, so the report
can point to one place and the numbers can't drift between scripts.
"""

# --- Rolling yearly snapshots -------------------------------------------------
# For each year Y we take three snapshots of the main branch:
#   T0 = Y-1-11-01   one year before (used to tell which TODOs are new)
#   T1 = Y-11-01     observation point; features are computed here
#   T2 = Y+1-11-01   one year later; the label is whether the TODO survived
# Only TODOs that appeared between T0 and T1 are kept ("young" TODOs), so
# every row is a TODO observed within a year of being written.
SNAPSHOT_YEARS = list(range(2019, 2025))   # T1 = 2019-11-01 ... 2024-11-01
SNAPSHOT_DAY = "11-01"

def snapshot_dates(year):
    return (f"{year - 1}-{SNAPSHOT_DAY}", f"{year}-{SNAPSHOT_DAY}", f"{year + 1}-{SNAPSHOT_DAY}")

# Latest observation point, used by check_repos.py for its TODO count.
T1 = snapshot_dates(SNAPSHOT_YEARS[-1])[1]
CHURN_SINCE = snapshot_dates(SNAPSHOT_YEARS[0])[0]

# --- Repo eligibility (checked by check_repos.py) -----------------------------
# History must cover at least the last three snapshot years. Older years are
# simply skipped for repos that didn't exist yet.
MAX_FIRST_COMMIT = snapshot_dates(SNAPSHOT_YEARS[-3])[0]
# Repo must still be alive well after T2, otherwise "rotting" might just
# mean "project abandoned".
MIN_LAST_COMMIT = "2026-02-01"
MIN_CONTRIBUTORS = 10
MIN_TODOS_AT_T1 = 30

# --- What counts as a TODO ---------------------------------------------------
# A Python comment ('#') containing one of the markers as a whole word.
# Uppercase only: lowercase "todo" is usually prose or a variable name.
GREP_PATTERN = r"#.*(TODO|FIXME|XXX|HACK)"
MARKERS = ("TODO", "FIXME", "XXX", "HACK")
FILE_GLOB = "*.py"

# Paths that hold code copied from other projects or generated code.
# Their TODOs are not the repo's own decisions, so we skip them.
EXCLUDED_DIRS = (
    "vendor", "vendored", "_vendor", "third_party", "thirdparty", "extern",
    "node_modules", "site-packages", ".venv", "venv", "build", "dist",
)

# A TODO body needs at least this many words. Bodies like "TODO" or
# "TODO: fix" appear many times per repo and can't be told apart.
MIN_BODY_WORDS = 2

# --- Dataset shape -----------------------------------------------------------
# Max TODOs kept per repo, so one TODO-heavy project can't dominate.
MAX_TODOS_PER_REPO = 1500
RANDOM_SEED = 42

REPOS_DIR = "repos"
