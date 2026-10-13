#!/bin/bash
# The loss-masked relay arm (docs/relay-lossmask-prereg-v0.1.md): r1R, OBJECT excluded from the loss, seeds 1-3,
# 15 epochs on the GPU, then the frozen census on CPU. Run under the ayllu GPU lease. Resumable.
cd /home/tony/projects/yupi
L=~/.cache/yupi-scratch/runs/relay-lossmask; C=corpus/c1prime-loop-40-8-2-r1R-eps1/fd5da4c31e43d73d; mkdir -p $L
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
echo "=== lossmask wave lease granted $(date); GPU memory used ${used} MiB"
if [ "${used:-99999}" -gt 3000 ]; then echo "=== REFUSED: card not released"; exit 3; fi
job() {
  out=$L/c1prime-loop-40-8-2-r1Rm-eps1-2M-d128-e15-s$1; final=$(( 7813 * 15 ))
  grep -q "\"step\": $final" $out/log.jsonl 2>/dev/null && { echo "=== done already $(basename $out)"; return; }
  resume=""; [ -f $out/ckpt.pt ] && resume="--resume"
  echo "=== $(basename $out) start $(date) $resume"
  uv run --extra learner python scripts/learner_train.py --corpus-dir $C --out $out --device cuda --epochs 15 \
    --ckpt-every 2000 --val-every 1000 --seed $1 --d-model 128 --lr 1e-3 --unscored-fields OBJECT $resume > $out.log 2>&1
  rc=$?; echo "=== $(basename $out) exit $rc $(date)"; return $rc
}
export -f job; export L C
printf "1\n2\n3\n" | xargs -P 3 -L 1 bash -c 'job "$@"' _ || { echo "=== a job FAILED $(date)"; exit 4; }
echo "=== lossmask GPU DONE $(date)"
