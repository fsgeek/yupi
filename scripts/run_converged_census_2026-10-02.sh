#!/bin/bash
# Censuses + evaluations owed to docs/converged-ladder-prereg-v0.1.md (C1-C4, actor A4) and
# docs/relay-intervention-prereg-v0.1.md + addendum v0.1.1 (R1-R4). Frozen scripts, CPU (as the
# 2026-09-29 held-out censuses), 4 threads each, P at once. Resumable: skips raws that exist.
# Launched 2026-10-02 by the instance that scores (it did not write the predictions).
cd /home/tony/projects/yupi
D=2026-10-02; LOG=~/.cache/yupi-scratch/census
census() {  # run-dir raw-name
  out=docs/learner-window-census-$2-$D.json
  [ -f $out ] && { echo "skip $out"; return; }
  OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 uv run --extra learner python scripts/learner_window_census.py --run $1 --k 7 \
    --device cpu --raw $out > $LOG/$(basename $1)-census-$D.log 2>&1 && echo "done $out $(date)" || echo "FAILED census $1 $(date)"
}
evaluate() {  # run-dir raw-name
  out=docs/learner-eval-$2-$D.json
  [ -f $out ] && { echo "skip $out"; return; }
  OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 uv run --extra learner python scripts/learner_evaluate.py --run $1 --device cpu \
    --k 1,2,3,4,5,6,7 --raw $out > $LOG/$(basename $1)-eval-$D.log 2>&1 && echo "done $out $(date)" || echo "FAILED eval $1 $(date)"
}
one() { $1 $2 $3; }
export -f census evaluate one; export D LOG
echo "=== start $(date)"
LAD=~/.cache/yupi-scratch/runs/ladder15; GPU=~/.cache/yupi-scratch/runs/gpu; REL=~/.cache/yupi-scratch/runs/relay
{
# censuses first (scoring needs them): 27 ladder, 3 r1 eps=1 e15, 6 r1R
for c in r0-eps1 r2-eps1 r3-eps1 r4-eps1 r0-eps1_2 r1-eps1_2 r2-eps1_2 r3-eps1_2 r4-eps1_2; do for s in 1 2 3; do
  echo "census $LAD/c1prime-loop-40-8-2-$c-2M-d128-e15-s$s $c-2M-e15-seed$s"; done; done
for s in 1 2 3; do echo "census $GPU/c1prime-loop-40-8-2-r1-eps1-2M-d128-lr1e-3-e15-s$s r1-eps1-2M-e15-seed$s"; done
for e in 5 15; do for s in 1 2 3; do
  echo "census $REL/c1prime-loop-40-8-2-r1R-eps1-2M-d128-e$e-s$s r1R-eps1-2M-e$e-seed$s"; done; done
# then the k=1..7 evaluations of the 27 new ladder runs (r1 eps=1 e15 has its raws of 2026-09-24/28)
for c in r0-eps1 r2-eps1 r3-eps1 r4-eps1 r0-eps1_2 r1-eps1_2 r2-eps1_2 r3-eps1_2 r4-eps1_2; do for s in 1 2 3; do
  echo "evaluate $LAD/c1prime-loop-40-8-2-$c-2M-d128-e15-s$s $c-2M-d128-e15-seed$s"; done; done
} | xargs -P ${P:-16} -L 1 bash -c 'one "$@"' _
echo "=== ALL DONE $(date)"
