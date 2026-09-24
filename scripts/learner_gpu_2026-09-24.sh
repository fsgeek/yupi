#!/bin/bash
# GPU items owed by first-results note §11 and §14, launched 2026-09-24 under the Hamut'ay lease. Resumable; skips finished runs.
#  A. eps = 1/2 seeds 4-6 at r2 and r4, 2M windows, the recipe of seeds 1-3 (5 epochs, d = 128, lr 1e-3 -> 1e-4); eval k = 1..7.
#  B. size axis, r1 eps = 1 at 2M, seed 1: a learning-rate sweep per width (cosine floor = lr / 10), so §11 can be read:
#     d = 64: lr 3e-3, 1e-2; d = 128: 3e-4, 3e-3; d = 256: 3e-4, 1e-4 (lr 1e-3 exists at every width).
cd /home/tony/projects/yupi
L=~/.cache/yupi-scratch/runs/gpu; D=2026-09-24
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
echo "=== lease granted $(date); GPU memory used ${used} MiB"
if [ "${used:-99999}" -gt 3000 ]; then echo "=== REFUSED: card not released (${used} MiB used) $(date)"; exit 3; fi
done_run() { grep -q '"step": 39065' $1/log.jsonl 2>/dev/null; }
train_eval() {  # name rid out raw extra-args...
  name=$1; rid=$2; out=$3; raw=$4; shift 4
  if ! done_run $out; then
    resume=""; [ -f $out/ckpt.pt ] && resume="--resume"
    echo "=== $(basename $out) start $(date) $resume"
    uv run --extra learner python scripts/learner_train.py --corpus-dir corpus/$name/$rid --out $out --device cuda --epochs 5 --ckpt-every 2000 --val-every 1000 "$@" $resume > $out.log 2>&1
    echo "=== $(basename $out) exit $? $(date)"
  fi
  if done_run $out && [ ! -f $raw ]; then
    echo "=== eval $(basename $out) $(date)"
    uv run --extra learner python scripts/learner_evaluate.py --run $out --device cuda --k 1,2,3,4,5,6,7 --raw $raw > $out.curve.log 2>&1 && grep "^k=7" $out.curve.log || echo "=== EVAL FAILED $(basename $out)"
  fi
}
# A
for pair in r2:aac405dd85f12bf6 r4:21a34684aa833e0e; do
  rung=${pair%%:*}; rid=${pair##*:}; name=c1prime-loop-40-8-2-$rung-eps1_2
  for S in 4 5 6; do
    train_eval $name $rid $L/$name-2M-s$S docs/learner-eval-$rung-eps1_2-2M-seed$S-$D.json --seed $S
  done
done
# B
name=c1prime-loop-40-8-2-r1-eps1; rid=fd5da4c31e43d73d
for pair in 64:3e-3 64:1e-2 128:3e-4 128:3e-3 256:3e-4 256:1e-4; do
  d=${pair%%:*}; lr=${pair##*:}
  train_eval $name $rid $L/$name-2M-d$d-lr$lr-s1 docs/learner-eval-r1-eps1-2M-d$d-lr$lr-seed1-$D.json --seed 1 --d-model $d --lr $lr
done
echo "=== GPU DONE $(date)"
