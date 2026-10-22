"""Build the anonymised TMLR supplementary ZIP for the methods paper (owner, 2026-10-22).

Contents: the yupi package (src/), its tests, the analysis scripts, pyproject/uv.lock, the result files and the
declaration/verdict notes the paper cites, and a README. Identifying strings are replaced; the build fails if any
remain.  python scripts/build_supplement.py   -> docs/tmlr/paper1m-supplement-anon.zip
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "tmlr"
STAGE = OUT / "build-supplement" / "supplement"
RESULT_PREFIXES = ("kind-uncertainty-split-", "one-step-identifiability-", "identifiability-tolerance-",
                   "learner-precision-monitor-", "support-audit-table-", "state-vs-predictive-", "implicit-info-lag-kind-",
                   "converged-ladder-", "b1-", "count-baseline-", "gru-baseline-", "relay-2x2-", "relay-lossmask-",
                   "relay-v-diagnosis-", "relay-free-difficulty-", "pattern-ceilings-40-8-2-", "split-v2-rows-sha256-",
                   "three-arm-exact-side-", "reset-injectivity-")
NOTES = ("learner-precision-monitor-check-2026-10-15.md", "identifiability-tolerance-check-2026-10-15.md",
         "one-step-identifiability-check-2026-10-15.md", "relay-2x2-verdict-v0.1.md", "relay-lossmask-verdict-v0.1.md",
         "gru-baseline-verdict-v0.1.md", "relay-free-difficulty-results-v0.1.md", "paper1m-supplement-provenance-v1.md")
SUBS = [(r"/home/tony", "$HOME"), (r"tony@wamason\.com", "[email]"), (r"fsgeek@cs\.ubc\.ca", "[email]"),
        (r"wamason(\.com)?", "[site]"), (r"\bW\. Anthony Mason\b", "[author]"), (r"\bTony Mason\b", "[author]"),
        (r"\bMason\b(?! & Anand| and Anand)", "[author]"), (r"\bTony\b", "the author"), (r"\btony\b", "user"),
        (r"\bayllu\b", "collaboration"), (r"\bfsgeek\b", "user"), (r"\bUBC\b", "[institution]"),
        (r"\bVaastav\b", "[coauthor]")]
CHECK = re.compile(r"tony|wamason|fsgeek|ayllu|vaastav|\bubc\b|W\. Anthony", re.I)
TEXT = {".py", ".md", ".json", ".jsonl", ".txt", ".toml", ".sh", ".cfg", ".ini", ".lock", ".log"}


def sanitise(p: Path):
    if p.suffix not in TEXT:
        return
    t = p.read_text(errors="ignore")
    for a, b in SUBS:
        t = re.sub(a, b, t)
    p.write_text(t)


if STAGE.exists():
    shutil.rmtree(STAGE)
STAGE.mkdir(parents=True)
for d in ("src", "tests", "scripts"):
    shutil.copytree(ROOT / d, STAGE / d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.sh", "build_supplement.py", "build_tmlr.py"))
for f in ("pyproject.toml", "uv.lock"):
    shutil.copy(ROOT / f, STAGE / f)
(STAGE / "results").mkdir()
n = 0
for p in sorted((ROOT / "docs").iterdir()):
    if p.is_file() and (p.name.startswith(RESULT_PREFIXES) and p.suffix in {".json", ".jsonl", ".txt", ".log"} or p.name in NOTES):
        shutil.copy(p, STAGE / "results" / p.name)
        n += 1
(STAGE / "docs").mkdir()
for p in sorted((ROOT / "docs").iterdir()):
    if p.is_file() and p.suffix in {".json", ".jsonl", ".log", ".txt"}:
        shutil.copy(p, STAGE / "docs" / p.name)
if (ROOT / "docs" / "corpus-manifests").is_dir():
    shutil.copytree(ROOT / "docs" / "corpus-manifests", STAGE / "docs" / "corpus-manifests")
(STAGE / "README.md").write_text("""# Supplementary material (anonymised)

`src/` is the instrument: the kernel (`yupi/kernel.py`), interfaces, exact filters and ceilings, and the learner code.
`docs/` holds every committed result file the test suite checks against; `tests/` holds the test suite (`uv run --extra learner pytest -q`). `scripts/` holds the analyses; `results/` holds the summary
result files every number in the paper is computed from, and the notes recording what was declared before each check
ran. `results/paper1m-supplement-provenance-v1.md` maps each section of the paper to its result files.

Exact tables are regenerated, not shipped (they are large): for example
`uv run python scripts/kind_uncertainty_split.py --eps 1 --rows-dir <dir>` rebuilds the per-class rows behind §3.1
and §4 (minutes on a workstation CPU), whose hashes are listed in `results/split-v2-rows-sha256-2026-10-15.txt`;
`scripts/support_audit_table.py` then reproduces the §4.2 table and the §4.3 exact sweep. Trained checkpoints are
not included (about 3 MB each); `scripts/learner_train.py` retrains them.

**Expected test results.** In this anonymised copy, 1,044 tests pass and 5 fail, all in
`tests/test_relay_replication_score.py`: four check the byte-for-byte hash of a frozen result file whose contents
anonymisation necessarily altered (a local path was replaced), and one reads a design note that is not included. In
the original repository all five pass.
""")
for p in STAGE.rglob("*"):
    if p.is_file():
        sanitise(p)
left = [(str(p.relative_to(STAGE)), m.group(0)) for p in STAGE.rglob("*") if p.is_file() and p.suffix in TEXT
        for m in [CHECK.search(p.read_text(errors="ignore"))] if m]
if left:
    print("IDENTIFYING STRINGS REMAIN:", left[:20])
    sys.exit(1)
zpath = OUT / "paper1m-supplement-anon.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(STAGE.rglob("*")):
        if p.is_file():
            z.write(p, Path("supplement") / p.relative_to(STAGE))
print(f"results files: {n}; zip: {zpath.stat().st_size / 1e6:.1f} MB; identifying strings: none")
