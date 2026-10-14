#!/bin/bash
# GRU baseline census + score (docs/gru-baseline-prereg-v0.1.md). Waits (deadline 5 h) for all 8 runs' final step,
# then the frozen census (CPU, k = 7, full test split, each run's own corpus) and scripts/gru_baseline_score.py.
cd /home/tony/projects/yupi
L=~/.cache/yupi-scratch/runs/gru; LOG=~/.cache/yupi-scratch/census; final=$(( 7813 * 15 )); end=$((SECONDS+18000))
CELLS="r1-eps1 r2-eps1 r3-eps1 r4-eps1 r1-eps1_2 r2-eps1_2 r3-eps1_2 r4-eps1_2"
for c in $CELLS; do
  until grep -q "\"step\": $final" $L/c1prime-loop-40-8-2-$c-2M-gru256x2-e15-s1/log.jsonl 2>/dev/null; do
    [ $SECONDS -ge $end ] && { echo "=== DEADLINE waiting for $c $(date)"; exit 2; }
    grep -q -E "FAILED|exit [1-9]|REFUSED|GATE.*FAIL" $L/wave.log 2>/dev/null && { echo "=== the wave reported a failure $(date)"; exit 3; }
    sleep 60
  done
done
echo "=== all eight trained $(date)"
census() {
  out=docs/learner-window-census-gru-$1-2M-e15-seed1-2026-10-13.json
  [ -f $out ] && { echo "skip $out"; return; }
  OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 uv run --extra learner python scripts/learner_window_census.py \
    --run $L/c1prime-loop-40-8-2-$1-2M-gru256x2-e15-s1 --k 7 --device cpu --raw $out \
    > $LOG/gru-$1-census-2026-10-13.log 2>&1 && echo "done $out $(date)" || { echo "FAILED census $1"; return 1; }
}
export -f census; export L LOG
echo $CELLS | tr ' ' '\n' | xargs -P 8 -L 1 bash -c 'census "$@"' _ || { echo "=== a census FAILED"; exit 4; }
uv run --extra learner python scripts/gru_baseline_score.py --raw docs/gru-baseline-score-2026-10-13.json || { echo "=== SCORE refused"; exit 6; }
echo "=== GRU CENSUS AND SCORE DONE $(date)"
