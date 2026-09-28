#!/bin/bash
# GPU items owed by first-results note §22.1 (RQ5, the size axis at matched budget), launched 2026-09-28 under the
# Hamut'ay lease. Resumable; skips finished runs and finished evals.
#  - seeds 2 and 3 at 15 epochs, lr 1e-3 -> 1e-4, at d = 64 / 128 / 256 (seed 1 exists from 2026-09-24);
#  - one longer point: d = 256, seed 1, 45 epochs (does the wide model's curve pass d = 128's?).
# r1 eps = 1, 2M windows, the recipe of §22.1 otherwise. Runs are independent processes; P of them share the card
# at once (each ~65 min alone at 15 epochs on 2026-09-24, width-independent). Co-scheduling does not change any run's
# arithmetic (deterministic algorithms, fixed seeds, per-process state).
cd /home/tony/projects/yupi
L=~/.cache/yupi-scratch/runs/gpu; D=2026-09-28
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
echo "=== lease granted $(date); GPU memory used ${used} MiB"
if [ "${used:-99999}" -gt 3000 ]; then echo "=== REFUSED: card not released (${used} MiB used) $(date)"; exit 3; fi
name=c1prime-loop-40-8-2-r1-eps1; rid=fd5da4c31e43d73d
job() {  # d:lr:epochs:seed
  d=$(echo $1 | cut -d: -f1); lr=$(echo $1 | cut -d: -f2); ep=$(echo $1 | cut -d: -f3); s=$(echo $1 | cut -d: -f4)
  final=$(( 7813 * ep ))
  out=$L/$name-2M-d$d-lr$lr-e$ep-s$s; raw=docs/learner-eval-r1-eps1-2M-d$d-lr$lr-e$ep-seed$s-$D.json
  if ! grep -q "\"step\": $final" $out/log.jsonl 2>/dev/null; then
    resume=""; [ -f $out/ckpt.pt ] && resume="--resume"
    echo "=== $(basename $out) start $(date) $resume"
    uv run --extra learner python scripts/learner_train.py --corpus-dir corpus/$name/$rid --out $out --device cuda \
      --epochs $ep --ckpt-every 2000 --val-every 1000 --seed $s --d-model $d --lr $lr $resume > $out.log 2>&1
    echo "=== $(basename $out) exit $? $(date)"
  fi
  if grep -q "\"step\": $final" $out/log.jsonl 2>/dev/null && [ ! -f $raw ]; then
    echo "=== eval $(basename $out) $(date)"
    uv run --extra learner python scripts/learner_evaluate.py --run $out --device cuda --k 1,2,3,4,5,6,7 --raw $raw \
      > $out.curve.log 2>&1 && grep "^k=7" $out.curve.log || echo "=== EVAL FAILED $(basename $out)"
  fi
}
export -f job; export L D name rid
# the long run first so it is not the tail
echo ${JOBS:-256:1e-3:45:1 64:1e-3:15:2 128:1e-3:15:2 256:1e-3:15:2 64:1e-3:15:3 128:1e-3:15:3 256:1e-3:15:3} \
  | tr ' ' '\n' | xargs -P ${P:-4} -I{} bash -c 'job {}'
echo "=== GPU DONE $(date)"
