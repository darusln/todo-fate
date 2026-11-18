import re

VERSION = r"v?\d+\.\d+(\.\d+)?"
DEADLINE_RE = re.compile(
    rf"\b(remove|removed|deprecat\w*|revert|drop|delete|clean ?up|enforce)\b.*\b{VERSION}\b"
    rf"|\b(in|after|before|until|once|since|by)\s+(version\s+|v)?{VERSION}\b"
    rf"|\bpython\s*[<>=]*\s*[23]\.\d+",
    re.IGNORECASE,
)

def is_deadline_tagged(owner, text):
    return int(bool(re.fullmatch(VERSION, owner or "") or DEADLINE_RE.search(text)))