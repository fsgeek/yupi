"""Scorer for docs/relay-2x2-prereg-v0.1.md §3 (written 2026-10-13, after the freeze and before any 2x2 model finished).

Per arm and seed: mean by_field.kind (and .actor) over the k = 7 test windows of each census JSONL, sha256-checked
against its census raw. Contrasts with the pre-registered directions:
  C1 r1Rm vs r1m  (predicted r1Rm > r1m)
  C2 r1Rs vs r1   (predicted r1Rs < r1)
  C3 r1R  vs r1Rs (predicted r1R  < r1Rs)
  C4 r1m  vs r1   (descriptive)
  I  (r1R - r1Rs) - (r1Rm - r1m), per seed, two-sided
Decision rule: complete separation in the predicted direction / against / not resolved (ties = not resolved).
Paired p: exact sign-flip on sum of d_s over 2^3 flips, one-sided in the predicted direction, inclusive tail;
for I, two-sided on |sum|.

  uv run python scripts/relay_2x2_score.py --raw docs/relay-2x2-score-2026-10-13.json
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

RAWS = {
    "r1": "docs/learner-window-census-r1-eps1-2M-e15-seed{s}-2026-10-02.json",
    "r1R": "docs/learner-window-census-r1R-eps1-2M-e15-seed{s}-2026-10-02.json",
    "r1Rm": "docs/learner-window-census-r1Rm-eps1-2M-e15-seed{s}-2026-10-13.json",
    "r1m": "docs/learner-window-census-r1m-eps1-2M-e15-seed{s}-2026-10-13.json",
    "r1Rs": "docs/learner-window-census-r1Rs-eps1-2M-e15-seed{s}-2026-10-13.json",
}
CONTRASTS = [("C1", "r1Rm", "r1m", +1), ("C2", "r1Rs", "r1", -1), ("C3", "r1R", "r1Rs", -1), ("C4", "r1m", "r1", 0)]


def seed_means(arm, s):
    raw = json.load(open(RAWS[arm].format(s=s)))
    pw = raw["per_window_file"]
    if hashlib.sha256(Path(pw).read_bytes()).hexdigest() != raw["per_window_sha256"]:
        raise SystemExit(f"GATE: {pw} does not match its recorded sha256")
    n = k = a = 0.0
    for line in open(pw):
        r = json.loads(line)
        n += 1; k += r["by_field"]["kind"]; a += r["by_field"]["actor"]
    return dict(kind=k / n, actor=a / n, n=int(n))


def signflip_p(d, direction):
    obs = sum(d)
    flips = [sum(x * sg for x, sg in zip(d, signs)) for signs in itertools.product((1, -1), repeat=len(d))]
    if direction == 0:
        return sum(abs(f) >= abs(obs) - 1e-15 for f in flips) / len(flips)
    return sum(direction * f >= direction * obs - 1e-15 for f in flips) / len(flips)


def decide(x, y, direction):
    if direction == 0:
        return "descriptive"
    if direction > 0:
        return ("resolved in the predicted direction" if min(x) > max(y) else
                "resolved against" if max(x) < min(y) else "not resolved with three seeds")
    return ("resolved in the predicted direction" if max(x) < min(y) else
            "resolved against" if min(x) > max(y) else "not resolved with three seeds")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--field", default="kind")
    a = ap.parse_args()
    if Path(a.raw).exists():
        raise SystemExit(f"refusing to overwrite {a.raw}")
    m = {arm: [seed_means(arm, s) for s in (1, 2, 3)] for arm in RAWS}
    v = {arm: [x[a.field] for x in m[arm]] for arm in m}
    out = {"prereg": "docs/relay-2x2-prereg-v0.1.md", "field": a.field, "seed_means": m, "contrasts": {}}
    for name, x, y, direction in CONTRASTS:
        d = [v[x][i] - v[y][i] for i in range(3)]
        out["contrasts"][name] = dict(x=x, y=y, predicted=direction, d_s=d, decision=decide(v[x], v[y], direction),
                                      paired_p=(signflip_p(d, direction) if direction else None))
    I = [(v["r1R"][i] - v["r1Rs"][i]) - (v["r1Rm"][i] - v["r1m"][i]) for i in range(3)]
    out["contrasts"]["I"] = dict(I_s=I, signs=[1 if t > 0 else -1 if t < 0 else 0 for t in I],
                                 paired_p_two_sided=signflip_p(I, 0))
    Path(a.raw).write_text(json.dumps(out, indent=1))
    for k, c in out["contrasts"].items():
        print(k, json.dumps(c))


if __name__ == "__main__":
    main()
