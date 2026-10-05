#!/bin/bash
# One pilot wave (docs/three-arm-pilot-v0.1.md): one seed x four rungs, 15 epochs, four in parallel. Resumable.
cd /home/tony/projects/yupi
L=~/.cache/yupi-scratch/runs/threearm-pilot; SEED=$1; RUN=0582ffbeb4693d27
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
echo "=== wave seed $SEED lease granted $(date); GPU memory used ${used} MiB"
if [ "${used:-99999}" -gt 3000 ]; then echo "=== REFUSED: card not released"; exit 3; fi
job() {  # rung seed
  C=corpus/c1prime-loop-40-8-2-$1-eps1/$RUN; out=$L/c1prime-loop-40-8-2-$1-eps1-2M-d128-e15-s$2; final=$(( 7813 * 15 ))
  [ -d $C ] || { echo "=== missing corpus $C"; return 4; }
  grep -q "\"step\": $final" $out/log.jsonl 2>/dev/null && { echo "=== done already $(basename $out)"; return; }
  resume=""; [ -f $out/ckpt.pt ] && resume="--resume"
  echo "=== $(basename $out) start $(date) $resume"
  uv run --extra learner python scripts/learner_train.py --corpus-dir $C --out $out --device cuda --epochs 15 \
    --ckpt-every 2000 --val-every 1000 --seed $2 --d-model 128 --lr 1e-3 $resume > $out.log 2>&1
  echo "=== $(basename $out) exit $? $(date)"
}
export -f job; export L RUN
printf "r1 $SEED\nr1R $SEED\nr1D $SEED\nr1S $SEED\n" | xargs -P 4 -L 1 bash -c 'job "$@"' _
echo "=== wave seed $SEED GPU DONE $(date)"
