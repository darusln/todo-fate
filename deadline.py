"""Detect TODOs tied to a deadline: a release version or a supported Python version.

Examples that match:
    "Remove the check in 0.23"
    "REMOVE in v0.23"
    "pass ignore_cleanup_errors=True when we no longer support python < 3.10"
    TODO(1.6): ...  /  TODO(py38): ...   (owner tag holding a version)
Examples that don't:
    "multiply by 1.5 to leave some headroom"
    "The commented lines below lead to a segfault in Python 3.9"
"""

import re

VERSION = r"v?\d+\.\d+(\.\d+)?"
DEADLINE_RE = re.compile(
    rf"\b(remove|removed|deprecat\w*|revert|drop|delete|clean ?up|enforce)\b.*\b{VERSION}\b"
    rf"|\b(in|after|before|until|once)\s+(version\s+|v)?{VERSION}\b"
    # A Python version only counts as a deadline when it is a support condition
    # ("python < 3.10", "drop support for Python 3.8"), not a plain mention
    # ("segfaults in Python 3.9").
    rf"|\bpython\s*(<|<=|>|>=)\s*[23]\.\d+"
    rf"|\b(support\w*|drop\w*|require\w*|minimum|no longer)\b.*\bpython\s*[23]\.\d+",
    re.IGNORECASE,
)


# An owner tag that is a version: TODO(1.6), TODO(v2.0), TODO(py38), TODO(python3.9)
VERSION_TAG_RE = re.compile(rf"{VERSION}|py(thon)?\s?[23]\.?\d+", re.IGNORECASE)


def is_version_tag(owner):
    return bool(VERSION_TAG_RE.fullmatch((owner or "").strip()))


def is_deadline_tagged(owner, text):
    return int(is_version_tag(owner) or bool(DEADLINE_RE.search(text)))