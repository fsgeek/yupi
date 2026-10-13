#!/bin/bash
# Census + lookup check for the relay 2x2 (docs/relay-2x2-prereg-v0.1.md §2, §5). Waits (deadline 4 h) for all six
# runs' final step, then runs the frozen census (CPU, k = 7; each run's own corpus = r1) and relay_object_ce.py.
cd /home/tony/projects/yupi
L=~/.cache/yupi-scratch/runs/relay-2x2; LOG=~/.cache/yupi-scratch/census; D=2026-10-13; final=$(( 7813 * 15 ))
end=$((SECONDS+14400))
for arm in r1m r1Rs; do for s in 1 2 3; do
  until grep -q "\"step\": $final" $L/c1prime-loop-40-8-2-$arm-eps1-2M-d128-e15-s$s/log.jsonl 2>/dev/null; do
    [ $SECONDS -ge $end ] && { echo "=== DEADLINE waiting for $arm s$s $(date)"; exit 2; }
    grep -q -E "FAILED|exit [1-9]|REFUSED" $L/wave.log 2>/dev/null && { echo "=== the wave reported a failure $(date)"; exit 3; }
    sleep 60
  done
done; done
echo "=== all six trained $(date)"
census() {
  out=docs/learner-window-census-$1-eps1-2M-e15-seed$2-$D.json
  [ -f $out ] && { echo "skip $out"; return; }
  OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 uv run --extra learner python scripts/learner_window_census.py \
    --run $L/c1prime-loop-40-8-2-$1-eps1-2M-d128-e15-s$2 --k 7 --device cpu --raw $out \
    > $LOG/c1prime-loop-40-8-2-$1-eps1-2M-d128-e15-s$2-census-$D.log 2>&1 && echo "done $out $(date)" || { echo "FAILED census $1 $2 $(date)"; return 1; }
}
export -f census; export L LOG D
printf "r1m 1\nr1m 2\nr1m 3\nr1Rs 1\nr1Rs 2\nr1Rs 3\n" | xargs -P 6 -L 1 bash -c 'census "$@"' _ || { echo "=== a census FAILED"; exit 4; }
uv run --extra learner python scripts/relay_object_ce.py --inputs corpus/c1prime-loop-40-8-2-r1-eps1/fd5da4c31e43d73d \
  --runs $L/c1prime-loop-40-8-2-r1Rs-eps1-2M-d128-e15-s{1,2,3} > docs/relay-2x2-object-ce-r1Rs-$D.jsonl 2>/dev/null || { echo "=== object CE FAILED"; exit 6; }
echo "=== CENSUS AND LOOKUP CHECK DONE $(date)"
