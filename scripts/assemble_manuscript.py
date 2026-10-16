"""Assemble the methods paper from its section drafts (owner, 2026-10-16).

Writes docs/paper1m-manuscript-v1.md (reader-facing: no status blocks, no provenance) and
docs/paper1m-supplement-provenance-v1.md (every section's provenance block, in order).
  python scripts/assemble_manuscript.py
"""
import re
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "docs"
FB = D / "paper1m-draft-front-back-v0.3.md"
SECTIONS = [D / "paper1m-draft-s2-v0.2.md", D / "paper1m-draft-s3-v0.3.md",
            D / "paper1m-draft-s4-v0.3.md", D / "paper1m-draft-s5-v0.2.md"]


def body_and_provenance(path):
    text = path.read_text()
    start = re.search(r"^## \d", text, re.M).start()
    rule = text.index("\n---\n", start)
    return text[start:rule].strip(), text[rule + 5:].strip()


def block(text, heading):
    """The text from '## heading' up to the next '## ' heading or '---' rule."""
    m = re.search(rf"^## {re.escape(heading)}.*$", text, re.M)
    rest = text[m.end():]
    nxt = re.search(r"^(## |---)", rest, re.M)
    return text[m.start():m.end() + (nxt.start() if nxt else len(rest))].strip()


fb = FB.read_text()
title = block(fb, "Title").split("\n", 1)[1].strip()
abstract = block(fb, "Abstract").split("\n", 1)[1].strip()
parts = [title, "## Abstract\n\n" + abstract, block(fb, "1. Introduction")]
prov = ["# Supplement: provenance of every number in the methods paper\n\n"
        "Each section's sources: result files, scripts and review records in the repository, all OpenTimestamps-stamped."]
for p in SECTIONS:
    b, pv = body_and_provenance(p)
    parts.append(b)
    prov.append(f"## From {b.splitlines()[0].lstrip('# ').strip()}\n\n" + pv.replace("## Provenance", "").strip())
for h in ("6. Pitfalls", "7. Related work", "8. Limits", "Contribution statement"):
    parts.append(block(fb, h))
refs = fb[fb.index("## References"):]
parts.append("## References\n\n" + refs.split("\n", 1)[1].strip())
manuscript = "\n\n".join(parts) + "\n"
(D / "paper1m-manuscript-v1.md").write_text(manuscript)
(D / "paper1m-supplement-provenance-v1.md").write_text("\n\n".join(prov) + "\n")
left = sorted(set(re.findall(r"`[^`]*\.(?:md|json|jsonl|py|log)`", manuscript)))
print("words", len(manuscript.split()), "| file names left in body:", left or "none")
