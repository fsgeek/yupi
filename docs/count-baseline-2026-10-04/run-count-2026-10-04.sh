#!/bin/bash
cd /home/tony/projects/yupi
one() { c=$(basename $(dirname $1)); out=docs/count-baseline-${c#c1prime-loop-40-8-2-}-2026-10-04.json
  [ -f $out ] && { echo "skip $out"; return; }
  OMP_NUM_THREADS=2 uv run --extra learner python scripts/count_baseline.py --corpus $1 --raw $out \
    > ~/.cache/yupi-scratch/census/count-$c-2026-10-04.log 2>&1 && echo "done $out $(date)" || echo "FAILED $c $(date)"; }
export -f one
cat ~/.cache/yupi-scratch/census/count-corpora-2026-10-04.txt | xargs -P 5 -I{} bash -c 'one {}'
echo "=== ALL DONE $(date)"
