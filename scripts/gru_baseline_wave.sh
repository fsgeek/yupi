#!/bin/bash
# GRU baseline (docs/gru-baseline-prereg-v0.1.md): transformer reproduction gate, GRU GPU determinism check, then
# 8 GRU runs (one per r1-r4 x eps cell, seed 1, 15 epochs) in parallel. Run under the ayllu GPU lease. Resumable.
cd /home/tony/projects/yupi
L=~/.cache/yupi-scratch/runs/gru; mkdir -p $L
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
echo "=== gru wave lease granted $(date); GPU memory used ${used} MiB"
if [ "${used:-99999}" -gt 3000 ]; then echo "=== REFUSED: card not released"; exit 3; fi
R1=corpus/c1prime-loop-40-8-2-r1-eps1/fd5da4c31e43d73d
REC="--device cuda --epochs 15 --lr 1e-3 --warmup 500 --batch-size 256 --ckpt-every 2000 --val-every 1000"
# Gate 1: HEAD reproduces the 10-02 transformer r1 seed-1 step-1000 losses exactly.
G=$L/repro-gate-r1-s1
grep -q '"step": 1000,' $G/log.jsonl 2>/dev/null || uv run --extra learner python scripts/learner_train.py --corpus-dir $R1 --out $G \
  $REC --seed 1 --d-model 128 --max-steps 1000 > $G.log 2>&1 || { echo "=== GATE run failed"; exit 5; }
python3 -c "
import json,sys
r=[json.loads(l) for l in open('$G/log.jsonl') if '\"step\": 1000,' in l][0]
ok=r['train_loss']==0.6791265606880188 and r['val_loss']==0.6846594339672173
print('=== GATE transformer', 'PASS' if ok else 'FAIL', r['train_loss'], r['val_loss']); sys.exit(0 if ok else 1)" || exit 5
# Check 2 (recorded, not a stop): two identical 200-step GRU runs on the GPU give identical losses.
for t in a b; do D=$L/det-gru-$t; [ -f $D/log.jsonl ] || uv run --extra learner python scripts/learner_train.py --corpus-dir $R1 --out $D \
  $REC --seed 1 --arch gru --d-model 256 --n-layer 2 --max-steps 200 --val-every 200 > $D.log 2>&1; done
python3 -c "
import json
a=[json.loads(l) for l in open('$L/det-gru-a/log.jsonl')][-1]; b=[json.loads(l) for l in open('$L/det-gru-b/log.jsonl')][-1]
print('=== GRU GPU determinism', 'IDENTICAL' if (a['train_loss'],a.get('val_loss'))==(b['train_loss'],b.get('val_loss')) else 'DIFFERENT', a['train_loss'], b['train_loss'])"
job() {  # cell corpus
  out=$L/c1prime-loop-40-8-2-$1-2M-gru256x2-e15-s1; final=$(( 7813 * 15 ))
  grep -q "\"step\": $final" $out/log.jsonl 2>/dev/null && { echo "=== done already $(basename $out)"; return; }
  resume=""; [ -f $out/ckpt.pt ] && resume="--resume"
  echo "=== $(basename $out) start $(date) $resume"
  uv run --extra learner python scripts/learner_train.py --corpus-dir $2 --out $out $REC --seed 1 --arch gru --d-model 256 --n-layer 2 $resume > $out.log 2>&1
  rc=$?; echo "=== $(basename $out) exit $rc $(date)"; return $rc
}
export -f job; export L REC
cat <<'CELLS' | xargs -P 8 -L 1 bash -c 'job "$@"' _ || { echo "=== a job FAILED $(date)"; exit 4; }
r1-eps1 corpus/c1prime-loop-40-8-2-r1-eps1/fd5da4c31e43d73d
r2-eps1 corpus/c1prime-loop-40-8-2-r2-eps1/125f89ba98065599
r3-eps1 corpus/c1prime-loop-40-8-2-r3-eps1/b32b8f15767eae2f
r4-eps1 corpus/c1prime-loop-40-8-2-r4-eps1/ee9475787e67a1cc
r1-eps1_2 corpus/c1prime-loop-40-8-2-r1-eps1_2/76939d7414401e8b
r2-eps1_2 corpus/c1prime-loop-40-8-2-r2-eps1_2/aac405dd85f12bf6
r3-eps1_2 corpus/c1prime-loop-40-8-2-r3-eps1_2/82fa177578b77b27
r4-eps1_2 corpus/c1prime-loop-40-8-2-r4-eps1_2/21a34684aa833e0e
CELLS
echo "=== gru GPU DONE $(date)"
