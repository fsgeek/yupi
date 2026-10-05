#!/bin/bash
# Three one-wave leases with >= 60 min gaps (design v0.2 §6; Tony 2026-10-05: the card is the ayllu's).
G=~/projects/hamutay/deploy/ayllu-gpu; L=~/.cache/yupi-scratch/runs/threearm-pilot
cd /home/tony/projects/yupi
for SEED in 101 102 103; do
  for attempt in $(seq 1 60); do
    until=$(date -d "+60 min" -Iseconds)
    $G run --holder yupi --purpose "Yupi: three-arm blind variance pilot, seed $SEED x 4 rungs, 15 ep (one wave)" \
      --ttl 90m --expected-until "$until" -- bash $L/wave.sh $SEED 2>&1 | grep -v VIRTUAL_ENV >> $L/queue.log
    if tail -5 $L/queue.log | grep -q "lease refused"; then sleep 300; continue; fi
    break
  done
  echo "=== queue: seed $SEED returned $(date); gap 60 min" >> $L/queue.log
  [ $SEED != 103 ] && sleep 3600
done
echo "=== queue: PILOT TRAINING DONE $(date)" >> $L/queue.log
