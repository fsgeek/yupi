#!/bin/bash
# Census for the loss-masked relay arm (docs/relay-lossmask-prereg-v0.1.md §2): the frozen census script, CPU, k = 7.
# Waits (deadline 3 h) for all three runs' final step, then runs the three censuses in parallel. Resumable.
cd /home/tony/projects/yupi
L=~/.cache/yupi-scratch/runs/relay-lossmask; LOG=~/.cache/yupi-scratch/census; D=2026-10-13; final=$(( 7813 * 15 ))
end=$((SECONDS+10800))
for s in 1 2 3; do
  until grep -q "\"step\": $final" $L/c1prime-loop-40-8-2-r1Rm-eps1-2M-d128-e15-s$s/log.jsonl 2>/dev/null; do
    [ $SECONDS -ge $end ] && { echo "=== DEADLINE waiting for seed $s $(date)"; exit 2; }
    grep -q "exit [1-9]" $L/wave.log 2>/dev/null && { echo "=== a training job failed $(date)"; exit 3; }
    sleep 60
  done
done
echo "=== all three trained $(date)"
census() {
  out=docs/learner-window-census-r1Rm-eps1-2M-e15-seed$1-$D.json
  [ -f $out ] && { echo "skip $out"; return; }
  OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 uv run --extra learner python scripts/learner_window_census.py \
    --run $L/c1prime-loop-40-8-2-r1Rm-eps1-2M-d128-e15-s$1 --k 7 --device cpu --raw $out \
    > $LOG/c1prime-loop-40-8-2-r1Rm-eps1-2M-d128-e15-s$1-census-$D.log 2>&1 && echo "done $out $(date)" || echo "FAILED census seed $1 $(date)"
}
export -f census; export L LOG D
printf "1\n2\n3\n" | xargs -P 3 -L 1 bash -c 'census "$@"' _
echo "=== CENSUS DONE $(date)"
