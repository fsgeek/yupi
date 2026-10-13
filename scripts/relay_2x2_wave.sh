#!/bin/bash
# Completing the relay 2x2 (docs/relay-2x2-prereg-v0.1.md): r1m (r1, OBJECT unscored) and r1Rs (r1 inputs, r1R
# targets), seeds 1-3 each, 15 epochs on the GPU, six in parallel. Run under the ayllu GPU lease. Resumable.
cd /home/tony/projects/yupi
L=~/.cache/yupi-scratch/runs/relay-2x2; A=corpus/c1prime-loop-40-8-2-r1-eps1/fd5da4c31e43d73d
B=corpus/c1prime-loop-40-8-2-r1R-eps1/fd5da4c31e43d73d; mkdir -p $L
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
echo "=== 2x2 wave lease granted $(date); GPU memory used ${used} MiB"
if [ "${used:-99999}" -gt 3000 ]; then echo "=== REFUSED: card not released"; exit 3; fi
job() {  # arm seed
  out=$L/c1prime-loop-40-8-2-$1-eps1-2M-d128-e15-s$2; final=$(( 7813 * 15 ))
  grep -q "\"step\": $final" $out/log.jsonl 2>/dev/null && { echo "=== done already $(basename $out)"; return; }
  resume=""; [ -f $out/ckpt.pt ] && resume="--resume"
  case $1 in
    r1m)  extra="--unscored-fields OBJECT" ;;
    r1Rs) extra="--target-corpus-dir $B --target-fields OBJECT" ;;
  esac
  echo "=== $(basename $out) start $(date) $resume"
  uv run --extra learner python scripts/learner_train.py --corpus-dir $A --out $out --device cuda --epochs 15 \
    --ckpt-every 2000 --val-every 1000 --seed $2 --d-model 128 --lr 1e-3 $extra $resume > $out.log 2>&1
  echo "=== $(basename $out) exit $? $(date)"
}
export -f job; export L A B
printf "r1m 1\nr1m 2\nr1m 3\nr1Rs 1\nr1Rs 2\nr1Rs 3\n" | xargs -P 6 -L 1 bash -c 'job "$@"' _
echo "=== 2x2 GPU DONE $(date)"
