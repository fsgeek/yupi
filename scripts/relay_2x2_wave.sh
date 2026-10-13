#!/bin/bash
# Completing the relay 2x2 (docs/relay-2x2-prereg-v0.1.md): r1m (r1, OBJECT unscored) and r1Rs (r1 inputs, r1R
# targets), seeds 1-3 each, 15 epochs on the GPU, six in parallel. Run under the ayllu GPU lease. Resumable.
cd /home/tony/projects/yupi
L=~/.cache/yupi-scratch/runs/relay-2x2; A=corpus/c1prime-loop-40-8-2-r1-eps1/fd5da4c31e43d73d
B=corpus/c1prime-loop-40-8-2-r1R-eps1/fd5da4c31e43d73d; mkdir -p $L
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
echo "=== 2x2 wave lease granted $(date); GPU memory used ${used} MiB"
if [ "${used:-99999}" -gt 3000 ]; then echo "=== REFUSED: card not released"; exit 3; fi
# Gate (prereg §6): HEAD reproduces the 10-02 r1 seed-1 run's step-1000 losses exactly on this GPU.
G=$L/repro-gate-r1-s1
if ! grep -q '"step": 1000,' $G/log.jsonl 2>/dev/null; then
  uv run --extra learner python scripts/learner_train.py --corpus-dir $A --out $G --device cuda --epochs 15 \
    --ckpt-every 2000 --val-every 1000 --seed 1 --d-model 128 --lr 1e-3 --max-steps 1000 > $G.log 2>&1 || { echo "=== GATE run failed"; exit 5; }
fi
python3 - "$G/log.jsonl" <<'PY' || { echo "=== GATE FAILED: HEAD does not reproduce 10-02 r1 s1 at step 1000 $(date)"; exit 5; }
import json, sys
r = [json.loads(l) for l in open(sys.argv[1]) if '"step": 1000,' in l][0]
ok = r["train_loss"] == 0.6791265606880188 and r["val_loss"] == 0.6846594339672173
print("=== GATE", "PASS" if ok else "FAIL", r["train_loss"], r["val_loss"])
sys.exit(0 if ok else 1)
PY
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
  rc=$?; echo "=== $(basename $out) exit $rc $(date)"; return $rc
}
export -f job; export L A B
printf "r1m 1\nr1m 2\nr1m 3\nr1Rs 1\nr1Rs 2\nr1Rs 3\n" | xargs -P 6 -L 1 bash -c 'job "$@"' _ || { echo "=== a job FAILED $(date)"; exit 4; }
echo "=== 2x2 GPU DONE $(date)"
