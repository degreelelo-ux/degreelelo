"""One-time extraction: Master Database xlsx (INSTITUTIONS sheet) -> data/colleges.json.

NOT run automatically. Run manually whenever the source spreadsheet
changes, pointing it at the current export of the Master Database:

    python3 dev/build_colleges_json.py /path/to/Master_Database.xlsx

Writes <repo_root>/data/colleges.json, overwriting the committed export.
Re-run `python3 dev/build.py` afterward so colleges.html's state/category/
course filter options (derived from data/colleges.json at build time)
pick up any new values.

See README.md's "College Directory" section for the exclusion rules and
provenance discipline this script follows: nothing is inferred that
isn't explicitly present in a source field (no fabricated fees,
placement figures, or course lists).
"""
import json
import os
import re
import sys
from collections import Counter

import openpyxl

if len(sys.argv) != 2:
    print("Usage: python3 dev/build_colleges_json.py /path/to/Master_Database.xlsx")
    sys.exit(1)

XLSX = sys.argv[1]
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(REPO_ROOT, "data", "colleges.json")

wb = openpyxl.load_workbook(XLSX, data_only=True)


def rows_as_dicts(sheet_name, header_row=2):
    ws = wb[sheet_name]
    headers = [c.value for c in ws[header_row]]
    out = []
    for row in ws.iter_rows(min_row=header_row + 1, values_only=True):
        d = {}
        for h, v in zip(headers, row):
            if h:
                d[h] = v
        out.append(d)
    return out


def clean(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s or s in ("Unknown", "N/A", "None"):
        return None
    # Some cells are a full sentence starting with "Needs Verification -
    # ..." rather than the bare literal, e.g. "Needs Verification - no
    # reliable figure found" — treat any such cell as unverified too.
    if s.startswith("Needs Verification"):
        return None
    return s


CATEGORY_MAP = {
    "B.Tech": "Engineering",
    "Engineering": "Engineering",
    "MBA": "Management",
    "Management": "Management",
    "MBBS": "Medical",
    "Medical": "Medical",
    "Law": "Law",
    "Design": "Design",
    "Distance/Regular Education": "Distance & Open Education",
    "Other": "Other",
}

NOTES_FEE_RE = re.compile(r"Avg fees/yr\s*(₹.+?)\s*(?:\(partner-quoted|$)")
# Non-greedy up to the literal ". Entrance route:" (not just any period) —
# degree abbreviations like "B.Des" or "B.Arch" contain periods themselves,
# which a bare "stop at first period" pattern would truncate at "B".
NOTES_APPROVALS_RE = re.compile(r"Approvals/programmes:\s*(.+?)(?:\.\s*Entrance route:|$)")
NOTES_ENTRANCE_RE = re.compile(r"Entrance route:\s*(.+?)\.?\s*$")

# Study Abroad institutions' "Important Notes" use a different, non-Indian
# format — no "Avg fees/yr ₹", no "Approvals/programmes:", no "Entrance
# route:" — e.g. "Country: Australia. Entry requirement: 75-85%, IELTS
# 6.5-7. Specialties: Engineering, Business, AI, Architecture. Fees/yr:
# 45k-58k (AUD/yr) (partner-quoted, NOT independently verified). Intake:
# February, September." These two patterns extract the fee and the entry
# requirement from that format. The fee pattern stops after the first
# parenthetical (the currency/unit) and deliberately excludes the second
# "(partner-quoted, NOT independently verified)" parenthetical — that
# caveat stays in the internal data, not on the public card, matching how
# NOTES_FEE_RE already excludes "(partner-quoted" for Indian institutions.
# The entry-requirement pattern anchors on the literal ". Specialties:"
# marker rather than a bare period, for the same reason NOTES_APPROVALS_RE
# does: "IELTS 6.5-7" contains a period that would otherwise truncate it.
# There's no Study Abroad equivalent of "Approvals/programmes" (degree
# tokens), so courses correctly stays empty for these institutions rather
# than guessing from "Specialties" (a list of broad subject areas, not
# degree names).
STUDY_ABROAD_FEE_RE = re.compile(r"Fees/yr:\s*([^(]+\([^)]*\))")
STUDY_ABROAD_ENTRY_RE = re.compile(r"Entry requirement:\s*(.+?)(?:\.\s*Specialties:|$)")

# Degree/programme tokens we recognise in free-text "Approvals/programmes"
# notes, e.g. "MBBS, BDS, MD" or "BA LLB, BBA LLB, LLM" or "B.Des, M.Des".
# Only real degree names are matched — accreditation strings like
# "UGC/AICTE" or "AICTE/VTU/NAAC A+" contain no recognised token and so
# correctly produce no course tag.
KNOWN_COURSE_TOKENS = [
    "BA LLB", "BBA LLB", "B.Com LLB", "LLB", "LLM",
    "B.Arch", "M.Arch", "B.Des", "M.Des",
    "B.Pharm", "M.Pharm", "Pharm.D", "D.Pharm",
    "MBBS", "BDS", "MDS", "BAMS", "MD", "MS",
    "BBA", "MBA", "PGDM",
    "BA", "B.Com", "B.Sc", "BCA", "MCA", "M.Com", "M.Sc", "MA",
]
# Longest-first so e.g. "BA LLB" matches before the bare "BA" token does.
KNOWN_COURSE_TOKENS.sort(key=len, reverse=True)


def extract_courses(approvals_text):
    if not approvals_text:
        return []
    found = []
    # Strip parenthetical asides first — they can contain their own commas
    # (e.g. "B.Des (Fashion, Comm.)"), which would otherwise split a single
    # degree token into unmatched fragments before we ever get to compare it.
    text = re.sub(r"\([^)]*\)", "", approvals_text)
    for segment in re.split(r"[,/]", text):
        segment = segment.strip().strip(".")
        if not segment:
            continue
        for token in KNOWN_COURSE_TOKENS:
            if segment == token:
                if token not in found:
                    found.append(token)
                break
    return found


def parse_notes(notes):
    fee = approvals = entrance = None
    if notes:
        m = NOTES_FEE_RE.search(notes)
        if m:
            fee = m.group(1).strip() + " / year"
        else:
            # Study Abroad format — "Fees/yr: 45k-58k (AUD/yr) (partner-
            # quoted, ...)" — the unit is already embedded in the captured
            # group, so no " / year" suffix is appended here.
            m = STUDY_ABROAD_FEE_RE.search(notes)
            if m:
                fee = m.group(1).strip()
        m = NOTES_APPROVALS_RE.search(notes)
        if m:
            approvals = m.group(1).strip()
        m = NOTES_ENTRANCE_RE.search(notes)
        if m:
            entrance = m.group(1).strip()
        else:
            # Study Abroad format has no "Entrance route:" — use the
            # equivalent "Entry requirement:" (academic % + English test
            # score) instead.
            m = STUDY_ABROAD_ENTRY_RE.search(notes)
            if m:
                entrance = m.group(1).strip()
    return fee, approvals, entrance


institutions = rows_as_dicts("INSTITUTIONS")

colleges = []
for r in institutions:
    if r.get("Active for 2027") != "Yes":
        continue  # not an active vertical yet — see Important Notes

    name = clean(r.get("University/College Name"))
    if not name:
        continue

    status = str(r.get("Verification Status") or "")
    verified = status.startswith("Verified") or status.startswith("Partially verified")

    notes = clean(r.get("Important Notes"))
    fee_from_notes, approvals_from_notes, entrance_from_notes = parse_notes(notes)

    primary_course = r.get("Primary Course")
    category = CATEGORY_MAP.get(primary_course, primary_course or "Other")

    # courses: real, explicit degree/programme names only — never guessed
    # from category. Either the row's own fine-grained "Primary Course"
    # value (only ever B.Tech / MBA / MBBS — genuinely a distinct source
    # field, not an inference), or degree tokens found in the institution's
    # own approvals text. A row with neither gets no course tag at all and
    # only shows up when no course filter is applied.
    courses = extract_courses(approvals_from_notes)
    if primary_course in ("B.Tech", "MBA", "MBBS") and primary_course not in courses:
        courses.append(primary_course)

    entry = {
        "id": r.get("Institution ID"),
        "name": name,
        "type": clean(r.get("Institution Type")),
        "state": clean(r.get("State")),
        "city": clean(r.get("City")),
        "category": category,
        "established": clean(r.get("Established Year")),
        "website": clean(r.get("Official Website")),
        "ranking": clean(r.get("Ranking Information")),
        "avg_placement": clean(r.get("Average Placement")),
        "fee": fee_from_notes,
        "approvals": approvals_from_notes,
        "entrance_exam": entrance_from_notes,
        "courses": courses,
        "verified": verified,
    }
    # drop empty-ish (courses is a list, so also drop when empty)
    entry = {k: v for k, v in entry.items() if v not in (None, "", [])}
    colleges.append(entry)

print("Total public college records:", len(colleges))
print("By category:", Counter(c["category"] for c in colleges))
print("Verified count:", sum(1 for c in colleges if c.get("verified")))

with open(OUT_PATH, "w") as f:
    json.dump(colleges, f, indent=1, ensure_ascii=False)

print(f"\nWrote {OUT_PATH}")
